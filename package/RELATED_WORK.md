# Related Work

Organised by **problem layer**, not as a paper list. For each source: what it solves, what it
does **not** claim, and its exact relation to this work.

A standing rule, applied throughout: **do not manufacture novelty by describing prior systems
narrowly.** Where a prior system does something well, that is recorded as occupied territory,
and where one independently arrived at a discipline we also use, that is recorded as
*reducing* our novelty claim.

---

## A. Procedural agent traces

### ProcGrep — arXiv:2606.16988

**Solves.** Procedural fingerprinting of agent behaviour — recognising *how* an agent went
about a task from its trace.

**Does not claim.** Visual perception or scene modelling. The implementation's atom vocabulary
was inspected in an earlier audit and contains no explicit visual-perception atom.

**Relation.** Adjacent and untouched. This project deliberately made no ProcGrep
modifications. Procedural structure is a different question from whether a delivered image
depicts the target's state.

## B. Trajectory evaluation and reward hacking

### WeaveBench — arXiv:2606.09426v3

**Solves.** A hybrid GUI+CLI agent benchmark with an LLM/VLM judge that detects fabricated
visual evidence and hard-coded metrics, including a zeroing rule; its graders call
`vlm_score_rubric` to confirm target UI visibility.

**Does not claim.** Deterministic, capture-time attribution. Its judge reads the same
trajectory and deliverables it evaluates.

**Relation — and a methodological constraint we had to obey.** WeaveBench supplies the corpus
for all retrospective results here. Its judge emits `is_hack`, `hack_confidence`,
`hack_patterns`, `hack_evidence_quotes`, `dimensions.evidence_authenticity` and per-artifact
`fake_signal` — **correlated outputs of one evaluator apparatus, not independent labels**. We
used them for candidate localisation and validation sampling only. *Detection* of fabricated
visual evidence is occupied; deterministic *attribution* is the open question.

One consequence worth stating: our structural instrument reached a substitute-lineage
conclusion on a record the judge scored `is_hack = False`. That is not evidence the judge is
wrong — it is evidence the two instruments measure different things.

### AgentRewardBench — arXiv:2504.08942

**Solves.** Evaluation of reward models and judges for agent trajectories.

**Does not claim.** Anything about display state or capture provenance.

**Relation.** Establishes that judge reliability is itself a research object — which is why
this project refused to treat judge output as ground truth.

## C. Post-hoc agent provenance and causality

### AgentTrails — arXiv:2607.18816

**Solves.** An Activity/Entity provenance graph over agent execution with
`generatedBy` / `usedBy` / `informedBy` relations across tool-calling traces.

**Does not claim.** Scene, window, or process-identity modelling.

**Relation.** Occupies generic structural agent provenance. **This project claims no novelty
there.** Its graph would represent "the agent wrote `proof.png`" perfectly and would say
nothing about what was on screen when the capture happened.

### PROV-AGENT — arXiv:2508.02866

**Solves.** W3C PROV modelling for agentic workflows.

**Does not claim.** Visual or GUI-state modelling.

**Relation.** Same layer as AgentTrails. Standardised provenance vocabulary is occupied.

### CHIEF — arXiv:2602.23701

**Solves.** Hierarchical causal graphs for failure attribution in agent systems.

**Does not claim.** Adversarial evidence generation; assumes failures rather than fabrications.

**Relation.** Causal-graph territory is occupied. Our adversary is not failing — it is
succeeding at producing passing evidence.

### AgentProvenance — `ByteYellow/AgentProvenance` @ `fc2e62647dc64b6d23144b88e0e0ac101b4f2793`

**The most directly relevant prior system, and the one that most constrains our claims.**
Pinned and verified at that commit (379 tracked files; six files read in full; software **not
executed**).

**Solves — verified at the pinned revision:**

| Capability | Evidence |
|---|---|
| three-axis evidence graph: model intent + application context + runtime telemetry | `README.md` |
| process / file / network / runtime provenance (`execve`, `file_open`/`file_write`, `network_connect`, `process_exit`, `setuid`, `ptrace`, `file_rename`, `file_unlink`, `tls_write`/`tls_read`, `dns_query`) | `docs/telemetry-schema.md` |
| native eBPF telemetry, marked **IMPLEMENTED**, with compiled BPF objects | `docs/ebpf-sensor-plan.md`, `internal/sensor/`, `cmd/agentprov-sensor` |
| pid / tgid / ppid / cgroup / container correlation, with **graded confidences** (0.98 cgroup+window, 0.92 container+window, 0.85 pid+window) and an `abnormal_process_tree` signal | `docs/telemetry-schema.md` |
| content-addressed, hash-verifiable evidence (`DigestSHA256`, in-toto-style subject digests) | `internal/attest/attest.go` |
| **explicit, ingest-enforced separation of runtime identity from application-asserted context** | `docs/telemetry-schema.md` |

**Does not claim.** No generic visual-display/scene provenance mechanism was found in the
inspected pinned repository surface: `compositor` and `wayland` return **zero** hits;
`screen capture`, `display server` and `window manager` return zero in source and docs; the two
`screenshot` hits describe the project's own dashboard documentation images; all four `x11`
hits are false positives. **This is not a claim that AgentProvenance cannot capture
screenshots** — it is a statement about what a term-based search plus targeted reading found at
one revision, and the software was not executed.

**Relation — two directions, and the second is uncomfortable:**

1. **It occupies the runtime layer completely.** Process/file/network provenance, eBPF
   collection and content-addressed evidence are not open problems, and this project neither
   rebuilds them nor claims them. This is precisely why the filesystem-telemetry ladder was
   **not built** in the final phase.
