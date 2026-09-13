# Hostile Review

An adversarial pass over the package, run against the completed drafts. Every issue found is
listed with its resolution. **Nothing was silently fixed.**

The standing questions, applied to every major conclusion:

1. Is this measured or inferred?
2. Could another explanation produce it?
3. Is the wording broader than the tested platform/model?
4. Is an apparatus defect being presented as a scientific property?
5. Is an absence-of-evidence claim being treated as evidence-of-absence?
6. Is a judge-derived label being treated as human ground truth?
7. Does a cited prior-art source actually support the comparison?
8. Has a stale figure survived?
9. Does the claim table license this exact sentence?

---

## Issues found

### H-1 — A withdrawn claim was nearly reproduced as a figure **[FOUND, FIXED]**

**Question 8.** While building Figure 4, the natural framing from the frozen contract —
*"Tier D: the dominant tier, 240 of 287 eligible cases (83.6%)"* — was about to be plotted as
"four display-composition fields cover 83.6%".

That is a **withdrawn claim**. `outputs/field_set_analysis.md` §1 records that an earlier
draft said exactly this and that it was retracted for conflating three distinct outcomes
(closure / resolution / adjudication), with the strongest never measured.

**How caught.** The raw CSV gave 208 unique cases for the four-field bundle, not 240. The
mismatch forced a re-read of the source analysis.

**Resolution.** Figure 4 now plots the **adjudication** curve, and the four display-composition
fields are shown at **0.0%** — which is the actual measured value. Re-verified directly from
`outputs/information_deficits.csv`: filtering on
`bundle_fields = VISIBLE_WINDOW_SET+Z_ORDER+CAPTURE_REGION+WINDOW_GEOMETRY` and
`eligible = yes` gives 832 rows representing 208 unique cases, with
`enables_target_substitute_adjudication = no` on all of them. The withdrawal
is stated explicitly in `RESULTS.md` §3, `TECHNICAL_REPORT.md` §4.1 and
`package/figures/FIGURE_DATA.json`.

**Residual.** The frozen contract's own sentence attributing 240/83.6% to "Tier D" remains
loose: the six-field set that achieves it includes `ACTIVE_PID`, a **Tier B** field. The
frozen artifact was not edited (it is frozen); the package never repeats the attribution and
always names the six-field set.

### H-2 — A non-reproducible comparative claim **[FOUND, WITHDRAWN]**

**Questions 2, 8.** The draft stated that recorder skew was lower on the Wayland arm
(75–78 ms vs 133–159 ms), hedged as "not a security claim".

**How caught.** The final IC-5 re-run produced X11 137–208 ms and Wayland 80–100 ms. The
quoted ranges were from a superseded run **and** the underlying quantity moved materially
between runs of the identical image.

**Resolution.** The comparative claim is **withdrawn as not reproducible**, in
`package/RESULTS.md`, `outputs/x11_wayland_comparison.md` and `research/PROGRESS.md`. Skew here
is a property of recorder architecture and machine load, not of the platform. No result in the
package rests on it.

**Note on what this means.** The hedge "not a security claim" was not sufficient. A number
that moves between runs should not be quoted as a comparison at all, hedged or otherwise.

### H-3 — Ground truth contradicted the recorder **[FOUND, FIXED, RESULT STABLE]**

**Question 4.** Final verification compared construction-time ground truth against the
recorder's independent observation. On the Wayland arm the ground truth said
`viewer_binary: null` — "NO LEGITIMATE VIEWER COULD BE STARTED" — while the recorder reported
`/usr/bin/eog` running with a genuine native surface.

**Cause (IC-5).** `subprocess.Popen(cmd, shell=True)` forks rather than execs, so `Popen.pid`
was the shell's; the Wayland surface check matched surface pid against it exactly and timed
out. The X11 arm did not exhibit this because its check ignores pid — that asymmetry is what
made the defect visible.

**Resolution.** `exec` in the spawner plus an ancestor-tolerant process-tree match; both arms
re-run; documented in `infra/wayland_lab/IMPLEMENTATION_CORRECTIONS.md` **before** re-running.

**Stability verified, not assumed:** all four capture sha256 values are byte-identical before
and after, and the binding matrix is unchanged at 0/12. The defect was in the **ground-truth
record**, not the measurement.

**What this says about the apparatus.** It was caught only because the recorder observes
independently of the case constructor. An apparatus that has produced six documented
corrections has probably not produced its last — stated in `LIMITATIONS.md` §12.

### H-4 — A prior-art citation was unverified **[FOUND, RESOLVED]**

**Question 7.** AgentProvenance was carried through the research phase with citation status
**UNVERIFIED** — adopted on the research director's word with no pinned source.

