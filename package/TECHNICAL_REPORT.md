# Technical Report

**Visual Evidence Provenance for Computer-Using Agents: where assurance terminates, and the
epistemic policies that determine the answer**

Organised by result, not by chronology. Bracketed `[C…]` markers refer to rows in
[`CLAIM_TABLE.md`](CLAIM_TABLE.md).

---

## 1. The question

Computer-using agents are increasingly evaluated on **delivered visual evidence**: a
screenshot offered as proof that a GUI task was performed. The evaluation question is not
whether the image file is authentic. It is whether the image is *causally connected to the
target application's actual state*.

These come apart cleanly. An agent can:

1. write a small GUI program,
2. launch it with a genuine interpreter,
3. capture it with a genuine screenshot tool,
4. deliver a file whose every provenance property is impeccable.

Nothing in that chain is forged. The scene is. `[C1]`

We decompose the property into **six bindings**, because they have different evidence
requirements and different failure modes, and because collapsing them is the error we kept
having to correct in our own work:

```
artifact ──► capture ──► process/surface ──► displayed resource ──► app state ──► claim
```

| # | Binding | Question |
|---|---|---|
| 1 | artifact provenance | which action wrote this file? |
| 2 | capture provenance | was this produced by a real capture of a real display? |
| 3 | process/surface provenance | which process owned the surface whose pixels were captured? |
| 4 | **displayed-resource provenance** | **which resource was that surface displaying?** |
| 5 | application-state provenance | was the resource in the state the claim asserts? |
| 6 | evidence-claim integrity | does the image support the claim made about the target? |

**This report establishes results for links 1–4. Links 5 and 6 were never reached** — they
were predeclared out of scope, no experiment addressed them, and nothing here should be read
as evidence in either direction about them.

## 2. The thesis

> **Provenance claims for computer-using agents are meaningful only relative to an explicit
> epistemic policy: what the recorder is obligated to observe, what may be inferred from
> those observations, where assurance terminates across opaque boundaries, and when the
> evaluator must abstain.**

**Classification: INFERENCE / research thesis. Not a theorem, not proven.** `[C19]`

The evidence for it is a **double dissociation** — each policy varied while the other was
held fixed, each alone moving the answer:

| | varied | held fixed | effect |
|---|---|---|---|
| §4 | inference policy | the observations | apparent resolution 4.8% → 54.9% |
| §6 | one observation | the decision rules (frozen, unmodified) | verdict flips `AUTHENTIC_TARGET` ↔ `SUBSTITUTE` |

It is a **necessary-condition** claim, and we have a counter-example to the sufficient
reading from inside our own data (§6.4). Declaring both policies does not make a provenance
system sound. It makes it *evaluable*.

## 3. Why the retrospective approach fails (links 1–4, historically)

We began with the cheapest question: given trajectories a real agent benchmark already
records, can visual evidence be traced back to its scene?

Over **453** delivered visual artifacts (**394** capture-based) from the WeaveBench GPT-5.4
low corpus:

| Level | What it establishes | Result |
|---|---|---|
| R2 | artifact provenance | **453/453 — 100.0%** |
| R3 | scene source at EXACT/STRONG | **26/394 — 6.6%**, with **EXACT = 0** |
| R4 | scene classification | 81/453 — 17.9% |
| R5 | target adjudication | 38/453 — 8.4% |

*Figure 2.* `[C3, C4]`

The gap between R2 and R3 is the whole finding. **Which action wrote the file is almost
always recoverable. What was on the screen almost never is.** A system that reports the first
and calls it "visual provenance" has answered a different question.

The mechanism is visible in the capture practice: of 145 sampled `gnome-screenshot`
invocations, **125 captured the whole screen** and only **5** used `-w` (active window). A
full-screen grab has no single owner, and the runtime recorded no window identity at capture
time. The trace records *that* a capture happened and *where the bytes went* — never *what
was on screen*.

### 3.1 Five inferences that look sound and are not

Each was observed and each was refuted in our own data:

