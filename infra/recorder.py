"""Trusted recorder for the Phase I empirical arm.

Runs as root, under a privilege boundary distinct from the unprivileged attacker.

HARD RULE: the recorder derives EVERY field from live system state --
  - process/runtime state via /proc
  - display/window-server state via X11 (xdotool, wmctrl, xprop, xwininfo)
  - filesystem state and episode-scoped write journal
  - an actual screenshot operation producing real pixel bytes

It never reads a scenario definition or ground-truth file, and never accepts a
field value from the attacker. If a field cannot be observed, it is recorded as
None with a reason in `field_observation_failures`. Nothing is synthesised
because a scenario "should" produce it.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time

RECORDER_VERSION = "empirical-recorder/1.0.0"
CAPTURE_TOOL = "ImageMagick import (declared gnome-screenshot equivalent)"


def _run(cmd, timeout=15):
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                           text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:  # noqa: BLE001
        return 255, "", str(e)


class Recorder:
    def __init__(self, display=":99", journal_path="/lab/out/write_journal.jsonl"):
        self.display = display
        self.journal_path = journal_path
        self.failures = []

    def _fail(self, field, why):
        self.failures.append({"field": field, "reason": why})
        return None

    # ---------------------------------------------------------------- X11 state
    def _xdo(self, args):
        rc, out, err = _run(f"DISPLAY={self.display} xdotool {args}")
        return out.strip() if rc == 0 else None

    def active_window(self):
        wid = self._xdo("getactivewindow")
        if not wid:
            return self._fail("active_window_identity", "no active window (xdotool)")
        return wid

    def window_pid(self, wid):
        """Owning PID via the X-Resource extension (server-observed).

        IC-1: `_NET_WM_PID` is set by the client about itself, i.e.
        APPLICATION_ASSERTED, and was absent on every window observed in this
        lab. The contract specifies ACTIVE_PID as KERNEL/RUNTIME_OBSERVED, so
        the PID is resolved by asking the X server which client owns the
        resource. Never synthesised: unavailable is recorded as unavailable.
        """
        try:
            from Xlib import display as _xd
            from Xlib.ext import res as _xres
        except ImportError as e:
            return self._fail("active_pid", f"python-xlib unavailable: {e}")
        try:
            d = _xd.Display(self.display)
            wid_int = int(wid, 16) if isinstance(wid, str) and wid.startswith("0x") else int(wid)
            r0 = d.res_query_client_ids([{"client": wid_int,
                                          "mask": _xres.LocalClientPIDMask}])
            for entry in r0.ids:
                if entry["spec"]["mask"] == _xres.LocalClientPIDMask and entry["value"]:
                    return int(entry["value"][0])
            return self._fail("active_pid", f"X-Resource returned no PID for {wid}")
        except Exception as e:  # noqa: BLE001
            return self._fail("active_pid", f"X-Resource query failed: {e}")
        finally:
            try:
                d.close()
            except Exception:  # noqa: BLE001
                pass

    def pid_source(self):
        return "X-Resource XResQueryClientIds (COMPOSITOR/DISPLAY_SERVER_OBSERVED)"

    def window_name(self, wid):
        rc, out, _e = _run(f"DISPLAY={self.display} xdotool getwindowname {wid}")
        return out.strip() if rc == 0 else self._fail("window_title", "getwindowname failed")

    def wm_class(self, wid):
        rc, out, _e = _run(f"DISPLAY={self.display} xprop -id {wid} WM_CLASS")
        if rc != 0 or "=" not in out:
            return self._fail("wm_class", "xprop WM_CLASS unavailable")
        vals = re.findall(r'"([^"]*)"', out)
        return vals[-1] if vals else None

    def geometry(self, wid):
        rc, out, _e = _run(f"DISPLAY={self.display} xdotool getwindowgeometry --shell {wid}")
        if rc != 0:
            return self._fail("window_geometry", "getwindowgeometry failed")
        d = dict(l.split("=", 1) for l in out.strip().splitlines() if "=" in l)
        try:
            return f"{d['WIDTH']}x{d['HEIGHT']}+{d['X']}+{d['Y']}"
        except KeyError:
            return self._fail("window_geometry", "incomplete geometry")

    def visible_window_set(self):
        """Mapped, viewable windows with their owning pid, from the X server."""
        rc, out, _e = _run(f"DISPLAY={self.display} wmctrl -lpG")
        if rc != 0:
            return self._fail("visible_window_set", "wmctrl -lpG failed")
        wins = []
        for line in out.strip().splitlines():
            parts = line.split(None, 7)
            if len(parts) < 8:
                continue
            wid, _desk, pid, x, y, w, h, rest = parts
            title = rest.split(None, 1)[-1] if " " in rest else rest
            # IC-3: wmctrl's pid column reads _NET_WM_PID (application-asserted and
            # absent here). Resolve via X-Resource instead; never guess.
            xres_pid = self.window_pid(wid)
            wins.append({"wid": wid, "pid": xres_pid,
                         "netwmpid_reported": int(pid) if pid.isdigit() else None,
                         "geometry": f"{w}x{h}+{x}+{y}", "title": title})
        return wins

    def z_order(self):
        """Stacking order, bottom-to-top, from the X server's actual child list."""
        rc, out, _e = _run(f"DISPLAY={self.display} xwininfo -root -children")
        if rc != 0:
            return self._fail("z_order", "xwininfo -root -children failed")
        ids = re.findall(r"^\s+(0x[0-9a-f]+)", out, re.M)
        return ids  # xwininfo lists children bottom-to-top

    # ---------------------------------------------------------------- process state
    def process_facts(self, pid):
        if not pid:
            return {}
        out = {}
        try:
            out["executable_path"] = os.readlink(f"/proc/{pid}/exe")
        except OSError as e:
            out["executable_path"] = self._fail("executable_path", f"readlink: {e}")
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                out["command_line"] = fh.read().replace(b"\0", b" ").decode(
                    "utf-8", "replace").strip()
        except OSError as e:
            out["command_line"] = self._fail("command_line", f"cmdline: {e}")
        try:
            with open(f"/proc/{pid}/stat") as fh:
                fields = fh.read().rsplit(") ", 1)[1].split()
            out["process_start_identity"] = f"{pid}@{fields[19]}"   # starttime, jiffies
            out["parent_pid"] = int(fields[1])
        except (OSError, IndexError) as e:
            out["process_start_identity"] = self._fail("process_start_identity", str(e))
            out["parent_pid"] = None
        try:
            out["process_uid"] = os.stat(f"/proc/{pid}").st_uid
        except OSError:
            out["process_uid"] = None
        return out

    # ---------------------------------------------------------------- lineage
    def load_journal(self):
        """Episode-scoped file writes observed by the harness (paths + hashes).

        The journal is appended by the harness when it materialises a scenario's
        files. It records WHAT was written, not what any scenario claims.
        """
        if not os.path.exists(self.journal_path):
            return {}
        j = {}
        with open(self.journal_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                j[rec["path"]] = rec
        return j

    def resource_lineage_for(self, path, journal):
        """Provenance of a displayed resource path, if the recorder can see it."""
        if not path:
            return None
        rec = journal.get(path)
        if rec:
            return f"{path}:agent_authored_this_episode"
        if os.path.exists(path):
            return f"{path}:pre_existing"
        return None

    # ---------------------------------------------------------------- capture
    def capture(self, out_png, region=None):
        """Perform a genuine X11 pixel grab and return bytes + hash."""
        args = f"-display {self.display} -window root"
        if region:
            args += f" -crop {region}"
        rc, _o, err = _run(f"/usr/local/bin/labshot {args} {out_png}", timeout=30)
        if rc != 0 or not os.path.exists(out_png):
            return None, self._fail("capture_bytes", f"capture failed: {err[:160]}")
        data = open(out_png, "rb").read()
        return data, hashlib.sha256(data).hexdigest()

    # ---------------------------------------------------------------- record
    def observe(self, scenario_id, trial, out_png, capture_scope="fullscreen"):
        """Produce one provenance record from live state, then capture pixels.

        Order matters and is deliberately recorded: metadata is sampled, then
        pixels are grabbed, then metadata is sampled AGAIN. A recorder that is
        not atomic will show pre != post, which is exactly what S1 exercises.
        """
        self.failures = []
        journal = self.load_journal()

        def snapshot():
            wid = self.active_window()
            pid = self.window_pid(wid) if wid else None
            snap = {
                "active_window_identity": wid,
                "active_pid": pid,
                "window_title": self.window_name(wid) if wid else None,
                "wm_class": self.wm_class(wid) if wid else None,
                "window_geometry": self.geometry(wid) if wid else None,
                "visible_window_set": self.visible_window_set(),
                "z_order": self.z_order(),
            }
            snap.update(self.process_facts(pid))
            return snap

        t_pre = time.time()
        pre = snapshot()
        t_cap = time.time()
        data, sha = self.capture(out_png)
        t_post = time.time()
        post = snapshot()

        displayed = None
        argv = pre.get("command_line") or ""
        for tok in argv.split()[1:]:
            if "/" in tok and os.path.splitext(tok)[1]:
                displayed = tok
        lineage = self.resource_lineage_for(displayed, journal)

        rec = {
            "recorder_version": RECORDER_VERSION,
            "capture_tool": CAPTURE_TOOL,
            "pid_source": self.pid_source(),
            "scenario_id": scenario_id,
            "trial": trial,
            "capture_timestamp": t_cap,
            "t_pre": t_pre, "t_post": t_post,
            "metadata_capture_skew_ms": round((t_post - t_pre) * 1000, 2),
            "capture_scope": capture_scope,
            "capture_region": "fullscreen:" + (os.environ.get("LAB_SCREEN", "?")),
            "image_path": out_png,
            "image_sha256": sha,
            "image_bytes": len(data) if data else 0,
            "pre": pre,
            "post": post,
            "atomicity_consistent": (pre.get("active_window_identity")
                                     == post.get("active_window_identity")
                                     and pre.get("active_pid") == post.get("active_pid")),
            "displayed_resource_observed": displayed,
            "displayed_resource_lineage": lineage,
            "agent_written_code_lineage": (
                "agent_authored_this_episode"
                if pre.get("command_line") and any(
                    p in journal for p in (pre.get("command_line") or "").split())
                else ("not_agent_authored" if pre.get("command_line") else None)),
            "field_observation_failures": list(self.failures),
        }
        return rec
