"""Prove the adjudicator cannot read scenario ground truth.

Three independent checks:
  1. static  - no adjudicator-side source mentions the ground-truth path
  2. dynamic - open() of anything under ground_truth/ raises while adjudicating
  3. content - ground truth exists and is non-trivial, so the guard is meaningful
"""
from __future__ import annotations
import builtins, glob, json, os, sys

OUT = "/lab/out"
GT = os.path.join(OUT, "ground_truth")
FAIL = []

# ---- 1. static ----
for src in ("/lab/adjudicator.py", "/lab/adjudicate_empirical.py", "/lab/recorder.py"):
    text = open(src, encoding="utf-8").read()
    for line in text.splitlines():
        s = line.strip()
        if "ground_truth" not in s:
            continue
        # allowed: comments, and the assertion/marker in adjudicate_empirical
        if s.startswith("#") or s.startswith('"') or "NEVER read" in s or "never read" in s:
            continue
        if "GROUND_TRUTH_DIR" in s and "referenced only" in s:
            continue
        if 'assert not any("ground_truth"' in s:
            continue
        FAIL.append(f"static: {src}: {s[:90]}")

# ---- 3. content ----
gts = glob.glob(os.path.join(GT, "*.json"))
if not gts:
    FAIL.append("content: no ground-truth files exist; guard would be vacuous")

# ---- 2. dynamic ----
_real_open = builtins.open
opened = []
def guard(path, *a, **k):
    p = str(path)
    opened.append(p)
    if "ground_truth" in p:
        raise AssertionError(f"ADJUDICATOR READ GROUND TRUTH: {p}")
    return _real_open(path, *a, **k)

builtins.open = guard
try:
    sys.path.insert(0, "/lab")
    import adjudicate_empirical
    adjudicate_empirical.main()
except AssertionError as e:
    FAIL.append(f"dynamic: {e}")
finally:
    builtins.open = _real_open

leaked = [p for p in opened if "ground_truth" in p]
if leaked:
    FAIL.append(f"dynamic: touched {leaked[:3]}")

print(json.dumps({
    "ground_truth_files": len(gts),
    "files_opened_during_adjudication": len(opened),
    "ground_truth_touched": leaked,
    "failures": FAIL,
    "PASS": not FAIL,
}, indent=2))
sys.exit(1 if FAIL else 0)
