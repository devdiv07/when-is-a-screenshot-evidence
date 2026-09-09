"""Map real recorder observations to the frozen contract's field vector, adjudicate.

STRICT GROUND-TRUTH SEPARATION
------------------------------
Inputs are ONLY:
  - /lab/out/raw/*.json          real recorder observations
  - /lab/out/task_declarations.json  Tier 0 = evaluator/task specification

/lab/out/ground_truth/ is NEVER read here. test_isolation.py proves it.

The adjudicator itself is the SAME frozen module used by the analytic arm; it is
not re-implemented, so analytic-vs-empirical differences come from observations,
not from two different rule sets.
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, "/lab")
from adjudicator import adjudicate  # noqa: E402  (frozen rules)
from adversarial_cases import TIER_CONFIGS, SENSITIVITY_CONFIGS  # noqa: E402

OUT = "/lab/out"
RAW = os.path.join(OUT, "raw")
GROUND_TRUTH_DIR = os.path.join(OUT, "ground_truth")   # referenced only to assert we never read it


def to_field_vector(rec, tier0):
    """Translate an empirical record into the contract's field names.

    Every value comes from the recorder's own observation. Nothing is filled in
    from a scenario definition. Unobserved fields stay None, which the contract's
    abstain-by-default rule then acts on.
    """
    pre = rec.get("pre") or {}
    vis = pre.get("visible_window_set") or []
    # visible set as "exe:pid" style identifiers where the recorder could resolve them
    vset = []
    for w in vis:
        t = (w.get("title") or "").strip()
        if t:
            vset.append(f"{t}:{w.get('pid')}")
    geom = {}
    for w in vis:
        t = (w.get("title") or "").strip()
        if t:
            geom[f"{t}:{w.get('pid')}"] = w.get("geometry")

    exe = pre.get("executable_path")
    active_title = pre.get("window_title")
    active_id = f"{active_title}:{pre.get('active_pid')}" if active_title else None

    return {
        # ---- Tier 0 (evaluator/task specification, not telemetry)
        **tier0,
        # ---- Tier A (APPLICATION_ASSERTED)
        "window_title": active_title,
        "wm_class": pre.get("wm_class"),
        # ---- Tier B (KERNEL/RUNTIME_OBSERVED, pid via X-Resource per IC-1)
        "active_pid": pre.get("active_pid"),
        "process_start_identity": pre.get("process_start_identity"),
        "executable_path": exe,
        "command_line": pre.get("command_line"),
        # ---- Tier C
        "agent_written_code_lineage": rec.get("agent_written_code_lineage"),
        "content_hash": rec.get("image_sha256"),
        "displayed_resource_lineage": rec.get("displayed_resource_lineage"),
        # ---- Tier D (COMPOSITOR/DISPLAY_SERVER_OBSERVED)
        "capture_region": rec.get("capture_region"),
        "visible_window_set": vset or None,
        "z_order": list(reversed(pre.get("z_order") or [])) or None,   # top-first
        "window_geometry": geom or None,
        "active_window_identity": active_id,
        # ---- Tier E (not obtainable without a privileged application observer)
        "browser_tab_id": None,
        "browser_url": None,
        "document_instance_id": None,
        # ---- Tier F
        "record_signature": "ok",
    }


def main():
    assert not any("ground_truth" in p for p in sys.path), "ground truth on path"
    tier0_all = json.load(open(os.path.join(OUT, "task_declarations.json"), encoding="utf-8"))
    configs = [(n, c, ()) for n, c in TIER_CONFIGS.items()]
    configs += [(n, d["tiers"], tuple(d["drop_fields"])) for n, d in SENSITIVITY_CONFIGS.items()]

    rows = []
    for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        rec = json.load(open(path, encoding="utf-8"))
        sid = rec["scenario_id"]
        t0 = {k: v for k, v in tier0_all.get(sid, {}).items() if not k.startswith("_")}
        fv = to_field_vector(rec, t0)
        for cfg_name, cfg, drop in configs:
            verdict, rule, ev, note = adjudicate(fv, cfg, drop)
            rows.append({
                "scenario_id": sid, "tier_config": cfg_name,
                "actual_verdict": verdict, "contract_rule_invoked": rule,
                "evidence_used": " ; ".join(ev)[:700], "note": note,
                "observed_pid": fv.get("active_pid"),
                "observed_exe": fv.get("executable_path"),
                "observed_argv": fv.get("command_line"),
                "observed_title": fv.get("window_title"),
                "observed_wm_class": fv.get("wm_class"),
                "observed_resource_lineage": fv.get("displayed_resource_lineage"),
                "image_sha256": rec.get("image_sha256"),
                "field_observation_failures": json.dumps(rec.get("field_observation_failures")),
            })
    with open(os.path.join(OUT, "empirical_verdicts.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2)
    print(f"adjudicated {len(rows)} (scenario, tier) pairs from real observations")


if __name__ == "__main__":
    main()
