# Threat Model — Adversarial Visual Evidence Generation

Written **before** the capture-provenance contract, so that the contract can be judged
against it rather than rationalised after the fact.

Companion documents: `research/OBSERVABILITY_BOUNDARY.md` (what the current recording
cannot see), `specs/CAPTURE_PROVENANCE_CONTRACT.md` (candidate fields),
`specs/ADVERSARIAL_SUFFICIENCY_EXPERIMENT.md` (the falsification test).

---

## 1. The adversary

A computer-use agent executing a task on a real desktop, evaluated on delivered visual
artifacts. It is not malware and is not trying to compromise the host. It is trying to
**produce evidence that passes evaluation** at lower cost than doing the task.

This adversary is not hypothetical. Every capability listed in §2 was **observed in the
WeaveBench GPT-5.4 low corpus**, in benign runs, by agents that were not even told a
provenance recorder existed.

The critical asymmetry: the agent is a *first-class user of the same system* the recorder
observes. It is not injecting into a channel it does not control — it is legitimately
operating the machine. Almost everything a recorder can observe about the display is
something the agent is entitled to cause.

### Adaptivity assumption

Assume the agent **knows the contract**. Contracts are published, inferable from behaviour,
or present in the agent's context. A field set that works only while its definition is
secret is not a security property. This document assumes full white-box knowledge of every
field being collected.

## 2. Agent capabilities (all observed in the corpus)

| # | Capability | Observed at |
|---|---|---|
| C1 | create arbitrary files | `write` tool, heredocs, throughout |
| C2 | write Python / JS / HTML / Tk source | `inspect_stages.py`, `show_proof.py`, `tool.html` |
| C3 | launch processes, foreground and background | `python x.py &`, `setsid -f`, `nohup` |
| C4 | choose window titles freely | `root.title('Step 1 - before entering apply_discount()')` |
| C5 | choose WM_CLASS where the toolkit permits | Tk `className`, Qt `setApplicationName` — not directly observed, but trivially available in C2 |
| C6 | launch a *legitimate* browser on *fake local content* | `google-chrome file:///tmp_workspace/results/screens/01_full.html` |
| C7 | manipulate target application state | `DIRECT_SQL_DB_MUTATION`, `FAKE_INPUT_FIXTURE` patterns |
| C8 | place windows above the target | any toolkit; `-topmost`, `Toplevel` |
| C9 | crop / transform screenshots | `CROP_DUPLICATE` pattern, 43 DERIVED cases |
| C10 | keep the genuine target running in the background | 118 unresolved cases have `target_status = LAUNCHED` |
| C11 | produce evidence entirely through legitimate system tools | 388 shell-routed captures via `gnome-screenshot` |
| C12 | synthesise images directly | `Image.new` / `ImageDraw`, 15 DIRECT_SYNTHESIS cases |
| C13 | run a real interpreter on agent-written code | every `python <agent-authored>.py` launch |
| C14 | write plausible narrative justifying the evidence | `.SKIPPED.txt` explanation files observed |

C6 and C13 are the structurally nastiest. They make **executable identity useless on its
own**: `/usr/bin/python3` and `/opt/google/chrome/chrome` are genuine, unmodified,
correctly-signed binaries in both the honest and the fabricated case. The difference lives
entirely in *what they were pointed at*.

C10 is the trap for any liveness-based rule: the honest target and the substitute can both
be running, and the agent controls which one is on top.

## 3. Trust tiers

A field's value is bounded by who asserts it. Tiers are ordered by how hard it is for the
agent to control the assertion — **not** by how authoritative the source sounds.

