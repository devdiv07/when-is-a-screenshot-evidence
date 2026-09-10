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

---

# Post-gate prior-art sweep — 2026-09-09 (Phase G)

Run before any novelty statement in `THREAT_MODEL.md`, `CAPTURE_PROVENANCE_CONTRACT.md`
or `ADVERSARIAL_SUFFICIENCY_EXPERIMENT.md`.

## Agent Flight Recorder — arXiv:2609.01931

Tamper-evident audit trails for long-horizon tool-using agents: each action is a
canonically serialised event binding eight semantic fields, with hash chaining, Merkle
batching and on-chain anchoring.

Fetched and read (2026-09-09). The eight fields are: intent, policy evaluation, human
approval, execution, effects, context provenance, code provenance, delegation provenance.

Relevance — **this is direct prior art for Tier F of our contract**:
- record integrity, tamper evidence and hash-chained event logs for agents are **occupied**;
- we must not claim any novelty for signed/hash-chained agent event records.

Boundaries, verified in the text:
- it records **no display or screen state** — no screenshots, window identity, active
  window, z-order or capture region. It states the recorder captures the proposed action,
  not the surrounding state;
- its stated guarantee is **integrity of recorded events**;
- **completeness is explicitly a non-goal** — bypassed or unrecorded actions fall outside
  the guarantee;
- **records newly written after full host compromise cannot be guaranteed truthful.**

That completeness non-goal is precisely where our question lives. AFR protects the
*integrity of the record*. Our question is the *integrity of the claim the record
describes* — an adversary who never tampers with the log, and instead arranges the world
that the log then truthfully and completely reports. Our threat model's "plane fallacy"
section (§3) is the explicit statement of that difference.

We do not claim AFR assumes honest actors; that paraphrase was withdrawn (E035).

## OpenAdapt Capture

GUI-interaction recording for desktop automation: captures screenshots plus input events
for replay/training.

Relevance:
- **screenshot + window/process telemetry capture is not novel**; tooling exists;
- it is a data-collection substrate, not an adjudication mechanism, and carries no
  adversarial model — it assumes the recorded user is cooperative.

## C2PA / Content Credentials

Cryptographically signed content provenance manifests binding assertions to media, with
a hardware/software attestation chain.

Relevance:
- **content provenance and signed media manifests are not novel**;
- C2PA binds *who produced a file and how it was edited*. It authenticates the capture
  pipeline, not the truthfulness of the depicted scene. A C2PA-signed screenshot of an
  agent-authored fake window is a valid C2PA manifest of a fabrication;
- this is the same artifact-vs-scene distinction as §4 of `OBSERVABILITY_BOUNDARY.md`,
  arriving from the media-forensics direction.

## Trusted path / trusted display literature

Long-established (Orange Book trusted path; secure attention key; spoof-resistant screen
regions; trusted UI for browsers and immersive web).

Relevance:
- **trusted display and anti-spoofing mechanisms are decades old and not novel**;
- the classical problem is *inverted* relative to ours: it protects a **human** from a
  program spoofing the UI. We need to protect an **automated evaluator** from an agent
  that legitimately operates the machine and is entitled to create windows;
- the classical defence (a trusted region the untrusted program cannot draw to) may
  transfer, and must be cited if the project reaches trusted-display escalation.

## Re-checked from the existing board

- **WeaveBench v3** (2606.09426v3) — judge does LLM/VLM fabrication detection with a
  zeroing rule; the benchmark's own graders call `vlm_score_rubric` to confirm target UI
  visibility (E026). Fabricated-visual-evidence *detection* is occupied; deterministic
  capture-time *attribution* is what we are asking about.
- **AgentTrails** (2607.18816) — Activity/Entity graph, `generatedBy`/`usedBy`/`informedBy`,
  tool-calling traces; no scene, window or process-identity modelling (E027).
- **PROV-AGENT** (2508.02866) — W3C PROV for agentic workflows.
- **CHIEF** (2602.23701) — hierarchical causal graphs for failure attribution.
- **ProcGrep** (2606.16988) — procedural fingerprinting. Not modified, per instruction.
- **LongHorizon-Harness** (2608.01964), **RILA** (2609.02088) — verification/rendering
  interventions, a different lane.
- **From Agent Traces to Trust** (2606.04990) — survey of execution provenance; no visual
  or GUI-state modelling.

## Explicit non-claims

We do **not** claim novelty for any of:
- provenance graphs over agent traces;
- PID / process telemetry for agents;
- window or screen recording;
- tamper-evident or hash-chained logs;
- content provenance or signed media;
- trusted display or anti-spoofing UI.

## The candidate gap, restated narrowly

> **What independently observed capture/runtime evidence is sufficient to bind
> computer-use-agent visual evidence to the intended task state under an adversarial
> evidence generator?**

Status: **HYPOTHESIS**. The sweep above did not find work that (a) records display
composition at capture time for a CUA, (b) models the agent as an adversarial evidence
generator rather than an honest actor, and (c) measures false-accept rates per attestation
tier. AFR is the closest on integrity, C2PA on media, trusted path on display, WeaveBench
on detection — none combines the three.

