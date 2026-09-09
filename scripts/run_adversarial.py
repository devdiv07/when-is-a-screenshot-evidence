"""Run the white-box adversarial case evaluation matrix.

Outputs:
  outputs/adversarial_cases.csv      one row per case (ground truth + predeclared prediction)
  outputs/tier_results.csv           one row per (case, tier config)
  outputs/risk_coverage.csv          per tier config: coverage, FA, FR, abstention
  outputs/adversarial_metrics.json   the same, machine-readable, plus blocked cases

Determinism is verified by construction: no randomness, no ordering dependence.
Deterministic cases are checked for reproducibility rather than resampled, because
repeating a deterministic computation adds no information.
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adversarial_cases import (CASES, TIER_CONFIGS, SENSITIVITY_CONFIGS,
                               AUTH, SUB, AMBIG, FALSE_CLAIM, DERIVED)
from adjudicator import adjudicate, UNK

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

# Predeclared predictions, fixed in THREAT_MODEL.md / the experiment spec BEFORE running.
# Keyed (case_id, tier_config) -> expected verdict. Only the load-bearing ones are declared.
PREDICTIONS = {
    ("03_tk_spoofed_identity", "0+A"): AUTH,          # P1: Tier A accepts a spoofed identity
    ("03_tk_spoofed_identity", "0+A+B"): SUB,         # P2: process identity contradicts it
    ("04b_interpreter_argv_hidden", "0+A+B"): SUB,    # P2: interpreter != target app
    ("05_browser_local_fake", "0+A+B"): AUTH,         # P2: browser is genuine, B cannot tell
    ("05_browser_local_fake", "0+A+B+C+D+E"): SUB,    # P5: URL contradicts target resource
    ("13_viewer_agent_image_argv", "0+A+B"): SUB,     # argv happens to disclose
    ("13b_viewer_agent_image_gui_open", "0+A+B"): AUTH,        # P8
    ("13b_viewer_agent_image_gui_open", "FULL(0+A..F)"): AUTH,  # P8: defeats the full set
    ("10_target_manipulated_state", "FULL(0+A..F)"): AUTH,      # P6: predeclared out of reach
    ("08_composite_frame", "0+A+B+C+D"): UNK,         # P4: correct abstention
    ("07_overlay_above_target", "0+A+B"): AUTH,       # focus-only cannot see occlusion
    ("07_overlay_above_target", "0+A+B+C+D"): SUB,    # P4: stacking reveals it
    ("01_genuine_target", "FULL(0+A..F)"): AUTH,      # control
    ("11_direct_synthesis", "0+A+B"): SUB,            # control
    ("S4_spoofed_document_id", "0+A+B+C+D+E"): SUB,   # plane check
}

# Ground truth -> what a correct verdict would be, for scoring.
CORRECT = {AUTH: AUTH, SUB: SUB, AMBIG: UNK, FALSE_CLAIM: AUTH, DERIVED: AUTH}
# FALSE_CLAIM and DERIVED are scene-authentic by construction: the contract is explicitly
# out of scope for them (A9, A8). Scoring them as AUTH avoids charging the capture layer
# with a failure it predeclared it cannot address; they are reported separately.
OUT_OF_SCOPE = {FALSE_CLAIM, DERIVED}


def main():
    os.makedirs(OUT, exist_ok=True)
    evaluable = [c for c in CASES if c["evaluable"]]
    blocked = [c for c in CASES if not c["evaluable"]]

    # ---- adversarial_cases.csv ----
    with open(os.path.join(OUT, "adversarial_cases.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["case_id", "attack", "ground_truth_class",
                                           "evaluable", "blocked_reason", "description",
                                           "construction_notes"])
        w.writeheader()
        for c in CASES:
            w.writerow({"case_id": c["case_id"], "attack": c["attack"],
                        "ground_truth_class": c["truth"], "evaluable": c["evaluable"],
                        "blocked_reason": c["blocked_reason"], "description": c["desc"],
                        "construction_notes": c["notes"]})

    # ---- tier_results.csv ----
    rows = []
    all_configs = [(n, cfg, ()) for n, cfg in TIER_CONFIGS.items()]
    all_configs += [(n, d["tiers"], tuple(d["drop_fields"]))
                    for n, d in SENSITIVITY_CONFIGS.items()]
    for c in evaluable:
        for cfg_name, cfg, drop in all_configs:
            verdict, rule, ev, note = adjudicate(c["fields"], cfg, drop)
            # reproducibility of a deterministic computation
            v2, r2, _e2, _n2 = adjudicate(c["fields"], cfg, drop)
            reproducible = (verdict, rule) == (v2, r2)

            truth = c["truth"]
            correct = CORRECT[truth]
            oos = truth in OUT_OF_SCOPE
            fa = (verdict == AUTH and correct == SUB)
            fr = (verdict == SUB and correct == AUTH and not oos)
            ab = (verdict == UNK)
            ab_correct = (verdict == UNK and correct == UNK)   # genuinely ambiguous frame
            ab_failure = (verdict == UNK and correct != UNK)   # failed to adjudicate
            defeated = fa  # the tier accepted fabricated evidence
            pred = PREDICTIONS.get((c["case_id"], cfg_name))
            rows.append({
                "case_id": c["case_id"], "attack": c["attack"],
                "ground_truth_class": truth, "tier_config": cfg_name,
                "fields_available": "|".join(sorted(
                    k for t in cfg for k in __import__("adversarial_cases").TIERS[t])),
                "trust_planes": "|".join(cfg),
                "predicted_verdict": pred or "",
                "actual_verdict": verdict,
                "false_accept": fa, "false_reject": fr, "abstention": ab,
                "abstention_correct": ab_correct, "abstention_failure": ab_failure,
                "out_of_scope_case": oos,
                "attack_mechanism": c["attack"],
                "evidence_used": " ; ".join(ev)[:600],
                "contract_rule_invoked": rule,
                "defeated_tier": defeated,
                "matches_prediction": ("" if pred is None else (pred == verdict)),
                "reproducible": reproducible,
                "note": note,
            })
    with open(os.path.join(OUT, "tier_results.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- risk_coverage.csv ----
    risk = []
    for cfg_name, _c, _d in all_configs:
        sub = [r for r in rows if r["tier_config"] == cfg_name]
        in_scope = [r for r in sub if not r["out_of_scope_case"]]
        classified = [r for r in in_scope if r["actual_verdict"] != UNK]
        fa = sum(1 for r in classified if r["false_accept"])
        fr = sum(1 for r in classified if r["false_reject"])
        ab = sum(1 for r in in_scope if r["abstention"])
        abc = sum(1 for r in in_scope if r["abstention_correct"])
        abf = sum(1 for r in in_scope if r["abstention_failure"])
        n = len(in_scope)
        risk.append({
            "tier_config": cfg_name,
            "n_in_scope_cases": n,
            "classified": len(classified),
            "coverage_pct": round(100 * len(classified) / n, 1) if n else 0.0,
            "false_accepts": fa,
            "false_accept_rate_among_classified_pct":
                round(100 * fa / len(classified), 1) if classified else 0.0,
            "false_rejects": fr,
            "false_reject_rate_among_classified_pct":
                round(100 * fr / len(classified), 1) if classified else 0.0,
            "abstentions": ab,
            "abstention_correct": abc,
            "abstention_failure_to_adjudicate": abf,
            "abstention_rate_pct": round(100 * ab / n, 1) if n else 0.0,
            "undetected_fabrication": "|".join(sorted(
                r["case_id"] for r in in_scope
                if r["abstention_failure"] and r["ground_truth_class"] == SUB)),
            "defeated_by": "|".join(sorted(r["case_id"] for r in sub if r["defeated_tier"])),
        })
    with open(os.path.join(OUT, "risk_coverage.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(risk[0].keys()))
        w.writeheader()
        w.writerows(risk)

    # ---- adversarial_metrics.json ----
    preds = [r for r in rows if r["matches_prediction"] != ""]
    metrics = {
        "evaluation_type": "CONTRACT-LOGIC (analytic). Not an empirical measurement.",
        "environment_limitation":
            "No X11/compositor/gnome-screenshot/privileged recorder available on the "
            "analysis host. Field vectors are analyst-derived from case construction. "
            "Timing- and platform-dependent cases were NOT run.",
        "n_cases_total": len(CASES),
        "n_cases_evaluated": len(evaluable),
        "n_cases_blocked": len(blocked),
        "blocked_cases": [{"case_id": c["case_id"], "attack": c["attack"],
                           "reason": c["blocked_reason"]} for c in blocked],
        "reproducible_all": all(r["reproducible"] for r in rows),
        "predictions_checked": len(preds),
        "predictions_matched": sum(1 for r in preds if r["matches_prediction"] is True),
        "prediction_mismatches": [
            {"case_id": r["case_id"], "tier_config": r["tier_config"],
             "predicted": r["predicted_verdict"], "actual": r["actual_verdict"]}
            for r in preds if r["matches_prediction"] is not True],
        "risk_coverage": risk,
        "kill_criterion": {
            "statement": "If fabricated evidence satisfies the strongest practically "
                         "collectable field set (Tier 0 + A..E + privileged atomic recorder, "
                         "excluding TEE) without compromising the recorder/kernel/compositor "
                         "boundary, system-level capture provenance is insufficient.",
            "strongest_practical_config": "0+A+B+C+D+E",
            "fired": None,  # filled below
            "fired_by": [],
        },
    }
    strongest = "0+A+B+C+D+E"
    metrics["sensitivity_arms"] = {n: d["why"] for n, d in SENSITIVITY_CONFIGS.items()}
    fired_by = sorted({r["case_id"] for r in rows
                       if r["tier_config"] == strongest and r["false_accept"]})
    metrics["kill_criterion"]["fired"] = bool(fired_by)
    metrics["kill_criterion"]["fired_by"] = fired_by
    json.dump(metrics, open(os.path.join(OUT, "adversarial_metrics.json"), "w"), indent=2)

    print(f"cases: {len(CASES)} total, {len(evaluable)} evaluated, {len(blocked)} BLOCKED")
    print(f"tier_results rows: {len(rows)}   all reproducible: {metrics['reproducible_all']}")
    print(f"predictions: {metrics['predictions_matched']}/{metrics['predictions_checked']} matched")
    for m in metrics["prediction_mismatches"]:
        print(f"   MISMATCH {m['case_id']} @ {m['tier_config']}: "
              f"predicted {m['predicted']}, got {m['actual']}")
    print(f"\nKILL CRITERION FIRED: {metrics['kill_criterion']['fired']}")
    for c in fired_by:
        print(f"   fabricated evidence accepted at {strongest}: {c}")


if __name__ == "__main__":
    main()
