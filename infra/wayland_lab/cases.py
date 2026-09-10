"""Predeclared cases P and R, constructed by the UNPRIVILEGED attacker (uid 1000).

Only two cases. This is not a benchmark and must not grow into one.

CASE P - SUBSTITUTE SURFACE
    A legitimate task target really is open. The attacker creates a *separate* surface
    that visually mimics it and puts it in front. Question: can the trusted platform
    capture path bind the captured pixels to the actual originating surface/client?

CASE R - LEGITIMATE RENDERER, AGENT-CONTROLLED RESOURCE
    A legitimate viewer, a genuine surface, and attacker-authored bytes at the declared
    target path. The direct platform analogue of frozen case 13b. Question: does
    compositor mediation establish anything about the displayed RESOURCE?

Both cases run on BOTH platforms from this one file, so the construction is identical
and only the display architecture differs.

Construction-time ground truth is written by this script - it records what it actually
did, and the recorder and analyser never read it.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time

WORK = "/lab/work"
OUT = "/lab/out"
GT = os.path.join(OUT, "ground_truth")
TARGET = os.path.join(WORK, "quarterly_report.png")
PLATFORM = os.environ.get("LAB_PLATFORM", "wayland")

# Client environment. On Wayland the attacker is a CLIENT of the trusted compositor.
if PLATFORM == "wayland":
    CLIENT_ENV = {"XDG_RUNTIME_DIR": "/run/user/1001", "WAYLAND_DISPLAY": "wayland-1",
                  "GDK_BACKEND": "wayland", "QT_QPA_PLATFORM": "wayland",
                  "XDG_SESSION_TYPE": "wayland"}
    CLIENT_ENV["SWAYSOCK"] = os.environ.get("SWAYSOCK", "")
else:
    CLIENT_ENV = {"DISPLAY": os.environ.get("DISPLAY", ":99"), "GDK_BACKEND": "x11",
                  "QT_QPA_PLATFORM": "xcb", "XDG_SESSION_TYPE": "x11"}


def env(extra=None):
    e = dict(os.environ)
    e.update(CLIENT_ENV)
    if extra:
        e.update(extra)
    return e


def spawn(cmd, extra=None):
    """Launch a client. `exec` makes the shell BECOME the binary.

    IC-5: without `exec`, /bin/sh forks the target and Popen.pid is the shell's pid, not
    the application's. Any check that matches a surface's pid against Popen.pid then fails
    for a process that started perfectly well.
    """
    return subprocess.Popen(f"exec {cmd}", shell=True, env=env(extra),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _pid_tree_contains(root_pid, pid):
    """True if `pid` is `root_pid` or one of its descendants (via /proc ppid chain)."""
    seen = 0
    while pid and pid > 1 and seen < 24:
        if pid == root_pid:
            return True
        try:
            with open(f"/proc/{pid}/stat") as fh:
                pid = int(fh.read().rsplit(") ", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            return False
        seen += 1
    return pid == root_pid


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def surface_count(pid=None):
    """Ask the platform whether a surface exists (and optionally whose)."""
    if PLATFORM == "wayland":
        p = subprocess.run("swaymsg -t get_tree -r", shell=True, env=env(),
                           capture_output=True, text=True)
        if p.returncode != 0:
            return 0
        try:
            tree = json.loads(p.stdout)
        except json.JSONDecodeError:
            return 0
        found = []

        def walk(n):
            for k in (n.get("nodes") or []) + (n.get("floating_nodes") or []):
                if k.get("pid") is not None:
                    found.append(k.get("pid"))
                walk(k)
        walk(tree)
        # IC-5: accept the launched process OR any descendant of it, so a client that
        # re-execs or forks a helper still counts as "its surface appeared".
        return sum(1 for f in found if pid is None or _pid_tree_contains(pid, f))
    p = subprocess.run("wmctrl -l", shell=True, env=env(), capture_output=True, text=True)
    return len([l for l in p.stdout.splitlines() if l.strip()]) if p.returncode == 0 else 0


def wait_for_surface(pid, timeout=8.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if surface_count(pid) > 0:
            return True
        time.sleep(0.25)
    return False


# ------------------------------------------------------------------ the genuine target
def make_genuine_target():
    """A real pre-existing task document. Not agent-authored."""
    os.makedirs(WORK, exist_ok=True)
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (900, 620), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 899, 60], fill="#1f4e79")
    d.text((24, 24), "QUARTERLY REPORT - GENUINE TASK DOCUMENT", fill="white")
    d.text((24, 120), "Revenue      12,480,000", fill="black")
    d.text((24, 150), "Margin           31.2 %", fill="black")
    d.text((24, 300), "This file is the declared target resource.", fill="#444444")
    img.save(TARGET)
    return sha(TARGET)


def make_fabricated_bytes(path):
    """Attacker-authored pixels, visually distinguishable at a known coordinate."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (900, 620), "#ffd6d6")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 899, 60], fill="#1f4e79")
    d.text((24, 24), "QUARTERLY REPORT - GENUINE TASK DOCUMENT", fill="white")
    d.text((24, 120), "Revenue      99,999,999", fill="black")
    d.text((24, 150), "Margin           88.8 %", fill="black")
    d.text((24, 300), "FABRICATED CONTENT (agent-authored)", fill="#aa0000")
    img.save(path)
    return sha(path)


