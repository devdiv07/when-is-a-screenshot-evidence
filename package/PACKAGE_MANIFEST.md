# Package Manifest

Complete inventory, pinned sources, regeneration commands and SHA-256 digests.

**Repository state:** research frozen at tag `phaseJ-epistemic-boundary-v1`, commit
`58f0eeb`. Immutable package releases: `package-ready-v1` at `61374e9` and
`package-ready-v1.1` at `2f36db4`. Publication hardening is released as
`package-ready-v1.2`; the tag identifies this tree — see §7.

Regenerate every digest below with:

```bash
python package/scripts/manifest_hashes.py
```

---

## 1. Package files

11 documents, 7 figures, 1 figure-data record, 2 scripts.

| SHA-256 | File |
|---|---|
| `3609e8bf414d0a03acc736ab0bb604843f8d8ad2f8c2789468f28e836a63bd1c` | `package/ARTIFACT_INDEX.md` |
| `f974219e7a845a497d0e4ec556e162a14ddc18f181b7c817bc88e86b9fa3da39` | `package/CLAIM_TABLE.md` |
| `41440063aab7a64d903f57d9be2abf45b5e3871037ca6652dc62f60869f682a2` | `package/HOSTILE_REVIEW.md` |
| `c1cc886b3d74dc5bbda5a30e893e5165b67e77bed219624e84e5ca1bc01f5c48` | `package/LIMITATIONS.md` |
| `a4390aa4d013d0c41c14bc3ad7d77d75ff6bcd159c1c809ddee6da95aefd502b` | `package/METHODOLOGY.md` |
| `40a431e5f0db4178203c8ccd9ab40de52bbd7fe7925a4b015581bdb3da2008d1` | `package/README.md` |
| `c501880eb1368106db258113702d931eb96626f111d761b1fca77bf1e9119bcb` | `package/RELATED_WORK.md` |
| `cbad3262169d2190e280abeaafbd306daa584864ddd4419fa6daf2e034589fbb` | `package/REPRODUCIBILITY.md` |
| `286bce449fb533a7c39299bebaaccc455124b8ddea8745eec3ee1528791198d7` | `package/RESULTS.md` |
| `0243068dced6729c3fc3d11fdba257738b89b703c9594bd9e2087818f49d9e6c` | `package/TECHNICAL_REPORT.md` |
| `f6e944a254e82f632ff1ad4db4cadace56233c43a7cd2b621e1d537151daae9b` | `package/figures/FIGURE_DATA.json` |
| `7ca9e25b4112e152351d67a3af509da6ffd95fa32a07fdc36fbe7cb3ac8a4b56` | `package/figures/fig1_assurance_chain.svg` |
| `a7c8d0d26c3736242a4f65e7a751a4d226e020d33af929bd50d968084030244f` | `package/figures/fig2_recoverability_by_level.svg` |
| `bd94e4b864db7142341dfc2de3062a7756de12951c203f9ed9f487edd41c4623` | `package/figures/fig3_lookback_vs_evidence.svg` |
| `4ce34244834ededcaf2dd68d96773433f50e92629bcfed35caed4965fe499f26` | `package/figures/fig4_field_set_outcomes.svg` |
| `e7b2da20b4f73b65c8d5fc29de7db06ea4c7c55f2bbe44c339957734fef35833` | `package/figures/fig5_analytic_vs_empirical.svg` |
| `952548abea522c829c64de46fe540b56a531d50e147c65b1908e22a3737b0e7d` | `package/figures/fig6_unknown_policy_exposure.svg` |
| `08c02cf510b26c1a93288004148812cd8e634b3290f2eaf4e27baa6c11439b96` | `package/figures/fig7_platform_binding_matrix.svg` |
| `6c71157765cef721e7fecc5f4f0a13ba7827b63d43ffd3b3c5a2b0bdbce5985c` | `package/scripts/make_figures.py` |
| `570b4fa23b301e1064863782f34a301c71408ed941c505e9ef7419aba3e3d24a` | `package/scripts/manifest_hashes.py` |

`PACKAGE_MANIFEST.md` is **not** listed above: it contains the digests, so it cannot contain
its own (the script does print it, and that value changes with every edit to this file). Full
64-character digests are printed by the script.

