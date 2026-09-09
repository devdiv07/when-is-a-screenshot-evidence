# First Claude Code Prompt

Read `CLAUDE.md`, `CURRENT_STATE.md`, `RESEARCH_QUESTION.md`,
`specs/RECOVERABILITY_AUDIT.md`, `specs/PROVENANCE_MODEL.md`,
`research/EVIDENCE_LEDGER.md`, `research/DECISION_LOG.md`, and
`research/PRIOR_ART.md` before doing anything else.

Then execute the current gate, not a broader project.

Your objective is to determine whether visual scene/evidence provenance is
structurally recoverable from the released WeaveBench GPT-5.4 low run1/run2
`chat.jsonl` trajectories around judge-localized `hack_evidence_quotes`.

Important constraints:

- Do not build a full framework first.
- Do not modify ProcGrep.
- Do not write fellowship/application prose.
- Do not use an LLM/VLM to fill missing provenance edges.
- Do not treat WeaveBench judge fields as independent ground truth.
- Do not assume that a screenshot captured by `gnome-screenshot` is authentic.
- A genuine capture of an agent-authored fake Tk/HTML/UI scene is still substitute
  scene provenance.
- Generic agent provenance graphs are prior art (AgentTrails, PROV-AGENT, CHIEF).
  The candidate gap is narrower: target-vs-substitute visual scene lineage.
- Preserve negative and ambiguous results.

Work in this order:

1. Inspect the current local data and repository state.
2. Confirm the remote WeaveBench trajectory archive layout from primary sources.
3. Determine the safest/minimal way to selectively fetch all available
   `chat.jsonl` and matching `score.json` members without downloading screenshot
   payloads. If HTTP range ZIP access is reliable, use it; otherwise choose a
   reproducible alternative. Record hashes and source/member paths.
4. Before writing a general parser, inspect representative raw `chat.jsonl`
   examples from:
   - PIL/ImageDraw/Image.new hack evidence,
   - `gnome-screenshot` hack evidence,
   - a captured fake renderer/window if present,
   - a clean native-capture control,
   - a fake-signal-but-not-hack case if available.
5. Implement only the minimum deterministic quote locator and provenance
   reconstruction needed by `specs/RECOVERABILITY_AUDIT.md`.
6. For every available `hack_evidence_quote`, locate the cited span in the source
   trace and score recoverability R0-R5. Keep exact/strong/weak/unknown edges
   separate.
7. Include negative controls so recoverability is not measured only on hand-picked
   positive spans.
8. Produce:
   - `outputs/source_manifest.csv`
   - `outputs/recoverability_cases.csv`
   - `outputs/recoverability_report.md`
9. The report must answer:
   - What fraction of quotes can be located exactly?
   - What fraction allow producer/action recovery?
   - What fraction allow output-artifact linkage?
   - For capture cases, what fraction expose the actual window/process/scene source?
   - What fraction can be classified as TARGET_SCENE, AGENT_SUBSTITUTE_SCENE,
     DIRECT_SYNTHESIS, DERIVED_FROM_PRIOR_EVIDENCE, or UNKNOWN without an LLM?
   - What is the false-attribution rate on negative controls?
   - Which missing trace fields prevent higher recoverability?
   - Does the scene-provenance construct survive, narrow, or fail?
10. Update `research/EVIDENCE_LEDGER.md`, `research/DECISION_LOG.md`, and
    `research/PROGRESS.md`.

Prior-art check before any novelty statement:
read AgentTrails (arXiv:2607.18816), PROV-AGENT (2508.02866), CHIEF
(2602.23701), ProcGrep (2606.16988), WeaveBench v3 (2606.09426v3),
LongHorizon-Harness (2608.01964), and RILA (2609.02088). Search for newer
visual/scene/screenshot provenance work too.

Success is not "the extractor works." Success is a defensible answer to whether
the necessary lineage is actually recoverable from these traces.