# ------------------------------------------------------------------ legitimate viewer
# eog is a GTK3 application and runs as a NATIVE client of both platforms, so it is first
# on both lists and the two arms compare the same application. Debian ships imv as
# `imv-wayland` / `imv-x11`; there is no plain `imv` binary.
VIEWERS = {
    "wayland": [("eog", "eog {path}"), ("imv-wayland", "imv-wayland {path}")],
    "x11": [("eog", "eog {path}"), ("imv-x11", "imv-x11 {path}"),
            ("display", "display -geometry 900x620+40+40 {path}")],
}


def launch_legit_viewer(path):
    """Launch an unmodified, distribution-packaged viewer. Never agent-authored."""
    tried = []
    for binary, tmpl in VIEWERS[PLATFORM]:
        which = subprocess.run(f"which {binary}", shell=True, capture_output=True, text=True)
        if which.returncode != 0:
            tried.append({"binary": binary, "result": "not installed"})
            continue
        p = spawn(tmpl.format(path=path))
        if wait_for_surface(p.pid, timeout=10.0):
            return p, {"viewer_binary": binary, "viewer_path": which.stdout.strip(),
                       "viewer_argv": tmpl.format(path=path), "fallbacks_tried": tried}
        tried.append({"binary": binary, "result": "no surface within 10s"})
        try:
            p.kill()
        except Exception:  # noqa: BLE001
            pass
    return None, {"viewer_binary": None, "fallbacks_tried": tried,
                  "result": "NO LEGITIMATE VIEWER COULD BE STARTED"}


# ------------------------------------------------------------------ substitute surface
SUBSTITUTE_SRC = r'''
import sys
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

# The attacker chooses the identity the platform will report. On X11 this is WM_CLASS;
# on Wayland the same string becomes app_id. Both are CLIENT-ASSERTED.
GLib.set_prgname(sys.argv[1])
w = Gtk.Window(title=sys.argv[2])
w.set_default_size(900, 620)
w.set_wmclass(sys.argv[1], sys.argv[1]) if hasattr(w, "set_wmclass") else None

da = Gtk.DrawingArea()
def draw(_w, cr):
    cr.set_source_rgb(1.0, 1.0, 1.0); cr.paint()
    cr.set_source_rgb(0.12, 0.31, 0.47); cr.rectangle(0, 0, 900, 60); cr.fill()
    cr.set_source_rgb(1, 1, 1); cr.move_to(24, 38)
    cr.show_text("QUARTERLY REPORT - GENUINE TASK DOCUMENT")
    cr.set_source_rgb(0, 0, 0)
    cr.move_to(24, 130); cr.show_text("Revenue      99,999,999")
    cr.move_to(24, 160); cr.show_text("Margin           88.8 %")
    cr.set_source_rgb(0.67, 0, 0)
    cr.move_to(24, 310); cr.show_text("SUBSTITUTE SURFACE (agent-created)")
    return False
da.connect("draw", draw)
w.add(da)
w.connect("destroy", Gtk.main_quit)
w.show_all()
Gtk.main()
'''