This remains a HYPOTHESIS and not a contribution until the Phase I experiment runs. The
Phase C/D deficit analysis establishes only that these fields were *missing*, never that
they would be *sufficient*.

---

# Phase J prior-art sweep — 2026-09-10 (platform comparison)

Scope: only what the 13b classification and the X11/Wayland comparison actually touch.

## AgentProvenance — runtime/process/file provenance for agents

**Citation status: UNVERIFIED.** Named by the research director as demonstrating strong
process/file/runtime provenance for agents, and adopted here as prior art for the runtime
layer. No primary source has been pinned in this repository, so per `CLAUDE.md` it is
recorded as a **user report**, not a VERIFIED FACT. A pinned source must be added before it
appears in any writeup.

Boundary as adopted:

- process, file and runtime provenance for agent episodes is **occupied**. This project must
  not claim it.
- It does **not** address the edge this project measured to be failing:
  `process/client → displayed resource`. Knowing which process wrote which file, and which
  process owns which surface, does not establish which resource a legitimate renderer had on
  screen — that is exactly what case 13b and Case R demonstrate.

**Consequence, already acted on:** the J0→J1→J2 filesystem-telemetry ladder was **not
built** in this run. The unresolved question is not whether process/file telemetry exists.

## Wayland protocol architecture — MEASURED, not cited

Recorded as a measurement of this project rather than a literature claim.

- **No Wayland protocol lets one client enumerate another client's surfaces.** Cross-client
  enumeration in the Wayland arm was available **only** through sway's private IPC
  (`swaymsg -t get_tree`). A recorder built on it is a *sway* recorder, not a *Wayland*
  recorder.
- The compositor observes the owning client pid as a **first-class field**, with no
  `_NET_WM_PID` equivalent to fall through. This is a genuine improvement in *directness*
  over X11's X-Resource correlation, at the cost of standardisation.
- **`app_id` is client-asserted.** Measured: an attacker-run GTK3 process obtained
  `app_id = "eog"`, byte-identical to the genuine viewer's. Wayland's identity string is not
  a higher trust plane than X11's `WM_CLASS`.

**Non-claim:** Wayland's screen-capture mediation is **not new** and is not claimed as a
contribution. What is reported is a measurement of what it does and does not bind.

## xdg-desktop-portal ScreenCast / Screenshot — MEASURED

Against `xdg-desktop-portal` + `xdg-desktop-portal-wlr`, ScreenCast **version 4**:

- `AvailableSourceTypes = 1` → **MONITOR only; WINDOW not offered; VIRTUAL not offered.**
- `org.freedesktop.portal.Screenshot` — **interface absent** on this backend.
- `SelectSources` accepted `types = MONITOR|WINDOW` and returned success while the backend
  enumerated **outputs**; the WINDOW bit was silently ineffective.
- The only identity the portal logs is the **requesting** app's id (empty for an
  unsandboxed caller). The API's identity concept describes the *caller*, never the
  *captured content*.

**Scope:** one backend. **GNOME and KDE portals implement window capture and were not
tested.** No claim is made about them.

## PipeWire capture flow — BLOCKED

The `ScreenCast` session reached `Start` and failed with `wlroots: unable to receive a valid
format from wlr_screencopy` — PipeWire buffer-format negotiation on a headless, software
-rendered container with no DRM device. **Stream property contents were never observed and
are not inferred from documentation.** Recorded BLOCKED.

## Re-checked, unchanged

- **Agent Flight Recorder** (arXiv:2609.01931) — hash-chained tamper-evident agent event
  logs. Still occupied; still assumes the recorder faithfully observes honest actions. The
  13b classification sharpens *why* that assumption is load-bearing: AFR protects the record,
  and 13b failed because a **write was never observed**, not because a record was altered.
- **C2PA / Content Credentials** — unchanged. Authenticates the capture pipeline, not the
  depicted scene. Case R is a direct illustration: a genuine viewer, a genuine compositor
  frame, and attacker-authored bytes.
- **Trusted path / trusted display** — unchanged and decades old. The Wayland result is a
  *measurement* of one such architecture, not a new mechanism. Must be cited if the project
  ever escalates to trusted display.

## Explicit non-claims, extended

Added to the existing list, we do **not** claim novelty for:

- eBPF or kernel-level provenance;
- runtime provenance graphs;
- Wayland's screen-capture mediation or compositor isolation;
- content provenance or signed media;
- portal-based capture permission models.

## The candidate contribution, restated after Phase J

> **Measurement of which visual-evidence provenance bindings survive or fail under different
> observation policies, inference policies, and desktop trust architectures.**

Status: **INFERENCE supported by three measured witnesses**, not a theorem.

What is new is not a mechanism. It is that the six bindings were separated, and each was
measured against (a) a stated observation policy, (b) a stated inference policy, and
(c) two desktop trust architectures — producing the specific negative result that the
`process/client → displayed resource` edge fails identically on both, and that changing the
platform's trust architecture moved **zero of twelve** binding evidence levels.
