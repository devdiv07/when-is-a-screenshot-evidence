# `outputs/` — reader map

This directory holds derived artifacts from several successive phases. **They are not equally
authoritative, and some deliberately record conclusions that later, stronger evidence
superseded.** Historical artifacts are preserved as produced; none is rewritten to agree with
a later phase. This file adds no result — it only states provenance and authority.

For current interpretation, start at [`package/RESULTS.md`](../package/RESULTS.md),
[`package/CLAIM_TABLE.md`](../package/CLAIM_TABLE.md) and
[`research/FROZEN_FINDINGS.md`](../research/FROZEN_FINDINGS.md). Per-file index:
[`package/ARTIFACT_INDEX.md`](../package/ARTIFACT_INDEX.md).

---

## 1. Layers, in phase order

| # | Layer | Files | What it is | Status for current interpretation |
|---|---|---|---|---|
| 1 | **Retrospective audit** (`recoverability-audit-v1`) and post-gate analysis | `audit_metrics.json`, `recoverability_cases.csv`, `recoverability_report.md`, `source_manifest.csv`; `information_deficits.csv`, `field_coverage.csv`, `field_set_analysis.md`, `post_gate_summary.md` | deterministic structural audit of benign WeaveBench traces; no LLM/VLM | authoritative for R0–R5, controls and field-set counts; narrative prose is scoped by the package (§3) |
| 2 | **ANALYTIC ARM** (`phase1-analytic-v1`) | `adversarial_metrics.json`, `adversarial_cases.csv`, `tier_results.csv`, `risk_coverage.csv`, `adversarial_experiment_report.md` | contract logic over **analyst-derived** field vectors; no process launched, no pixel captured | **historical, frozen**; superseded wherever it disagrees with the empirical arm |
| 3 | **EMPIRICAL ARM** (`phase1-empirical-v1`) | `empirical_cases.csv`, `empirical_metrics.json`, `empirical_tier_results.csv`, `empirical_risk_coverage.csv`, `analytic_vs_empirical.csv`, `empirical_raw/`, `phase1_empirical_report.md` | real Xvfb/Openbox display, real processes, windows and pixels, unprivileged attacker, independent privileged recorder | governs Phase I where the arms disagree |
| 4 | **Phase I synthesis** (`phase1-closed-v1`) | `phase1_final_metrics.json`, `phase1_final_summary.md` | synthesis of layers 2 and 3, evidence classes kept separate | **use this for final Phase I conclusions** |
| 5 | **Phase J — 13b static classification** (`phaseJ-epistemic-boundary-v1`) | `13b_static_trace/` (writeup: [`research/13B_STATIC_CLASSIFICATION.md`](../research/13B_STATIC_CLASSIFICATION.md)) | frozen 13b record replayed through the frozen adjudicator, plus one injected observation | authoritative for *why* 13b happened |
| 6 | **Phase J — X11/Wayland comparison** (`phaseJ-epistemic-boundary-v1`) | `platform_binding_matrix.csv`, `platform_comparison_cases.csv`, `platform_comparison_metrics.json`, `platform_raw/`, `x11_wayland_comparison.md` | two predeclared cases on X11 and one tested Wayland stack | authoritative for the tested stack only |
| — | Closing board | `final_research_board.md` | the closing questions answered at Phase J | closing record |

`raw/` and `cache/` are gitignored and not redistributed; every cited number regenerates
without them ([`package/REPRODUCIBILITY.md`](../package/REPRODUCIBILITY.md) §3). Digests of
the key frozen artifacts are in [`package/PACKAGE_MANIFEST.md`](../package/PACKAGE_MANIFEST.md)
§2; this README is reader guidance, not a frozen artifact.

## 2. The kill-criterion disagreement is intentional

| File | Records |
|---|---|
| `adversarial_metrics.json` | `"evaluation_type": "CONTRACT-LOGIC (analytic). Not an empirical measurement."` · `kill_criterion.fired = false` |
| `phase1_final_metrics.json` | `evidence_classes.ANALYTIC.status = "FROZEN, superseded in the unsafe direction by the empirical arm"` · `evidence_classes.EMPIRICAL.kill_criterion_fired = true` · false accept `13b_viewer_agent_image_hidden` |

- `adversarial_metrics.json` is the frozen **ANALYTIC ARM** result. Its
  `kill_criterion.fired = false` is a **true record of what that arm computed** over
  analyst-derived vectors. It is weaker evidence, not a data error.
- It **must not be rewritten** to match later experiments. The JSON and CSV files in layer 2
  carry no in-file banner; this README is that banner. (The analytic Markdown report carries
  its own.)
- Empirical execution later **superseded the analytic arm in the unsafe direction**: 5
  `UNKNOWN → AUTHENTIC_TARGET` transitions, all from case 13b
  ([`package/RESULTS.md`](../package/RESULTS.md) §7). When `phase1_empirical_report.md` says
  it "supersedes nothing in the analytic arm", it means no analytic file was overwritten — not
  that the analytic conclusion stands.
- `phase1_final_metrics.json` is the Phase I synthesis to use for final Phase I conclusions.
- Phase J then sharpened **why** 13b happened and classified it as
  **CONTRACT_UNDERSPECIFICATION**. That classification does not un-fire the criterion, which
  fired on its own predeclared terms ([`package/CLAIM_TABLE.md`](../package/CLAIM_TABLE.md)
  C7, C23).
- Identifiers differ by arm: analytic `13b_viewer_agent_image_gui_open` → empirical
  `13b_viewer_agent_image_hidden`, a corrected successor after IC-4, not a rename
  ([`package/RESULTS.md`](../package/RESULTS.md) §7.1).

## 3. Other historical wording the package supersedes

Raw historical artifacts may contain conclusions later superseded or scoped by stronger
evidence. They are left as written. The current reading is:

| Where | Historical wording | Current reading |
|---|---|---|
| `post_gate_summary.md` §3 item 4; `recoverability_report.md` §7 | "High precision, ~5% recall"; "high-precision and low-recall" (from 0/99 and 0/73 on controls) | no violation claims in either control pool, both containing resolvable capture evidence — a non-vacuity/specificity check, **not a population precision estimate** (C26) |
| `recoverability_report.md` §7 | judge comparison 5 / 0 / 186 / 192, counts only | no incremental artifact-level flagging coverage relative to judge `fake_signal` in this corpus; the judge is not ground truth (C27) |
| `field_set_analysis.md` §1 | "83.6% of cases resolved by four fields" | **withdrawn**; 83.6% is the six-field adjudication figure over 287 (C5) |
| `x11_wayland_comparison.md` | comparative recorder skew | **withdrawn as not reproducible** (`package/HOSTILE_REVIEW.md` H-2) |

Runs discarded for documented apparatus defects are listed in
[`package/REPRODUCIBILITY.md`](../package/REPRODUCIBILITY.md) §7 and are not results.
