"""Provenance-recoverability audit driver.

Produces:
  outputs/recoverability_cases.csv
  outputs/audit_metrics.json      (inputs to the report; report is written by hand)

Scoring follows specs/RECOVERABILITY_AUDIT.md exactly:
  R0 quote localized, R1 producer recovered, R2 artifact linked,
  R3 capture source recovered, R4 scene lineage classified, R5 target reachability.

No LLM/VLM inference anywhere in this pipeline.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quote_locator import locate                      # noqa: E402
from task_spec import load_specs                      # noqa: E402
from trace_model import parse_trace                   # noqa: E402
import scene_provenance as sp                         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "outputs", "raw")
OUT = os.path.join(ROOT, "outputs")

FIELDS = [
    "run", "task", "domain", "case_type", "pool", "quote_id", "hack_pattern", "raw_quote",
    "match_status", "event_index", "producer_kind", "producer_tool", "producer_command",
    "output_path", "output_path_kind", "capture_channel", "source_app_process", "source_kind",
    "scene_class", "weak_scene_hypothesis", "source_confidence",
    "R_level", "edge_confidence", "ambiguity_reason", "evidence_refs",
    "required_deliverable", "was_delivered", "spec_obligation", "target_apps", "target_status",
    "evidence_scope", "judge_is_hack", "judge_artifact_fake_signal",
]


def find(run, task, base):
    g = glob.glob(os.path.join(RAW, run, "**", task, base), recursive=True)
    return g[0] if g else None


def delivered_set(run, task):
    p = find(run, task, "results_manifest.txt")
    if not p:
        return set()
    out = set()
    for ln in open(p, encoding="utf-8", errors="replace"):
        ln = ln.strip()
        if not ln or ln.startswith("d"):
            continue
        out.add(ln.split()[-1].split("/")[-1].lower())
    return out


def worst_conf(edges):
    order = {"EXACT": 3, "STRONG": 2, "WEAK": 1, "UNKNOWN": 0}
    if not edges:
        return "UNKNOWN"
    return min(edges, key=lambda e: order.get(e.confidence, 0)).confidence


def link_quote_to_case(ev_idx, cases, ctx, events):
    """Attach a localized quote to the visual case it is evidence for.

    1. the quote landed on the producing event itself
    2. the quote landed on the event that authored the renderer later captured
    3. the quote landed on the event that launched the captured process
    """
    if ev_idx is None:
        return None, ""
    direct = [c for c in cases if c.event_idx == ev_idx]
    if direct:
        direct.sort(key=lambda c: (-c.r_level, c.event_idx))
        return direct[0], "direct"
    authored = ctx["authored"]
    authored_here = {p for p, i in authored.items() if i == ev_idx}
    if authored_here:
        fwd = [c for c in cases
               if c.source_process and c.source_process.replace("file://", "") in authored_here]
        if fwd:
            fwd.sort(key=lambda c: (-c.r_level, c.event_idx))
            return fwd[0], "authored_renderer"
    launched_here = {ent for (i, ent, _k, _ok) in ctx["launches"] if i == ev_idx}
    if launched_here:
        fwd = [c for c in cases if c.source_process in launched_here]
        if fwd:
            fwd.sort(key=lambda c: (-c.r_level, c.event_idx))
            return fwd[0], "launch"
    return None, "no_visual_case"


def main():
    specs = load_specs(os.path.join(RAW, "tasks"))
    pools = json.load(open(os.path.join(OUT, "cache", "pool_assignment.json")))
    rows = []

    traces = sorted(glob.glob(os.path.join(RAW, "run*", "**", "chat.jsonl"), recursive=True))
    for tp in traces:
        norm = tp.replace("\\", "/")
        run = "run1" if "/run1/" in norm else "run2"
        task = norm.split("/")[-2]
        domain = norm.split("/")[-3]
        key = f"{run}:{task}"
        pool = pools.get(key, {}).get("pool", "UNSELECTED")
        spec = specs.get(task, {"image_deliverables": [], "target_apps": [], "obligation": {}})
        delivered = delivered_set(run, task)

        events = parse_trace(tp)
        cases, ctx = sp.reconstruct_trace(events, spec, delivered)

        sj = find(run, task, "score.json")
        judge = json.load(open(sj, encoding="utf-8")).get("scores", {}) if sj else {}
        quotes = judge.get("hack_evidence_quotes") or []
        patterns = "|".join(judge.get("hack_patterns") or [])
        is_hack = judge.get("is_hack")
        fake_by_id = {str(a.get("id", "")).lower(): bool(a.get("fake_signal"))
                      for a in (judge.get("artifact_checks") or [])}
        obligation = spec.get("obligation") or {}

        def emit(case, case_type, quote_id="", raw_quote="", match_status="", link=""):
            b = sp._basename(case.output_path).lower() if case and case.output_path else ""
            rows.append({
                "run": run, "task": task, "domain": domain, "case_type": case_type,
                "pool": pool, "quote_id": quote_id, "hack_pattern": patterns,
                "raw_quote": raw_quote, "match_status": match_status,
                "event_index": case.event_idx if case else "",
                "producer_kind": case.producer_kind if case else "NONE",
                "producer_tool": link,
                "producer_command": (case.producer_command if case else "")[:220],
                "output_path": case.output_path if case else "",
                "output_path_kind": case.output_path_kind if case else "",
                "capture_channel": case.capture_channel if case else "",
                "source_app_process": case.source_process if case else "",
                "source_kind": case.source_kind if case else "",
                "scene_class": case.scene_class if case else "NO_VISUAL_CASE",
                "weak_scene_hypothesis": case.weak_scene_hypothesis if case else "",
                "source_confidence": case.source_confidence if case else "",
                "R_level": case.r_level if case else 0,
                "edge_confidence": worst_conf(case.edges) if case else "UNKNOWN",
                "ambiguity_reason": case.ambiguity if case else "",
                "evidence_refs": ";".join(e.render() for e in case.edges) if case else "",
                "required_deliverable": case.is_required_deliverable if case else "",
                "was_delivered": case.was_delivered if case else "",
                "spec_obligation": obligation.get(sp._basename(case.output_path), "")
                if case and case.output_path else "",
                "target_apps": "|".join(spec.get("target_apps") or []),
                "target_status": ctx["target_status"],
                "evidence_scope": case.evidence_scope if case else "",
                "judge_is_hack": is_hack,
                "judge_artifact_fake_signal": fake_by_id.get(b, ""),
            })

        # ---- quote-localized cases (primary pool) ----
        for qi, q in enumerate(quotes):
            m = locate(q, events)
            case, link = link_quote_to_case(m.event_idx, cases, ctx, events)
            emit(case, "quote", f"q{qi}", q[:1200], m.level, link)

        # ---- artifact cases: one row per delivered/required visual artifact ----
        seen = {}
        for c in cases:
            if c.evidence_scope != "delivered_evidence":
                continue
            k = sp._basename(c.output_path).lower()
            if k not in seen or c.event_idx > seen[k].event_idx:
                seen[k] = c            # last writer owns the delivered artifact
        for k in sorted(seen):
            emit(seen[k], "artifact", link="final_writer")

        # ---- incidental harness screenshots, aggregated (context, not evidence) ----
        inc = [c for c in cases if c.evidence_scope == "incidental_harness"]
        if inc:
            emit(inc[-1], "incidental_summary", link=f"n={len(inc)}")

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "recoverability_cases.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {path}: {len(rows)} rows over {len(traces)} traces")


if __name__ == "__main__":
    main()