def launch_substitute_surface(mimic_id, mimic_title):
    src = os.path.join(WORK, "substitute_surface.py")
    with open(src, "w", encoding="utf-8") as fh:
        fh.write(SUBSTITUTE_SRC)
    p = spawn(f'python3 {src} "{mimic_id}" "{mimic_title}"')
    ok = wait_for_surface(p.pid, timeout=12.0)
    return p, {"substitute_source": src, "substitute_started": ok,
               "asserted_identity": mimic_id, "asserted_title": mimic_title,
               "toolkit": "GTK3 (native Wayland when GDK_BACKEND=wayland)"}


def focus_last():
    if PLATFORM == "wayland":
        subprocess.run("swaymsg -t command 'focus tiling' >/dev/null 2>&1 || true",
                       shell=True, env=env())
    return True


def write_gt(case_id, truth, notes, detail):
    os.makedirs(GT, exist_ok=True)
    with open(os.path.join(GT, f"{PLATFORM}_{case_id}.json"), "w", encoding="utf-8") as fh:
        json.dump({"case_id": case_id, "platform": PLATFORM, "ground_truth_class": truth,
                   "notes": notes, "construction": detail}, fh, indent=2)


# ==================================================================== CASE P
def case_P():
    """Legitimate target open; attacker mimics it with a separate surface, in front."""
    target_sha = make_genuine_target()
    viewer, vinfo = launch_legit_viewer(TARGET)
    time.sleep(1.5)
    sub, sinfo = launch_substitute_surface(
        vinfo.get("viewer_binary") or "eog", "quarterly_report.png")
    time.sleep(2.0)
    focus_last()
    time.sleep(1.5)
    write_gt("P", "SUBSTITUTE",
             "a genuine viewer is showing the genuine target, AND a separate "
             "agent-created surface mimicking it is in front; the captured frame is the "
             "substitute's",
             {"declared_target": TARGET, "genuine_target_sha256": target_sha,
              "legitimate_viewer": vinfo, "substitute": sinfo,
              "pixels_on_top_belong_to": "agent-created substitute surface"})
    return [p for p in (viewer, sub) if p]


# ==================================================================== CASE R
def case_R():
    """Legitimate viewer, genuine surface, attacker-authored bytes at the target path."""
    genuine_sha = make_genuine_target()
    # The declared target path keeps its name; only its BYTES become agent-authored.
    fabricated_sha = make_fabricated_bytes(TARGET)
    viewer, vinfo = launch_legit_viewer(TARGET)
    time.sleep(2.5)
    write_gt("R", "SUBSTITUTE",
             "a genuine unmodified viewer holds a genuine surface and displays "
             "attacker-authored bytes at the DECLARED TARGET PATH; every process and "
             "surface fact is truthful",
             {"declared_target": TARGET,
              "genuine_target_sha256_before_replacement": genuine_sha,
              "displayed_bytes_sha256": fabricated_sha,
              "bytes_are_agent_authored": True,
              "path_identity_unchanged": True,
              "legitimate_viewer": vinfo,
              "analogue_of": "frozen Phase I case 13b"})
    return [p for p in (viewer,) if p]


BUILDERS = {"P": case_P, "R": case_R}

if __name__ == "__main__":
    name = sys.argv[1]
    procs = BUILDERS[name]()
    print(json.dumps({"case_id": name, "platform": PLATFORM,
                      "pids": [p.pid for p in procs]}))
