"""Phase C — retrospective information-deficit attribution.

For every delivered visual artifact whose scene lineage did NOT reach
EXACT/STRONG, determine which specific missing information prevented it.

This measures RETROSPECTIVE INFORMATION DEFICIT on benign historical traces.
It is NOT a security or attestation-sufficiency test: a field that would have
resolved an old benign case may be trivially spoofable by an adversarial agent.
Adversarial sufficiency is Phase I and is explicitly NOT evaluated here.

Attribution is rule-based and deterministic. Each rule fires from the evidence
state actually recorded for the case (capture channel, source confidence,
source kind, ambiguity reason, target status), never from guesswork about what
the pixels contained.

RESOLUTION BUNDLES
------------------
Fields are emitted in conjunctive *bundles*, not as independent items. A single
field almost never resolves a case: Z_ORDER without VISIBLE_WINDOW_SET is
"stacking order of what?", and neither can be intersected with the image
without CAPTURE_REGION. A case counts as resolvable only when a whole bundle
is supplied. Each row carries `bundle_id`; rows sharing (case_id, bundle_id)
are a conjunction, and separate bundles are alternative ways to resolve the
same case.

Output: outputs/information_deficits.csv, one row per (case, bundle, field).
"""
from __future__ import annotations

import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

# ---------------------------------------------------------------- vocabulary
# Only categories justified by at least one real case in this corpus.
FIELDS = {
    "ACTIVE_WINDOW_IDENTITY": "which window held input focus at the capture instant",
    "ACTIVE_PID": "pid of the process owning the focused window",
    "PROCESS_START_IDENTITY": "pid + start time, to defeat pid reuse and stale liveness",
    "EXECUTABLE_PATH": "resolved executable backing the owning process",
    "COMMAND_LINE": "argv of the owning process (exposes the script an interpreter runs)",
    "AGENT_WRITTEN_CODE_LINEAGE": "whether the owning executable/script was authored this episode",
    "WINDOW_TITLE": "title string of the relevant window",
    "WM_CLASS": "window manager class of the relevant window",
    "WINDOW_GEOMETRY": "position and size of each relevant window",
    "VISIBLE_WINDOW_SET": "all mapped/visible windows at the capture instant",
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

# Composite-scene bundle: what it takes to say what a full-screen grab depicted.
COMPOSITE = ["VISIBLE_WINDOW_SET", "Z_ORDER", "CAPTURE_REGION", "WINDOW_GEOMETRY"]
# Focus bundle: what it takes to name the foreground owner.
FOCUS = ["ACTIVE_WINDOW_IDENTITY", "ACTIVE_PID"]


def bundles_for(r):
    """[(bundle_id, [fields], would_resolve, note)] — alternatives, each conjunctive."""
    ch, conf, kind = r["capture_channel"], r["source_confidence"], r["source_kind"]
    amb = r["ambiguity_reason"] or ""
    tstat, scene = r["target_status"], r["scene_class"]
    src = r["source_app_process"] or ""
    out = []

    # ---- derivation chains
    if scene == "DERIVED_FROM_PRIOR_EVIDENCE" or "lineage_depends_on_source_image" in amb:
        out.append(("B_derivation", ["CONTENT_HASH"], YES,
                    "hashing source and output chains the derivation to a specific prior image"))
        out.append(("B_derivation_root", ["CONTENT_HASH"] + COMPOSITE, UNC,
                    "resolves fully only if the ultimate ancestor was itself a capture; the "
                    "recursion may terminate in a synthesised image instead"))
        return out

    # ---- direct writes: no capture happened, no capture-time field applies
    if ch == "none":
        out.append(("B_none", ["UNKNOWN_OTHER"], NO,
                    "artifact was written directly, not captured; no capture-time field is relevant"))
        return out

    unbound = ("no_launch_or_window_evidence_within_lookback" in amb
               or (conf == "UNKNOWN" and kind == "unknown"))
    contested = ("competing_launches" in amb or "multiple_gui_processes_live" in amb
                 or "multiple_windows_no_focus_evidence" in amb)
    wrong_owner = "nearest_launch_is_non_gui_script" in amb
    browserish = (kind == "external_url" or ch == "browser"
                  or src.startswith(("http://", "https://", "file://")))

    # ---- the dominant failure: capture wholly unbound
    if unbound:
        out.append(("B_composite", COMPOSITE, YES,
                    "enumerating mapped windows with stacking and the captured rectangle bounds "
                    "what the pixels could depict, including composite scenes"))
        out.append(("B_focus", FOCUS + ["CAPTURE_REGION"], UNC,
                    "names the foreground owner, but a full-screen grab may still contain other "
                    "windows; decisive only for a window-scoped capture"))
        out.append(("B_labels", ["WINDOW_TITLE", "WM_CLASS"], NO,
                    "human-readable labels narrow the candidate set but never bind the scene, and "
                    "both are agent-choosable"))

    # ---- a launch was found but cannot own a window: the real owner is unnamed
    if wrong_owner:
        out.append(("B_owner", FOCUS, YES,
                    "the actual scene owner is a process the trace never names; focus identity "
                    "supplies it directly"))
        out.append(("B_owner_composite", COMPOSITE, YES,
                    "alternatively, enumerating the visible set names the owner"))

    # ---- several plausible candidates
    if contested:
        out.append(("B_disambiguate", ["ACTIVE_WINDOW_IDENTITY", "Z_ORDER"], YES,
                    "focus plus stacking disambiguates among competing live candidates"))
        out.append(("B_contested_composite", COMPOSITE, YES,
                    "alternatively, the full visible set bounds the composite scene"))

    # ---- browser-mediated scenes
    if browserish:
        out.append(("B_browser", ["BROWSER_TAB_ID", "BROWSER_URL", "ACTIVE_WINDOW_IDENTITY"], YES,
                    "the tab and URL actually foreground at capture time, plus evidence the browser "
                    "window itself was foreground"))
        out.append(("B_browser_weak", ["BROWSER_URL"], UNC,
                    "a launch-time URL is not the URL displayed at capture time"))

    # ---- target application live but capture not bindable to it
    if kind == "target_app" and conf == "WEAK":
        out.append(("B_target_bind", FOCUS + ["PROCESS_LIFECYCLE_AT_CAPTURE"], YES,
                    "target was running; only the binding of capture to target window was missing"))
        out.append(("B_target_state", FOCUS + ["DOCUMENT_INSTANCE_ID"], UNC,
                    "a running target displaying the wrong document is still not target-state evidence"))

    # ---- an agent-authored or unknown script was the candidate
    if kind in ("agent_authored", "unknown_script"):
        out.append(("B_script", ["ACTIVE_PID", "COMMAND_LINE"], YES,
                    "argv exposes which script an interpreter is running; pid binds it to the window"))
        out.append(("B_script_lineage",
                    ["ACTIVE_PID", "COMMAND_LINE", "AGENT_WRITTEN_CODE_LINEAGE",
                     "PROCESS_START_IDENTITY"], YES,
                    "adds whether that script was authored during the episode"))

    # ---- stale liveness was a measured error source (report Sect. 8)
    if conf == "WEAK" and not any(b[0] == "B_target_bind" for b in out):
        out.append(("B_liveness", ["PROCESS_LIFECYCLE_AT_CAPTURE", "PROCESS_START_IDENTITY"], YES,
                    "the audit had to approximate liveness and got it wrong at least once; a "
                    "capture-instant liveness record removes the approximation"))

    # ---- capture/artifact binding
    if unbound or contested:
        out.append(("B_trigger", ["CAPTURE_TRIGGER_ACTION_ID"], NO,
                    "binds the image file to the triggering action but says nothing about the scene"))

    # ---- the task itself never named a target application
    if tstat == "NO_TARGET_KNOWN":
        out.append(("B_target_def", ["TARGET_APPLICATION_IDENTITY"], YES,
                    "task specification names no application, so no capture-side field can decide "
                    "target vs substitute for this case"))

    if not out:
        out.append(("B_unmatched", ["UNKNOWN_OTHER"], UNC, "no rule matched this evidence state"))
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
              "ambiguity_reason", "bundle_id", "bundle_fields", "missing_field_category",
              "would_field_resolve_historical_case", "eligible", "evidence_refs", "notes"]
    out_rows = []
    for r in unresolved:
        base = r["output_path"].split("/")[-1] or "noout"
        case_id = f"{r['run']}:{r['task']}:{base}@e{r['event_index']}"
        if r["target_status"] == "NO_TARGET_KNOWN":
            eligible = "no_target_defined"
        elif r["scene_class"] == "DERIVED_FROM_PRIOR_EVIDENCE":
            eligible = "derivation_chain"
        else:
            eligible = "yes"
        for bid, bfields, verdict, note in bundles_for(r):
            for f in bfields:
                out_rows.append({
                    "run": r["run"], "task": r["task"], "domain": r["domain"],
                    "case_id": case_id, "quote_id": r["quote_id"],
                    "current_R_level": r["R_level"], "capture_channel": r["capture_channel"],
                    "current_scene_class": r["scene_class"],
                    "source_confidence": r["source_confidence"], "source_kind": r["source_kind"],
                    "ambiguity_reason": r["ambiguity_reason"],
                    "bundle_id": bid, "bundle_fields": "+".join(bfields),
                    "missing_field_category": f,
                    "would_field_resolve_historical_case": verdict,
                    "eligible": eligible,
                    "evidence_refs": r["evidence_refs"][:400],
                    "notes": note,
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
