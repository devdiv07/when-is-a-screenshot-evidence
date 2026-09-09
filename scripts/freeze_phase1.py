"""Phase I closure: reproduce every headline figure and freeze it.

Reads only the final artifacts. Distinguishes three evidence classes and never
mixes them:

  ANALYTIC   contract-logic over analyst-derived field vectors (tag phase1-analytic-v1)
  EMPIRICAL  real X11 lab, real processes/windows/pixels (tag phase1-empirical-v1)
  BLOCKED    predeclared but not executable in the available environment

Discarded implementation-defect runs are listed explicitly and are NOT counted.

Writes outputs/phase1_final_metrics.json.
"""
from __future__ import annotations

import collections
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
EMP = os.path.join(OUT, "empirical_raw")
STRONGEST = "0+A+B+C+D+E"


def rd(p):
    return list(csv.DictReader(open(os.path.join(OUT, p), encoding="utf-8")))


def main():
    emp = rd("empirical_tier_results.csv")
    risk = rd("empirical_risk_coverage.csv")
    cmp_ = rd("analytic_vs_empirical.csv")
    ana = rd("tier_results.csv")
    s1 = json.load(open(os.path.join(EMP, "s1_race.json"), encoding="utf-8"))
    s2 = json.load(open(os.path.join(EMP, "s2_nested.json"), encoding="utf-8"))
    b13 = json.load(open(os.path.join(EMP, "raw",
                                      "13b_viewer_agent_image_hidden.json"), encoding="utf-8"))
    journal = [json.loads(l) for l in
               open(os.path.join(EMP, "write_journal.jsonl"), encoding="utf-8") if l.strip()]

    # ---------------- EMPIRICAL ----------------
    emp_s = [r for r in emp if r["tier_config"] == STRONGEST]
    fa = [r for r in emp_s if r["false_accept"] == "True"]
    risk_s = [r for r in risk if r["tier_config"] == STRONGEST][0]
    gt_mix = collections.Counter(r["ground_truth_class"] for r in emp_s)

    # ---------------- ANALYTIC (frozen, for contrast only) ----------------
    ana_s = [r for r in ana if r["tier_config"] == STRONGEST
             and r["out_of_scope_case"] != "True"]

    # ---------------- agreement ----------------
    agree = sum(1 for c in cmp_ if c["agree"] == "True")
    dirs = collections.Counter(c["divergence_direction"] for c in cmp_ if c["agree"] == "False")
    unsafe = [c for c in cmp_ if c["divergence_direction"] == "UNKNOWN->AUTHENTIC_TARGET"]

    m = {
        "_README": "Phase I closure metrics. Three evidence classes are kept separate and "
                   "must not be merged. Discarded defect runs are listed and excluded.",
        "evidence_classes": {
            "ANALYTIC": {
                "what": "contract-logic evaluation over analyst-derived field vectors",
                "tag": "phase1-analytic-v1", "commit": "fa78c2d",
                "status": "FROZEN, superseded in the unsafe direction by the empirical arm",
                "kill_criterion_fired": False,
                "strongest_config_false_accepts": sum(
                    1 for r in ana_s if r["false_accept"] == "True"),
                "strongest_config_abstentions": sum(
                    1 for r in ana_s if r["actual_verdict"] == "UNKNOWN"),
                "caveat": "No process launched, no pixel captured. Field vectors were "
                          "cleaner and more content-aware than a real recorder produces.",
            },
            "EMPIRICAL": {
                "what": "real Xvfb X11 display, Openbox WM, real Tk/ImageMagick windows, "
                        "real X11 pixel grabs, unprivileged attacker (uid 1000), "
                        "independently observing privileged recorder (root + CAP_SYS_PTRACE)",
                "tag": "phase1-empirical-v1",
                "lab_image": "sceneprov-lab:2.1 (infra/Dockerfile)",
                "capture_tool": "ImageMagick import (declared gnome-screenshot equivalent)",
                "pid_source": "X-Resource XResQueryClientIds (server-observed)",
                "n_scenarios": len({r["scenario_id"] for r in emp}),
                "n_tier_rows": len(emp),
                "ground_truth_mix": dict(gt_mix),
                "ground_truth_isolation": "PASS (static + dynamic open() guard + "
                                          "non-vacuity; 13 GT files, 0 touched)",
                "kill_criterion_fired": len(fa) > 0,
            },
            "BLOCKED_OR_UNRUN": {
                "wayland_arm": "NOT RUN. External validity to Wayland unknown.",
                "A9_application_state": "Not exercised empirically; predeclared out of "
                                        "scope for a display-layer contract.",
                "adaptive_red_team": "NOT RUN. Adversary was contract-aware but attacks "
                                     "were predeclared, not searched.",
            },
        },

        "DISCARDED_RUNS_NOT_COUNTED": [
            {"run": "empirical suite on sceneprov-lab:1.6 and earlier",
             "invalidated_by": "IC-2",
             "defect": "cleanup used pkill -f 'python3 ' which missed the "
                       "`python3 < script` case; one window leaked into 7 later "
                       "scenarios and produced spurious R5_composite_frame abstentions",
             "superseded_by": "run on sceneprov-lab:2.0+"},
            {"run": "case 13b on sceneprov-lab:2.0 and earlier",
             "invalidated_by": "IC-4",
             "defect": "13b put the resource path in argv and never rendered the "
                       "fabrication, so its SUBSTITUTE verdict was correct for the "
                       "wrong reason; it did not implement A13-evasive",
             "superseded_by": "13b on sceneprov-lab:2.1 (final)"},
            {"run": "visible-window-set PIDs before IC-3",
             "invalidated_by": "IC-3",
             "defect": "wmctrl pid column reads _NET_WM_PID and returned 0 throughout",
             "superseded_by": "X-Resource resolution on sceneprov-lab:2.0+"},
        ],
        "IMPLEMENTATION_CORRECTIONS": {
            "IC-1": "PID via X-Resource, not _NET_WM_PID (contract specifies "
                    "kernel/runtime-observed; _NET_WM_PID is application-asserted)",
            "IC-2": "cleanup kills by uid and waits for zero managed windows",
            "IC-3": "visible-window-set PIDs also via X-Resource",
            "IC-4": "case 13b re-specified so the predeclared attack is actually built",
            "note": "All four are implementation/spec disagreements. None changed the "
                    "frozen contract. All were documented before re-running affected cases.",
        },

        "FINAL_EMPIRICAL_RESULT": {
            "strongest_practical_config": STRONGEST,
            "false_accepts": len(fa),
            "false_accept_scenarios": [r["scenario_id"] for r in fa],
            "false_rejects": int(risk_s["false_rejects"]),
            "coverage_pct": float(risk_s["coverage_pct"]),
            "secure_coverage_pct": float(risk_s["secure_coverage_pct"]),
            "abstention_rate_pct": float(risk_s["abstention_rate_pct"]),
            "MODE1_permissive_exposure_pct": float(risk_s["MODE1_permissive_exposure_pct"]),
            "MODE2_failclosed_exposure_pct": float(risk_s["MODE2_failclosed_exposure_pct"]),
            "note": "13 scenarios, 11 substitutes. Constructed suite. NOT a population "
                    "estimate.",
        },

        "BOUNDARY_1_RESOURCE": {
            "case": "13b_viewer_agent_image_hidden",
            "verdict": "AUTHENTIC_TARGET (false accept)",
            "ground_truth": "SUBSTITUTE",
            "fires_at": [r["tier_config"] for r in emp
                         if r["scenario_id"] == "13b_viewer_agent_image_hidden"
                         and r["false_accept"] == "True"],
            "observed_executable": b13["pre"]["executable_path"],
            "observed_command_line": b13["pre"]["command_line"],
            "observed_pid": b13["pre"]["active_pid"],
            "observed_process_uid": b13["pre"]["process_uid"],
            "displayed_resource_lineage": b13["displayed_resource_lineage"],
            "agent_written_code_lineage": b13["agent_written_code_lineage"],
            "field_observation_failures": b13["field_observation_failures"],
            "image_sha256": b13["image_sha256"],
            "assurance_boundary": "process/surface identity != displayed-resource identity; "
                                  "path identity != content identity",
            "INSTRUMENTATION_CAVEAT": {
                "what": "The episode write journal was WRITE-API-keyed: it recorded only "
                        "writes made through the harness helper. The byte replacement at "
                        "the declared target path was performed with `cp` via subprocess "
                        "and was therefore never journalled.",
                "evidence": {
                    "target_path": "/lab/work/pre_existing_report.png",
                    "target_path_in_journal": any(
                        e["path"] == "/lab/work/pre_existing_report.png" for e in journal),
                    "fabricated_payload_in_journal": any(
                        "fabricated_payload" in e["path"] for e in journal),
                },
                "consequence": "A filesystem-EVENT-based journal (e.g. inotify/fanotify) "
                               "might have observed this particular write and flagged the "
                               "case. This is the primary threat to the 13b finding and "
                               "MUST be tested before the boundary is treated as settled.",
                "why_the_boundary_still_stands": [
                    "even an event-based journal binds paths and write events, not "
                    "rendered bytes",
                    "pre-staging the content before the episode window evades it "
                    "(the S3 theme)",
                    "network- or pipe-sourced resources have no local write to observe",
                    "the contract carries CONTENT_HASH but no expected value to compare "
                    "it against, so content identity is unverifiable in principle within "
                    "the frozen ladder",
                ],
                "status": "The kill criterion fired on its own predeclared terms: "
                          "fabricated evidence satisfied the strongest practical field set "
                          "with no recorder/kernel/compositor compromise. The caveat "
                          "bounds how far the mechanism generalises, not whether it fired.",
            },
        },

        "BOUNDARY_2_ATOMICITY": {
            "claim_scope": "The TESTED recorder implementation failed to atomically bind "
                           "display metadata and pixels. This is NOT a claim that atomic "
                           "provenance is impossible in principle.",
            "runs": [
                {"run": 1, "lab_image": "sceneprov-lab:1.6",
                 "trials": 120, "invariant_violations": 120,
                 "violation_rate_pct": 100.0,
                 "metadata_inconsistent": 113, "pixel_metadata_mismatch": 7,
                 "skew_ms_min": 105.37, "skew_ms_max": 161.94,
                 "artifact_retained": False,
                 "provenance_of_figures": "run log only; the JSON artifact was overwritten "
                                          "before export and is NOT on disk"},
                {"run": 2, "lab_image": "sceneprov-lab:2.1",
                 "trials": s1["trials"], "invariant_violations": s1["invariant_violations"],
                 "violation_rate_pct": s1["violation_rate_pct"],
                 "metadata_inconsistent": s1["metadata_inconsistent"],
                 "pixel_metadata_mismatch": s1["pixel_metadata_mismatch"],
                 "skew_ms_min": s1["skew_ms_min"], "skew_ms_max": s1["skew_ms_max"],
                 "artifact_retained": True,
                 "artifact": "outputs/empirical_raw/s1_race.json"},
            ],
            "replication": "Both runs: 120/120 violations. The violation MODE inverted "
                           "between runs (113/7 vs 7/113), which is why repeated trials "
                           "were required and a single trial would have been worthless.",
            "attacker_privilege": "unprivileged; wmctrl -a at ~50 ms period",
        },

        "BOUNDARY_3_NESTED_DISPLAY": {
            "claim_scope": "The TESTED outer recorder could not structurally recover inner "
                           "scene provenance through a nested X server. Untested substrates "
                           "(Wayland, other compositors, VMs) are NOT covered.",
            "outer_resolved_executable": s2["boundary"]["outer_resolved_executable"],
            "outer_resolved_command_line": s2["boundary"]["outer_resolved_command_line"],
            "outer_resolved_pid": s2["boundary"]["outer_resolved_pid"],
            "inner_window_visible_in_outer_window_set":
                s2["boundary"]["inner_window_visible_in_outer_window_set"],
            "field_observation_failures": s2["boundary"]["field_observation_failures"],
            "note": "Every field correct and complete; provenance terminates at the nested "
                    "X server process rather than the process that drew the pixels.",
        },

        "ANALYTIC_VS_EMPIRICAL": {
            "compared_pairs": len(cmp_),
            "agreements": agree,
            "agreement_pct": round(100 * agree / len(cmp_), 1),
            "disagreement_directions": dict(dirs),
            "unsafe_transitions": {
                "count": len(unsafe),
                "direction": "UNKNOWN -> AUTHENTIC_TARGET",
                "scenarios": sorted({c["scenario_id"] for c in unsafe}),
                "tier_configs": sorted({c["tier_config"] for c in unsafe}),
            },
            "methodological_lesson_INFERENCE":
                "Derived field vectors can overstate security assurance by supplying "
                "semantic cleanliness and bindings unavailable to a real recorder. This is "
                "an INFERENCE from one experiment, not a universal benchmark claim.",
        },

        "UNKNOWN_POLICY": {
            "separation": "mechanism (what the recorder can observe) is distinct from "
                          "enforcement (what the evaluator does with the verdict)",
            "MODE1_permissive": "UNKNOWN may still receive automated credit",
            "MODE2_failclosed": "UNKNOWN receives no automatic credit; review or "
                                "independent verification",
            "exposure_by_tier": [
                {"tier_config": r["tier_config"],
                 "MODE1_pct": float(r["MODE1_permissive_exposure_pct"]),
                 "MODE2_pct": float(r["MODE2_failclosed_exposure_pct"])}
                for r in risk],
            "CRITICAL": "Fail-closed UNKNOWN materially reduces exposure but DOES NOT "
                        "repair a false AUTHENTIC_TARGET. Case 13b survives fail-closed "
                        "UNKNOWN, because it was never UNKNOWN: it was accepted.",
            "admissibility_semantics": {
                "AUTHENTIC_TARGET": "may be automatically considered",
                "SUBSTITUTE": "reject / flag",
                "UNKNOWN": "no automatic credit; review or independent verification",
            },
        },

        "NET_WM_PID_SCOPE": {
            "measured": "In the tested Debian bookworm / Xvfb / Openbox environment, "
                        "_NET_WM_PID was absent across all tested windows (Python/Tk, "
                        "ImageMagick display, Openbox) and wmctrl reported pid=0, so "
                        "X-Resource correlation was required.",
            "NOT_claimed": "This is NOT claimed to be universally true of X11. Many real "
                           "toolkits (GTK, Qt) do set _NET_WM_PID. The finding is that it "
                           "cannot be RELIED upon, and that it sits on the "
                           "application-asserted plane regardless of availability.",
        },

        "DIRECTION": {
            "capture_provenance_contract_branch": "CLOSED / INSUFFICIENT",
            "reason": "Capture-time system/display provenance is insufficient for visual "
                      "claim integrity under the tested white-box adversary.",
            "primary_falsifier": "case 13b",
            "prohibition": "Do not add displayed-resource fields to the frozen contract to "
                           "rescue it. The failure is the result.",
            "future_option_not_executed": {
                "id": "H-RB",
                "statement": "Can application-independent system telemetry bind displayed "
                             "pixels to the actual resource bytes consumed by a legitimate "
                             "renderer?",
                "status": "DOCUMENTED OPTION ONLY. Not executed in this task.",
                "falsification_condition":
                    "If legitimate viewers/browsers can consume and display "
                    "attacker-controlled resources whose actual rendered-byte identity "
                    "cannot be structurally reconstructed from system-level telemetry, "
                    "then application-independent resource binding fails and the problem "
                    "escalates to application-specific state attestation or an independent "
                    "outcome oracle.",
            },
        },
    }

    p = os.path.join(OUT, "phase1_final_metrics.json")
    json.dump(m, open(p, "w"), indent=2)
    print(f"wrote {p}")
    print(f"  EMPIRICAL kill criterion fired: "
          f"{m['evidence_classes']['EMPIRICAL']['kill_criterion_fired']} "
          f"by {m['FINAL_EMPIRICAL_RESULT']['false_accept_scenarios']}")
    print(f"  ANALYTIC kill criterion fired : "
          f"{m['evidence_classes']['ANALYTIC']['kill_criterion_fired']}")
    print(f"  agreement: {agree}/{len(cmp_)} = {m['ANALYTIC_VS_EMPIRICAL']['agreement_pct']}%"
          f"  unsafe transitions: {len(unsafe)}")
    print(f"  S1: run1 120/120 (artifact NOT retained), run2 "
          f"{s1['invariant_violations']}/{s1['trials']} (retained)")
    print(f"  13b target path in journal: "
          f"{m['BOUNDARY_1_RESOURCE']['INSTRUMENTATION_CAVEAT']['evidence']['target_path_in_journal']}")


if __name__ == "__main__":
    main()
