"""S2 — nested display. Where does provenance actually terminate?

The unprivileged attacker starts a nested X server (Xephyr) on the outer
display and runs a substitute scene INSIDE it. The trusted recorder observes
the OUTER display only, which is the realistic deployment: the recorder is
attached to the session it was configured for.

The question is not whether the outer recorder can be fooled about the outer
display -- it cannot. It is exactly where the provenance chain stops: what does
the outer recorder resolve the captured pixels to?

Nothing here assumes the recorder can see through the nested server. Whatever
it resolves to is recorded as the assurance boundary.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/lab")
from recorder import Recorder  # noqa: E402

OUT = "/lab/out"
DISPLAY = os.environ.get("DISPLAY", ":99")
INNER = ":77"

TK = """import tkinter as tk
root = tk.Tk(); root.title({t!r})
root.geometry("900x640+20+20")
tk.Label(root, text={t!r}, font=("DejaVu Sans", 40), bg="#00b000").pack(expand=True, fill="both")
root.mainloop()
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    work = "/lab/work"
    os.makedirs(work, exist_ok=True)
    with open(f"{work}/inner_scene.py", "w", encoding="utf-8") as fh:
        fh.write(TK.format(t="SUBSTITUTE INSIDE NESTED DISPLAY"))

    subprocess.run("pkill -u attacker Xephyr; pkill -u attacker -f inner_scene",
                   shell=True, capture_output=True)
    time.sleep(0.5)

    # attacker starts the nested server on the outer display
    xephyr = subprocess.Popen(
        ["su", "attacker", "-c",
         f"DISPLAY={DISPLAY} Xephyr {INNER} -screen 960x720 -ac -br -noreset"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    inner = subprocess.Popen(
        ["su", "attacker", "-c",
         f"DISPLAY={INNER} python3 {work}/inner_scene.py"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)

    rec = Recorder(display=DISPLAY)
    shot = f"{OUT}/s2_nested.png"
    r = rec.observe("S2_nested_compositor", trial=0, out_png=shot)

    pre = r["pre"]
    # What did the OUTER recorder resolve the pixels to?
    resolved_exe = pre.get("executable_path")
    resolved_argv = pre.get("command_line")
    resolved_title = pre.get("window_title")
    inner_visible_to_outer = False
    for w in (pre.get("visible_window_set") or []):
        if "SUBSTITUTE INSIDE NESTED" in (w.get("title") or ""):
            inner_visible_to_outer = True

    boundary = {
        "scenario_id": "S2_nested_compositor",
        "outer_display": DISPLAY,
        "inner_display": INNER,
        "outer_resolved_executable": resolved_exe,
        "outer_resolved_command_line": resolved_argv,
        "outer_resolved_window_title": resolved_title,
        "outer_resolved_pid": pre.get("active_pid"),
        "inner_window_visible_in_outer_window_set": inner_visible_to_outer,
        "outer_visible_window_titles": [w.get("title") for w in
                                        (pre.get("visible_window_set") or [])],
        "image_sha256": r["image_sha256"],
        "field_observation_failures": r["field_observation_failures"],
        "assurance_boundary": (
            "outer recorder resolves the captured pixels to the NESTED X SERVER "
            "process, not to the process that drew them"
            if resolved_exe and "Xephyr" in str(resolved_exe)
            else "see outer_resolved_* fields"),
    }
    with open(f"{OUT}/s2_nested.json", "w", encoding="utf-8") as fh:
        json.dump({"boundary": boundary, "record": r}, fh, indent=2)

    inner.kill(); xephyr.kill()
    subprocess.run("pkill -u attacker Xephyr; pkill -u attacker -f inner_scene",
                   shell=True, capture_output=True)
    print(json.dumps(boundary, indent=2))


if __name__ == "__main__":
    main()