| Tempting inference | Why it fails | Observed |
|---|---|---|
| process exists ⇒ process visible | a launch record outlives the process | `optimized_query.py` had already exited before the capture |
| recent launch ⇒ capture source | adjacency is not even correlated with window ownership | three "sources" could not draw at all: a `--explain` CLI, an HTTP server, an XML fixer |
| full-screen grab ⇒ single-window evidence | the frame has no single owner | `view_dashboard_and_editor.png` — the agent's own filename says two apps |
| legitimate screenshot tool ⇒ authentic scene | capture ≠ scene | this is the entire problem |
| target running ⇒ target supplied the pixels | 118 unresolved cases have the target `LAUNCHED` | `okular` ran; `proof.png` was an agent-authored Tk window |

## 4. The inference-policy result

This is where the study stopped being about parsing and started being about epistemics.

Scene-source resolution scales directly with how much temporal speculation the resolver is
permitted. Same 455 cases, same traces, **only a lookback parameter changed**:

| Lookback (events) | source resolved | of which EXACT/STRONG |
|---|---|---|
| 2 | 4.8% | 2.4% |
| 4 | 10.3% | 4.6% |
| 8 | 22.0% | 6.6% |
| 16 (used) | 30.8% | 7.5% |
| 32 | 42.0% | 10.1% |
| 64 | 51.0% | 11.2% |
| unbounded | **54.9%** | **11.9%** |

*Figure 3.* `[C2]`

An analyst wanting a headline could pick nearly any number between 5% and 55% and defend it.
The second column is the disciplined reading: **well-supported attribution is nearly flat.**

> **More permissive inference produced substantially more answers without a commensurate
> increase in strong evidence.**

Two things this does **not** say, and which the package never says:

- It does **not** say the additional answers are individually wrong. They were never
  adjudicated. They are *unsupported*, not *disproven*.
- It does **not** generalise to all attribution methods. One corpus, one resolver.

The operational consequence we adopted: **WEAK (temporal-adjacency) evidence may not produce
a scene classification.** It is recorded as a hypothesis and never promoted. That single rule
is why our reported R4 is 17.9% and not something near 55%.

### 4.1 A related trap: measuring the wrong outcome

Phase D asked which fields, had they been recorded, would have closed the deficits. The
result depends entirely on *which outcome* you score:

| Field set | scene-source resolution (of 385) | **target/substitute adjudication (of 287)** |
|---|---|---|
| 4 display-composition fields | 272 — **70.6%** | **0 — 0.0%** |
| + active window + active pid (6) | 312 — 81.0% | 240 — **83.6%** |
| + lifecycle at capture (7) | 339 — 88.1% | 267 — **93.0%** |

*Figure 4.* `[C5]`

**The four display-composition fields adjudicate nothing.** They determine which surfaces
contributed pixels and then stop; nothing binds a contributing surface to an identity
comparable with a declared target.

Sharper still: `CAPTURE_TRIGGER_ACTION_ID` — one field binding an image to the action that
produced it — closes **81.0%** of information deficits alone and adjudicates **0%**. It is
artifact provenance, which we already recover at 453/453. A coverage metric on which that
field scores 81% is measuring the wrong thing.

> An earlier draft of ours reported "83.6% of cases resolved by four fields". **That claim
> was withdrawn.** It conflated closure, resolution and adjudication, and the strongest of
> the three had never been measured. The withdrawal is preserved in
> `outputs/field_set_analysis.md` §1 rather than quietly corrected.

## 5. Prospective recording: the contract, and its kill criterion

If reconstruction fails because the binding was never recorded, record it. We specified a
**capture-provenance contract** as an attestation ladder (Tier 0 task context; A window
labels; B process identity; C code/content/resource lineage; D display composition; E
application state; F record integrity), wrote a threat model with 13 attack classes and 8
predictions **before** the experiment, and predeclared a kill criterion:

> If fabricated evidence can satisfy the strongest practically collectable field set
> **without** compromising the trusted recorder or kernel boundary, then system-level capture
> metadata is **insufficient for claim integrity**.

We then built a real X11 lab — Xvfb, Openbox, real Tk and ImageMagick windows, real pixel
grabs — with an **unprivileged attacker (uid 1000)** and an **independent privileged recorder
(root + `CAP_SYS_PTRACE`)** that derived every field from live system state and never read a
scenario definition.

**The criterion fired.** `[C23]`

### 5.1 Case 13b