**Resolution.** Pinned and verified at commit `fc2e62647dc64b6d23144b88e0e0ac101b4f2793`
(HEAD of `main` at inspection). Six claims checked against source and documentation, all
supported. Files read in full are listed with their sha256 prefixes in `research/PRIOR_ART.md`.

**Consequence that cuts against us, recorded deliberately.** AgentProvenance independently
enforces two disciplines this project also uses — separation of runtime identity from
application-asserted context (enforced at ingest), and graded-confidence correlation. That
**reduces** our claim to novelty on both, and `RELATED_WORK.md` says so.

**Residual limitation.** The software was **not executed**. All claims rest on source and docs
at one revision.

### H-5 — An absence-of-evidence claim about a third party **[FOUND, NARROWED]**

**Question 5.** The display-surface search over AgentProvenance could easily have been written
as "AgentProvenance has no display/screenshot capability". That would treat a term search as
proof of absence.

**Resolution.** The conclusion is stated exactly as: *"No generic visual-display/scene
provenance mechanism was found in the inspected pinned repository surface."* The prohibited
stronger forms are listed in `CLAIM_TABLE.md` C22, and the search limitations travel with the
claim everywhere it appears: term-based, one commit, binaries not decoded, six files read in
full, software not executed, forks/issues/PRs not considered.

**Verified mechanically.** A sweep for prohibited wording found the phrase "AgentProvenance
cannot capture screenshots" three times — all three inside explicit disclaimers or the
prohibited-wording column.

### H-6 — An apparent tag/commit discrepancy **[INVESTIGATED, NOT AN ISSUE]**

**Question 8.** `git for-each-ref` reported `phase1-analytic-v1 → 5dbc4bf` while the frozen
documents cite `fa78c2d`.

**Resolution.** `5dbc4bf` is the **annotated tag object**; the commit it points to is
`fa78c2d`. `git rev-parse --short <tag>^{commit}` confirms all five tags match their
documented commits. Recorded because it looked like a discrepancy and a reader running the
first command will see the same thing.

### H-7 — A latent fallback that could never fire **[FOUND, FIXED]**

**Question 4.** The viewer fallback probed `which imv`, which always fails on Debian — the
package ships `imv-wayland` and `imv-x11`. The ground truth recorded `"not installed"` for a
viewer that **was** installed.

**Resolution.** Fallback names corrected (IC-6). No result was affected: `eog` is first on both
lists and started natively on both platforms in every run, with **zero fallbacks taken**. A
latent fallback that cannot fire is a defect waiting for the run where it is needed.

### H-8 — A dependency that would have weakened reproducibility **[DECISION RECORDED]**

`matplotlib` is not available in the analysis environment. Installing it would have added a
version-pinned dependency to a package whose figures must regenerate anywhere.

**Resolution.** The figure generator emits SVG using the **standard library only**. Trade-off
accepted: less polish, exact reproducibility, and `REPRODUCIBILITY.md` can state "no
dependencies" truthfully.

---

## Checks run, with outcomes

| # | Check | Method | Result |
|---|---|---|---|
| 1 | Every referenced repo path exists | regex over all package docs | **149 references, 0 missing** (excluding the two files being written) |
| 2 | Markdown links resolve | link extraction + `os.path.exists` | **0 broken** after this file and the manifest were added |
| 3 | Package numbers match source artifacts | 29 assertions against `audit_metrics.json`, `analytic_vs_empirical.csv`, `empirical_risk_coverage.csv`, `field_coverage.csv`, `platform_comparison_metrics.json`, `phase1_final_metrics.json`, `trace_summary.json` | **29/29 match, 0 mismatches** |
| 4 | Prohibited wording | 12 banned patterns over all package docs | 23 hits, **all inside prohibition or disclaimer contexts**; 0 assertive uses (2 flagged were line-wrap false positives, confirmed by reading) |
| 5 | Invented citations | arXiv IDs in `RELATED_WORK.md` ⊄ `research/PRIOR_ART.md` | **NONE invented** (9 cited, all recorded in the prior-art board) |
| 6 | Claim-table coverage | all `[C…]` markers vs `## C…` rows | **25 rows defined, 25 cited, 0 dangling markers, 0 uncited rows** |
| 7 | Judge output as ground truth | "judge" ∧ "ground truth" co-occurrence | 2 hits, **both disclaimers** |
| 8 | Six-link overclaim | "all six" / "six links" | 1 hit, refers to AgentProvenance's six *checked claims*, not the chain |
| 9 | Links 5–6 always scoped | every mention | **4/4 paired with "never reached" / "out of scope"** |
| 10 | Unscoped "Wayland" as result subject | regex for result verbs without "tested" | **0 hits** |
| 11 | Figures are well-formed and match source | XML parse + `FIGURE_DATA.json` diff | **7/7 parse; every plotted value traced to its artifact** |
| 12 | Frozen artifacts unmodified | `git status` + sha256 vs values recorded in the static trace | **adjudicator, recorder, adjudicate_empirical, adversarial_cases all unchanged** |

