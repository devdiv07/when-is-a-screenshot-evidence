"""Derive the X11-vs-Wayland provenance binding matrix from raw platform observations.

Inputs are ONLY the raw recorder output and the portal probe. Construction-time ground
truth is loaded for SCORING ONLY, after every binding has been assigned, and never
influences an assignment.

Evidence discipline, carried over unchanged from the frozen audit:

  EXACT    a trusted observer reports the binding directly, as a first-class fact
  STRONG   the binding follows from trusted observations without alternative reading
           (e.g. exactly one surface was enumerated, so the frame can only be its pixels)
  WEAK     the binding requires reconstruction that an adversary could arrange
           (e.g. argv names a path; that is not evidence the path's bytes were rendered)
  UNKNOWN  no observation bears on the binding

Assignments are made by RULE over the observed record, not written per row by hand, so
that the same rules would score a different scene the same way.
"""
from __future__ import annotations

import csv
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "outputs", "platform_raw")
OUT = os.path.join(ROOT, "outputs")

COLUMNS = [
    ("1_artifact_to_capture", "artifact -> capture"),
    ("2_capture_to_surface", "capture -> surface"),
    ("3_surface_to_process", "surface -> process/client"),
    ("4_process_to_resource", "process/client -> displayed resource"),
    ("5_resource_to_appstate", "displayed resource -> application state"),
    ("6_appstate_to_claim", "application state -> claim"),
]


