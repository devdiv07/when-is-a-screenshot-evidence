# Artifact Index

Every artifact this package cites, what it is, and what it is authoritative for.

Paths are relative to the repository root. Package files live under `package/`; everything
else is the frozen research repository at tag `phaseJ-epistemic-boundary-v1` (`58f0eeb`).

**Reading raw `outputs/` directly?** Start with [`outputs/README.md`](../outputs/README.md). It
states which output files are historical, which are superseded, and which are authoritative
for current interpretation — including why the analytic and empirical arms record opposite
kill-criterion results.

---

## 1. Package documents

| File | Purpose |
|---|---|
| `package/README.md` | the result in one screen |
| `package/TECHNICAL_REPORT.md` | the full argument, organised by result |
| `package/METHODOLOGY.md` | how each result was produced, and what the discipline cost |
| `package/RESULTS.md` | every number, with its source artifact |
| `package/LIMITATIONS.md` | why you should doubt it, most material first |
| `package/REPRODUCIBILITY.md` | commands, environment, blocked arms, discarded runs |
| `package/RELATED_WORK.md` | prior art by problem layer, with explicit non-claims |
| `package/CLAIM_TABLE.md` | **the licensing spine** — every headline sentence maps to a row |
| `package/HOSTILE_REVIEW.md` | adversarial self-review and every issue it found |
| `package/PACKAGE_MANIFEST.md` | file list, hashes, pinned sources, regeneration commands |
| `package/ARTIFACT_INDEX.md` | this file |

## 2. Figures and their generator

| Figure | File | Authoritative for | Input artifact |
|---|---|---|---|
| 1 | `package/figures/fig1_assurance_chain.svg` | which links were tested | `research/FROZEN_FINDINGS.md`, `outputs/platform_binding_matrix.csv` |
| 2 | `package/figures/fig2_recoverability_by_level.svg` | R0–R5 rates | `outputs/audit_metrics.json` |
| 3 | `package/figures/fig3_lookback_vs_evidence.svg` | inference-policy sensitivity | `outputs/recoverability_report.md` §5.2 |
| 4 | `package/figures/fig4_field_set_outcomes.svg` | closure vs resolution vs adjudication | `outputs/field_coverage.csv`, `outputs/information_deficits.csv` |
| 5 | `package/figures/fig5_analytic_vs_empirical.svg` | the 3×3 transition matrix | `outputs/analytic_vs_empirical.csv` |
| 6 | `package/figures/fig6_unknown_policy_exposure.svg` | MODE 1 vs MODE 2 exposure | `outputs/empirical_risk_coverage.csv` |
| 7 | `package/figures/fig7_platform_binding_matrix.svg` | X11 vs tested Wayland bindings | `outputs/platform_binding_matrix.csv` |

| Support file | Purpose |
|---|---|
| `package/scripts/make_figures.py` | regenerates all seven; Python 3.11+, **standard library only** |
| `package/figures/FIGURE_DATA.json` | every plotted value, its source, and each SVG's sha256 — diff a figure against source without reading the script |

## 3. Frozen research documents

| File | Authoritative for |
|---|---|
| **`research/FROZEN_FINDINGS.md`** | **the seven frozen findings — the package entry point** |
| `research/13B_STATIC_CLASSIFICATION.md` | the 13b classification and its frozen-semantics trace |
| `research/EPISTEMIC_POLICY.md` | observation policy vs inference policy; the candidate thesis |
| `research/PHASE1_EMPIRICAL_CONCLUSIONS.md` | the six bindings; the three empirical boundaries |
| `research/OBSERVABILITY_BOUNDARY.md` | the retrospective boundary; five distinctions traces cannot make |
| `research/THREAT_MODEL.md` | adversary, 14 capabilities, 13 attack classes, trust planes, predictions P1–P8 |
| `research/PRIOR_ART.md` | prior-art board, including the pinned AgentProvenance verification |
| `research/EVIDENCE_LEDGER.md` | **E001–E091** — every material claim with class, source, caveat, confidence |
| `research/DECISION_LOG.md` | every decision that changed the research board, with its reopening condition |
| `research/PROGRESS.md` | state-of-work for a cold reader; Phase I section marked SUPERSEDED |

