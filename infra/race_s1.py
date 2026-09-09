"""S1 — recorder atomicity race, executed for real with repeated trials.

An unprivileged attacker alternates which of two real windows is raised, at a
period deliberately close to the recorder's metadata+capture interval. The
recorder samples metadata, grabs pixels, then samples metadata again.

PRIMARY INVARIANT
-----------------
The recorder must never attest metadata describing one scene while the captured
pixels come from another.

Two independent mismatch detectors, because neither alone is sufficient:

  1. metadata inconsistency  pre-snapshot active window/pid != post-snapshot
     (the recorder's own state moved across the capture)

  2. pixel/metadata disagreement  the captured image is compared against
     reference renderings of each window; if the pixels match window B while
     the metadata attests window A, that is a hard mismatch of the invariant.

Zero failures in a small sample is NOT evidence the race is closed, and the
report says so.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/lab")
from recorder import Recorder  # noqa: E402

OUT = "/lab/out"
DISPLAY = os.environ.get("DISPLAY", ":99")
TRIALS = int(os.environ.get("S1_TRIALS", "120"))

TK = """import tkinter as tk
root = tk.Tk(); root.title({t!r})
root.geometry("1280x1024+0+0")
tk.Label(root, text={t!r}, font=("DejaVu Sans", 90), bg={bg!r}).pack(expand=True, fill="both")
root.mainloop()
"""


def mean_color(png):
    """Mean RGB of the captured image, used to identify which window was shown."""
    p = subprocess.run(
        f"convert {png} -resize 1x1 -format '%[fx:int(255*r)],%[fx:int(255*g)],%[fx:int(255*b)]' info:",
        shell=True, capture_output=True, text=True)
    try:
        return tuple(int(x) for x in p.stdout.strip().split(","))
    except Exception:  # noqa: BLE001
        return None


def main():
    os.makedirs(f"{OUT}/s1", exist_ok=True)
    work = "/lab/work"
    os.makedirs(work, exist_ok=True)
    # two visually unmistakable full-screen windows: near-red and near-blue
    for name, bg in (("SCENE_A", "#e00000"), ("SCENE_B", "#0000e0")):
        with open(f"{work}/{name}.py", "w", encoding="utf-8") as fh:
            fh.write(TK.format(t=name, bg=bg))
    subprocess.run("pkill -u attacker -f 'python3 /lab/work/SCENE' ",
                   shell=True, capture_output=True)
    for name in ("SCENE_A", "SCENE_B"):
        subprocess.Popen(["su", "attacker", "-c",
                          f"DISPLAY={DISPLAY} python3 {work}/{name}.py"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)

    # attacker flips the stack continuously, as an unprivileged user
    flipper = subprocess.Popen(
        ["su", "attacker", "-c",
         f"while true; do DISPLAY={DISPLAY} wmctrl -a SCENE_A; sleep 0.05; "
         f"DISPLAY={DISPLAY} wmctrl -a SCENE_B; sleep 0.05; done"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    rec = Recorder(display=DISPLAY)
    trials = []
    try:
        for i in range(TRIALS):
            shot = f"{OUT}/s1/trial_{i:04d}.png"
            r = rec.observe("S1_recorder_race", trial=i, out_png=shot)
            rgb = mean_color(shot)
            pre_t = (r["pre"].get("window_title") or "")
            post_t = (r["post"].get("window_title") or "")
            # which scene do the pixels actually show?
            pixel_scene = None
            if rgb:
                pixel_scene = "SCENE_A" if rgb[0] > rgb[2] else "SCENE_B"
            meta_scene = "SCENE_A" if "SCENE_A" in pre_t else (
                "SCENE_B" if "SCENE_B" in pre_t else None)
            meta_inconsistent = not r["atomicity_consistent"]
            pixel_mismatch = (pixel_scene is not None and meta_scene is not None
                              and pixel_scene != meta_scene)
            trials.append({
                "trial": i,
                "pre_title": pre_t, "post_title": post_t,
                "meta_scene": meta_scene, "pixel_scene": pixel_scene,
                "mean_rgb": rgb,
                "metadata_inconsistent": meta_inconsistent,
                "pixel_metadata_mismatch": pixel_mismatch,
                "invariant_violated": bool(meta_inconsistent or pixel_mismatch),
                "skew_ms": r["metadata_capture_skew_ms"],
                "image_sha256": r["image_sha256"],
            })
            if (i + 1) % 20 == 0:
                v = sum(1 for t in trials if t["invariant_violated"])
                print(f"  {i+1}/{TRIALS} trials, {v} invariant violations", flush=True)
            os.remove(shot)      # disposable; hashes retained
    finally:
        flipper.kill()
        subprocess.run("pkill -u attacker -f 'python3 /lab/work/SCENE'; "
                       "pkill -u attacker -f 'while true'",
                       shell=True, capture_output=True)

    viol = [t for t in trials if t["invariant_violated"]]
    summary = {
        "trials": len(trials),
        "metadata_inconsistent": sum(1 for t in trials if t["metadata_inconsistent"]),
        "pixel_metadata_mismatch": sum(1 for t in trials if t["pixel_metadata_mismatch"]),
        "invariant_violations": len(viol),
        "violation_rate_pct": round(100 * len(viol) / len(trials), 2) if trials else None,
        "skew_ms_min": min((t["skew_ms"] for t in trials), default=None),
        "skew_ms_max": max((t["skew_ms"] for t in trials), default=None),
        "note": "Zero violations does NOT establish the race is closed; it bounds it "
                "only at this trial count and this scheduling regime.",
        "detail": trials,
    }
    with open(f"{OUT}/s1_race.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "detail"}, indent=2))


if __name__ == "__main__":
    main()
