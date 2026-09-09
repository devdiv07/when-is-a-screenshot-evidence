"""Phase C — retrospective information-deficit attribution.

For every delivered visual artifact whose scene lineage did NOT reach EXACT/STRONG,
determine which specific missing information prevented it.

RETROSPECTIVE INFORMATION DEFICIT on benign historical traces. NOT a security or
attestation-sufficiency test: a field that would have closed an old benign deficit may be
trivially satisfiable by an adversarial agent. That is the white-box adversarial case
evaluation, and it is not evaluated here.

THREE DISTINCT CONCEPTS (preflight correction 1)
------------------------------------------------
Earlier drafts said a bundle "resolves" a case. That was too strong: the contract itself
states that even complete display-composition metadata can leave a composite scene
genuinely UNKNOWN, and knowing which *surface* contributed pixels does not by itself say
whether that surface was the task's target. The three are now scored separately:

  1. INFORMATION_DEFICIT_CLOSURE
     the historically missing fields would no longer be missing.

  2. SCENE_SOURCE_RESOLUTION
     the recorded evidence is sufficient to identify which process / resource / display
     surface contributed the relevant captured pixels.

  3. TARGET_SUBSTITUTE_ADJUDICATION
     the evidence is sufficient to decide whether that scene corresponds to the declared
     task target. Requires (2), a binding from the contributing surface to a comparable
     identity, AND a declared target (Tier 0). Undefined target => UNKNOWN, never "no".

Closure is necessary for resolution; resolution is necessary for adjudication. Each is
strictly harder than the last, so the three coverage curves are nested and the third is
the one that answers the project's actual question.

RESOLUTION BUNDLES
------------------
Fields are conjunctive. Z_ORDER without VISIBLE_WINDOW_SET is "stacking order of what?",
and neither intersects the image without CAPTURE_REGION. Rows sharing
(case_id, bundle_id) are a conjunction; separate bundles are alternatives.

Output: outputs/information_deficits.csv, one row per (case, bundle, field).
"""
from __future__ import annotations

import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

FIELDS = {
    "ACTIVE_WINDOW_IDENTITY": "which surface held focus at the capture instant",
    "ACTIVE_PID": "pid of the process owning the relevant surface",
    "PROCESS_START_IDENTITY": "pid + start time, to defeat pid reuse and stale liveness",
    "EXECUTABLE_PATH": "resolved executable backing the owning process",
    "COMMAND_LINE": "argv of the owning process (exposes the script an interpreter runs)",
    "AGENT_WRITTEN_CODE_LINEAGE": "whether the owning executable/script was authored this episode",
    "DISPLAYED_RESOURCE_LINEAGE": "provenance of the resource the surface is displaying",
    "WINDOW_TITLE": "title string of the relevant surface",
    "WM_CLASS": "window manager class of the relevant surface",
    "WINDOW_GEOMETRY": "position and size of each relevant surface",
    "VISIBLE_WINDOW_SET": "all mapped/visible surfaces at the capture instant",
    "Z_ORDER": "stacking order / compositor state at the capture instant",
    "CAPTURE_REGION": "the screen rectangle actually captured",
    "BROWSER_TAB_ID": "identity of the foreground browser tab at capture time",
    "BROWSER_URL": "URL/origin loaded in that tab at capture time",
    "DOCUMENT_INSTANCE_ID": "application-specific open document / session identity",
    "TARGET_APPLICATION_IDENTITY": "an explicit statement of which application the task requires",
    "PROCESS_LIFECYCLE_AT_CAPTURE": "whether the candidate process was alive AND mapped at capture",
    "CONTENT_HASH": "hash of captured bytes and of any source image, to chain derivations",
    "CAPTURE_TRIGGER_ACTION_ID": "identifier binding the capture to the action that triggered it",
    "UNKNOWN_OTHER": "no rule matched this evidence state",
}

YES, NO, UNC = "yes", "no", "uncertain"
NEEDS_T0 = "unknown_no_declared_target"

COMPOSITE = ["VISIBLE_WINDOW_SET", "Z_ORDER", "CAPTURE_REGION", "WINDOW_GEOMETRY"]
FOCUS = ["ACTIVE_WINDOW_IDENTITY", "ACTIVE_PID"]
# Binding a resolved surface to an identity comparable with a declared target.
IDENTITY_BINDING = {"ACTIVE_PID", "EXECUTABLE_PATH", "COMMAND_LINE"}