## 4. Specifications

| File | Authoritative for |
|---|---|
| `specs/CAPTURE_PROVENANCE_CONTRACT.md` | the frozen contract — **CLOSED / INSUFFICIENT, do not extend** |
| `specs/ADVERSARIAL_SUFFICIENCY_EXPERIMENT.md` | the predeclaration of record: cases, metrics, kill criterion |

## 5. Retrospective arm — data and reports

| File | Authoritative for |
|---|---|
| `outputs/audit_metrics.json` | R0–R5, by-channel splits, negative controls, judge comparison |
| `outputs/recoverability_report.md` | the audit narrative; **§5.2 is the lookback sweep**; §7's "high-precision" inference is historical wording, scoped by C26 |
| `outputs/recoverability_cases.csv` | per-artifact audit rows |
| `outputs/information_deficits.csv` | per-case deficit bundles; source for the D4-adjudicates-zero check |
| `outputs/field_coverage.csv` | closure / resolution / adjudication curves |
| `outputs/field_set_analysis.md` | **§1 records the withdrawn "83.6% by four fields" claim** |
| `outputs/post_gate_summary.md` | the surviving narrow instrument: 23/453, 0/99 and 0/73 on controls; its "high precision, ~5% recall" phrasing is historical — scoped reading in `METHODOLOGY.md` §3.2 and C26 |

## 6. Prospective arm — Phase I

**Arm labels for historical filenames:** `outputs/tier_results.csv`,
`outputs/risk_coverage.csv`, `outputs/adversarial_metrics.json`, and
`outputs/adversarial_experiment_report.md` are the **ANALYTIC ARM**. Files prefixed
`empirical_` and `outputs/phase1_final_*` report or synthesize the **EMPIRICAL ARM**. The
analytic identifier `13b_viewer_agent_image_gui_open` maps to the corrected empirical
successor `13b_viewer_agent_image_hidden`; IC-4 changed the construction, so this is not a
simple rename. See `package/RESULTS.md` §7.1.

