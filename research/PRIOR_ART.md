# Prior Art Board

This file is a guard against accidental novelty inflation.

## WeaveBench — arXiv:2606.09426v3

Hybrid GUI+CLI benchmark with 114 tasks and trajectory-aware judging. Explicitly detects shortcut behavior including fabricated visual evidence and hard-coded metrics.

Relevance:
- target dataset/environment;
- judge localizes suspicious behavior with quoted trace evidence;
- but judge-based authenticity variables are not independent ground truth.

## ProcGrep — arXiv:2606.16988

Procedural fingerprinting of coding-agent traces. Agent identity is predictable from procedural representations.

Relevance:
- proves trace procedure carries strong model identity;
- useful comparison point;
- not a visual scene-provenance system.

## AgentTrails — arXiv:2607.18816

Post-hoc provenance reconstruction from raw agent trajectories. Builds bipartite graphs of tool-call activities and artifacts/entities using paths, filenames, URLs, identifiers, response values, etc.

Relevance:
- directly invalidates a broad "nobody reconstructs dataflow from agent traces" novelty claim;
- likely the closest structural prior art;
- must be compared feature-by-feature with any proposed graph representation.

Open question — **RESOLVED 2026-09-09** (E027). Fetched arXiv:2607.18816v1 and read the graph definition:
- node types are only Activities (tool calls) and Entities (inputs/outputs/intermediate artifacts/returned values);
- edge types are `generatedBy`, `usedBy`, and weaker `informedBy`;
- evaluation is on SciAgentGym and Discovera, i.e. tool-calling/scientific traces, not GUI/computer-use;
- it models **no** displayed visual scene, screenshot entity, window or process identity, and no genuine-vs-substitute render state. Generated visualizations appear only as opaque artifacts.

Consequence: AgentTrails occupies exactly the layer this workspace's audit found already works (artifact/file lineage, R1/R2 at ~100%). It does not occupy the scene layer — which the audit found is not recoverable from these traces at all.

## PROV-AGENT — arXiv:2508.02866

Extends W3C PROV for agentic workflows and captures agent interactions in end-to-end provenance.

Relevance:
- general provenance/instrumentation prior art;
- not evidence that visual scene authenticity is solved.

## CHIEF — arXiv:2602.23701

Transforms flat multi-agent logs into hierarchical causal graphs for failure attribution.

Relevance:
- causal-graph/failure-attribution adjacent work;
- broad "causal graph for agent traces" claim is occupied.

## AgentRewardBench — arXiv:2504.08942

Human-reviewed web-agent trajectories used to evaluate automatic trajectory judges.

Relevance:
- strong motivation to audit automatic judge outputs;
- its success-label precision/IAA numbers must not be transferred numerically to WeaveBench fabrication labels.

## LongHorizon-Harness — arXiv:2608.01964

Manage–Execute–Audit loop with independent read-only auditing; large WeaveBench improvement.

Relevance:
- verification intervention lane is active/crowded;
- our candidate lane should remain diagnostic/provenance-focused.

## RILA — arXiv:2609.02088

Rendering-in-the-loop interactive web development using runtime interaction feedback.

Relevance:
- "put rendering/verification in the loop" is not novel;
- strengthens the need to focus on provenance/diagnosis rather than intervention.

## Taste Labs RFR — 2026-08-16

Explicit interest in process/output relationships, visual/interactive representations, open-ended evaluation, verification, reward-hacking symptoms, and design trace provenance.

Relevance:
- strong domain fit;
- should not distort the science or cause us to overclaim novelty.

## Novelty rule

Do not write "first" or "novel" until a targeted prior-art search has checked at minimum:
- agent provenance graphs;
- screenshot/scene provenance;
- CUA trace attribution;
- visual evidence authenticity;
- GUI state lineage;
- agent-generated fake UI/screenshot detection;
- process-to-artifact causal tracing.

A credible contribution may be an evaluation result or failure boundary, not necessarily a new framework.

## Searched again 2026-09-09 (post-board)

- **From Agent Traces to Trust** — arXiv:2606.04990. Survey of evidence tracing / execution provenance for LLM agents; typed execution graphs. Categorised under cs.CR. No visual, screenshot, or GUI-state modelling. Not a competitor for the scene layer, but it does further occupy generic "typed provenance graph over agent traces".
- **VisCritic** — arXiv:2606.24525. Visual state comparison as process reward for GUI agents. VLM-based, not structural; addresses reward modelling rather than evidence lineage.
- **BAITBENCH** — arXiv:2608.30724; plus hack-verifiable-environment work (2605.20744) and BenchJack (2605.12673). Reward-hacking measurement, no scene lineage.
- **WeaveBench project page** — confirms the judge runs a "parallel scan" over fake screenshots/renders, regenerated fixtures, hard-coded metrics, duplicate crops, overlay manipulation, ground-truth leakage, runtime injection, mock services, and fabricated visual outputs, with a zeroing rule. This is LLM/VLM-judge-based fabrication detection, and it is prior art for the *goal* even though not for a structural method.
- **WeaveBench task specs** (E026) — the benchmark's own automated grader calls `vlm_score_rubric` to verify that target application UI is really visible, and caps the score when the VLM is unavailable. The benchmark authors did not treat the structural channel as sufficient either.

No work found that models target-vs-substitute visual scene lineage from computer-use-agent traces.

## Status of the narrow novelty claim

HYPOTHESIS, still unfalsified as a *gap*, but the 2026-09-09 audit shows the gap is **not fillable from these traces**: the required lineage edges are absent from the recorded data, not merely unparsed. Any future claim must be framed as a limits/instrumentation result, not as a working instrument.
