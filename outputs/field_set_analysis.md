# Field-Set Coverage Analysis

Phase D. Derived from `outputs/information_deficits.csv` by `scripts/field_coverage.py`.
Machine-readable results: `outputs/field_coverage.csv`.

> **Scope warning, applies to every number below.**
> This measures **HISTORICAL COVERAGE**: which fields, had they been recorded, would have
> resolved the scene-source question for benign traces already collected.
> It says **nothing** about **ADVERSARIAL SUFFICIENCY — NOT YET TESTED**. An agent that
> knows the contract can choose window titles, launch real interpreters, and place real
> windows. Every field here is evaluated for spoofability in
> `specs/CAPTURE_PROVENANCE_CONTRACT.md`, and only Phase I can decide sufficiency.

---

## 1. Population

| | n |
|---|---|
| delivered visual artifacts (frozen audit) | 453 |
| unresolved (UNKNOWN scene, or WEAK source, or derivation chain) | 415 |
| — **eligible**: a capture-time field could plausibly resolve it | **287** |
| — `no_target_defined`: task names no target application at all | 98 |
| — `derivation_chain`: artifact is a transform/copy of a prior image | 30 |

The 98 `no_target_defined` cases are excluded from the coverage universe on purpose.
No capture-side field can decide "target vs substitute" when the benchmark task never
says what the target is. That deficit is in the **task specification**, not the runtime,
and is recorded separately as `TARGET_APPLICATION_IDENTITY`.

## 2. Fields are conjunctive, not independent

The single most important structural result:

**In the STRICT model, no single field resolves a single case.**

`Z_ORDER` without `VISIBLE_WINDOW_SET` is "stacking order of what?". Neither can be
intersected with the delivered image without `CAPTURE_REGION`. An earlier version of this
analysis treated fields independently and reported that one field resolved 83.6% of cases;
that was an artifact of the encoding, not a finding, and it was discarded. Deficits are
therefore recorded as conjunctive **bundles** (`bundle_id`, `bundle_fields`), and a case
counts as covered only when a whole bundle is supplied.

Observed bundles, by number of eligible cases they would resolve:

| cases | bundle (all fields required together) | verdict |
|---|---|---|
| 240 | `CAPTURE_REGION + VISIBLE_WINDOW_SET + WINDOW_GEOMETRY + Z_ORDER` | yes |
| 41 | `ACTIVE_PID + ACTIVE_WINDOW_IDENTITY + PROCESS_LIFECYCLE_AT_CAPTURE` | yes |
| 36 | `PROCESS_LIFECYCLE_AT_CAPTURE + PROCESS_START_IDENTITY` | yes |
| 35 | `ACTIVE_PID + ACTIVE_WINDOW_IDENTITY` | yes |
| 32 | `ACTIVE_WINDOW_IDENTITY + Z_ORDER` | yes |
| 25 | `ACTIVE_WINDOW_IDENTITY + BROWSER_TAB_ID + BROWSER_URL` | yes |
| 14 | `ACTIVE_PID + COMMAND_LINE` | yes |
| 14 | `ACTIVE_PID + AGENT_WRITTEN_CODE_LINEAGE + COMMAND_LINE + PROCESS_START_IDENTITY` | yes |

Two bundles are recorded with verdict **no**, and they matter as much as the positive ones:

- `WINDOW_TITLE + WM_CLASS` (272 cases) — human-readable labels narrow the candidate set
  but never bind the scene, and **both are chosen by the agent**.
- `CAPTURE_TRIGGER_ACTION_ID` (312 cases) — binds the image *file* to the action that
  produced it. That is artifact provenance, which the audit already recovers at 453/453.
  It says nothing about what the pixels depicted.

## 3. Coverage curves

Two models, because the honest answer differs.
**STRICT** counts only bundles marked `yes`. **LENIENT** also counts `uncertain` bundles —
chiefly the assumption that focus identity plus capture region is decisive, which the
audit's own composite-scene finding says is *not* generally true.

### STRICT (defensible)

| fields | set | eligible covered | % |
|---|---|---|---|
| 4 | `CAPTURE_REGION + VISIBLE_WINDOW_SET + WINDOW_GEOMETRY + Z_ORDER` | 240 | **83.6%** |
| 6 | + `PROCESS_LIFECYCLE_AT_CAPTURE + PROCESS_START_IDENTITY` | 259 | **90.2%** |
| 8 | + `ACTIVE_PID + ACTIVE_WINDOW_IDENTITY` | 286 | **99.7%** |