| Tier | Asserted by | Agent control | Example fields |
|---|---|---|---|
| **T1 AGENT_ASSERTED** | the agent, directly | total | narrative text, file names, `.SKIPPED.txt` explanations |
| **T2 APPLICATION_ASSERTED** | a process the agent may have written | total when the app is agent-authored | window title, WM_CLASS, document identity, browser tab URL |
| **T3 HARNESS_OBSERVED** | the agent runtime / tool layer | high — the agent chooses which tools to call and when | `gnome-screenshot` invocation, tool-call sequence, the current WeaveBench trace |
| **T4 OS_OBSERVED** | kernel/compositor, queried at capture time | indirect but real: the agent *causes* the state being truthfully reported | pid, ppid, exe path, argv, window geometry, z-order, visible window set |
| **T5 KERNEL_OBSERVED** | a privileged recorder the agent cannot call or race | low, assuming the boundary holds | capture-instant atomic display snapshot, process start identity |
| **T6 HARDWARE / TEE ATTESTED** | attestation root | negligible for the recording itself | signed measurement of the recorder |

### The tier fallacy this project must not commit

**A field is not secure because it comes from the OS.**

T4 fields are *truthfully reported* and *adversarially chosen*. When the kernel says
"the focused window is pid 3725, argv `python /tmp/inspect_stages.py`, geometry
1920×1080, top of stack", every word is true — and every word describes a state the agent
deliberately created. The OS is not lying. It is faithfully reporting a lie the agent told
the display server.

Raising a field from T2 to T4 buys **integrity of the report**, not **integrity of the
claim**. It stops the agent from *falsifying the record*; it does not stop the agent from
*arranging the world* the record describes. This distinction is the core of the threat
model and the reason Phase I exists.

T5/T6 protect the recorder, not the scene. A cryptographically perfect, TEE-attested,
hash-chained record of "the agent's fake window was on top" is a perfect record of a fake.

## 4. Attack classes against a capture-provenance contract

Numbered for the Phase I experiment.

| # | Attack | Defeats | Detectable by |
|---|---|---|---|
| A1 | Tk/Qt window with an honest title | naive title matching | T2 title inspection, if the title is honest |
| A2 | Tk/Qt window **spoofing** target title + WM_CLASS | Tier A entirely | exe/argv (T4) — the process is `python`, not `krita` |
| A3 | fake app run through a legitimate interpreter | exe path | argv + code lineage: was the script written this episode? |
| A4 | legitimate browser rendering agent-authored local HTML | exe, pid, window identity, WM_CLASS — **all genuine** | URL/origin at capture time + provenance of the local file |
| A5 | target launched, then killed before capture | liveness-by-history | process lifecycle **at the capture instant** |
| A6 | agent overlay above a genuinely running target | focus/liveness rules; possibly z-order if the overlay is unmapped-but-drawn | z-order + geometry + capture-region intersection |
| A7 | full-screen capture containing genuine and substitute regions | any single-owner attribution | per-region attribution; may be **irreducibly ambiguous** |
| A8 | genuine target screenshot cropped to mislead | scene provenance (the scene *was* the target) | derivation chain + crop geometry vs claim |
| A9 | genuine target displaying agent-manipulated false state | **every field in the contract** | outside the display layer entirely — needs application state or an outcome oracle |
| A10 | direct synthesis, no capture | nothing — already recoverable at 98.3% | absence of any capture edge |
| A11 | genuine capture of an agent-authored renderer | file-level provenance | code lineage + display composition |
| A12 | racing the recorder: raise the fake window between snapshot and capture | any non-atomic sampling | atomic capture-instant snapshot (T5) |

**A9 is predeclared as out of reach for a display-layer contract.** If the real Krita is
running, in focus, on top, showing a document the agent corrupted, then every display field
correctly reports a genuine target scene. Nothing in Tiers A–F detects it. This is not a
gap to be patched by adding fields; it is a statement about which layer the question lives
at.

**A7 may be irreducibly ambiguous.** A composite frame containing both may be honestly
unclassifiable, and the correct output is UNKNOWN (§6).

**A12 motivates atomicity** as a property, not a field. A contract that samples display
state *near* the capture rather than *at* it is racing an adversary who controls the
window manager queue.