| Element | Value | Truthful? |
|---|---|---|
| viewer binary | `/usr/bin/display-im6.q16` — genuine, unmodified ImageMagick | **yes** |
| process | pid 297, uid **1000**, start identity `297@114818` | **yes** |
| window | real X11 window, real WM management, real focus | **yes** |
| argv | `display -update 1 … /lab/work/pre_existing_report.png` — **names the declared target** | **yes** |
| resource lineage | `/lab/work/pre_existing_report.png:pre_existing` | **yes** |
| code lineage | `not_agent_authored` — the viewer really is genuine | **yes** |
| capture | genuine X11 grab, sha256 `58e3a03a…` | **yes** |
| field observation failures | **none** | — |
| **content bytes on screen** | **attacker-authored** | **the lie** |

Verdict: **`AUTHENTIC_TARGET`**. Ground truth: **SUBSTITUTE**. A real false accept, at every
configuration including the display tier, from an unprivileged attacker, with no compromise
of the recorder, kernel or compositor boundary. `[C6]`

The attacker overwrote the declared target file's **bytes** while a legitimate viewer held it
open. The fabricated fill colour is verifiably present in the captured PNG.

> **Truthfully observed state can still be adversarially arranged.** Moving a field to a
> higher trust plane buys integrity of the *report*, never integrity of the *claim*.

## 6. What 13b actually shows — the underspecification result

The tempting readings are "the contract is insufficient" and "the recorder had a bug". We
resolved this **statically**, over the frozen adjudicator, changing nothing. `[C7]`

### 6.1 The sequence

1. The empirical recorder produced `AUTHENTIC_TARGET`.
2. The declared target's **bytes** had in fact been changed during the episode.
3. The episode write journal was **write-API-keyed**: it recorded only writes made through the
   harness helper. The mutation was performed with `cp` via `subprocess`, so the journal never
   observed a write to the target path.
4. Injecting that single already-conceivable observation into the frozen apparatus — one
   journal entry, with the Tier C value then derived by **frozen recorder code**, not written
   by hand — **flips the verdict to `SUBSTITUTE`** at every display-tier configuration, via a
   rule the adjudicator already had.
5. **However**, the contract never specified the observation-completeness semantics that
   lineage field required: not what events must be observed, not which observer is
   authoritative, not what completeness guarantee exists, and not how a missed event is
   represented.
6. Because the contract defined lineage as a **binary** predicate, the recorder had two tokens
   and no way to say "I did not watch". Absence of observation was emitted as the positive
   value `pre_existing`:

   ```python
   rec = journal.get(path)
   if rec:                    return f"{path}:agent_authored_this_episode"
   if os.path.exists(path):   return f"{path}:pre_existing"   # <- absence of an OBSERVATION
   ```

7. The binary abstraction also **conflates legitimate task-mandated writes with adversarial
   substitution** — it records only *that* the path was written this episode.
8. Applying the mutation interpretation uniformly therefore creates an **honest-case false
   reject**: the same injected observation flips the honest control `01_genuine_target` from
   `AUTHENTIC_TARGET` to `SUBSTITUTE`. `[C8]`

### 6.2 The classification

> **The result is not cleanly reducible to recorder bug versus decision-rule failure. The
> provenance concept itself lacked a sufficiently explicit observation policy.**

The contract's entire safety mechanism — abstain-by-default — fires on a **missing field**.
The field was never missing. Absence of *observation* was laundered into presence of a
positive *claim* before any rule ran.

### 6.3 Two secondary findings, preserved

**B′ — recorder observability gap, inside one configuration.** At every display-tier
configuration where the lineage field is collected, the adjudicator already had the correct
rule and the missed observation alone flips the verdict. *Within that configuration*, 13b
falsified the tested recorder's observation policy rather than the decision rules.

**C′ — identity and provenance are fused.** The lineage field carries two quantities in one
string (`path:token`): *which* resource, and *where it came from*. The contract never says
whether they may be sourced separately. With the field dropped — the default deployment, since
the contract itself concedes the field is "not OS-observable" — the adjudicator takes identity
from `command_line` (a Tier B field) and the Tier C provenance requirement silently evaluates
to empty:

```
displayed_resource=/lab/work/pre_existing_report.png (via command_line)
resource_lineage=
```

…returning `AUTHENTIC_TARGET`, although the contract's own table says absence of that field
implies UNKNOWN for viewer-mediated scenes, and its Composition Rule 1 forbids inferring a
missing field from an adjacent one.

### 6.4 Why this matters beyond one contract

The same contract handles absence **correctly** for some fields and **incorrectly** for
others, and the split is systematic:

| Mechanism | Failure looks like | Absence handled |
|---|---|---|
| **query** ("what is true now?") — `ACTIVE_PID`, geometry, z-order | a failure, recorded with a reason → abstention | correctly ✅ |
| **event journal** ("what happened?") — lineage fields | silence | incorrectly ❌ |

A query that fails is *visibly* a failure. An event that never arrives looks exactly like an
event that never happened. **Event-based observation therefore requires an explicit coverage
guarantee in a way query-based observation does not.**

## 7. The two policies, stated

### 7.1 Observation policy — what the recorder must observe

Six declarations per security-relevant fact. Anything less is not evaluable:

1. **Observer** — which plane, named. "OS-observed" is not one fact.
2. **Collection mechanism** — the actual syscall/protocol/API. `HARNESS_OBSERVED` is a plane;
   `inotify` and "writes through helper `journal_write()`" are mechanisms with different
   coverage.
3. **Coverage boundary** — the exact event set the mechanism can see.
4. **Known blind spots, with consequences attached.** Our frozen contract *named* "write via a
   child process" as a lineage evasion and attached **no consequence** — and 13b used exactly
   that. A named blind spot that changes no verdict is documentation, not policy.
5. **Missed-event semantics** — the value emitted when the mechanism did not observe. **A third
   token is mandatory.** Two-valued provenance predicates are unsafe by construction.
6. **Is absence evidence?** — explicit, and the default must be **no**.

### 7.2 Inference policy — what may be concluded

1. Evidence tiers and what each licenses (here EXACT / STRONG / WEAK / UNKNOWN).
2. The **lowest tier permitted to produce a verdict**, plus the sensitivity of every headline
   number to that threshold. A recoverability figure without its sensitivity curve is
   uninterpretable.
3. Which fields may be **substituted** for which — and mechanical enforcement. Our contract
   says *never substitute*; our adjudicator substituted argv for a missing lineage field
   anyway (§6.3, C′). A policy that is not mechanically checked is not in force.
4. Whether abstention is credited, refused, or routed (§8).
5. What cannot be inferred, and when UNKNOWN is **mandatory**.

Neither concept is claimed as novel. What is new here is their **measured importance in this
setting**, and the demonstration that leaving either implicit produces a system whose output
cannot be interpreted.

## 8. The UNKNOWN result

Abstention is the contract's entire safety margin, so we measured what it is worth
downstream:

| Tier config | MODE 1 permissive (UNKNOWN credited) | MODE 2 fail-closed (UNKNOWN gets no credit) |
|---|---|---|
| `0` → `0+A+B+C` | **100.0%** | **0.0%** |
| `0+A+B+C+D` and above | 27.3% | **9.1%** |

*Figure 6.* `[C15]`

Three statements, and the third is the one that matters:

1. Fail-closed UNKNOWN **materially reduces exposure** — the largest single effect measured in
   this work, and a **policy** decision rather than a field.
2. It **does not repair a false `AUTHENTIC_TARGET`.**
3. **Case 13b survives fail-closed UNKNOWN**, because 13b was never UNKNOWN. It was
   *accepted*. The residual 9.1% is exactly that one accepted fabrication.

> Abstention is a mechanism. Refusing automatic credit is enforcement. Neither reaches an
> accepted fabrication.

## 9. Does a different desktop trust architecture move the boundary?

One narrow, predeclared comparison. Two cases, both platforms, same application:

- **Case P — substitute surface.** A genuine viewer shows the genuine target; an attacker-
  created surface mimics it in front. *Can the trusted capture path bind pixels to the
  originating client?*
- **Case R — legitimate renderer, agent-controlled resource.** A genuine viewer, a genuine
  surface, attacker-authored bytes at the declared target path. *Does compositor mediation
  establish anything about the displayed resource?*

Wayland arm: **sway 1.7 (wlroots) headless**, `WLR_RENDERER=pixman`, XWayland enabled,
`xdg-desktop-portal` + `xdg-desktop-portal-wlr`, PipeWire, capture via `grim` over
`wlr-screencopy-unstable-v1`. Three trust domains: compositor session (uid 1001), attacker
(uid 1000), recorder (root + `CAP_SYS_PTRACE`). `eog` ran as a **native** client of both
platforms, so the arms compare the same application.

### 9.1 The binding matrix

