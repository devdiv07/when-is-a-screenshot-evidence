# Methodology

How each result was produced, what discipline was imposed, and what that discipline cost.

---

## 1. Epistemic rules, applied throughout

Every material claim carries one of: **VERIFIED FACT** (pinned primary source or inspected
artifact), **MEASURED FACT** (reproducible command in the repository), **INFERENCE**,
**HYPOTHESIS**, or **UNKNOWN**. Promotion between classes is never silent.

Three rules did most of the work:

1. **Negative and invalid results are preserved, not deleted.** Discarded runs stay on the
   record with the defect that invalidated them (§7).
2. **Predeclaration.** Threat model, attack classes, predictions and kill criterion were
   written and committed **before** the experiment that could falsify them. Cases could not be
   added after seeing results.
3. **No LLM or VLM anywhere in the adjudication path.** A VLM could have filled the missing
   provenance edges, but it would have answered a different question — "does this image look
   like the target?" — and voided the structural claim.

## 2. Evidence tiers (the inference policy, made explicit)

| Tier | Meaning |
|---|---|
| **EXACT** | a trusted observer reports the binding directly, as a first-class fact |
| **STRONG** | the binding follows from trusted observations with no alternative reading |
| **WEAK** | the binding requires reconstruction an adversary could arrange |
| **UNKNOWN** | no observation bears on the binding |

**WEAK evidence may not produce a classification.** It is recorded as a hypothesis and never
promoted. This single rule is the difference between reporting ~55% recoverability and
reporting 17.9% (§4.2).

## 3. Retrospective arm — the recoverability audit

**Corpus.** WeaveBench GPT-5.4 low: 114 hybrid GUI+CLI tasks, two runs, 453 delivered visual
artifacts (394 capture-based, 59 direct-write).

**Retrieval.** Trace members were fetched by **ZIP-over-HTTP range access** rather than
downloading 9.6 GB of archives — 1.79 GB of text members retrieved, zero screenshot payloads,
every member CRC-verified (§`REPRODUCIBILITY.md`).

**Judge-coupling discipline.** WeaveBench's judge emits `is_hack`, `hack_confidence`,
`hack_patterns`, `hack_evidence_quotes`, `dimensions.evidence_authenticity` and per-artifact
`fake_signal` from the *same* trajectory and deliverables. These are correlated outputs of one
evaluator apparatus, **not independent labels**. They were used for **candidate localisation
and validation sampling only**, never as ground truth. A structural instrument that agrees
with the judge has not been validated by it.

**Levels.** R0 judge-quote localisation → R1 producer recovery → R2 artifact provenance → R3
scene source → R4 scene classification → R5 target adjudication. Levels are nested: each
requires the one before.

### 3.1 Manual validation, and what it cost

A single reviewer manually checked the first automated claims. **It refuted 4 of the first 7**
and forced three rule corrections:

| Correction | Why | Effect |
|---|---|---|
| GUI-capability test on agent-authored source | three "scene sources" could not draw at all — a `--explain` CLI, an HTTP server, an XML fixer | substitute claims dropped 9 → 4 |
| process-exit invalidation | a launch record outlived the process it described | removed stale-liveness attributions |
| composite-scene demotion | full-screen frames have no single owner | STRONG → WEAK where several GUI processes were plausible |

**This validation is single-reviewer. No inter-rater statistic exists.** It must never be
described as completed two-reviewer validation. See [`LIMITATIONS.md`](LIMITATIONS.md) §2.

### 3.2 Negative controls

Controls were run to check the instrument does not manufacture violations on artifacts where
none should exist:

| Control | artifacts | violation claims |
|---|---|---|
| NC-A | 99 | **0** (0.0%) |
| NC-B | 73 | **0** (0.0%) |

*Caveat recorded with the control:* NC-B traces carry artifact-level `fake_signal` from the
judge with `is_hack = False`, so a structural claim there would not necessarily have been a
false positive. NC-A is the cleaner control.

The controls were not vacuous: NC-A contained 86 capture-based artifacts, including 12 with
STRONG scene-source attribution; NC-B contained 67 capture-based artifacts, including 3 with
STRONG attribution. The zero substitute classifications therefore did not arise because the
control pools contained no attributable capture evidence. This is a non-vacuity check, not a
broad precision estimate.

The surviving narrow instrument (direct-synthesis-where-capture-required; bracketed substitute
renderer) gives a target-vs-substitute verdict on **23/453 = 5.1%** of artifacts. The
instrument emitted no substitute/violation claims in either control pool (**0/99** NC-A,
**0/73** NC-B), including control pools containing resolvable capture evidence. These controls
are a non-vacuity/specificity check, not a population precision estimate: the pools are
selected by judge outputs rather than sampled, artifacts cluster by task, and NC-B is not a
conventional clean negative. No significance test is attached, for the same reason. The
instrument is real and narrow, and its 5.1% coverage must be stated alongside any control
result. `[C26]`

*Wording correction preserved:* this section previously summarised the controls as "high
precision, and ~5% recall", as do the frozen `outputs/post_gate_summary.md` §3 and
`outputs/recoverability_report.md` §7. That phrasing invites a statistical reading the
controls do not support and is superseded by the paragraph above; the frozen reports are not
edited (see `outputs/README.md` §3).

