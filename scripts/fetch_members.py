"""Selectively fetch WeaveBench delivery-archive members and record source provenance.

Writes:
  outputs/cache/cd_<run>.json      central directory index (member -> size/offset)
  outputs/raw/<run>/<path>         extracted member bytes (never mutated)
  outputs/source_manifest.csv      archive URL, member path, sizes, sha256, timestamp

Usage:
  python scripts/fetch_members.py index
  python scripts/fetch_members.py fetch --basenames score.json,results_manifest.txt
  python scripts/fetch_members.py fetch --basenames chat.jsonl --tasks-file <file>
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from remote_zip import RemoteZip, resolve  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://huggingface.co/datasets/wanlilll/weavebench-traj/resolve/main/gpt-5.4/"
ARCHIVES = {"run1": BASE + "deliver_low_run1.zip", "run2": BASE + "deliver_low_run2.zip"}
CACHE = os.path.join(ROOT, "outputs", "cache")
RAW = os.path.join(ROOT, "outputs", "raw")
MANIFEST = os.path.join(ROOT, "outputs", "source_manifest.csv")

MANIFEST_FIELDS = [
    "run", "task", "archive_url", "archive_member_path", "member_basename",
    "content_length_uncompressed", "content_length_compressed",
    "sha256", "fetch_timestamp_utc", "zip_crc32",
]


def task_of(member: str) -> str:
    """results/<runid>/gui/<model>/<domain>/<task>/<file> -> <task>."""
    parts = member.split("/")
    return parts[-2] if len(parts) >= 2 else ""


def domain_of(member: str) -> str:
    parts = member.split("/")
    return parts[-3] if len(parts) >= 3 else ""


def open_zip(run: str) -> RemoteZip:
    z = RemoteZip(resolve(ARCHIVES[run]))
    cd_path = os.path.join(CACHE, f"cd_{run}.json")
    if os.path.exists(cd_path):
        raw = json.load(open(cd_path))
        if raw.get("_size") == z.size:
            from remote_zip import Entry
            z.entries = {n: Entry(n, *v) for n, v in raw["entries"].items()}
            return z
    z.load_central_directory()
    os.makedirs(CACHE, exist_ok=True)
    json.dump(
        {"_size": z.size, "_url": ARCHIVES[run],
         "entries": {n: [e.compress_type, e.compressed_size, e.file_size, e.header_offset, e.crc]
                     for n, e in z.entries.items()}},
        open(cd_path, "w"),
    )
    return z


def load_manifest() -> dict[tuple[str, str], dict]:
    if not os.path.exists(MANIFEST):
        return {}
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        return {(r["run"], r["archive_member_path"]): r for r in csv.DictReader(f)}


def save_manifest(rows: dict[tuple[str, str], dict]) -> None:
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        w.writeheader()
        for k in sorted(rows):
            w.writerow(rows[k])


def cmd_index(args) -> None:
    for run in ARCHIVES:
        z = open_zip(run)
        print(f"{run}: size={z.size} entries={len(z.entries)}")


def cmd_fetch(args) -> None:
    wanted = set(args.basenames.split(","))
    only_tasks = None
    if args.tasks_file:
        only_tasks = {ln.strip() for ln in open(args.tasks_file) if ln.strip()}
    man = load_manifest()
    for run in (args.runs.split(",") if args.runs else list(ARCHIVES)):
        z = open_zip(run)
        targets = [
            n for n in sorted(z.entries)
            if n.rsplit("/", 1)[-1] in wanted
            and (only_tasks is None or f"{run}:{task_of(n)}" in only_tasks or task_of(n) in only_tasks)
        ]
        print(f"[{run}] {len(targets)} members to consider", flush=True)
        for i, name in enumerate(targets, 1):
            out = os.path.join(RAW, run, name)
            if (run, name) in man and os.path.exists(out):
                continue
            data = z.read(name)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "wb") as f:
                f.write(data)
            e = z.entries[name]
            man[(run, name)] = {
                "run": run, "task": task_of(name), "archive_url": ARCHIVES[run],
                "archive_member_path": name, "member_basename": name.rsplit("/", 1)[-1],
                "content_length_uncompressed": e.file_size,
                "content_length_compressed": e.compressed_size,
                "sha256": hashlib.sha256(data).hexdigest(),
                "fetch_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "zip_crc32": f"{e.crc:08x}",
            }
            if i % 20 == 0 or i == len(targets):
                print(f"  {i}/{len(targets)} fetched={z.bytes_fetched/1e6:.1f}MB", flush=True)
                save_manifest(man)
    save_manifest(man)
    print("manifest rows:", len(man))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(required=True)
    p = sub.add_parser("index"); p.set_defaults(func=cmd_index)
    p = sub.add_parser("fetch")
    p.add_argument("--basenames", required=True)
    p.add_argument("--tasks-file", default=None)
    p.add_argument("--runs", default=None)
    p.set_defaults(func=cmd_fetch)
    a = ap.parse_args()
    a.func(a)
