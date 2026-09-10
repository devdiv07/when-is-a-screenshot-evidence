"""Run cases P and R on BOTH platforms and emit raw observations.

    case constructor (attacker, uid 1000)
      -> real desktop state on the chosen platform
      -> trusted platform recorder (root)      <- derives every field itself
      -> raw provenance record

Ground truth is written by the constructor into /lab/out/ground_truth/ and is NEVER read
here. Binding assignment happens off-box in scripts/platform_matrix.py, from the raw
records only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/lab")
from platform_recorder import PlatformRecorder, RECORDER_VERSION  # noqa: E402

OUT = "/lab/out"
RAW = os.path.join(OUT, "raw")
SHOTS = os.path.join(OUT, "shots")
TARGET = "/lab/work/quarterly_report.png"


def stack_status():
    st = {}
    p = os.path.join(OUT, "stack_status")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                st[k] = v
    return st


def wayland_env():
    env = {}
    p = os.path.join(OUT, "wayland_env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                env[k] = v
    return env


def clean(platform):
    subprocess.run("pkill -9 -u attacker", shell=True, capture_output=True)
    deadline = time.time() + 12
    while time.time() < deadline:
        if platform == "x11":
            p = subprocess.run(f"DISPLAY={os.environ.get('DISPLAY', ':99')} wmctrl -l",
                               shell=True, capture_output=True, text=True)
            if p.returncode == 0 and not p.stdout.strip():
                time.sleep(0.4)
                return True
        else:
            e = dict(os.environ)
            e.update(wayland_env())
            p = subprocess.run("swaymsg -t get_tree -r", shell=True, capture_output=True,
                               text=True, env=e)
            if p.returncode == 0 and '"pid"' not in p.stdout:
                time.sleep(0.4)
                return True
        time.sleep(0.3)
    return False


def run_case(platform, case_id):
    clean(platform)
    e = dict(os.environ)
    e.update(wayland_env())
    e["LAB_PLATFORM"] = platform
    envprefix = " ".join(f"{k}={v}" for k, v in
                         {"LAB_PLATFORM": platform,
                          "SWAYSOCK": e.get("SWAYSOCK", ""),
                          "XDG_RUNTIME_DIR": e.get("XDG_RUNTIME_DIR", ""),
                          "WAYLAND_DISPLAY": e.get("WAYLAND_DISPLAY", ""),
                          "DISPLAY": os.environ.get("DISPLAY", ":99")}.items() if v)
    proc = subprocess.run(
        ["su", "attacker", "-c", f"cd /lab && {envprefix} python3 /lab/cases.py {case_id}"],
        capture_output=True, text=True, timeout=180)
    construction = {"stdout": proc.stdout.strip()[:400], "stderr": proc.stderr.strip()[:800],
                    "returncode": proc.returncode}
    time.sleep(1.0)

    rec = PlatformRecorder(platform)
    png = os.path.join(SHOTS, f"{platform}_{case_id}.png")
    out = rec.observe(f"{case_id}", png, declared_target=TARGET)
    out["construction"] = construction
    out["stack_status"] = stack_status()
    with open(os.path.join(RAW, f"{platform}_{case_id}.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    fail = len(out["field_observation_failures"])
    print(f"[{platform}/{case_id}] surfaces="
          f"{len(out['display_state_pre'].get('surfaces') or [])} "
          f"active_pid={out['display_state_pre'].get('active_pid')} "
          f"sha={str(out['capture'].get('capture_bytes_sha256'))[:12]} "
          f"failures={fail}")
    return out


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    st = stack_status()
    print("stack:", st)

    platforms = []
    if st.get("x11") == "up":
        platforms.append("x11")
    else:
        print("X11 arm BLOCKED:", st)
    if st.get("wayland") == "up":
        platforms.append("wayland")
    else:
        print("WAYLAND arm BLOCKED:", st)

    results = []
    for platform in platforms:
        for case_id in ("P", "R"):
            try:
                results.append(run_case(platform, case_id))
            except Exception as exc:  # noqa: BLE001
                print(f"[{platform}/{case_id}] FAILED: {exc}")
                results.append({"platform": platform, "case_id": case_id,
                                "run_error": str(exc)[:400]})

    # The standard capture API is probed once, as the compositor session user, because
    # that is the only identity the portal will talk to.
    if st.get("wayland") == "up":
        e = dict(os.environ)
        e.update(wayland_env())
        e["XDG_CURRENT_DESKTOP"] = "sway"
        subprocess.run(
            ["setpriv", "--reuid=1001", "--regid=1001", "--init-groups", "env",
             f"XDG_RUNTIME_DIR={e.get('XDG_RUNTIME_DIR', '/run/user/1001')}",
             f"WAYLAND_DISPLAY={e.get('WAYLAND_DISPLAY', 'wayland-1')}",
             f"DBUS_SESSION_BUS_ADDRESS={e.get('DBUS_SESSION_BUS_ADDRESS', '')}",
             "XDG_CURRENT_DESKTOP=sway",
             "python3", "/lab/portal_probe.py", "/lab/out/portal_probe.json"],
            capture_output=True, text=True, timeout=180)
        if os.path.exists("/lab/out/portal_probe.json"):
            pp = json.load(open("/lab/out/portal_probe.json", encoding="utf-8"))
            print("portal probe:", {k: v for k, v in pp.items()
                                    if k in ("portal_on_bus", "available_source_types",
                                             "session_completed", "blocked",
                                             "blocked_reason",
                                             "stream_exposes_client_identity")})

    with open(os.path.join(OUT, "platform_records.json"), "w", encoding="utf-8") as fh:
        json.dump({"recorder_version": RECORDER_VERSION, "stack_status": st,
                   "records": results}, fh, indent=2)
    print(f"wrote {len(results)} records")


if __name__ == "__main__":
    main()