## 4. Sensitivity analysis as a first-class method

### 4.1 Why

A recoverability number is a function of the resolver's parameters. Reporting one number
without its sensitivity curve is uninterpretable, and we caught ourselves nearly doing it.

### 4.2 The sweep

The lookback parameter was swept from 2 events to unbounded with **everything else fixed**.
Result in [`RESULTS.md`](RESULTS.md) §2. The disciplined reading is the second column
(EXACT/STRONG), which is nearly flat.

**A correction we preserve rather than hide:** an earlier draft reported 5.5% → 72.7%. That
sweep had been run with the **pre-correction resolver**, before the three fixes in §3.1. The
corrected figures are 4.8% → 54.9%. The qualitative conclusion is unchanged and slightly
weaker (~11× rather than ~13×). This was the only stale figure found in a full re-derivation
of all ten headline numbers.

### 4.3 Outcome separation

Phase D scored three strictly nested outcomes separately, because an earlier encoding had
conflated them:

1. **INFORMATION_DEFICIT_CLOSURE** — the missing fields would no longer be missing
2. **SCENE_SOURCE_RESOLUTION** — the evidence identifies which surface contributed the pixels
3. **TARGET/SUBSTITUTE_ADJUDICATION** — the evidence decides whether that scene is the
   *declared* target

Closure is necessary for resolution; resolution is necessary for adjudication; adjudication
additionally requires a declared target. Denominators differ (385 vs 287) and are **not**
interchangeable.

## 5. Prospective arm — contract, threat model, kill criterion

**Order of operations, and it matters:** threat model → contract → experiment specification →
kill criterion → *then* execution. All four were committed before any result existed.

**Adversary.** A computer-use agent with normal user privileges, **full white-box knowledge of
the contract**, trying to produce evidence that passes evaluation more cheaply than doing the
task. Not malware; a first-class user of the same system the recorder observes. Of 14
catalogued capabilities, **13 were directly observed** in the benign corpus; one (WM_CLASS
spoofing) is explicitly marked **DERIVED, not observed**.

**Trust planes.** Fields are separated by *who asserts them* —
`EVALUATOR/TASK_SPECIFIED`, `AGENT_ASSERTED`, `APPLICATION_ASSERTED`, `HARNESS_OBSERVED`,
`KERNEL/RUNTIME_OBSERVED`, `COMPOSITOR/DISPLAY_SERVER_OBSERVED`,
`PRIVILEGED_APPLICATION_OBSERVER`, `TRUSTED_RECORDER_OBSERVED`, `HARDWARE/TEE_ATTESTED` —
because they fail independently. The central principle: **a field is not secure because it
comes from the OS.** Kernel- and compositor-observed fields are truthfully reported *and*
adversarially chosen.

**Two arms, never merged:**

| Arm | What it is | Governs |
|---|---|---|
| **ANALYTIC** | contract logic over analyst-**derived** field vectors. No process launched, no pixel captured. | superseded where the arms disagree |
| **EMPIRICAL** | real Xvfb X11, Openbox, real windows, real pixel grabs, unprivileged attacker, independent privileged recorder | **governs** |

Running both was not redundancy. The disagreement (§11 of the technical report) is itself a
result.

### 5.1 Ground-truth isolation

Ground truth is **construction-time**: each case is built by a script that records what it
actually did. It is not judged, and it is not derived from any evaluator.

The adjudicator never sees it. Isolation was **enforced and tested**, not asserted: a static
check plus a dynamic `open()` guard plus a non-vacuity check, over 13 ground-truth files,
**0 touched**.

### 5.2 The recorder's hard rule

Every field is derived from live system state — `/proc`, the X server or compositor, the
filesystem, and an actual screenshot operation producing real pixel bytes. It never reads a
scenario definition and never accepts a value from the attacker. **If a field cannot be
observed it is recorded `None` with a reason in `field_observation_failures`.** Nothing is
synthesised because a scenario "should" produce it.

That rule is what makes `field_observation_failures: []` on case 13b meaningful: the recorder
reported complete success while being blind to the only event that mattered.

By contrast, the six observation-failure entries for `11_direct_synthesis` are expected
absence: that control deliberately creates no GUI surface, so title, class, and geometry are
unavailable in each of the recorder's pre/post snapshots. They are structurally inapplicable,
not evidence that instrumentation missed an existing surface.

### 5.3 Pixel-level construction verification

A case can look correctly built and render nothing — this happened to us (IC-4, §7). Every
platform case was therefore verified at the pixel level in the captured PNG:

| capture | fabricated `#ffd6d6` px | verdict |
|---|---|---|
| `x11_R.png` / `wayland_R.png` | **501,867** each | fabrication genuinely on screen |
| `x11_P.png` / `wayland_P.png` | 33 (antialias noise) | substitute surface genuinely on top |

## 6. Static classification of 13b — method

