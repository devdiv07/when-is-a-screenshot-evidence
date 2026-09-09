"""Orchestrate the empirical arm inside the container.

Architecture (strict ground-truth separation):

    scenario constructor (unprivileged attacker)
      -> real desktop state
      -> trusted recorder (root)            <- derives every field itself
      -> provenance record  (raw JSON)
      -> adjudicator                        <- never sees ground truth
      -> verdict
    only then: verdict + hidden ground truth -> scoring

Writes raw observations to /lab/out/raw/ SEPARATELY from adjudicator output.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/lab")
from recorder import Recorder, RECORDER_VERSION  # noqa: E402

OUT = "/lab/out"
RAW = os.path.join(OUT, "raw")
SHOTS = os.path.join(OUT, "shots")
DISPLAY = os.environ.get("DISPLAY", ":99")

SCENARIOS = [
    "01_genuine_target", "11_direct_synthesis", "02_tk_honest_title",
    "03_tk_spoofed_identity", "04_interpreter_argv_visible",
    "04b_interpreter_argv_hidden", "13_viewer_agent_image_argv",
    "13b_viewer_agent_image_hidden", "06_target_killed_before_capture",
    "07_overlay_above_target", "08_composite_frame",
    "12_capture_of_agent_renderer", "S3_prestaged_renderer",
]


def clean_desktop(timeout=12.0):
    """IC-2: kill every attacker-owned process, then WAIT for zero managed windows."""
    subprocess.run("pkill -9 -u attacker", shell=True, capture_output=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        p = subprocess.run(f"DISPLAY={DISPLAY} wmctrl -l", shell=True,
                           capture_output=True, text=True)
        if p.returncode == 0 and not p.stdout.strip():
            time.sleep(0.4)
            return True
        time.sleep(0.3)
    return False


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    jp = os.path.join(OUT, "write_journal.jsonl")
    open(jp, "w").close()
    os.chmod(jp, 0o666)      # attacker appends, recorder reads
    os.makedirs(os.path.join(OUT, "ground_truth"), exist_ok=True)

    rec = Recorder(display=DISPLAY)
    results = []
    for sid in SCENARIOS:
        clean_desktop()
        # scenario built by the UNPRIVILEGED attacker
        p = subprocess.run(
            ["su", "attacker", "-c",
             f"cd /lab && DISPLAY={DISPLAY} python3 /lab/scenarios.py {sid}"],
            capture_output=True, text=True, timeout=120)
        if p.returncode != 0:
            results.append({"scenario_id": sid, "construction_failed": True,
                            "stderr": p.stderr[-500:]})
            print(f"[{sid}] CONSTRUCTION FAILED: {p.stderr[-200:]}", flush=True)
            continue
        shot = os.path.join(SHOTS, f"{sid}.png")
        record = rec.observe(sid, trial=0, out_png=shot)
        with open(os.path.join(RAW, f"{sid}.json"), "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2)
        results.append(record)
        aw = (record.get("pre") or {}).get("window_title")
        print(f"[{sid}] pid={record['pre'].get('active_pid')} "
              f"title={aw!r} sha={record['image_sha256'][:12]} "
              f"fails={len(record['field_observation_failures'])}", flush=True)

    with open(os.path.join(OUT, "empirical_records.json"), "w", encoding="utf-8") as fh:
        json.dump({"recorder_version": RECORDER_VERSION, "records": results}, fh, indent=2)
    clean_desktop()
    print(f"\nwrote {len(results)} records")


if __name__ == "__main__":
    main()