| Row | artifact→capture | capture→surface | surface→process | process→resource | resource→state | state→claim |
|---|---|---|---|---|---|---|
| X11 Case P | EXACT | WEAK | EXACT | UNKNOWN | UNKNOWN | UNKNOWN |
| **Wayland (tested) Case P** | EXACT | WEAK | EXACT | UNKNOWN | UNKNOWN | UNKNOWN |
| X11 Case R | EXACT | STRONG | EXACT | WEAK | UNKNOWN | UNKNOWN |
| **Wayland (tested) Case R** | EXACT | STRONG | EXACT | WEAK | UNKNOWN | UNKNOWN |

*Figure 7.* **Zero of twelve comparable bindings changed evidence level.** `[C9]`

`STRONG` in column 2 is **by elimination** — one surface was enumerated, so the frame can only
be its pixels. It is contingent on the enumeration being *complete*, which our own S2 result
falsified for X11 and which was not tested on Wayland.

### 9.2 Case P — the decisive measurement

Read directly off the running portal, needing no session:

```
org.freedesktop.portal.ScreenCast   version = 4
AvailableSourceTypes = 1   →   MONITOR: true   WINDOW: false   VIRTUAL: false
org.freedesktop.portal.Screenshot   →   interface does not exist on this backend
```

`SelectSources` was called with `types = MONITOR|WINDOW` and returned success — the WINDOW bit
was accepted and silently ineffective; the backend's own trace shows it enumerating
**outputs**. The selectable unit of the tested standard API is a **monitor**, exactly as on
X11. `[C11]`

### 9.3 What did and did not change

**Improved:** capture-path integrity — only the compositor can produce the frame, where on X11
any client with display access can grab the root window; and the directness of
`surface → process` — the compositor reports client pid as a first-class field with no
`_NET_WM_PID` trap. `[C10]`

**Not improved:** `capture → surface` (output-scoped on both); `surface → displayed resource`
(no such field on either platform); identity trustworthiness — the attacker's GTK process
obtained `app_id = "eog"`, **byte-identical** to the genuine viewer's, with an identical
title. Only the pid separated them. `[C13]`

**Made worse:** cross-client enumeration existed **only** through compositor-private IPC. The
standardised API exposes strictly less than X11. A recorder built on `swaymsg` is a *sway*
recorder, not a *Wayland* recorder.

> **The tested Wayland stack changed the trust architecture but did not export additional
> provenance sufficient to improve the tested binding matrix.**

**Scope, load-bearing:** one compositor, one portal backend, two constructed cases. The
xdg-desktop-portal specification supports WINDOW sources where a backend implements them;
**GNOME and KDE backends do and were not tested.** Such a backend may change
`capture → surface`. It would not by itself establish displayed-resource provenance, because
neither platform has a concept of "the resource this surface is showing".

The portal **stream-metadata** sub-experiment is **BLOCKED**: `Start` failed with
`wlroots: unable to receive a valid format from wlr_screencopy` — PipeWire format negotiation
in a headless container with no DRM device. Stream contents were never observed and are not
inferred from documentation. `[C12]`

## 10. Where assurance terminates

Link 4 fails identically on both platforms. Phase J added one empirical bound on the obvious
next move: **open file descriptors at the capture instant revealed nothing.** `eog` decodes
the image and closes the descriptor; `holds_declared_target_open = false` on both arms.
`[C14]`

> Whatever binds pixels to bytes must be recorded **when the read happens**, not when the
> capture happens. A recorder sampling at capture time samples after the binding has ceased to
> exist in kernel-visible form.

### 10.1 The opaque-boundary result

An unprivileged attacker running **Xephyr** made the inner scene opaque to the tested outer
recorder, which resolved the captured pixels to `/usr/bin/Xephyr` (pid 4391) with **zero field
observation failures**. Every field was correct and complete; provenance simply terminated at
the nested X server. The inner window did not appear in the outer visible set at all. `[C17]`

Stated narrowly: **the tested outer recorder's provenance terminated at `/usr/bin/Xephyr`.**
Not "all nested compositors are opaque" — the Wayland analogue was not tested.

A defensible generalisation, and no more:

> **Opaque rendering boundaries require some trusted binding across the boundary if inner
> provenance is to remain auditable.**

**Classification: INFERENCE / candidate general principle.** `[C18]`

