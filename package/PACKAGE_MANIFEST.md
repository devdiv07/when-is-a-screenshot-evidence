# Package Manifest

Complete inventory, pinned sources, regeneration commands and SHA-256 digests.

**Repository state:** research frozen at tag `phaseJ-epistemic-boundary-v1`, commit
`58f0eeb`. Package released at tag `package-ready-v1`, commit `61374e9` — see §7.

Regenerate every digest below with:

```bash
python package/scripts/manifest_hashes.py
```

---

## 1. Package files

11 documents, 7 figures, 1 figure-data record, 2 scripts.

| SHA-256 | File |
|---|---|
| `dca652f875f7c9eb…` | `package/ARTIFACT_INDEX.md` |
| `d593c09af81943b5…` | `package/CLAIM_TABLE.md` |
| `bfe988f4985437cc…` | `package/HOSTILE_REVIEW.md` |
| `c1cc886b3d74dc5b…` | `package/LIMITATIONS.md` |
| `b99b645c4961ca0b…` | `package/METHODOLOGY.md` |
| `40a431e5f0db4178…` | `package/README.md` |
| `c501880eb1368106…` | `package/RELATED_WORK.md` |
| `af5f5f277f60bf40…` | `package/REPRODUCIBILITY.md` |
| `1b5a7f450e069b3d…` | `package/RESULTS.md` |
| `235a28426301cf2b…` | `package/TECHNICAL_REPORT.md` |
| `c7a0eb5c77afff78…` | `package/figures/FIGURE_DATA.json` |
| `7ca9e25b4112e152…` | `package/figures/fig1_assurance_chain.svg` |
| `a7c8d0d26c373624…` | `package/figures/fig2_recoverability_by_level.svg` |
| `bd94e4b864db7142…` | `package/figures/fig3_lookback_vs_evidence.svg` |
| `4ce34244834ededc…` | `package/figures/fig4_field_set_outcomes.svg` |
| `e7b2da20b4f73b65…` | `package/figures/fig5_analytic_vs_empirical.svg` |
| `952548abea522c82…` | `package/figures/fig6_unknown_policy_exposure.svg` |
| `08c02cf510b26c1a…` | `package/figures/fig7_platform_binding_matrix.svg` |
| `2d48b6310b8425b7…` | `package/scripts/make_figures.py` |
| `fc9728cc17e9ba4e…` | `package/scripts/manifest_hashes.py` |

`PACKAGE_MANIFEST.md` is **not** listed above: it contains the digests, so it cannot contain
its own (the script does print it, and that value changes with every edit to this file). Full
64-character digests are printed by the script.

## 2. Key frozen source artifacts

These are the artifacts every package number is quoted from. If a digest here changes, the
package numbers must be re-verified.

| SHA-256 | Artifact | Authoritative for |
|---|---|---|
| `2afe21ef5d210ac9…` | `outputs/audit_metrics.json` | R0–R5, channel splits, negative controls |
| `21b383622a88bad9…` | `outputs/field_coverage.csv` | closure / resolution / adjudication curves |
| `294f5c41e84a9303…` | `outputs/information_deficits.csv` | deficit bundles; D4-adjudicates-zero check |
| `046737306fad87b2…` | `outputs/analytic_vs_empirical.csv` | the 169 comparable pairs |
| `593fb31d31fb0a78…` | `outputs/empirical_risk_coverage.csv` | MODE 1 / MODE 2 exposure |
| `9fba2d99b02d5d67…` | `outputs/phase1_final_metrics.json` | Phase I closure metrics |
| `6f06d59e9c918f90…` | `outputs/platform_binding_matrix.csv` | **the main platform output** |
| `da73b07f2b627052…` | `outputs/platform_comparison_cases.csv` | per-case observed facts |
| `7fc86515592313ff…` | `outputs/platform_comparison_metrics.json` | portal + identity-spoofing blocks |
| `559a09501a616965…` | `outputs/13b_static_trace/trace_summary.json` | verdicts, flips, replay check |
| `ac20c2dd3e114516…` | `outputs/platform_raw/portal_probe.json` | `AvailableSourceTypes = 1` |
| `28412dd73f7399bc…` | `outputs/empirical_raw/empirical_records.json` | raw recorder output incl. 13b |
| `17aeec4b9621f682…` | `research/FROZEN_FINDINGS.md` | the seven frozen findings |

### 2.1 Frozen apparatus — must not change

| SHA-256 | File | Cross-check |
|---|---|---|
| `ac6c6ab3543d9d54865c2bd4431b342037a502a00829b9f35451cb0c137e826a` | `infra/adjudicator.py` | matches `frozen_rules_integrity.adjudicator_sha256` in `trace_summary.json` |
| `60590bbbde72683bd93718550b3f09c1218c52b42646753572f1025b3a249101` | `infra/recorder.py` | matches `frozen_rules_integrity.recorder_sha256` |

These two digests are recorded **inside** the static trace that used them, so the trace is
self-certifying: if the adjudicator changes, the recorded digest no longer matches the file and
the trace is known to be stale.

## 3. Git provenance

| Tag | Commit | Froze |
|---|---|---|
| `recoverability-audit-v1` | `f8e23a5` | retrospective audit — general post-hoc scene provenance NO-GO |
| `phase1-analytic-v1` | `fa78c2d` | contract-logic arm; empirical arm not run |
| `phase1-empirical-v1` | `a444f0d` | real X11 arm; kill criterion fired; S1, S2 |
| `phase1-closed-v1` | `c74cd36` | Phase I CLOSED / INSUFFICIENT |
| **`phaseJ-epistemic-boundary-v1`** | **`58f0eeb`** | 13b static classification + platform comparison |