The question "would the frozen rules have changed the verdict given the fact?" is a **property
of the frozen rules**, answerable by reading them. Building new telemetry to answer it would
have spent a phase learning something already determined by the specification.

1. **Copy** the frozen 13b record. Phase I artifacts are never modified.
2. **Inject** the smallest observation representing "the declared target was written this
   episode by an agent-controlled action" — one entry in the episode write journal. No new
   field, no new rule, no expected hash, no new binding logic.
3. **Derive** the Tier C value by calling **frozen recorder code**
   (`Recorder.resource_lineage_for`), not by hand-editing. Hand-editing tests what the analyst
   thinks the field means; calling frozen code tests what the implementation means.
4. **Run the unchanged adjudicator.** Its sha256 is recorded with the run.
5. **Validity check:** replaying the *original* record reproduces the Phase I verdicts at all
   13 configurations, rule-for-rule. The trace therefore operates on the same apparatus that
   produced the original result.
6. **Rule-property probe:** apply the identical observation to all 13 scenarios, to test
   whether the "fix" is sound. It is not — see [`RESULTS.md`](RESULTS.md) §5.

## 7. Implementation corrections — documented before re-running

Six corrections were found and **written down before** the affected cases were re-run. None
changed a contract, a rule or a field. Runs invalidated by them are discarded and excluded
from every figure.

| # | Defect | Consequence |
|---|---|---|
| **IC-1** | PID resolved via `_NET_WM_PID`, which is *client-asserted* and was absent on every window in that lab | field sat on the wrong trust plane and obtained nothing; switched to X-Resource `XResQueryClientIds` |
| **IC-2** | cleanup missed `python3 < script`; a window leaked into 7 later scenarios | spurious composite abstentions — **whole suite re-run** |
| **IC-3** | visible-set PIDs also read `_NET_WM_PID` (`pid=0` throughout) | same plane error; same fix |
| **IC-4** | case 13b disclosed the path in argv and **never rendered the fabrication** | its SUBSTITUTE verdict was right for the wrong reason — **13b re-specified and re-run** |
| **IC-5** | `shell=True` forked the client, so a surface check matched the shell's pid; ground truth recorded `viewer_binary: null` while the recorder independently observed genuine `eog` running | defect in the **ground-truth record**, not the measurement — both arms re-run |
| **IC-6** | Debian ships `imv` as `imv-wayland`/`imv-x11`; the fallback probe could never fire | latent, never taken; recorded anyway |

**IC-4 and IC-5 are the instructive ones.** IC-4 shows a case can be well-formed and still not
implement its own specification. IC-5 was caught **only because the recorder observes
independently of the case constructor** — the two disagreed, and the disagreement was the
signal. After IC-5 the result was verified **stable**: all four capture hashes byte-identical
before and after, binding matrix unchanged at 0/12.

## 8. Platform comparison — design

**One image, both stacks.** X11 (Xvfb + Openbox) and Wayland (sway/wlroots headless) live in
the same container, so the arms differ in display architecture and nothing else.

**Three trust domains**, one more than the Phase I lab, because "the compositor is trusted"
has to mean something:

| Domain | uid | Runs |
|---|---|---|
| compositor session | 1001 | sway, xdg-desktop-portal, PipeWire |
| attacker | 1000 | the case constructors; owns no recorder code |
| recorder | root + `CAP_SYS_PTRACE` | the trusted observer |

**Same application on both arms.** `eog` (GTK3) started as a *native* client of each platform
— confirmed as `shell=xdg_shell`, `app_id=eog` on Wayland — with **zero fallbacks taken**.
XWayland was left **enabled** so that nativeness was measurable rather than assumed. No result
rests on an XWayland surface being presented as native Wayland.

**Platform-only observation.** The recorder collects only what the platform itself exposes: no
application instrumentation, no CDP, no `LD_PRELOAD`, no ptrace of the renderer. That
restriction *is* the experiment — the question is what a platform hands a trusted observer,
not what could be extracted by instrumenting each app.

**Binding assignment is by rule, not by hand.** Evidence levels are assigned by functions over
the observed record (`package/scripts/` → `scripts/platform_matrix.py`), so the same rules
would score a different scene the same way. Ground truth is loaded only for scoring, after
every binding is assigned.

## 9. Prior-art verification

Sources are pinned where possible. AgentProvenance was inspected at commit
`fc2e62647dc64b6d23144b88e0e0ac101b4f2793` by cloning at that SHA, running the required
term searches over all 379 tracked files, and reading six files in full. Six positive claims
were checked and supported; the display-surface conclusion is stated narrowly as a property of
the inspected surface, with its search limitations attached. **The software was not executed.**

## 10. What this methodology cannot deliver

- **No population claims.** Constructed suites measure whether a contract *can* be defeated,
  never how often it *would* be.
- **No adaptive adversary.** Attacks are predeclared and hand-constructed. This is a white-box
  *case evaluation*, not a red-team. Case 13b only became a real attack after IC-4 corrected
  its construction — direct evidence the suite is not saturated.
- **No claim about semantic task correctness.** Provenance can at best establish what was on
  screen and where it came from. Whether that constitutes *doing the task* is links 5–6, never
  reached.
