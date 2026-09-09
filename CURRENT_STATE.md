# Current State — 2026-09-08

## Frozen prior projects

Razorpay / FINCORE and OPAQUE / AgenTrust are prior evidence and are not active work here.

## Active target

Taste Labs research/fellowship direction around open-ended design-agent evaluation, verification, process/output relations, and reward-hacking-like behavior.

## Why this workspace exists

The investigation moved from a broad "ProcGrep for browser agents" idea to a narrower measurement problem.

The current candidate question is:

> Can we structurally reconstruct whether a delivered visual artifact is causally descended from the target application state, rather than from substitute state synthesized by the agent?

This is called **scene provenance** in this workspace.

## Included score-level reconnaissance

Source file: `data/weavebench_gpt54_low_joined.csv`

Measured from the included table:

- 228 rows total = 114 tasks × 2 nominal low GPT-5.4 reruns.
- 223 rows have a valid `is_hack` judgment.
- 109 tasks have valid hack judgments in both runs.
- Valid paired matrix:
  - clean/clean = 66
  - clean/hack = 19
  - hack/clean = 10
  - hack/hack = 14
- valid discordant pairs = 29/109.
- Cohen's kappa across rerun hack occurrence ≈ 0.317.
- Interpret this as modest **behavioral/task-conditioned repeatability**, not judge inter-rater reliability.
- `hack_confidence` contains no values in the interval 0.61–0.85 in the 223 valid rows.
- minimum confidence among `is_hack=True` rows = 0.86.
- maximum confidence among `is_hack=False` rows = 0.60.
- This suggests the confidence field behaves like a thresholded decision score in this release; it must not be treated as calibrated probability without evidence.
- `PIL_FAKE_RENDER` appears 7 times across the two runs, concentrated in 4 unique tasks; 3 of those tasks show it in both runs.
- Therefore E5.1 is too sparse/task-concentrated to carry the primary analysis on these two runs.

Prior reconnaissance also found that raw native screenshot count is essentially uninformative about judge-rated evidence authenticity after accounting for runtime. Treat native screenshot count as a negative-control/effort feature, not perception.

## Reported reconnaissance not independently reproducible from the included CSV yet

These findings were reported from selective remote archive inspection and should remain `REPORTED / TO VERIFY` until their raw source rows are fetched into this repository:

- all 114 task slots exist in both low archives;
- run1/run2 have different chat/results completeness;
- `hack_evidence_quotes` frequently contain `gnome-screenshot`, PIL/ImageDraw/Image.new, etc.;
- some captured artifacts depict agent-created fake application scenes;
- artifact byte-density had a weak pooled association with fake-signal labels that did not survive a small within-task test.

Do not upgrade these to MEASURED FACT here until this repository reproduces them.

## Key null result

The crude hypothesis:

> "fabricators simply take fewer screenshots"

is rejected by reconnaissance.

The surviving mechanism is not observation volume. It concerns whether observation is **causally connected to the artifact being changed and to the target application state**.

## Current gate

Before building a full event grammar or provenance engine:

1. retrieve the available `chat.jsonl` traces;
2. locate the judge-quoted hack spans;
3. test whether structural scene provenance can be reconstructed around those spans;
4. quantify recoverability and ambiguity;
5. kill or narrow the project if the necessary lineage is not present in traces.

See `specs/RECOVERABILITY_AUDIT.md`.
