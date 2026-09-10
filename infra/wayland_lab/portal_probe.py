"""Probe the STANDARD desktop capture API - xdg-desktop-portal - and record exactly what
identity metadata it returns to a trusted observer.

This is the API a real deployment would have to use on Wayland, because no Wayland
protocol lets one client read another client's surfaces. The question it answers is
narrow and predeclared:

    when a capture is taken through the standard portal, does the portal tell the
    caller WHICH surface or client the pixels came from?

Nothing here is inferred from documentation. Every value recorded is a value actually
returned by the running portal on the session bus, or a recorded failure. If the portal
cannot complete a session in this environment, that is recorded as BLOCKED with the
exact D-Bus error, and NOT replaced by what the specification says would happen.
"""
from __future__ import annotations

import json
import os
import sys
import time

RESULT = {"probe_version": "portal-probe/1.0.0", "steps": [], "blocked": False}


def step(name, **kw):
    rec = {"step": name, **kw}
    RESULT["steps"].append(rec)
    return rec


def main(out_path):
    try:
        import dbus
        from dbus.mainloop.glib import DBusGMainLoop
        from gi.repository import GLib
    except Exception as e:  # noqa: BLE001
        RESULT["blocked"] = True
        RESULT["blocked_reason"] = f"D-Bus/GLib bindings unavailable: {e}"
        json.dump(RESULT, open(out_path, "w", encoding="utf-8"), indent=2)
        return

    DBusGMainLoop(set_as_default=True)
    try:
        bus = dbus.SessionBus()
    except Exception as e:  # noqa: BLE001
        RESULT["blocked"] = True
        RESULT["blocked_reason"] = f"no session bus: {e}"
        json.dump(RESULT, open(out_path, "w", encoding="utf-8"), indent=2)
        return

    # ---------------------------------------------------------------- reachability
    try:
        names = [str(n) for n in bus.list_names()]
        RESULT["portal_on_bus"] = "org.freedesktop.portal.Desktop" in names
        step("list_names", portal_present=RESULT["portal_on_bus"],
             portal_related=[n for n in names if "portal" in n.lower()])
    except Exception as e:  # noqa: BLE001
        RESULT["blocked"] = True
        RESULT["blocked_reason"] = f"ListNames failed: {e}"
        json.dump(RESULT, open(out_path, "w", encoding="utf-8"), indent=2)
        return

    if not RESULT["portal_on_bus"]:
        RESULT["blocked"] = True
        RESULT["blocked_reason"] = ("org.freedesktop.portal.Desktop is not on the session "
                                    "bus; the standard capture API does not exist in this "
                                    "environment")
        json.dump(RESULT, open(out_path, "w", encoding="utf-8"), indent=2)
        return

    obj = bus.get_object("org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop")
    props = dbus.Interface(obj, "org.freedesktop.DBus.Properties")

    # ------------------------------------------- what source types are even offered
    # AvailableSourceTypes is a bitmask: 1 = MONITOR, 2 = WINDOW, 4 = VIRTUAL.
    # Whether WINDOW is offered is the single most decisive fact for capture->surface
    # binding, and it is readable without starting a session.
    for iface, keys in (("org.freedesktop.portal.ScreenCast",
                         ["version", "AvailableSourceTypes", "AvailableCursorModes"]),
                        ("org.freedesktop.portal.Screenshot", ["version"])):
        got = {}
        for k in keys:
            try:
                v = props.Get(iface, k)
                got[k] = int(v) if isinstance(v, (dbus.UInt32, dbus.Int32)) else str(v)
            except Exception as e:  # noqa: BLE001
                got[k] = f"ERROR: {e}"
        step("read_properties", interface=iface, values=got)
        if iface.endswith("ScreenCast"):
            ast = got.get("AvailableSourceTypes")
            if isinstance(ast, int):
                RESULT["available_source_types_bitmask"] = ast
                RESULT["available_source_types"] = {
                    "MONITOR": bool(ast & 1), "WINDOW": bool(ast & 2),
                    "VIRTUAL": bool(ast & 4)}

    # ---------------------------------------------------------------- full session
    sender = bus.get_unique_name()[1:].replace(".", "_")
    loop = GLib.MainLoop()
    state = {"responses": {}}

    def on_response(token):
        def handler(code, results):
            state["responses"][token] = {
                "response_code": int(code),
                "results": json.loads(json.dumps(results, default=_dbus_default)),
            }
            loop.quit()
        return handler

    def wait_for(token, path, timeout=20):
        sub = bus.add_signal_receiver(on_response(token),
                                      dbus_interface="org.freedesktop.portal.Request",
                                      signal_name="Response", path=path)
        tid = GLib.timeout_add_seconds(timeout, lambda: (loop.quit(), False)[1])
        loop.run()
        GLib.source_remove(tid)
        sub.remove()
        return state["responses"].get(token)

    sc = dbus.Interface(obj, "org.freedesktop.portal.ScreenCast")
    try:
        tok = f"probe{int(time.time())}"
        rpath = f"/org/freedesktop/portal/desktop/request/{sender}/{tok}"
        sc.CreateSession({"handle_token": tok, "session_handle_token": f"s{tok}"})
        resp = wait_for("create", rpath)
        step("CreateSession", response=resp)
        if not resp or resp["response_code"] != 0:
            raise RuntimeError(f"CreateSession did not succeed: {resp}")
        session_handle = resp["results"].get("session_handle")
        RESULT["session_handle"] = session_handle

        tok2 = f"sel{int(time.time())}"
        rpath2 = f"/org/freedesktop/portal/desktop/request/{sender}/{tok2}"
        # Ask for WINDOW as well as MONITOR. If the backend cannot honour WINDOW, the
        # request itself is the measurement.
        sc.SelectSources(session_handle,
                         {"handle_token": tok2, "types": dbus.UInt32(3),
                          "multiple": False, "cursor_mode": dbus.UInt32(1)})
        resp2 = wait_for("select", rpath2)
        step("SelectSources", requested_types_bitmask=3,
             requested_types="MONITOR|WINDOW", response=resp2)
        if not resp2 or resp2["response_code"] != 0:
            raise RuntimeError(f"SelectSources did not succeed: {resp2}")

        tok3 = f"start{int(time.time())}"
        rpath3 = f"/org/freedesktop/portal/desktop/request/{sender}/{tok3}"
        sc.Start(session_handle, "", {"handle_token": tok3})
        resp3 = wait_for("start", rpath3, timeout=25)
        step("Start", response=resp3)
        if not resp3 or resp3["response_code"] != 0:
            raise RuntimeError(f"Start did not succeed: {resp3}")

        streams = (resp3["results"] or {}).get("streams")
        RESULT["streams"] = streams
        # The decisive question: does a returned stream carry an identity for the
        # surface/client whose pixels it contains?
        keys = set()
        for s in streams or []:
            if isinstance(s, (list, tuple)) and len(s) == 2 and isinstance(s[1], dict):
                keys |= set(s[1].keys())
        RESULT["stream_property_keys"] = sorted(keys)
        RESULT["stream_exposes_client_identity"] = bool(
            keys & {"app_id", "application_id", "pid", "client_id", "window_id",
                    "surface_id", "toplevel_id"})
        RESULT["session_completed"] = True
    except Exception as e:  # noqa: BLE001
        RESULT["session_completed"] = False
        RESULT["session_error"] = str(e)[:600]
        RESULT["blocked"] = True
        RESULT["blocked_reason"] = ("could not complete a ScreenCast session in this "
                                    f"environment: {str(e)[:300]}")

    json.dump(RESULT, open(out_path, "w", encoding="utf-8"), indent=2)


def _dbus_default(o):
    try:
        if hasattr(o, "keys"):
            return {str(k): _dbus_default(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_dbus_default(v) for v in o]
    except Exception:  # noqa: BLE001
        pass
    for cast in (int, str):
        try:
            return cast(o)
        except Exception:  # noqa: BLE001
            continue
    return repr(o)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/lab/out/portal_probe.json")
    print(json.dumps({k: v for k, v in RESULT.items() if k != "steps"}, indent=2))