def _adjudication(bundle_fields, resolution, target_declared):
    """TARGET/SUBSTITUTE adjudication verdict for one bundle.

    Strictly harder than resolution: needs the contributing surface resolved, a binding
    from that surface to a comparable identity, and a declared target.
    """
    if resolution != YES:
        return NO, "scene source not resolved, so nothing to compare against a target"
    if not target_declared:
        return NEEDS_T0, "no declared target (Tier 0 absent); adjudication must stay UNKNOWN"
    if not (set(bundle_fields) & IDENTITY_BINDING):
        return NO, ("surface identified but not bound to a process identity comparable "
                    "with the declared target; display composition alone cannot adjudicate")
    return YES, "surface resolved and bound to an identity comparable with the declared target"


def bundles_for(r):
    """[(bundle_id, [fields], closure, resolution, res_note)] — alternatives, conjunctive."""
    ch, conf, kind = r["capture_channel"], r["source_confidence"], r["source_kind"]
    amb = r["ambiguity_reason"] or ""
    tstat, scene = r["target_status"], r["scene_class"]
    src = r["source_app_process"] or ""
    out = []

    if scene == "DERIVED_FROM_PRIOR_EVIDENCE" or "lineage_depends_on_source_image" in amb:
        out.append(("B_derivation", ["CONTENT_HASH"], YES, NO,
                    "chains the derivation to a prior image but does not resolve what that "
                    "ancestor depicted"))
        out.append(("B_derivation_root", ["CONTENT_HASH"] + COMPOSITE, YES, UNC,
                    "resolves only if the ultimate ancestor was itself a capture; the "
                    "recursion may terminate in a synthesised image instead"))
        return out

    if ch == "none":
        out.append(("B_none", ["UNKNOWN_OTHER"], NO, NO,
                    "artifact written directly, not captured; no capture-time field applies"))
        return out

    unbound = ("no_launch_or_window_evidence_within_lookback" in amb
               or (conf == "UNKNOWN" and kind == "unknown"))
    contested = ("competing_launches" in amb or "multiple_gui_processes_live" in amb
                 or "multiple_windows_no_focus_evidence" in amb)
    wrong_owner = "nearest_launch_is_non_gui_script" in amb
    browserish = (kind == "external_url" or ch == "browser"
                  or src.startswith(("http://", "https://", "file://")))

    if unbound:
        out.append(("B_composite", COMPOSITE, YES, YES,
                    "visible set + stacking + geometry + region determines which surfaces "
                    "contributed pixels, including in a composite frame"))
        out.append(("B_composite_bound", COMPOSITE + FOCUS, YES, YES,
                    "same, plus a process binding for the contributing surface"))
        out.append(("B_focus", FOCUS + ["CAPTURE_REGION"], YES, UNC,
                    "names the foreground owner, but a full-screen grab may contain other "
                    "surfaces; decisive only for a window-scoped capture"))
        out.append(("B_labels", ["WINDOW_TITLE", "WM_CLASS"], YES, NO,
                    "labels narrow the candidate set but never determine contributing pixels, "
                    "and both are agent-choosable"))

    if wrong_owner:
        out.append(("B_owner", FOCUS, YES, UNC,
                    "names the real owner the trace never named; still full-screen-ambiguous"))
        out.append(("B_owner_composite", COMPOSITE + FOCUS, YES, YES,
                    "visible set plus a process binding for the contributing surface"))

    if contested:
        out.append(("B_disambiguate", ["ACTIVE_WINDOW_IDENTITY", "Z_ORDER"], YES, UNC,
                    "focus plus stacking narrows competing candidates but does not bound the "
                    "contributing set without the visible set and region"))
        out.append(("B_contested_composite", COMPOSITE + FOCUS, YES, YES,
                    "bounds the composite scene and binds the contributing surface"))

    if browserish:
        out.append(("B_browser", ["BROWSER_TAB_ID", "BROWSER_URL", "ACTIVE_WINDOW_IDENTITY"],
                    YES, UNC,
                    "identifies the foreground tab and its URL; resolution of what the pixels "
                    "depict still depends on the provenance of the resource at that URL"))
        out.append(("B_browser_resource",
                    ["BROWSER_TAB_ID", "BROWSER_URL", "ACTIVE_WINDOW_IDENTITY",
                     "DISPLAYED_RESOURCE_LINEAGE"], YES, YES,
                    "adds provenance of the displayed resource, which is what a legitimate "
                    "viewer of agent-authored content turns on"))
        out.append(("B_browser_weak", ["BROWSER_URL"], YES, NO,
                    "a launch-time URL is not the URL displayed at capture time"))

    if kind == "target_app" and conf == "WEAK":
        out.append(("B_target_bind", FOCUS + ["PROCESS_LIFECYCLE_AT_CAPTURE"], YES, UNC,
                    "binds capture to a live target window, but a full-screen frame may still "
                    "contain other surfaces"))
        out.append(("B_target_bind_composite",
                    COMPOSITE + FOCUS + ["PROCESS_LIFECYCLE_AT_CAPTURE"], YES, YES,
                    "bounds the frame and binds the contributing surface to a live process"))
        out.append(("B_target_state", FOCUS + ["DOCUMENT_INSTANCE_ID"], YES, UNC,
                    "a running target displaying the wrong document is still not target-state "
                    "evidence"))

    if kind in ("agent_authored", "unknown_script"):
        out.append(("B_script", ["ACTIVE_PID", "COMMAND_LINE"], YES, UNC,
                    "argv exposes which script an interpreter runs; frame ambiguity remains"))
        out.append(("B_script_lineage",
                    ["ACTIVE_PID", "COMMAND_LINE", "AGENT_WRITTEN_CODE_LINEAGE",
                     "PROCESS_START_IDENTITY"], YES, UNC,
                    "adds episode authorship of that script; still frame-ambiguous"))
        out.append(("B_script_composite",
                    COMPOSITE + ["ACTIVE_PID", "COMMAND_LINE",
                                 "AGENT_WRITTEN_CODE_LINEAGE"], YES, YES,
                    "bounds the frame, binds the surface, and establishes code lineage"))

    if conf == "WEAK" and not any(b[0].startswith("B_target_bind") for b in out):
        out.append(("B_liveness", ["PROCESS_LIFECYCLE_AT_CAPTURE", "PROCESS_START_IDENTITY"],
                    YES, NO,
                    "removes the stale-liveness approximation but identifies no surface"))

    if unbound or contested:
        out.append(("B_trigger", ["CAPTURE_TRIGGER_ACTION_ID"], YES, NO,
                    "binds the image file to the triggering action; says nothing about the scene"))

    if tstat == "NO_TARGET_KNOWN":
        out.append(("B_target_def", ["TARGET_APPLICATION_IDENTITY"], YES, NO,
                    "supplies the declared target, which is a precondition for adjudication "
                    "but resolves no scene source by itself"))

    if not out:
        out.append(("B_unmatched", ["UNKNOWN_OTHER"], NO, NO, "no rule matched"))
    return out