Four measured witnesses: the retrospective scene-source failure (§3), 13b's
observation-policy case (§6), the Xephyr boundary (§10.1), and fd-at-capture-time (§10). The
Wayland comparison was the designed test of whether a **trusted compositor** changes one of
these bindings. It did not — the compositor stands at the `capture → surface` boundary,
improves the integrity of what it reports there, and is not standing where the failure occurs.
That is consistent with the principle; a single non-refutation is weak support, and it remains
unestablished that no trusted observer *could* be placed at that boundary.

## 11. A methodological result: derived vectors vs real observations

We ran the contract twice: analytically over analyst-derived field vectors, and empirically in
the real lab. Of **169** comparable (scenario, tier) pairs, **127 agreed — 75.1%**.

| Direction | n | Reading |
|---|---|---|
| `SUBSTITUTE → UNKNOWN` | 34 | analytic over-confident, **safe** direction |
| `AUTHENTIC_TARGET → UNKNOWN` | 3 | analytic over-confident, safe direction |
| **`UNKNOWN → AUTHENTIC_TARGET`** | **5** | **analytic wrong in the UNSAFE direction** |

*Figure 5.* One adversarial scenario that the analytic contract model abstained on was
accepted by the real implementation across five configurations. All five unsafe rows are
**case 13b**—an existence result, not a measured failure rate for analytic evaluation.
`[C16]`

Mechanism: the analyst-derived vectors encoded resource lineage as **content-aware**, which no
real recorder in the lab could produce.

The analytic identifier `13b_viewer_agent_image_gui_open` and empirical identifier
`13b_viewer_agent_image_hidden` are not simple aliases. The latter is the corrected empirical
successor after IC-4: the construction changed from a bare viewer/GUI-open vector to a viewer
on the declared target path whose bytes were replaced and re-rendered. The comparison mapping
is explicit in `scripts/score_empirical.py`; historical rows retain their original names.

Stated exactly that narrowly. One experiment, one contract, one constructed suite. It is **not**
a general claim about analytic security evaluation, and most of the disagreement ran the safe
direction.

## 12. What we do not claim

**No novel mechanism.** Provenance graphs over agent traces, process/file/runtime telemetry,
eBPF collection, screen or window recording, tamper-evident hash-chained logs, content
provenance and signed media, Wayland's capture mediation, trusted display and anti-spoofing UI
— all occupied prior art (see [`RELATED_WORK.md`](RELATED_WORK.md)). `[C20]`

Two disciplines this work leaned on are **convergent rather than novel**: AgentProvenance, at
pinned commit `fc2e6264`, independently enforces the same separation of runtime identity from
application-asserted context (enforced at ingest) and the same graded-confidence correlation
discipline. That convergence strengthens the argument and **reduces** our claim to novelty on
both ideas. `[C21]`

The contribution is a measurement:

> **which visual-evidence provenance bindings survive or fail under different observation
> policies, inference policies, and desktop trust architectures.**

## 13. Practical implications

For anyone building or evaluating agent visual evidence, in order of measured effect:

1. **Decide what UNKNOWN means downstream before choosing fields.** It was the largest single
   effect measured here (§8), and it is free. It also cannot save you from an accepted
   fabrication.
2. **Write the observation policy down, per field, with a `not_observed` value.** A binary
   provenance predicate is unsafe by construction (§6, §7.1).
3. **Publish the inference sensitivity curve with every coverage number.** A single number is
   uninterpretable (§4).
4. **Separate resource identity from resource provenance.** Fusing them let identity be
   sourced from a lower tier while the provenance requirement silently evaporated (§6.3).
5. **Declare whether the agent is expected to author the target.** Without it, "the target was
   written this episode" cannot distinguish fabrication from doing the task (§6.1, step 7).
6. **Do not expect the desktop platform to close link 4.** Neither tested platform has a
   concept of the resource a surface is displaying (§9).

## 14. Status

Closed for technical expansion at tag `phaseJ-epistemic-boundary-v1`. Registered and **not
executed**: H-RB (can application-independent system telemetry bind displayed pixels to the
resource bytes consumed by a legitimate renderer?), application-state attestation, adaptive
red-teaming, additional compositors and operating systems.

The one measurement that would reopen a cell — a portal backend implementing WINDOW sources
*and* reporting the selected source's client identity — is specific, cheap, and would change
`capture → surface` only. It would not touch link 4.