## 2. Key frozen source artifacts

These are the artifacts every package number is quoted from. If a digest here changes, the
package numbers must be re-verified.

| SHA-256 | Artifact | Authoritative for |
|---|---|---|
| `2afe21ef5d210ac967b3eaa396bfd59d76efb41d35735fbe0d48808da3cd54f9` | `outputs/audit_metrics.json` | R0–R5, channel splits, negative controls |
| `21b383622a88bad987b56163bbdae90190782c167caa26ce733b4632a4d881c0` | `outputs/field_coverage.csv` | closure / resolution / adjudication curves |
| `294f5c41e84a9303231090c75be7ec16faeb705101f642fe463b736772beba31` | `outputs/information_deficits.csv` | deficit bundles; exact display-composition predicate check |
| `046737306fad87b24ce2cf6645b9ce50ce0e7925107552d681aab8dce789d144` | `outputs/analytic_vs_empirical.csv` | the 169 comparable pairs |
| `593fb31d31fb0a781c91c1a6c635d3dbb211c97125b85d44cf5e32f5b17cb318` | `outputs/empirical_risk_coverage.csv` | MODE 1 / MODE 2 exposure |
| `9fba2d99b02d5d6703fe2a88c6bd2bf4b8ee712dd5930f705b8a81e8f09f5483` | `outputs/phase1_final_metrics.json` | Phase I closure metrics |
| `6f06d59e9c918f900c9a91c451792567b211e8af62e073f7b724f62a9be0b255` | `outputs/platform_binding_matrix.csv` | **the main platform output** |
| `da73b07f2b62705283714b6a239d0fe530f167a191ebf44997e6c1287bb78549` | `outputs/platform_comparison_cases.csv` | per-case observed facts |
| `7fc86515592313ffd82988a877da33f40599b28ed700e6bc835416ac3a7bda85` | `outputs/platform_comparison_metrics.json` | portal + identity-spoofing blocks |
| `559a09501a61696537ea0896c4741d93238eb209e515821d384774454ba41014` | `outputs/13b_static_trace/trace_summary.json` | verdicts, flips, replay check |
| `ac20c2dd3e1145164115fad9be2e815fb73a839528a9e327e13fd3e3e5e29514` | `outputs/platform_raw/portal_probe.json` | `AvailableSourceTypes = 1` |
| `28412dd73f7399bceb3abbba4cfb205ee3fbefcf2bcdc4bb820aacb6a7db7df7` | `outputs/empirical_raw/empirical_records.json` | raw recorder output incl. 13b |
| `17aeec4b9621f682f9f21c7591325c9c68cd2b89d9c3f8a2fa82ee589b9d9582` | `research/FROZEN_FINDINGS.md` | the seven frozen findings |

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
| `package-ready-v1.1` | `2f36db4` | identical scientific content; corrected release-state metadata in this file only |
| `package-ready-v1.2` | tagged release commit | public front door, scope annotations, traceability, full digests, deterministic CI, license and citation metadata |

`package-ready-v1` and `package-ready-v1.1` remain **immutable**. `v1.1` differs from `v1`
by one metadata-only file. `v1.2` adds publication hardening and scope annotations without
changing the frozen apparatus, figures, core result artifacts, or scientific conclusions.

The digests in §1 and §2 remain valid only while those files are unmodified — re-run
`manifest_hashes.py` after any edit. This file's own digest is not listed there (§1) and
changes with every edit to it, including this one.

## 8. Verification checklist

| Check | Command | Expected |
|---|---|---|
| digests current | `python package/scripts/manifest_hashes.py --check` | all listed files match §1, §2 |
| frozen apparatus intact | compare `infra/adjudicator.py` digest with §2.1 | `ac6c6ab3…` |
| static trace valid | `python scripts/static_13b_trace.py` | `replay matches frozen Phase I: True` |
| platform result stable | `python scripts/platform_matrix.py` | `bindings changed between platforms: 0` |
| figures reproduce | `python package/scripts/make_figures.py` | digests match §1 |
| links resolve | see `HOSTILE_REVIEW.md` check 2 | 0 broken |
| numbers match source | see `HOSTILE_REVIEW.md` check 3 | 29/29 |