---

## Conclusions re-examined individually

| Conclusion | Measured or inferred? | Alternative explanation considered | Verdict |
|---|---|---|---|
| Scene provenance ~6.6% EXACT/STRONG, EXACT = 0 | MEASURED | *Parser weakness rather than information absence?* — refuted by manual validation: the missing edges are absent from the trace, and the two boundary cases in `OBSERVABILITY_BOUNDARY.md` §3 show one recoverable only because the agent bracketed its own window | stands, corpus-scoped |
| Lookback 4.8% → 54.9% | MEASURED | *An artifact of the corrected resolver?* — the correction **lowered** the whole curve (from 5.5%→72.7%); the qualitative conclusion survives and is weaker | stands, with the correction stated |
| 13b = CONTRACT_UNDERSPECIFICATION | MEASURED trace + INFERENCE classification | *Just a recorder bug?* — true **inside the optimistic configuration** (B′) and false in the default deployment; *just a contract failure?* — the adjudicator's rule was correct and the fact alone flips it. Both readings preserved as secondary findings rather than resolved away | stands, with B′ and C′ |
| Zero of twelve bindings changed | MEASURED | *A lab artifact — wrong compositor, broken portal?* — `grim` captures succeeded throughout and the decisive `AvailableSourceTypes` value needs no session; but **one backend** is a real limitation and is stated everywhere the claim appears | stands, backend-scoped |
| `app_id` is client-asserted | MEASURED, both arms | *The X11 `Eog`/`eog` case difference detects impostors?* — no: toolkit convention, attacker can set either, and on Wayland the strings are byte-identical | stands, with the caveat recorded |
| fds reveal nothing at capture time | MEASURED, both arms | *A property of `eog` specifically?* — **yes, possibly.** One viewer tested. A memory-mapping editor could differ | stands, narrowed in `LIMITATIONS.md` §9 |
| Analytic arm overconfident | MEASURED | *Cherry-picking the unsafe direction?* — no: 34 of 42 disagreements ran the **safe** direction, and that is stated alongside | stands, one-experiment wording |
| Renderer-boundary principle | **INFERENCE** | *Four witnesses from one project could share a common cause* — acknowledged; the Wayland comparison is a single non-refutation and weak support | classified INFERENCE, not promoted |
| Epistemic-policy thesis | **INFERENCE** | *Is it just "record more"?* — no, and the counter-example is ours: C8 shows the repairing observation creates an honest-case false reject. Necessary-condition claim only | classified INFERENCE, not promoted |

---

## What a reviewer should attack first

Written for the reader, not for us. The three softest points:

1. **One Wayland backend.** The headline "zero of twelve" is a statement about
   `xdg-desktop-portal-wlr` on a headless software-rendered container. A GNOME or KDE backend
   implements WINDOW sources and was not tested. This is the cheapest experiment that could
   change a cell of the matrix — and it still would not touch link 4.
2. **Single-reviewer validation.** The manual pass refuted 4 of the first 7 automated claims,
   which is evidence it was necessary and *no* evidence it was sufficient. There is no
   inter-rater statistic.
3. **Constructed suites, one corpus.** Two cases per platform; 13 scenarios; one benchmark and
   model family. Nothing here is a base rate, and the attack suite is demonstrably
   unsaturated — 13b only became a real attack after IC-4 fixed its construction.

---

## Standing prohibitions

Reproduced from `CLAIM_TABLE.md` because these are the sentences most likely to be written by
someone summarising this work:

- ✗ "Wayland does not help provenance" / "Wayland solves capture provenance"
- ✗ "AgentProvenance cannot capture screenshots"
- ✗ "All nested compositors are opaque"
- ✗ "Atomic provenance is impossible"
- ✗ "Analytic security evaluation is unreliable"
- ✗ "Scene provenance is impossible to recover"
- ✗ "83.6% of cases resolved by four fields" *(withdrawn)*
- ✗ Any comparative recorder-skew figure *(withdrawn as not reproducible)*
- ✗ "`_NET_WM_PID` is absent on X11" *(falsified by our own Phase J data)*
- ✗ Any claim about portal stream metadata contents *(never observed)*
- ✗ "First work to…" for any mechanism in the non-claims list
