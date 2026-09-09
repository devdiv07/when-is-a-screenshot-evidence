"""Fetch WeaveBench task specifications (independent of the judge).

Task .md files define the *required target application/state*. Using them keeps
target definitions independent of judge-produced score.json fields.
"""
from __future__ import annotations
import csv, hashlib, json, os, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "wanlilll/WeaveBench"
API = f"https://huggingface.co/api/datasets/{REPO}"
RAWBASE = f"https://huggingface.co/datasets/{REPO}/resolve/main/"
OUT = os.path.join(ROOT, "outputs", "raw", "tasks")
MANIFEST = os.path.join(ROOT, "outputs", "source_manifest.csv")
UA = {"User-Agent": "Mozilla/5.0 (scene-provenance-lab; research)"}
FIELDS = ["run","task","archive_url","archive_member_path","member_basename",
          "content_length_uncompressed","content_length_compressed","sha256",
          "fetch_timestamp_utc","zip_crc32"]

def get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()

def main() -> None:
    tree = json.loads(get(f"{API}/tree/main/tasks?recursive=1").decode())
    mds = [t["path"] for t in tree if t.get("type") == "file" and t["path"].endswith(".md")]
    print("task md files:", len(mds))
    rows = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, newline="", encoding="utf-8") as f:
            rows = {(r["run"], r["archive_member_path"]): r for r in csv.DictReader(f)}
    for i, p in enumerate(mds, 1):
        dest = os.path.join(OUT, p.replace("tasks/", "", 1))
        if ("taskspec", p) in rows and os.path.exists(dest):
            continue
        data = get(RAWBASE + urllib.request.quote(p))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        rows[("taskspec", p)] = {
            "run": "taskspec", "task": os.path.basename(p)[:-3],
            "archive_url": RAWBASE + p, "archive_member_path": p,
            "member_basename": os.path.basename(p),
            "content_length_uncompressed": len(data), "content_length_compressed": "",
            "sha256": hashlib.sha256(data).hexdigest(),
            "fetch_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "zip_crc32": "",
        }
        if i % 25 == 0: print(f"  {i}/{len(mds)}", flush=True)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for k in sorted(rows): w.writerow(rows[k])
    print("manifest rows:", len(rows))

if __name__ == "__main__":
    main()