| File | Authoritative for |
|---|---|
| `outputs/phase1_final_metrics.json` | closure metrics; the three evidence classes; discarded runs |
| `outputs/phase1_final_summary.md` | Phase I in one page |
| `outputs/phase1_empirical_report.md` | full empirical run detail |
| `outputs/adversarial_experiment_report.md` | the analytic arm (superseded where the arms disagree) |
| `outputs/analytic_vs_empirical.csv` | the 169 comparable pairs |
| `outputs/empirical_risk_coverage.csv` | MODE 1 / MODE 2 exposure by tier |
| `outputs/empirical_cases.csv` · `outputs/empirical_metrics.json` | per-case empirical results |
| `outputs/empirical_raw/empirical_records.json` | **raw recorder output, including case 13b** |
| `outputs/empirical_raw/empirical_verdicts.json` | adjudicator output per (scenario, tier) |
| `outputs/empirical_raw/ground_truth/` | 13 construction-time labels, never read by the adjudicator |
| `outputs/empirical_raw/s1_race.json` | S1 atomicity, **run 2** (run 1's JSON was not retained) |
| `outputs/empirical_raw/s2_nested.json` | S2 nested-display result |
| `outputs/empirical_raw/13b_viewer_agent_image_hidden.png` | the captured false-accept frame |

## 7. Phase J — 13b static trace

| File | Authoritative for |
|---|---|
| `outputs/13b_static_trace/original_record.json` | the frozen 13b record as replayed |
| `outputs/13b_static_trace/counterfactual_record.json` | CF-1, the minimal injection |
| `outputs/13b_static_trace/counterfactual_record_cf2.json` | CF-2, frozen-recorder-faithful |
| `outputs/13b_static_trace/injected_observation.json` | **the single injected journal entry** |
| `outputs/13b_static_trace/original_decision_trace.md` | full decision trace, original |
| `outputs/13b_static_trace/counterfactual_decision_trace.md` | full decision trace, counterfactual |
| `outputs/13b_static_trace/rule_property_probe.md` | **the honest-case false reject** |
| `outputs/13b_static_trace/trace_summary.json` | verdicts, flips, frozen-rule hashes, replay check |

## 8. Phase J — platform comparison

| File | Authoritative for |
|---|---|
| `outputs/x11_wayland_comparison.md` | the comparison writeup |
| `outputs/platform_binding_matrix.csv` | **the main experimental output** — per-cell evidence, observer, mechanism, native-vs-reconstructed, attacker control |
| `outputs/platform_comparison_cases.csv` | per-case observed facts |
| `outputs/platform_comparison_metrics.json` | machine-readable metrics, incl. portal and identity-spoofing blocks |
| `outputs/platform_raw/raw/{x11,wayland}_{P,R}.json` | raw recorder output, four runs |
| `outputs/platform_raw/ground_truth/` | construction-time labels, four cases |
| `outputs/platform_raw/shots/*.png` | the four captured frames |
| `outputs/platform_raw/portal_probe.json` | **`AvailableSourceTypes = 1`; the session attempt** |
| `outputs/platform_raw/portal_start_diagnostic.log` | **backend TRACE showing why `Start` failed** |
| `outputs/platform_raw/boot.log` · `stack_status` | stack bring-up evidence |
| `outputs/final_research_board.md` | the eight closing questions answered |

## 9. Code

| File | Purpose |
|---|---|
| `infra/adjudicator.py` | **the frozen adjudicator** — contract rules, deterministic, no LLM |
| `infra/recorder.py` | **the frozen Phase I recorder** |
| `infra/adjudicate_empirical.py` | maps recorder output to the contract's field vector |
| `infra/adversarial_cases.py` | tier/field vocabulary, tier configurations, sensitivity arms |
| `infra/scenarios.py` · `infra/run_empirical.py` | Phase I case construction and orchestration |
| `infra/race_s1.py` · `infra/nested_s2.py` | the S1 and S2 experiments |
| `infra/test_isolation.py` | **enforces ground-truth isolation** (static + dynamic + non-vacuity) |
| `infra/Dockerfile` · `infra/entrypoint.sh` | the X11 lab |
| `infra/IMPLEMENTATION_CORRECTIONS.md` | **IC-1…IC-4**, written before re-running |
| `infra/wayland_lab/` | the dual-stack lab (Dockerfile, sway.conf, entrypoint, recorder, portal probe, cases, runner) |
| `infra/wayland_lab/IMPLEMENTATION_CORRECTIONS.md` | **IC-5, IC-6**, with the stability check |
| `scripts/static_13b_trace.py` | the 13b static trace + rule-property probe |
| `scripts/platform_matrix.py` | binding-matrix derivation |
| `scripts/run_audit.py` · `scripts/scene_provenance.py` | the retrospective audit |
| `scripts/field_coverage.py` · `scripts/information_deficits.py` | Phase C/D analysis |
| `scripts/remote_zip.py` | selective ZIP-over-HTTP corpus retrieval |
| `scripts/quote_locator.py` · `scripts/adjudicator.py` | quote localisation; adjudicator copy |

## 10. Not redistributed

| Path | Why |
|---|---|
| `outputs/raw/` (697 files) | raw benchmark corpus — gitignored, not ours to redistribute |
| `outputs/cache/` (8 files) | derived retrieval caches |
| S1 run 1 JSON | **overwritten before export; only the run log survives** — stated wherever run 1 is quoted |

Every number cited in this package regenerates **without** these, because the derived
artifacts they produced are committed.

## 11. External sources

| Source | Pin |
|---|---|
| AgentProvenance | `ByteYellow/AgentProvenance` @ `fc2e62647dc64b6d23144b88e0e0ac101b4f2793` |
| WeaveBench | arXiv:2606.09426v3 |
| ProcGrep | arXiv:2606.16988 |
| AgentTrails | arXiv:2607.18816 |
| PROV-AGENT | arXiv:2508.02866 |
| CHIEF | arXiv:2602.23701 |
| AgentRewardBench | arXiv:2504.08942 |
| Agent Flight Recorder | arXiv:2609.01931 |
| RILA | arXiv:2609.02088 |
| LongHorizon-Harness | arXiv:2608.01964 |
| C2PA / Content Credentials | specification, not version-pinned here |
| trusted path / trusted display | literature body, not pinned |
