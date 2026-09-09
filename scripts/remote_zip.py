"""Selective ZIP member access over HTTP range requests.

Purpose: read specific members (chat.jsonl, score.json) out of multi-GB WeaveBench
delivery archives without downloading screenshot payloads.

Stdlib only. Deterministic. Never mutates remote data.
"""
from __future__ import annotations

import struct
import time
import urllib.request
import zlib
from dataclasses import dataclass

UA = "Mozilla/5.0 (scene-provenance-lab; research; selective-zip-reader)"

EOCD_SIG = b"PK\x05\x06"
EOCD64_LOC_SIG = b"PK\x06\x07"
EOCD64_SIG = b"PK\x06\x06"
CEN_SIG = b"PK\x01\x02"
LOC_SIG = b"PK\x03\x04"


@dataclass(frozen=True)
class Entry:
    name: str
    compress_type: int
    compressed_size: int
    file_size: int
    header_offset: int
    crc: int


class RemoteZip:
    """Random-access reader for a remote ZIP served with Accept-Ranges: bytes."""

    def __init__(self, url: str, retries: int = 4):
        self.url = url
        self.retries = retries
        self.n_requests = 0
        self.bytes_fetched = 0
        self.size = self._content_length()
        self.entries: dict[str, Entry] = {}

    # ---- low level ----
    def _open(self, headers: dict[str, str]):
        req = urllib.request.Request(self.url, headers={"User-Agent": UA, **headers})
        return urllib.request.urlopen(req, timeout=120)

    def _content_length(self) -> int:
        last = None
        for attempt in range(self.retries):
            try:
                with self._open({"Range": "bytes=0-0"}) as r:
                    cr = r.headers.get("Content-Range")
                    if cr and "/" in cr:
                        return int(cr.rsplit("/", 1)[1])
                    return int(r.headers["Content-Length"])
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"cannot size {self.url}: {last}")

    def get(self, start: int, length: int) -> bytes:
        if length <= 0:
            return b""
        start = max(0, start)
        end = min(self.size - 1, start + length - 1)
        last = None
        for attempt in range(self.retries):
            try:
                with self._open({"Range": f"bytes={start}-{end}"}) as r:
                    data = r.read()
                self.n_requests += 1
                self.bytes_fetched += len(data)
                return data
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"range {start}-{end} failed: {last}")

    # ---- central directory ----
    def load_central_directory(self, tail: int = 128 * 1024) -> int:
        buf = self.get(self.size - tail, tail)
        i = buf.rfind(EOCD_SIG)
        if i < 0:
            raise RuntimeError("EOCD not found in tail")
        (cd_entries, cd_size, cd_off) = struct.unpack("<HII", buf[i + 10 : i + 20])

        j = buf.rfind(EOCD64_LOC_SIG, 0, i)
        if j >= 0:
            eocd64_off = struct.unpack("<Q", buf[j + 8 : j + 16])[0]
            e64 = self.get(eocd64_off, 56)
            if e64[:4] == EOCD64_SIG:
                cd_entries = struct.unpack("<Q", e64[32:40])[0]
                cd_size = struct.unpack("<Q", e64[40:48])[0]
                cd_off = struct.unpack("<Q", e64[48:56])[0]

        cd = self.get(cd_off, cd_size)
        self._parse_central(cd)
        return cd_entries

    def _parse_central(self, cd: bytes) -> None:
        p = 0
        n = len(cd)
        while p + 46 <= n and cd[p : p + 4] == CEN_SIG:
            (
                flags, method, _t, _d, crc, csize, usize, nlen, elen, clen,
                _dsk, _ia, _ea, loc_off,
            ) = struct.unpack("<HHHHIIIHHHHHII", cd[p + 8 : p + 46])
            name_raw = cd[p + 46 : p + 46 + nlen]
            extra = cd[p + 46 + nlen : p + 46 + nlen + elen]
            name = name_raw.decode("utf-8" if flags & 0x800 else "cp437", "replace")

            # ZIP64 extra field
            if 0xFFFFFFFF in (csize, usize, loc_off):
                q = 0
                while q + 4 <= len(extra):
                    hid, hsz = struct.unpack("<HH", extra[q : q + 4])
                    body = extra[q + 4 : q + 4 + hsz]
                    if hid == 0x0001:
                        k = 0
                        if usize == 0xFFFFFFFF and k + 8 <= len(body):
                            usize = struct.unpack("<Q", body[k : k + 8])[0]; k += 8
                        if csize == 0xFFFFFFFF and k + 8 <= len(body):
                            csize = struct.unpack("<Q", body[k : k + 8])[0]; k += 8
                        if loc_off == 0xFFFFFFFF and k + 8 <= len(body):
                            loc_off = struct.unpack("<Q", body[k : k + 8])[0]; k += 8
                        break
                    q += 4 + hsz
            self.entries[name] = Entry(name, method, csize, usize, loc_off, crc)
            p += 46 + nlen + elen + clen

    # ---- member read ----
    def read(self, name: str) -> bytes:
        e = self.entries[name]
        head = self.get(e.header_offset, 30)
        if head[:4] != LOC_SIG:
            raise RuntimeError(f"bad local header for {name}")
        nlen, elen = struct.unpack("<HH", head[26:30])
        data_off = e.header_offset + 30 + nlen + elen
        raw = self.get(data_off, e.compressed_size)
        if e.compress_type == 0:
            out = raw
        elif e.compress_type == 8:
            out = zlib.decompress(raw, -15)
        else:
            raise RuntimeError(f"unsupported compression {e.compress_type} for {name}")
        if len(out) != e.file_size:
            raise RuntimeError(f"size mismatch {name}: {len(out)} != {e.file_size}")
        if zlib.crc32(out) & 0xFFFFFFFF != e.crc:
            raise RuntimeError(f"CRC mismatch for {name}")
        return out


def resolve(url: str) -> str:
    """Follow redirects once to a CDN URL that supports ranges."""
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="HEAD")
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.url