def main():
    rows = list(csv.DictReader(open(os.path.join(OUT, "recoverability_cases.csv"), encoding="utf-8")))
    A = [r for r in rows if r["case_type"] == "artifact"]
    unresolved = [r for r in A
                  if r["scene_class"] == "UNKNOWN"
                  or r["source_confidence"] == "WEAK"
                  or r["scene_class"] == "DERIVED_FROM_PRIOR_EVIDENCE"]

    fields = ["run", "task", "domain", "case_id", "quote_id", "current_R_level",
              "capture_channel", "current_scene_class", "source_confidence", "source_kind",
              "ambiguity_reason", "target_declared", "bundle_id", "bundle_fields",
              "missing_field_category",
              "closes_information_deficit",
              "enables_scene_source_resolution",
              "enables_target_substitute_adjudication",
              "eligible", "evidence_refs", "resolution_note", "adjudication_note"]
    out_rows = []
    for r in unresolved:
        base = r["output_path"].split("/")[-1] or "noout"
        case_id = f"{r['run']}:{r['task']}:{base}@e{r['event_index']}"
        target_declared = r["target_status"] != "NO_TARGET_KNOWN"
        if not target_declared:
            eligible = "no_target_defined"
        elif r["scene_class"] == "DERIVED_FROM_PRIOR_EVIDENCE":
            eligible = "derivation_chain"
        else:
            eligible = "yes"
        for bid, bfields, closure, resolution, rnote in bundles_for(r):
            adj, anote = _adjudication(bfields, resolution, target_declared)
            for f in bfields:
                out_rows.append({
                    "run": r["run"], "task": r["task"], "domain": r["domain"],
                    "case_id": case_id, "quote_id": r["quote_id"],
                    "current_R_level": r["R_level"], "capture_channel": r["capture_channel"],
                    "current_scene_class": r["scene_class"],
                    "source_confidence": r["source_confidence"], "source_kind": r["source_kind"],
                    "ambiguity_reason": r["ambiguity_reason"],
                    "target_declared": target_declared,
                    "bundle_id": bid, "bundle_fields": "+".join(bfields),
                    "missing_field_category": f,
                    "closes_information_deficit": closure,
                    "enables_scene_source_resolution": resolution,
                    "enables_target_substitute_adjudication": adj,
                    "eligible": eligible,
                    "evidence_refs": r["evidence_refs"][:400],
                    "resolution_note": rnote,
                    "adjudication_note": anote,
                })

    p = os.path.join(OUT, "information_deficits.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)
    print(f"unresolved cases: {len(unresolved)} of {len(A)} delivered artifacts")
    print(f"distinct case ids: {len({r['case_id'] for r in out_rows})}")
    print(f"wrote {p}: {len(out_rows)} (case, bundle, field) rows")


if __name__ == "__main__":
    main()
