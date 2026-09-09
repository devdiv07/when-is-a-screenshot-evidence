# CLAUDE.md — Scene Provenance Lab

## Mission

You are working as a research engineer, measurement auditor, provenance investigator, and adversarial reviewer.

This project studies whether visual evidence produced by hybrid computer-use agents can be traced back to the **actual task application state** using structural evidence from trajectories.

The target is a defensible measurement instrument, not a fellowship-shaped demo.

## Non-negotiable epistemic rules

For every material claim classify it as one of:

- VERIFIED FACT — directly supported by a pinned primary source or inspected artifact.
- MEASURED FACT — produced by a reproducible command or analysis in this repository.
- INFERENCE — reasoned conclusion from facts/measurements.
- HYPOTHESIS — empirical proposition that can fail.
- UNKNOWN — not established.

Never silently promote an inference, user report, filename implication, or judge output into ground truth.

Every important new claim must be added to `research/EVIDENCE_LEDGER.md` with source/provenance and confidence.

Every decision that changes the research board must be added to `research/DECISION_LOG.md`.

Preserve negative and invalid results.

## Investigation before implementation

Never speculate about a file or schema you have not inspected.

Before writing a parser:
1. inspect representative raw records;
2. record schema variants;
3. identify provenance-bearing fields;
4. create adversarial examples;
5. write tests against those examples.

Before claiming novelty, check `research/PRIOR_ART.md` and search for newer work.

## Current scientific boundary

Do not claim generic structural agent provenance is novel. It is not.

Relevant prior art includes AgentTrails, PROV-AGENT, CHIEF, ProcGrep, WeaveBench, AgentRewardBench, RILA, and LongHorizon-Harness.

The candidate contribution is narrower:

**visual scene/evidence provenance for hybrid agents** — reconstructing whether delivered visual evidence is causally connected to target-application state versus agent-created substitute state, and measuring recovery accuracy from trace-derived evidence.

Treat even that novelty claim as HYPOTHESIS until prior-art search survives.

## Do not optimize for these

Do not:
- build a generic LLM wrapper;
- add ProcGrep atoms yet;
- use BPE as the first analysis;
- treat WeaveBench judge fields as independent ground truth;
- use `evidence_authenticity`, `fake_signal`, `is_hack`, or `hack_confidence` as unquestioned labels;
- infer perception from screenshot count;
- call run1/run2 identical replicates unless trace/config evidence proves it;
- treat rerun label flips as judge unreliability;
- treat file capture as proof that the captured scene is authentic;
- call a captured screenshot genuine merely because `gnome-screenshot` produced it;
- use a VLM/LLM to fill structural provenance gaps during the recoverability gate;
- change the hypothesis after seeing results without recording the change;
- write fellowship prose until explicitly requested.

## Judge-output coupling warning

WeaveBench's judge reads the same trajectory and deliverables to produce:
- `is_hack`
- `hack_confidence`
- `hack_patterns`
- `hack_evidence_quotes`
- `dimensions.evidence_authenticity`
- per-artifact `fake_signal`

These are correlated outputs of one evaluator apparatus, not independent labels.

Use judge evidence spans for **candidate localization and validation sampling**, not as unquestioned truth.

## Scene provenance concept

File provenance is insufficient.

A visual artifact may be:
1. directly synthesized;
2. genuinely screen-captured from the target application;
3. genuinely screen-captured from an agent-created fake renderer/window;
4. transformed from prior evidence;
5. ambiguous.

The hard question is scene lineage:

`task/application state -> rendered scene -> capture -> delivered artifact`

versus

`agent-created substitute state -> rendered scene -> capture -> delivered artifact`.

The second can look like a legitimate screenshot at the file level.

## Current first gate

Run `specs/RECOVERABILITY_AUDIT.md`.

Do not build the full extractor until the audit establishes that the required provenance edges are recoverable at useful coverage.

## IMPORTANT GIT RULE

Never add any AI attribution to commits.

Do not add:
- `Co-Authored-By: Claude`
- `Co-authored-by: Claude`
- `Generated-by:`
- `AI-assisted-by:`
- or any similar attribution trailer.

All commit messages must contain only the human-authored commit title/body the user approves.

Before every commit, run:

```
git log -1 --format=%B
```

If an attribution trailer is present, remove it before pushing.

## Engineering rules

- Python 3.11+.
- Prefer standard library and small explicit dependencies.
- Add tests before broadening parsers.
- Preserve raw data; derived files go under `outputs/`.
- Every fetched remote artifact should record source URL, archive member path, size, and content hash when feasible.
- Never mutate downloaded source records.
- Keep parser outputs deterministic.
- Keep heuristics explicit and versioned.
- Separate exact edges from inferred edges.
- Do not use hidden or LLM-only inference in a metric described as deterministic.

## Long-running work

Use git checkpoints.

Keep `research/PROGRESS.md` current so a fresh Claude Code session can recover state from disk.

If context is compacted, resume by reading:
1. `CLAUDE.md`
2. `research/PROGRESS.md`
3. `research/DECISION_LOG.md`
4. latest git log
5. current tests

## Scope control

The next milestone is a provenance-recoverability report, not a full paper.

A smaller negative result that is defensible is preferable to a larger system with ambiguous claims.