Thresholds: 50% and 75% are both first crossed at **4 fields**; 90% at **6 fields**.

### LENIENT (optimistic)

| fields | set | eligible covered | % |
|---|---|---|---|
| 3 | `ACTIVE_PID + ACTIVE_WINDOW_IDENTITY + CAPTURE_REGION` | 208 | 72.5% |
| 4 | + `PROCESS_LIFECYCLE_AT_CAPTURE` | 249 | 86.8% |
| 5 | + `PROCESS_START_IDENTITY` | 285 | 99.3% |

The gap between the models is the whole composite-scene problem. LENIENT reaches 72.5%
with three cheap fields *only by assuming* that naming the focused window settles what a
full-screen grab depicted. The audit refuted that assumption on real data
(`view_dashboard_and_editor.png`, report §8). **STRICT is the number to quote.**

### Greedy vs optimal

Exact minimum set cover is NP-hard, and the yes/uncertain mapping carries genuine
ambiguity, so exact minimality would be false precision. Bundle-greedy was used and is
labelled an approximation. Brute force over all subsets up to size 7 gives the gap:

| size | STRICT optimal | greedy | gap |
|---|---|---|---|
| 2 | 36 (12.5%) | 0 | 36 |
| 3 | 76 (26.5%) | 0 | 76 |
| 4 | 240 (83.6%) | 240 | **0** |
| 5 | 240 (83.6%) | 240 | 0 |
| 6 | 259 (90.2%) | 259 | **0** |
| 7 | 267 (93.0%) | 259 | 8 |

Greedy is optimal at the sizes that matter (4 and 6) and within 8 cases at size 7.
The sub-4 gaps are an artifact of greedy committing to a whole 4-field bundle first.

## 4. What this does and does not license

**Supported (HISTORICAL COVERAGE, MEASURED FACT):**

- Four display-composition fields would have retrospectively resolved 83.6% of the
  eligible unresolved cases; six reach 90.2%.
- No single field is useful alone.
- Window title and WM_CLASS are *not* on the critical path; they were already available in
  the 12 traces carrying `xwininfo` and did not resolve those cases.
- Process-lifecycle fields are the second-largest block, and they correspond to a
  measured error the audit actually made (stale "still running" evidence, report §8).

**Not supported (would be an overclaim):**

- That recording these fields makes visual evidence trustworthy. Coverage is measured on
  agents that were **not trying to defeat a recorder**. None of these fields was collected
  adversarially, and the strongest ones — `VISIBLE_WINDOW_SET`, `Z_ORDER`, `WINDOW_GEOMETRY` —
  describe a display the agent can populate at will.
- That 99.7% is the practical ceiling. It is coverage of the **eligible** universe only.
  Against all 415 unresolved cases the 8-field set reaches 371/415 = **89.4%**, and the
  4-field set 312/415 = **75.2%**. Both figures overstate what is actually answered: for
  the 98 `no_target_defined` cases these fields identify *what produced the pixels* but
  still cannot say whether that thing was the task's target, because the task never named
  one. Scene-source recovery and target-vs-substitute adjudication are different questions,
  and only the first is addressed by capture-time fields.
- Any statement about false-accept rates. This analysis has no adversarial cases in it.

## 5. Direct input to the contract

Phase H must justify every proposed field from this table or from the threat model. The
mapping is:

| Contract tier | Fields | Justification here |
|---|---|---|
| A window labels | `WINDOW_TITLE`, `WM_CLASS` | verdict **no** — included only as context, never as evidence |
| B process identity | `ACTIVE_PID`, `PROCESS_START_IDENTITY`, `COMMAND_LINE`, `EXECUTABLE_PATH` | 35 + 36 + 14 cases |
| C code lineage | `AGENT_WRITTEN_CODE_LINEAGE`, `CONTENT_HASH` | 14 cases + all 30 derivation chains |
| D display composition | `CAPTURE_REGION`, `VISIBLE_WINDOW_SET`, `Z_ORDER`, `WINDOW_GEOMETRY`, `ACTIVE_WINDOW_IDENTITY` | **240 cases — the dominant block** |
| E application state | `BROWSER_TAB_ID`, `BROWSER_URL`, `DOCUMENT_INSTANCE_ID` | 25 + 41 cases |
| F record integrity | — | no historical deficit; required by the threat model only |

Tier F earns no cases in this analysis at all. It is included in the contract solely
because the threat model requires it, and that distinction is stated explicitly there.