2. **It independently enforces two disciplines we also use**, which *reduces* our novelty
   claim on both: runtime identity must not be conflated with application-asserted context
   (their schema enforces this at ingest, "without pretending the kernel knows agent-level
   identifiers"), and correlation carries explicit graded confidence rather than a boolean.
   Convergent design by an independent team is evidence the disciplines are right and evidence
   they are **not ours**.

What it does not reach is the edge we measured failing: `process/client → displayed resource`.
Knowing which process wrote which file, and which process owns which surface, does not
establish which resource a legitimate renderer had on screen. That is exactly case 13b and
platform Case R.

## D. Tamper-evident audit records

### Agent Flight Recorder — arXiv:2609.01931

**Solves.** Hash-chained, tamper-evident agent event logs.

**Does not claim.** That the recorded actions are honest — AFR's own threat model assumes the
recorder faithfully observes honest actions.

**Relation.** Occupies Tier F of our contract entirely; we claim no novelty for hash-chained
logs. Our 13b result sharpens *why* AFR's assumption is load-bearing: **13b failed because a
write was never observed, not because a record was altered.** Tamper-evidence protects the
record. It does not protect the claim.

> A cryptographically perfect, TEE-attested record of "the agent's fake window was on top" is
> a perfect record of a fabrication.

## E. Rendering and verification loops

### RILA — arXiv:2609.02088 · LongHorizon-Harness — arXiv:2608.01964

**Solve.** Verification and rendering interventions inside the agent loop — checking or
re-rendering during execution.

**Do not claim.** Post-hoc attribution of delivered evidence, or an adversarial evidence
generator.

**Relation.** A different lane: intervene during execution versus audit afterwards. Our
finding that the binding must be recorded *when the read happens* is, if anything, an argument
for their lane — but we did not test it.

## F. Content provenance

### C2PA / Content Credentials

**Solves.** Cryptographically binding *who produced a media file and how it was edited*,
authenticating the capture pipeline.

**Does not claim.** Truthfulness of the depicted scene.

**Relation.** The sharpest illustration in this package: **a C2PA-signed screenshot of an
agent-authored fake window is a valid C2PA manifest of a fabrication.** Case R is exactly
that shape — a genuine viewer, a genuine compositor frame, attacker-authored bytes. Content
provenance and scene provenance are orthogonal, and we claim no novelty in the former.

## G. Display mediation and trusted-path architecture

### X11, Wayland, xdg-desktop-portal, PipeWire

**Solve.** Wayland provides client isolation and compositor-mediated capture; `xdg-desktop
-portal` provides a permissioned capture API; PipeWire carries the stream.

**Do not claim.** Resource, content, or application-state provenance. The portal's identity
concept describes the **requesting** application, never the captured content.

**Relation — measured here rather than cited.** Against the tested backend
(`xdg-desktop-portal-wlr`), ScreenCast v4 advertised `AvailableSourceTypes = 1` — **MONITOR
only**, no window source — and the `Screenshot` interface was absent. Cross-client enumeration
existed only through compositor-private IPC. `app_id` proved client-asserted and spoofable
exactly as `WM_CLASS` is.

**Wayland's screen-capture mediation is not new and is not claimed as a contribution.** What is
reported is a measurement of what it does and does not bind — and a scope caveat that matters:
the specification supports WINDOW sources where a backend implements them, and **GNOME and KDE
backends do and were not tested.**

### Trusted path / trusted display literature

**Solves.** Spoof-resistant screen regions, secure attention keys, trusted display paths —
Orange Book era onward.

**Does not claim.** Anything about agent-produced evidence or post-hoc audit.

**Relation.** Decades old and directly relevant if this problem ever escalates to a trusted
-display solution. **Trusted display and anti-spoofing mechanisms are not novel** and must be
cited if that escalation happens. Our Wayland result is a *measurement of one such
architecture*, not a new mechanism.

---

## Explicit non-claims

We claim **no novelty** for any of:

- provenance graphs over agent traces;
- PID / process / file / network telemetry for agents;
- eBPF collection or kernel-level provenance;
- runtime provenance graphs;
- window or screen recording;
- tamper-evident or hash-chained logs;
- content provenance or signed media;
- Wayland's screen-capture mediation or compositor isolation;
- portal-based capture permission models;
- trusted display or anti-spoofing UI;
- trust-plane separation, or graded-confidence correlation — **both independently present in
  AgentProvenance at the pinned commit**.

## The candidate contribution

> **Measurement of which visual-evidence provenance bindings survive or fail under different
> observation policies, inference policies, and desktop trust architectures.**

Classified **INFERENCE**, supported by measured witnesses, and deliberately not a mechanism.

What is new is not a system. It is that the six bindings were **separated** and each measured
against (a) a stated observation policy, (b) a stated inference policy, and (c) two desktop
trust architectures — producing the specific negative result that `process/client → displayed
resource` fails identically on both, and that changing the platform's trust architecture moved
**zero of twelve** binding evidence levels.

The prior-art sweep did not find work that simultaneously (i) records or reasons about display
composition at capture time for a computer-using agent, (ii) models the agent as an
**adversarial evidence generator** rather than an honest actor, and (iii) measures false-accept
rates per attestation tier. AFR is closest on record integrity, C2PA on media, trusted path on
display, AgentProvenance on runtime, WeaveBench on detection — none combines the three.

**That gap statement remains a HYPOTHESIS**, bounded by a prior-art search that is not
exhaustive (see [`LIMITATIONS.md`](LIMITATIONS.md) §14).