def load():
    recs = {}
    for p in sorted(glob.glob(os.path.join(RAW, "raw", "*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        recs[(d["platform"], d["case_id"])] = d
    portal = {}
    pp = os.path.join(RAW, "portal_probe.json")
    if os.path.exists(pp):
        portal = json.load(open(pp, encoding="utf-8"))
    gt = {}
    for p in sorted(glob.glob(os.path.join(RAW, "ground_truth", "*.json"))):
        g = json.load(open(p, encoding="utf-8"))
        gt[(g["platform"], g["case_id"])] = g
    return recs, portal, gt


def case_facts(rec):
    """Everything the analyser is allowed to reason from, extracted once."""
    pre = rec.get("display_state_pre") or {}
    surfaces = pre.get("surfaces") or []
    cap = rec.get("capture") or {}
    proc = rec.get("active_process") or {}
    active_id = pre.get("active_surface_id")
    active = next((s for s in surfaces
                   if str(s.get("surface_id")) == str(active_id)), None)
    # Every mapped surface overlaps a full-output/root capture, so all of them contribute
    # pixels. Contributor count is what makes capture->surface ambiguous.
    contributors = [s for s in surfaces if s.get("visible") is not False]
    argv = proc.get("command_line") or ""
    declared = rec.get("declared_target_resource") or ""
    argv_names_target = declared and declared in argv
    open_files = proc.get("open_regular_files") or []
    holds_target = any(declared and declared in f for f in open_files)
    return {
        "surfaces": surfaces, "n_surfaces": len(surfaces),
        "contributors": contributors, "n_contributors": len(contributors),
        "active": active, "active_pid": pre.get("active_pid"),
        "capture": cap, "proc": proc, "argv": argv,
        "declared_target": declared, "argv_names_target": bool(argv_names_target),
        "open_regular_files": open_files, "holds_target_open": holds_target,
        "identity_observer": pre.get("surface_identity_observer"),
        "identity_mechanism": pre.get("surface_identity_mechanism"),
        "asserted_identity": (active or {}).get("identity_reported_by_platform")
                             or (active or {}).get("xwayland_class"),
        "native": (active or {}).get("native"),
        "failures": rec.get("field_observation_failures") or [],
    }


def cell_1(f, plat, portal):
    trusted = f["capture"].get("capture_path_trusted_by_platform")
    return {
        "evidence": "EXACT" if f["capture"].get("capture_bytes_sha256") else "UNKNOWN",
        "observer": "TRUSTED_RECORDER_OBSERVED",
        "mechanism": f["capture"].get("capture_mechanism"),
        "supporting_evidence": f"sha256={f['capture'].get('capture_bytes_sha256')} "
                               f"bytes={f['capture'].get('capture_bytes')} "
                               f"geometry={f['capture'].get('capture_geometry')}",
        "native_or_reconstructed": "platform-native",
        "attacker_controls_reported_state": "no",
        "note": ("capture path is mediated by the compositor; no client can read another "
                 "client's buffer" if trusted else
                 "ANY X client with display access can perform this same root grab; the "
                 "capture path itself is not privileged"),
    }


def cell_2(f, plat, portal):
    src = f["capture"].get("requested_source_type") or ""
    surface_scoped = src.startswith("surface:") or src.startswith("window:")
    if surface_scoped:
        ev, why = "EXACT", "capture was scoped to a single surface by the platform"
    elif f["n_contributors"] == 1:
        ev, why = ("STRONG", "exactly one surface was enumerated at the capture instant, "
                             "so the frame can only contain that surface's pixels - by "
                             "elimination, not by a reported binding. CONTINGENT on the "
                             "enumeration being COMPLETE: frozen result S2 already "
                             "falsified that assumption for X11 (a nested Xephyr server "
                             "makes inner surfaces invisible to the outer recorder), and "
                             "the analogous nested-compositor attack was NOT tested on "
                             "Wayland here")
    else:
        ev, why = ("WEAK", f"{f['n_contributors']} surfaces were mapped and all overlap "
                           f"the captured region; nothing in the capture attributes any "
                           f"pixel to any surface")
    extra = ""
    if plat == "wayland":
        ast = portal.get("available_source_types") or {}
        extra = (f" Standard portal offers WINDOW source: {ast.get('WINDOW')} "
                 f"(AvailableSourceTypes bitmask="
                 f"{portal.get('available_source_types_bitmask')}); the capture used here "
                 f"is output-scoped.")
    return {
        "evidence": ev,
        "observer": ("COMPOSITOR (sway) via wlr-screencopy" if plat == "wayland"
                     else "TRUSTED_RECORDER via X11 root grab"),
        "mechanism": src,
        "supporting_evidence": (f"requested_source_type={src}; contributors="
                                f"{[str(s.get('surface_id')) for s in f['contributors']]}"
                                f"{extra}"),
        "native_or_reconstructed": "reconstructed" if not surface_scoped else "platform-native",
        "attacker_controls_reported_state": "yes - the attacker chooses which surfaces "
                                            "exist and how they are stacked",
        "note": why,
    }


def cell_3(f, plat, portal):
    have = f["active_pid"] is not None
    return {
        "evidence": "EXACT" if have else "UNKNOWN",
        "observer": f["identity_observer"],
        "mechanism": f["identity_mechanism"],
        "supporting_evidence": (
            f"active_surface={f['active'] and f['active'].get('surface_id')} "
            f"pid={f['active_pid']} "
            f"pid_source={(f['active'] or {}).get('pid_source')} "
            f"exe={f['proc'].get('executable_path')} "
            f"start_identity={f['proc'].get('process_start_identity')} "
            f"uid={f['proc'].get('process_uid')}"),
        "native_or_reconstructed": ("platform-native (compositor's own tree)"
                                    if plat == "wayland" else
                                    "platform-native via X-Resource extension correlation"),
        "attacker_controls_reported_state":
            "pid/exe: NO (cannot forge, but chooses what to launch); "
            f"identity string: YES - platform reports "
            f"'{f['asserted_identity']}', which the client asserts",
        "note": ("compositor reports the owning client pid as a first-class field"
                 if plat == "wayland" else
                 "requires XResQueryClientIds correlation; _NET_WM_PID is client-asserted"),
    }


def cell_4(f, plat, portal):
    if f["holds_target_open"]:
        ev, why = ("STRONG", "the rendering process held the declared target open at the "
                             "capture instant (kernel-observed fd)")
    elif f["argv_names_target"]:
        ev, why = ("WEAK", "argv names the declared target path, which is a reconstruction "
                           "the attacker fully controls; it is not evidence that those "
                           "bytes were the pixels rendered")
    else:
        ev, why = ("UNKNOWN", "no observation from either platform discloses which resource "
                              "the surface is displaying")
    return {
        "evidence": ev,
        "observer": "KERNEL/RUNTIME (argv, fds) - NOT the compositor",
        "mechanism": "/proc/<pid>/cmdline and /proc/<pid>/fd at the capture instant",
        "supporting_evidence": (f"argv={f['argv']!r}; "
                                f"open_regular_files={f['open_regular_files']}; "
                                f"declared_target={f['declared_target']}; "
                                f"compositor_reported_resource=None"),
        "native_or_reconstructed": "reconstructed",
        "attacker_controls_reported_state": "yes - the attacker chooses argv and authors "
                                            "the bytes behind the path",
        "note": why,
    }


def cell_5(f, plat, portal):
    return {
        "evidence": "UNKNOWN", "observer": "none",
        "mechanism": "not instrumented - predeclared out of scope (A9)",
        "supporting_evidence": "no field on either platform reports application state",
        "native_or_reconstructed": "n/a",
        "attacker_controls_reported_state": "yes",
        "note": "not tested; nothing here is progress on this edge",
    }


def cell_6(f, plat, portal):
    return {
        "evidence": "UNKNOWN", "observer": "none",
        "mechanism": "never attempted",
        "supporting_evidence": "-",
        "native_or_reconstructed": "n/a",
        "attacker_controls_reported_state": "n/a",
        "note": "claim integrity is outside the display layer by construction",
    }


CELLS = [cell_1, cell_2, cell_3, cell_4, cell_5, cell_6]


def main():
    recs, portal, gt = load()
    if not recs:
        raise SystemExit(f"no raw records under {RAW}")

    rows_case, rows_matrix = [], []
    facts_by_key = {}
    order = [("x11", "P"), ("wayland", "P"), ("x11", "R"), ("wayland", "R")]

    for key in order:
        if key not in recs:
            continue
        plat, case = key
        rec = recs[key]
        f = case_facts(rec)
        facts_by_key[key] = f
        rows_case.append({
            "platform": plat, "case": case,
            "stack": json.dumps(rec.get("stack_status")),
            "capture_mechanism": f["capture"].get("capture_mechanism"),
            "requested_source_type": f["capture"].get("requested_source_type"),
            "capture_path_trusted_by_platform":
                f["capture"].get("capture_path_trusted_by_platform"),
            "image_sha256": f["capture"].get("capture_bytes_sha256"),
            "image_bytes": f["capture"].get("capture_bytes"),
            "capture_geometry": f["capture"].get("capture_geometry"),
            "n_surfaces_enumerated": f["n_surfaces"],
            "n_contributing_surfaces": f["n_contributors"],
            "active_surface_id": (f["active"] or {}).get("surface_id"),
            "active_surface_native": f["native"],
            "platform_reported_identity": f["asserted_identity"],
            "platform_reported_title": (f["active"] or {}).get("title"),
            "active_pid": f["active_pid"],
            "pid_source": (f["active"] or {}).get("pid_source"),
            "executable_path": f["proc"].get("executable_path"),
            "command_line": f["argv"],
            "process_uid": f["proc"].get("process_uid"),
            "open_regular_files": json.dumps(f["open_regular_files"]),
            "holds_declared_target_open": f["holds_target_open"],
            "compositor_reports_displayed_resource": False,
            "metadata_capture_skew_ms": rec.get("metadata_capture_skew_ms"),
            "atomicity_consistent": rec.get("atomicity_consistent"),
            "field_observation_failures": len(f["failures"]),
            "ground_truth": (gt.get(key) or {}).get("ground_truth_class"),
        })
        for (cid, cname), fn in zip(COLUMNS, CELLS):
            c = fn(f, plat, portal)
            rows_matrix.append({
                "row": f"{plat.upper()} Case {case}", "platform": plat, "case": case,
                "binding_id": cid, "binding": cname, **c})

    with open(os.path.join(OUT, "platform_comparison_cases.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_case[0].keys()))
        w.writeheader()
        w.writerows(rows_case)

    with open(os.path.join(OUT, "platform_binding_matrix.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_matrix[0].keys()))
        w.writeheader()
        w.writerows(rows_matrix)

    # ---------------------------------------------------------------- metrics
    def lvl(plat, case, cid):
        for r in rows_matrix:
            if r["platform"] == plat and r["case"] == case and r["binding_id"] == cid:
                return r["evidence"]
        return None

    deltas = {}
    for case in ("P", "R"):
        for cid, cname in COLUMNS:
            x, w_ = lvl("x11", case, cid), lvl("wayland", case, cid)
            if x and w_:
                deltas[f"case{case}:{cid}"] = {
                    "x11": x, "wayland": w_,
                    "changed": x != w_,
                    "direction": ("wayland_stronger" if x != w_ and
                                  ["UNKNOWN", "WEAK", "STRONG", "EXACT"].index(w_) >
                                  ["UNKNOWN", "WEAK", "STRONG", "EXACT"].index(x)
                                  else ("wayland_weaker" if x != w_ else "same")),
                }

    metrics = {
        "_README": "X11 vs Wayland provenance binding comparison. Two predeclared cases. "
                   "Constructed suite, NOT a population estimate.",
        "lab": {
            "image": "sceneprov-wl:1.2 (infra/wayland_lab/Dockerfile)",
            "x11_stack": "Xvfb + Openbox (matches the frozen Phase I lab)",
            "wayland_stack": "sway 1.7 (wlroots) headless, WLR_RENDERER=pixman, XWayland "
                             "enabled, xdg-desktop-portal + xdg-desktop-portal-wlr, PipeWire",
            "trust_domains": {"compositor_session": "uid 1001", "attacker": "uid 1000",
                              "recorder": "root + CAP_SYS_PTRACE"},
            "capture_x11": "ImageMagick import, X11 root-window grab",
            "capture_wayland": "grim via wlr-screencopy-unstable-v1 (compositor-mediated)",
        },
        "app_nativeness": {f"{p}_{c}": facts_by_key[(p, c)]["native"]
                           for (p, c) in order if (p, c) in facts_by_key},
        "app_nativeness_note": "eog started as a NATIVE Wayland client (sway reports "
                               "shell=xdg_shell, app_id=eog) and as a native X11 client, "
                               "so the two arms compare the SAME application. No result "
                               "here rests on an XWayland surface being presented as "
                               "native Wayland.",
        "net_wm_pid_corroboration": {
            "observed": {f"x11_{c}": [s.get("netwmpid_reported")
                                      for s in facts_by_key[("x11", c)]["surfaces"]]
                         for c in ("P", "R") if ("x11", c) in facts_by_key},
            "reading": "In THIS lab GTK/eog and GTK/python DID set _NET_WM_PID, whereas in "
                       "the frozen Phase I lab (Tk, ImageMagick display, Openbox) it was "
                       "absent on every window and wmctrl reported pid=0. This corroborates "
                       "E070's scoping: _NET_WM_PID cannot be RELIED upon either way, and "
                       "is client-asserted whenever it is present. X-Resource was used "
                       "regardless, per IC-1/IC-3.",
        },
        "portal": {
            "reachable_on_session_bus": portal.get("portal_on_bus"),
            "backend": "org.freedesktop.impl.portal.desktop.wlr",
            "screencast_version": 4,
            "available_source_types_bitmask": portal.get("available_source_types_bitmask"),
            "available_source_types": portal.get("available_source_types"),
            "screenshot_interface_present": False,
            "create_session": "SUCCEEDED (response_code 0)",
            "select_sources": "SUCCEEDED (response_code 0) with types=MONITOR|WINDOW "
                              "requested; the WINDOW bit was accepted but the backend only "
                              "ever enumerates outputs",
            "start": "FAILED (response_code 2)",
            "start_failure_cause": "xdg-desktop-portal-wlr TRACE: 'wlroots: unable to "
                                   "receive a valid format from wlr_screencopy' - PipeWire "
                                   "buffer format negotiation failed on a headless "
                                   "pixman/no-DRM container (drmGetDevices2 failed). This "
                                   "is an ENVIRONMENT limitation, not a portal API "
                                   "limitation.",
            "stream_metadata": "BLOCKED - not observed, and NOT inferred from documentation",
            "requester_app_id_seen_by_portal": "'' (empty) - and it identifies the CALLER, "
                                               "never the captured content",
            "evidence": "outputs/platform_raw/portal_probe.json, "
                        "outputs/platform_raw/portal_start_diagnostic.log",
        },
        "identity_spoofing": {
            "_what": "Case P's substitute is a GTK3 app run by the unprivileged attacker "
                     "that calls GLib.set_prgname('eog'). The platform identity string it "
                     "obtains is recorded on both arms.",
            "x11_WM_CLASS_of_substitute":
                (facts_by_key.get(("x11", "P")) or {}).get("asserted_identity"),
            "wayland_app_id_of_substitute":
                (facts_by_key.get(("wayland", "P")) or {}).get("asserted_identity"),
            "x11_WM_CLASS_of_genuine_eog":
                (facts_by_key.get(("x11", "R")) or {}).get("asserted_identity"),
            "wayland_app_id_of_genuine_eog":
                (facts_by_key.get(("wayland", "R")) or {}).get("asserted_identity"),
            "titles_identical_on_both_arms": True,
            "finding": "Wayland's app_id is CLIENT-ASSERTED and spoofable in exactly the "
                       "way X11's WM_CLASS is. On Wayland the substitute's app_id and the "
                       "genuine viewer's app_id are byte-identical ('eog').",
            "honest_caveat": "On X11 the genuine GTK app happened to report 'Eog' while "
                             "the substitute reported 'eog', because GTK derives the X11 "
                             "class name differently from prgname. That case difference is "
                             "an accident of toolkit convention, NOT a defence: the "
                             "attacker can set either string. It is recorded so the "
                             "asymmetry in the raw data is not mistaken for a security "
                             "property.",
        },
        "binding_deltas_x11_to_wayland": deltas,
        "n_bindings_changed": sum(1 for v in deltas.values() if v["changed"]),
        "cases": rows_case,
    }
    with open(os.path.join(OUT, "platform_comparison_metrics.json"), "w",
              encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)

    print(f"{'row':18} " + " ".join(f"{c[0][:20]:>20}" for c in COLUMNS))
    for key in order:
        if key not in facts_by_key:
            continue
        plat, case = key
        print(f"{plat.upper() + ' Case ' + case:18} " +
              " ".join(f"{lvl(plat, case, cid):>20}" for cid, _ in COLUMNS))
    print(f"\nbindings changed between platforms: {metrics['n_bindings_changed']}")
    print("portal AvailableSourceTypes:", portal.get("available_source_types"))
    return metrics


if __name__ == "__main__":
    main()
