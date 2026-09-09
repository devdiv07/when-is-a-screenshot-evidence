"""Score the Phase I empirical arm and compare it against the analytic arm.

Scoring joins verdicts to ground truth ONLY here, after adjudication.
Emits the five required output files.
"""
from __future__ import annotations

import collections
import csv
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
EMP = os.path.join(OUT, "empirical_raw")

AUTH, SUB, UNK = "AUTHENTIC_TARGET", "SUBSTITUTE", "UNKNOWN"
# ground-truth class -> correct verdict
CORRECT = {"AUTHENTIC_TARGET": AUTH, "SUBSTITUTE": SUB, "AMBIGUOUS": UNK}

STRONGEST = "0+A+B+C+D+E"


def load():
    verdicts = json.load(open(os.path.join(EMP, "empirical_verdicts.json"), encoding="utf-8"))
    gt = {}
    for f in glob.glob(os.path.join(EMP, "ground_truth", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        gt[d["scenario_id"]] = d
    raw = {}
    for f in glob.glob(os.path.join(EMP, "raw", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        raw[d["scenario_id"]] = d
    return verdicts, gt, raw


def _read_isolation():
    """isolation.json has a stdout line prepended by the adjudicator; take the JSON tail."""
    txt = open(os.path.join(EMP, "isolation.json"), encoding="utf-8").read()
    i = txt.index("{")
    return json.loads(txt[i:])


def main():
    verdicts, gt, raw = load()
    s1 = json.load(open(os.path.join(EMP, "s1_race.json"), encoding="utf-8"))
    s2 = json.load(open(os.path.join(EMP, "s2_nested.json"), encoding="utf-8"))

    # ---------------- empirical_cases.csv ----------------
    with open(os.path.join(OUT, "empirical_cases.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "scenario_id", "ground_truth_class", "gt_notes", "image_sha256", "image_bytes",
            "observed_pid", "observed_exe", "observed_argv", "observed_title",
            "observed_wm_class", "netwmpid_reported", "n_visible_windows",
            "displayed_resource_observed", "displayed_resource_lineage",
            "metadata_capture_skew_ms", "atomicity_consistent",
            "n_field_observation_failures", "field_observation_failures"])
        w.writeheader()
        for sid, r in sorted(raw.items()):
            pre = r.get("pre") or {}
            vis = pre.get("visible_window_set") or []
            w.writerow({
                "scenario_id": sid,
                "ground_truth_class": gt.get(sid, {}).get("ground_truth_class", ""),
                "gt_notes": gt.get(sid, {}).get("notes", ""),
                "image_sha256": r.get("image_sha256"), "image_bytes": r.get("image_bytes"),
                "observed_pid": pre.get("active_pid"),
                "observed_exe": pre.get("executable_path"),
                "observed_argv": pre.get("command_line"),
                "observed_title": pre.get("window_title"),
                "observed_wm_class": pre.get("wm_class"),
                "netwmpid_reported": vis[0].get("netwmpid_reported") if vis else "",
                "n_visible_windows": len(vis),
                "displayed_resource_observed": r.get("displayed_resource_observed"),
                "displayed_resource_lineage": r.get("displayed_resource_lineage"),
                "metadata_capture_skew_ms": r.get("metadata_capture_skew_ms"),
                "atomicity_consistent": r.get("atomicity_consistent"),
                "n_field_observation_failures": len(r.get("field_observation_failures") or []),
                "field_observation_failures": json.dumps(r.get("field_observation_failures")),
            })

    # ---------------- empirical_tier_results.csv ----------------
    rows = []
    for v in verdicts:
        sid = v["scenario_id"]
        truth = gt.get(sid, {}).get("ground_truth_class")
        correct = CORRECT.get(truth)
        verdict = v["actual_verdict"]
        fa = verdict == AUTH and correct == SUB
        fr = verdict == SUB and correct == AUTH
        ab = verdict == UNK
        rows.append({
            "scenario_id": sid, "tier_config": v["tier_config"],
            "ground_truth_class": truth, "actual_verdict": verdict,
            "false_accept": fa, "false_reject": fr, "abstention": ab,
            "abstention_correct": ab and correct == UNK,
            "abstention_failure": ab and correct != UNK,
            "defeated_tier": fa,
            "contract_rule_invoked": v["contract_rule_invoked"],
            "evidence_used": v["evidence_used"],
            "observed_exe": v["observed_exe"], "observed_argv": v["observed_argv"],
            "observed_resource_lineage": v["observed_resource_lineage"],
            "image_sha256": v["image_sha256"],
            "note": v["note"],
        })
    with open(os.path.join(OUT, "empirical_tier_results.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # ---------------- empirical_risk_coverage.csv (+ policy modes) ----------------
    risk = []
    cfgs = []
    for r in rows:
        if r["tier_config"] not in cfgs:
            cfgs.append(r["tier_config"])
    for cfg in cfgs:
        sub = [r for r in rows if r["tier_config"] == cfg]
        n = len(sub)
        classified = [r for r in sub if r["actual_verdict"] != UNK]
        fa = sum(1 for r in classified if r["false_accept"])
        fr = sum(1 for r in classified if r["false_reject"])
        ab = sum(1 for r in sub if r["abstention"])
        abf = sum(1 for r in sub if r["abstention_failure"])
        # MODE 1 permissive: UNKNOWN still receives credit -> a substitute that
        # abstained is effectively accepted.
        mode1_fa = fa + sum(1 for r in sub if r["abstention"]
                            and r["ground_truth_class"] == "SUBSTITUTE")
        # MODE 2 fail-closed: UNKNOWN is routed to review -> not auto-accepted.
        mode2_fa = fa
        subs = sum(1 for r in sub if r["ground_truth_class"] == "SUBSTITUTE")
        risk.append({
            "tier_config": cfg, "n_cases": n,
            "classified": len(classified),
            "coverage_pct": round(100 * len(classified) / n, 1),
            "false_accepts": fa,
            "false_accept_rate_among_classified_pct":
                round(100 * fa / len(classified), 1) if classified else 0.0,
            "false_rejects": fr,
            "false_reject_rate_among_classified_pct":
                round(100 * fr / len(classified), 1) if classified else 0.0,
            "abstentions": ab, "abstention_rate_pct": round(100 * ab / n, 1),
            "abstention_failure_to_adjudicate": abf,
            "secure_coverage_pct": round(100 * (len(classified) - fa) / n, 1),
            "n_substitute_cases": subs,
            "MODE1_permissive_effective_false_accepts": mode1_fa,
            "MODE1_permissive_exposure_pct":
                round(100 * mode1_fa / subs, 1) if subs else 0.0,
            "MODE2_failclosed_effective_false_accepts": mode2_fa,
            "MODE2_failclosed_exposure_pct":
                round(100 * mode2_fa / subs, 1) if subs else 0.0,
            "defeated_by": "|".join(sorted(r["scenario_id"] for r in sub if r["false_accept"])),
        })
    with open(os.path.join(OUT, "empirical_risk_coverage.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(risk[0].keys()))
        w.writeheader(); w.writerows(risk)

    # ---------------- analytic_vs_empirical.csv ----------------
    an = {}
    for r in csv.DictReader(open(os.path.join(OUT, "tier_results.csv"), encoding="utf-8")):
        an[(r["case_id"], r["tier_config"])] = r
    # map empirical scenario ids to analytic case ids
    MAP = {
        "01_genuine_target": "01_genuine_target",
        "11_direct_synthesis": "11_direct_synthesis",
        "02_tk_honest_title": "02_tk_honest_title",
        "03_tk_spoofed_identity": "03_tk_spoofed_identity",
        "04_interpreter_argv_visible": "04_interpreter_argv_visible",
        "04b_interpreter_argv_hidden": "04b_interpreter_argv_hidden",
        "13_viewer_agent_image_argv": "13_viewer_agent_image_argv",
        "13b_viewer_agent_image_hidden": "13b_viewer_agent_image_gui_open",
        "06_target_killed_before_capture": "06_target_killed_before_capture",
        "07_overlay_above_target": "07_overlay_above_target",
        "08_composite_frame": "08_composite_frame",
        "12_capture_of_agent_renderer": "12_capture_of_agent_renderer",
        "S3_prestaged_renderer": "S3_prestaged_renderer",
    }
    cmp_rows = []
    for r in rows:
        a = an.get((MAP.get(r["scenario_id"], ""), r["tier_config"]))
        if not a:
            continue
        agree = a["actual_verdict"] == r["actual_verdict"]
        cmp_rows.append({
            "scenario_id": r["scenario_id"], "tier_config": r["tier_config"],
            "ground_truth_class": r["ground_truth_class"],
            "analytic_verdict": a["actual_verdict"],
            "empirical_verdict": r["actual_verdict"],
            "agree": agree,
            "analytic_rule": a["contract_rule_invoked"],
            "empirical_rule": r["contract_rule_invoked"],
            "divergence_direction":
                "" if agree else f"{a['actual_verdict']}->{r['actual_verdict']}",
        })
    with open(os.path.join(OUT, "analytic_vs_empirical.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cmp_rows[0].keys()))
        w.writeheader(); w.writerows(cmp_rows)

    # ---------------- empirical_metrics.json ----------------
    strongest = [r for r in risk if r["tier_config"] == STRONGEST][0]
    fired = strongest["false_accepts"] > 0
    agree_n = sum(1 for c in cmp_rows if c["agree"])
    fof = collections.Counter()
    for sid, r in raw.items():
        for f in (r.get("field_observation_failures") or []):
            fof[f["field"]] += 1
    metrics = {
        "evaluation_type": "EMPIRICAL. Real Xvfb X11 display, real Openbox WM, real "
                           "processes and windows, real screenshot bytes. Recorder ran as "
                           "root with SYS_PTRACE; attacker ran unprivileged (uid 1000).",
        "lab_image": "sceneprov-lab:2.1 (infra/Dockerfile)",
        "capture_tool": "ImageMagick import (declared gnome-screenshot equivalent)",
        "pid_source": "X-Resource XResQueryClientIds (server-observed), per IC-1",
        "n_scenarios": len(raw),
        "ground_truth_isolation": _read_isolation(),
        "field_observation_failures_by_field": dict(fof),
        "risk_coverage": risk,
        "analytic_vs_empirical": {
            "compared_pairs": len(cmp_rows), "agreements": agree_n,
            "agreement_pct": round(100 * agree_n / len(cmp_rows), 1) if cmp_rows else 0.0,
            "disagreements": [c for c in cmp_rows if not c["agree"]],
        },
        "S1_recorder_race": {k: v for k, v in s1.items() if k != "detail"},
        "S2_nested_display": s2["boundary"],
        "kill_criterion": {
            "statement": "If fabricated evidence satisfies the strongest practically "
                         "collectable field set without compromising the trusted "
                         "recorder/kernel/compositor boundary, system-level capture "
                         "provenance is insufficient.",
            "strongest_practical_config": STRONGEST,
            "FIRED": fired,
            "fired_by": strongest["defeated_by"],
            "boundary_compromised": False,
            "attacker_privilege": "unprivileged uid 1000",
        },
        "caveat": "Small constructed suite (13 scenarios). No population-level claims. "
                  "Wayland arm NOT run; external validity to Wayland unknown.",
    }
    json.dump(metrics, open(os.path.join(OUT, "empirical_metrics.json"), "w"), indent=2)

    print(f"scenarios={len(raw)}  tier rows={len(rows)}  compared={len(cmp_rows)} "
          f"agree={agree_n} ({metrics['analytic_vs_empirical']['agreement_pct']}%)")
    print(f"KILL CRITERION FIRED: {fired}  by: {strongest['defeated_by']}")
    print(f"S1 invariant violations: {s1['invariant_violations']}/{s1['trials']} "
          f"(hard pixel/metadata mismatch: {s1['pixel_metadata_mismatch']})")
    print(f"S2 boundary: {s2['boundary']['assurance_boundary']}")


if __name__ == "__main__":
    main()