The first four are annotated tags; `git rev-parse --short <tag>^{commit}` yields the commits
above (see `HOSTILE_REVIEW.md` H-6).

## 4. External primary sources

| Source | Pin | Verification status |
|---|---|---|
| **AgentProvenance** | `ByteYellow/AgentProvenance` @ `fc2e62647dc64b6d23144b88e0e0ac101b4f2793` | **PINNED AND VERIFIED** — cloned at SHA, 379 tracked files searched, 6 files read in full. Software **not executed**. |
| WeaveBench | arXiv:2606.09426v3 | cited; corpus source |
| ProcGrep | arXiv:2606.16988 | cited |
| AgentTrails | arXiv:2607.18816 | cited |
| PROV-AGENT | arXiv:2508.02866 | cited |
| CHIEF | arXiv:2602.23701 | cited |
| AgentRewardBench | arXiv:2504.08942 | cited |
| Agent Flight Recorder | arXiv:2609.01931 | cited |
| RILA | arXiv:2609.02088 | cited |
| LongHorizon-Harness | arXiv:2608.01964 | cited |
| C2PA / Content Credentials | specification | **not version-pinned** |
| trusted path / trusted display | literature body | **not pinned** |

Files read at the AgentProvenance pin, with digests at that revision:
`README.md` `b1d5477bc6c094e3…` · `docs/telemetry-schema.md` `3287874f948bbfce…` ·
`docs/ebpf-sensor-plan.md` `3ef8364ad9bba3c9…` · `internal/attest/attest.go`
`83346abf2ee105b7…` · `docs/img/README.md` `34db9a1baad435fb…` ·
`internal/provenance/outbound_surface.go` `627d28967f5329ad…`

**Unverified citations remaining: none.** C2PA and the trusted-display literature are cited as
bodies of work rather than pinned artifacts, and no numeric or behavioural claim rests on
either.

## 5. Figure generation

```bash
python package/scripts/make_figures.py
```

Python 3.11+, **standard library only**. Deterministic: same inputs → byte-identical SVGs.

| Figure | Output | Input artifact |
|---|---|---|
| 1 | `fig1_assurance_chain.svg` | `research/FROZEN_FINDINGS.md`, `outputs/platform_binding_matrix.csv` |
| 2 | `fig2_recoverability_by_level.svg` | `outputs/audit_metrics.json` |
| 3 | `fig3_lookback_vs_evidence.svg` | `outputs/recoverability_report.md` §5.2 (parsed) |
| 4 | `fig4_field_set_outcomes.svg` | `outputs/field_coverage.csv`, `outputs/information_deficits.csv` |
| 5 | `fig5_analytic_vs_empirical.svg` | `outputs/analytic_vs_empirical.csv` |
| 6 | `fig6_unknown_policy_exposure.svg` | `outputs/empirical_risk_coverage.csv` |
| 7 | `fig7_platform_binding_matrix.svg` | `outputs/platform_binding_matrix.csv` |

`package/figures/FIGURE_DATA.json` records every plotted value, its source artifact, and each
SVG's own digest — so a figure can be diffed against source without reading the generator.

## 6. Result regeneration

```bash
python scripts/static_13b_trace.py     # 13b static trace + rule-property probe
python scripts/platform_matrix.py      # binding matrix + platform metrics
python scripts/run_audit.py            # R0-R5 -> outputs/audit_metrics.json
python scripts/field_coverage.py       # field-set curves
python package/scripts/make_figures.py # all seven figures
git status --porcelain                 # expect no unexpected diffs
```

Container-based arms and blocked experiments: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) §5–6.

## 7. Release checkpoint

**Package committed at `61374e9`, tag `package-ready-v1`.**

The research package and its four supporting ledger/prior-art files were committed **together**
in a single checkpoint — `package/` (21 files) plus `research/PRIOR_ART.md`,
`research/EVIDENCE_LEDGER.md`, `research/PROGRESS.md` and
`outputs/x11_wayland_comparison.md`, carrying the AgentProvenance pin, ledger entries
E089–E091, and the withdrawn skew claim. Staging was explicit, never `git add -A`, so that
artifact isolation held at the checkpoint. 25 files, +4264 / −24. **The working tree was clean
immediately after the checkpoint.**

Splitting those files across two commits would have produced a checkpoint whose public package
cited evidence rows and a pinned citation that the committed ledger did not yet contain.

| Tag | Commit | Contents |
|---|---|---|
| `package-ready-v1` | `61374e9` | the package exactly as generated and hostile-reviewed |
| `package-ready-v1.1` | *this commit* | identical scientific content; corrected release-state metadata in this file only |

`package-ready-v1` is **immutable** and is the checkpoint the verification in §8 was run
against. `v1.1` differs from it by one metadata-only file and changes no result, figure,
digest of any other file, or claim.

The digests in §1 and §2 remain valid only while those files are unmodified — re-run
`manifest_hashes.py` after any edit. This file's own digest is not listed there (§1) and
changes with every edit to it, including this one.

## 8. Verification checklist

| Check | Command | Expected |
|---|---|---|
| digests current | `python package/scripts/manifest_hashes.py` | matches §1, §2 |
| frozen apparatus intact | compare `infra/adjudicator.py` digest with §2.1 | `ac6c6ab3…` |
| static trace valid | `python scripts/static_13b_trace.py` | `replay matches frozen Phase I: True` |
| platform result stable | `python scripts/platform_matrix.py` | `bindings changed between platforms: 0` |
| figures reproduce | `python package/scripts/make_figures.py` | digests match §1 |
| links resolve | see `HOSTILE_REVIEW.md` check 2 | 0 broken |
| numbers match source | see `HOSTILE_REVIEW.md` check 3 | 29/29 |
