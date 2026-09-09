# Provenance Recoverability Audit

## Objective

Determine whether visual scene/evidence provenance can be reconstructed from WeaveBench trace structure strongly enough to justify building a deterministic provenance instrument.

This audit comes **before** the full extractor.

## Input population

Start with GPT-5.4 low run1/run2 because score-level reconnaissance already exists.

Use all available cases with non-empty `hack_evidence_quotes` as the primary localization pool.

Add negative controls sampled from:
- `is_hack=False` with `fake_signal=False`;
- `is_hack=False` with artifact `fake_signal=True` if recoverable from score records;
- ordinary failures if available.

Do not use only positive cases.

## Source integrity

For every fetched member record:

- archive URL
- archive member path
- content length
- SHA-256 of extracted content
- fetch timestamp
- run id if present
- task id

Store this in `outputs/source_manifest.csv`.

## Do not bulk-download images during the first pass

The first question is whether the trace itself carries enough provenance-bearing structure.

Fetch `chat.jsonl` and relevant `score.json` records first.

Only fetch image/result artifacts for explicitly selected validation cases when needed.

## Quote localization

For every `hack_evidence_quote`:

1. Normalize only minimally (whitespace/escaping) and preserve raw quote.
2. Search exact substring in `chat.jsonl`.
3. If exact match fails, use a documented deterministic normalization.
4. Do not use semantic/LLM matching in the main recoverability number.
5. Record quote match quality and event/turn index.

## Recoverability levels

Use these levels. Never silently infer a higher level.

### R0 — Quote localized

The judge-cited span is found in the trace with deterministic matching.

### R1 — Producer/action recovered

The tool call or command responsible for the suspicious action is structurally identified.

Examples:
- `python` command creating a PNG;
- `gnome-screenshot`;
- ImageMagick/`convert`;
- browser/screenshot tool;
- file copy/crop operation.

### R2 — Output artifact linked

A concrete output path/entity can be connected to the action and, when applicable, to a required delivered artifact.

Exact path/name/hash evidence preferred.

### R3 — Capture source context recovered

For captured evidence, enough trace evidence exists to identify what application/process/window/URL/display state the capture likely came from.

This must be based on structural evidence, not visual-semantic guessing.

Possible evidence:
- explicit app-launch command;
- active-window query;
- process/window title from tool output;
- URL/tab identity;
- display/app state emitted by harness.

If only temporal adjacency suggests the source, mark weak/inferred.

### R4 — Scene lineage classified

The evidence can be classified structurally as one of:

- TARGET_SCENE
- AGENT_SUBSTITUTE_SCENE
- DIRECT_SYNTHESIS
- DERIVED_FROM_PRIOR_EVIDENCE
- UNKNOWN

The classification must cite graph edges / exact events.

### R5 — Target reachability established

A deterministic or explicitly bounded inference path connects:

`target application state -> rendered scene -> evidence capture -> delivered artifact`

or proves a substitute lineage:

`agent-created substitute state -> rendered scene -> evidence capture -> delivered artifact`.

R5 is deliberately hard.

## Edge confidence

Every provenance edge is one of:

- EXACT — explicit identifier/path/value reference.
- STRONG — deterministic rule using adjacent structured fields.
- WEAK — temporal/heuristic evidence.
- UNKNOWN.

Do not collapse these.

## Primary audit metrics

Report:

- quote localization rate (R0);
- action/producer recoverability (R1);
- artifact-link rate (R2);
- capture-source recoverability (R3);
- scene-lineage classification coverage (R4);
- target/substitute reachability coverage (R5);
- exact/strong/weak edge proportions;
- ambiguity rate;
- missing-trace rate;
- breakdown by hack pattern;
- breakdown by native vs shell-routed capture;
- negative-control false attribution rate.

## Manual validation

For a stratified sample, two independent human reviewers should inspect raw trace evidence and classify:
- producer mechanism;
- output path;
- capture source;
- target vs substitute scene;
- ambiguity.

Do not reveal the automated classification during first annotation.

Report agreement and adjudication.

## Kill criteria

Stop or materially reframe if any is true:

1. R1/R2 cannot be recovered reliably from trace structure.
2. R3/R4 require LLM semantic interpretation for most capture cases.
3. Structural target-vs-substitute classification is too sparse/selective to support a useful instrument.
4. Negative controls produce frequent false provenance chains.
5. The graph can recover file lineage but not scene lineage; in that case report the boundary rather than call it visual provenance.
6. The system only reproduces WeaveBench judge judgments rather than establishing independent structural facts.

## Deliverables

`outputs/source_manifest.csv`

`outputs/recoverability_cases.csv` with at least:
- run
- task
- quote_id
- hack_pattern
- raw_quote
- match_status
- event_index
- producer_kind
- producer_command/tool
- output_path
- capture_channel
- source_app_process
- scene_class
- R_level
- edge_confidence
- ambiguity_reason
- evidence_refs

`outputs/recoverability_report.md`

The report must include negative cases and unresolved cases, not only successes.
