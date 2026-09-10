"""Trusted platform recorder for the X11-vs-Wayland comparison.

Runs as root, in a trust domain separate from both the attacker (uid 1000) and the
compositor session (uid 1001).

HARD RULE, carried over from the frozen Phase I recorder: every field is derived from
live platform state. Nothing is synthesised because a case "should" produce it. If a
fact cannot be observed, it is recorded as None with a reason in
`field_observation_failures`.

DELIBERATE SCOPE: this recorder collects only what the PLATFORM itself exposes. No
application-specific instrumentation, no CDP, no LD_PRELOAD, no ptrace of the renderer.
That restriction is the experiment: the question is what a platform hands a trusted
observer, not what could be extracted by instrumenting each app.

Each observation records its OBSERVER and MECHANISM alongside its value, because the
13b classification showed that a value without a stated observation policy is not
interpretable (research/EPISTEMIC_POLICY.md).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time

RECORDER_VERSION = "platform-recorder/2.0.0"


def _run(cmd, timeout=20, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                           text=True, timeout=timeout, env=e)
        return p.returncode, p.stdout, p.stderr
    except Exception as exc:  # noqa: BLE001
        return 255, "", str(exc)


def wayland_env():
    env = {}
    if os.path.exists("/lab/out/wayland_env"):
        for line in open("/lab/out/wayland_env", encoding="utf-8"):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                env[k] = v
    return env


class PlatformRecorder:
    def __init__(self, platform):
        self.platform = platform            # "x11" | "wayland"
        self.failures = []
        self.wenv = wayland_env()
        self.display = os.environ.get("DISPLAY", ":99")

    def _fail(self, field, why):
        self.failures.append({"field": field, "reason": str(why)[:300]})
        return None

    # ================================================================ process facts
    def process_facts(self, pid):
        """KERNEL/RUNTIME_OBSERVED. Identical on both arms, so it is not a difference."""
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
            out["process_start_identity"] = f"{pid}@{fields[19]}"
            out["parent_pid"] = int(fields[1])
        except (OSError, IndexError) as e:
            out["process_start_identity"] = self._fail("process_start_identity", str(e))
            out["parent_pid"] = None
        try:
            out["process_uid"] = os.stat(f"/proc/{pid}").st_uid
        except OSError:
            out["process_uid"] = None
        # Open file descriptors are a KERNEL-observed fact about which resources the
        # process currently HOLDS. Recorded because it is the closest platform-native
        # approach to a resource binding, and its limits are part of the result.
        try:
            fds = []
            for fd in os.listdir(f"/proc/{pid}/fd"):
                try:
                    t = os.readlink(f"/proc/{pid}/fd/{fd}")
                except OSError:
                    continue
                if t.startswith("/") and not t.startswith(("/dev/", "/proc/", "/sys/",
                                                           "/run/", "/usr/lib", "/usr/share",
                                                           "/etc/")):
                    fds.append(t)
            out["open_regular_files"] = sorted(set(fds))
        except OSError as e:
            out["open_regular_files"] = self._fail("open_regular_files", str(e))
        return out

    # ================================================================ X11 observation
    def _xres_pid(self, wid):
        try:
            from Xlib import display as _xd
            from Xlib.ext import res as _xres
        except ImportError as e:
            return self._fail("active_pid", f"python-xlib unavailable: {e}")
        d = None
        try:
            d = _xd.Display(self.display)
            wi = int(wid, 16) if isinstance(wid, str) and wid.startswith("0x") else int(wid)
            r0 = d.res_query_client_ids([{"client": wi, "mask": _xres.LocalClientPIDMask}])
            for entry in r0.ids:
                if entry["spec"]["mask"] == _xres.LocalClientPIDMask and entry["value"]:
                    return int(entry["value"][0])
            return self._fail("active_pid", f"X-Resource returned no PID for {wid}")
        except Exception as e:  # noqa: BLE001
            return self._fail("active_pid", f"X-Resource query failed: {e}")
        finally:
            if d is not None:
                try:
                    d.close()
                except Exception:  # noqa: BLE001
                    pass

    @staticmethod
    def _canon_wid(wid):
        """xdotool prints window ids in decimal, wmctrl in 0x%08x. Same id, two spellings.

        Without normalising, the active window never matches the enumerated set and the
        recorder silently reports an unresolvable active surface.
        """
        if wid in (None, ""):
            return None
        try:
            n = int(str(wid), 16) if str(wid).lower().startswith("0x") else int(str(wid))
        except ValueError:
            return str(wid)
        return f"0x{n:08x}"

    def _wm_class(self, wid):
        """The X11 counterpart of Wayland's app_id. APPLICATION_ASSERTED on both."""
        rc, out, _ = _run(f"xprop -id {wid} WM_CLASS", env={"DISPLAY": self.display})
        if rc != 0 or "=" not in out:
            return None
        vals = re.findall(r'"([^"]*)"', out)
        return vals[-1] if vals else None

    def observe_x11(self):
        env = {"DISPLAY": self.display}
        rc, out, _ = _run("xdotool getactivewindow", env=env)
        wid = self._canon_wid(out.strip()) if rc == 0 and out.strip() else self._fail(
            "active_window_identity", "xdotool getactivewindow failed")
        surfaces = []
        rc, out, _ = _run("wmctrl -lpG", env=env)
        if rc != 0:
            self._fail("visible_window_set", "wmctrl -lpG failed")
        else:
            for line in out.strip().splitlines():
                parts = line.split(None, 7)
                if len(parts) < 8:
                    continue
                w, _desk, netpid, x, y, ww, hh, rest = parts
                title = rest.split(None, 1)[-1] if " " in rest else rest
                surfaces.append({
                    "surface_id": self._canon_wid(w),
                    # WM_CLASS is X11's application identity string: the direct counterpart
                    # of Wayland's app_id, and client-asserted in exactly the same way.
                    "identity_reported_by_platform": self._wm_class(w),
                    "title": title,                          # APPLICATION_ASSERTED
                    "pid": self._xres_pid(w),                # via X-Resource (IC-1/IC-3)
                    "pid_source": "X-Resource XResQueryClientIds",
                    "netwmpid_reported": int(netpid) if netpid.isdigit() else None,
                    "geometry": f"{ww}x{hh}+{x}+{y}",
                    "native": "x11",
                })
        rc, out, _ = _run("xwininfo -root -children", env=env)
        z = re.findall(r"^\s+(0x[0-9a-f]+)", out, re.M) if rc == 0 else self._fail(
            "z_order", "xwininfo failed")
        active_pid = self._xres_pid(wid) if wid else None
        rc, title, _ = _run(f"xdotool getwindowname {wid}", env=env) if wid else (1, "", "")
        return {
            "active_surface_id": wid,
            "active_surface_title": title.strip() if rc == 0 else None,
            "active_pid": active_pid,
            "surfaces": surfaces,
            "z_order_bottom_to_top": z,
            "surface_identity_observer": "COMPOSITOR/DISPLAY_SERVER (X server)",
            "surface_identity_mechanism": "wmctrl -lpG + xwininfo -root -children + "
                                          "XResQueryClientIds for the owning pid",
            "cross_client_enumeration": True,
        }

    # ============================================================ Wayland observation
    def _swaymsg(self, what):
        rc, out, err = _run(f"swaymsg -t {what} -r", env=self.wenv)
        if rc != 0:
            return self._fail(f"sway_{what}", f"swaymsg -t {what}: {err[:160]}")
        try:
            return json.loads(out)
        except json.JSONDecodeError as e:
            return self._fail(f"sway_{what}", f"unparsable: {e}")

    @staticmethod
    def _walk(node, acc):
        for kid in (node.get("nodes") or []) + (node.get("floating_nodes") or []):
            if kid.get("pid") is not None or kid.get("app_id") or kid.get("window_properties"):
                acc.append(kid)
            PlatformRecorder._walk(kid, acc)
        return acc

    def observe_wayland(self):
        tree = self._swaymsg("get_tree")
        if not tree:
            return {"surfaces": None,
                    "surface_identity_observer": "COMPOSITOR (sway) - UNAVAILABLE"}
        nodes = self._walk(tree, [])
        surfaces, active_id, active_pid, active_title = [], None, None, None
        for n in nodes:
            wp = n.get("window_properties") or {}
            is_xwayland = n.get("shell") == "xwayland" or bool(wp)
            rect = n.get("rect") or {}
            s = {
                "surface_id": n.get("id"),
                # app_id is the Wayland-native application identity, set by the client.
                "identity_reported_by_platform": n.get("app_id"),
                "xwayland_class": wp.get("class"),
                "xwayland_instance": wp.get("instance"),
                "title": n.get("name"),
                "pid": n.get("pid"),
                "pid_source": "sway IPC get_tree (compositor-observed client pid)",
                "geometry": f"{rect.get('width')}x{rect.get('height')}"
                            f"+{rect.get('x')}+{rect.get('y')}",
                "shell": n.get("shell"),
                "native": "xwayland" if is_xwayland else "wayland",
                "focused": bool(n.get("focused")),
                "visible": n.get("visible"),
            }
            surfaces.append(s)
            if s["focused"]:
                active_id, active_pid, active_title = s["surface_id"], s["pid"], s["title"]
        outputs = self._swaymsg("get_outputs") or []
        return {
            "active_surface_id": active_id,
            "active_surface_title": active_title,
            "active_pid": active_pid,
            "surfaces": surfaces,
            "z_order_bottom_to_top": [s["surface_id"] for s in surfaces],
            "outputs": outputs,
            "surface_identity_observer": "COMPOSITOR (sway)",
            "surface_identity_mechanism": "sway IPC `swaymsg -t get_tree` - COMPOSITOR-"
                                          "SPECIFIC IPC, not a Wayland protocol and not "
                                          "the xdg-desktop-portal API",
            "cross_client_enumeration": True,
            "cross_client_enumeration_note": "available ONLY through the compositor's "
                                             "private IPC. No Wayland protocol lets one "
                                             "client enumerate another client's surfaces.",
        }

    # ==================================================================== capture
    def capture(self, out_png):
        """A genuine pixel grab through each platform's supported capture path."""
        if self.platform == "x11":
            mech = {"capture_mechanism": "X11 root-window pixel grab (ImageMagick import)",
                    "requested_source_type": "root window / full screen",
                    "capture_path_trusted_by_platform": False,
                    "note": "any X client with display access can perform this grab"}
            rc, _o, err = _run(f"/usr/local/bin/labshot -display {self.display} "
                               f"-window root {out_png}", timeout=40)
        else:
            outname = "HEADLESS-1"
            mech = {"capture_mechanism": "wlr-screencopy-unstable-v1 via grim",
                    "requested_source_type": f"output:{outname}",
                    "capture_path_trusted_by_platform": True,
                    "note": "the compositor copies its own output buffer; no client can "
                            "read another client's buffer"}
            rc, _o, err = _run(f"grim -o {outname} {out_png}", timeout=40, env=self.wenv)
            if rc != 0:
                rc, _o, err = _run(f"grim {out_png}", timeout=40, env=self.wenv)
                mech["requested_source_type"] = "output:default (fallback)"
        if rc != 0 or not os.path.exists(out_png):
            mech["capture_bytes_sha256"] = self._fail("capture_bytes",
                                                      f"capture failed: {err[:200]}")
            mech["capture_bytes"] = 0
            return mech
        data = open(out_png, "rb").read()
        mech["capture_bytes_sha256"] = hashlib.sha256(data).hexdigest()
        mech["capture_bytes"] = len(data)
        rc, o, _ = _run(f"identify -format '%wx%h' {out_png}")
        mech["capture_geometry"] = o.strip() if rc == 0 else None
        return mech

    # ==================================================================== record
    def observe(self, case_id, out_png, declared_target=None):
        self.failures = []
        t0 = time.time()
        state = self.observe_x11() if self.platform == "x11" else self.observe_wayland()
        t_cap = time.time()
        cap = self.capture(out_png)
        t_post = time.time()
        post = self.observe_x11() if self.platform == "x11" else self.observe_wayland()

        proc = self.process_facts(state.get("active_pid"))
        rec = {
            "recorder_version": RECORDER_VERSION,
            "platform": self.platform,
            "case_id": case_id,
            "capture_timestamp": t_cap,
            "metadata_capture_skew_ms": round((t_post - t0) * 1000, 2),
            "declared_target_resource": declared_target,
            "image_path": out_png,
            "capture": cap,
            "display_state_pre": state,
            "display_state_post": post,
            "active_process": proc,
            "atomicity_consistent": (state.get("active_surface_id")
                                     == post.get("active_surface_id")
                                     and state.get("active_pid") == post.get("active_pid")),
            "field_observation_failures": list(self.failures),
        }
        return rec