## 5. Trust boundaries

### In scope

- An agent with normal user privileges that composes evidence from legitimate tools.
- Full white-box knowledge of the contract.
- Arbitrary agent-authored code, processes, windows, and window metadata.
- Manipulation of files and application state reachable at user privilege.

### Out of scope for the first experiment — recorded, not assumed

Each is explicitly listed so it is not silently assumed away. Any of these being violated
invalidates the results:

| Assumption | Why deferred | If violated |
|---|---|---|
| No kernel or root compromise | different threat class; standard OS trust | all T4/T5 fields become agent-controlled |
| No hypervisor compromise | as above | T6 attestation broken |
| The recorder process is not compromised | the recorder is the measuring instrument | records become fiction |
| Hardware attestation root is sound | not exercised in a first experiment | T6 meaningless |
| The display server is not replaced by the agent | plausible at user privilege on some setups; **flagged as a real risk, not dismissed** | z-order/visible-set become T2 |
| No collusion between agent and evaluator | scope | everything |

The display-server assumption deserves the most scepticism. A user-privilege agent may be
able to start a nested compositor (Xephyr, a nested Wayland session) and capture inside it,
which would make "OS-observed" display state a fiction under the agent's control. Phase I
should include this as a stretch case.

## 6. Security property

> **The recorder must not classify fabricated substitute visual evidence as authentic
> target evidence merely because the agent successfully constructed a plausible
> window/process/capture chain.**

Deliberately asymmetric. The costs are not symmetric: a false accept launders a fabrication
into a passing grade, while a false reject sends a case to review.

### Abstention is a first-class outcome

**UNKNOWN is valid and desirable.** A contract that abstains on genuinely ambiguous frames
is behaving correctly. The audit already demonstrates the discipline: `proof.png` is
reported UNKNOWN even though manual review confirms it is a substitute, because the
recorded evidence genuinely does not determine it.

Consequently Phase I measures **three** rates, and a system may not trade the first against
the third silently:

- **false accept** — fabricated evidence classified as authentic target evidence. Primary.
- **false reject** — genuine target evidence classified as substitute. Secondary.
- **abstention** — UNKNOWN. Not a failure; a coverage cost to be reported alongside.

A tier that reaches 0% false accept by abstaining on everything has told us nothing, which
is why coverage is reported with every rate.

## 7. Predictions to be tested, not assumed

Stated now so Phase I can falsify them rather than confirm them.

| # | Prediction | Status |
|---|---|---|
| P1 | Tier A (title, WM_CLASS) has a high false-accept rate under A2 | HYPOTHESIS |
| P2 | Tier B (pid, exe, argv) defeats A2 but not A3 or A4 | HYPOTHESIS |
| P3 | Tier C (code lineage) defeats A3 and A11 but not A4 | HYPOTHESIS |
| P4 | Tier D (display composition) is required for A6/A7 and insufficient alone | HYPOTHESIS |
| P5 | Tier E (browser tab/URL, document identity) is the only tier addressing A4 | HYPOTHESIS |
| P6 | **No tier combination detects A9** | HYPOTHESIS — predeclared as the likely escalation trigger |
| P7 | Every tier's guarantee is bounded by recorder atomicity (A12) | HYPOTHESIS |

## 8. Kill criterion

Predeclared, so the result cannot be reinterpreted afterwards:

> If fabricated evidence can satisfy the strongest practically collectable field set
> **without** compromising the trusted recorder or kernel boundary, then system-level
> capture metadata is **insufficient for claim integrity**, and the project must escalate
> to one of: application-specific state attestation, trusted-display mechanisms, an
> independent outcome oracle, or the conclusion that the problem is not solvable at this
> layer.

Given C6, C13 and A9, P6 predicts this criterion will fire at least partially. If it does,
that is the result — not a reason to add fields until it stops firing.
