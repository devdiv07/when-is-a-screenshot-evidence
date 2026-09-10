# Epistemic Policy — observation policy and inference policy are different things

Written after the 13b static classification (`research/13B_STATIC_CLASSIFICATION.md`) and
before the platform comparison, so that the comparison is read under a stated policy rather
than an implicit one.

This document does **not** modify the frozen contract, the frozen adjudicator, or any Phase I
verdict. It names two policies that Phase I conflated, and states what a successor must
declare.

---

## 0. The distinction

A provenance system makes two separate commitments, and this project has now been damaged by
each of them being left implicit:

| | **Observation policy** | **Inference policy** |
|---|---|---|
| Question | what is the recorder *obligated to see*? | what may be *concluded* from what was seen? |
| Failure mode | an event happens and is never recorded | a recorded event is stretched to answer a question it does not answer |
| Where it bit us | **case 13b** — a write occurred that the journal did not observe, and "not observed" was reported as "did not happen" | **the lookback sweep** — apparent scene-source resolution rose 11× purely by permitting more temporal speculation |
| Symptom | a false accept with **zero** field observation failures | a coverage number that is a property of a parameter, not of the data |

Both are *policy*, not fields. Neither is visible in the output. Both determine what the
output means.

---

## 1. Inference policy

> **What conclusions may be drawn from observations that were actually recorded.**

### The measured witness — the lookback sweep

Over 455 capture-based delivered-evidence cases, permitting more temporal lookback between a
process launch and a capture (`outputs/recoverability_report.md` §5.2, E020, corrected):

| Lookback (events) | source resolved | of which EXACT/STRONG |
|---|---|---|
| 2 | 4.8% | 2.4% |
| 4 | 10.3% | 4.6% |
| 8 | 22.0% | 6.6% |
| 16 (used) | 30.8% | 7.5% |
| 32 | 42.0% | 10.1% |
| 64 | 51.0% | 11.2% |
| unbounded | 54.9% | 11.9% |

**MEASURED FACT.** Apparent resolution rises **4.8% → 54.9%, roughly 11×**. Well-supported
attribution rises **2.4% → 11.9%**, and almost all of that is in the first few steps.

The gap between the two columns is the entire finding. At unbounded lookback, **43 of every
55 resolved cases** are resolved by nothing but the willingness to look further back.

### The principle

> **An answer created by temporal permissiveness is not equivalent to new evidence.**

Loosening an inference rule always raises coverage. It cannot raise the amount of evidence in
the trace, because the trace does not change. What moves is the *threshold at which a guess
is printed as a conclusion*. A recoverability figure quoted without its sensitivity curve is
therefore uninterpretable, and this project treats any such figure as unusable.

The operational consequence already adopted in Phase A (`DECISION_LOG`, 2026-09-09) stands:
**WEAK (temporal-adjacency) evidence may not produce a scene classification.** It is recorded
as `weak_scene_hypothesis` and never promoted.

### What an inference policy must declare

1. The evidence tiers and what each licenses — here `EXACT` / `STRONG` / `WEAK` / `UNKNOWN`.
2. The **lowest tier permitted to produce a verdict**, and the sensitivity of every headline
   number to that threshold.
3. Which fields may be **substituted** for which. Composition Rule 1 says *never* — and
   `adjudicator.py:190-195` substitutes `command_line` for a missing
   `displayed_resource_lineage` anyway (finding C′). A policy that is not mechanically
   checked is not in force.
4. Whether abstention is credited, refused, or routed — the **largest single effect measured
   in Phase I** (exposure 100% → 0% below Tier D, 27.3% → 9.1% at the strongest tier) is this
   choice, and it is not a field.

---

## 2. Observation policy

> **What the recorder is obligated to observe, by what mechanism, with what coverage, and
> what it must say when it did not look.**

### The measured witness — case 13b

The target file's bytes were replaced by `cp` through `subprocess`. The episode journal was
**write-API-keyed**: it recorded only writes made through the harness helper. The write was
never observed. The frozen recorder then emitted:

```python
rec = journal.get(path)
if rec:                    return f"{path}:agent_authored_this_episode"
if os.path.exists(path):   return f"{path}:pre_existing"      # <-- absence of observation
```

`field_observation_failures: []`. The recorder reported **complete success** while being
blind to the only event that mattered.

The static trace (`outputs/13b_static_trace/`) shows that injecting that single missed
observation flips the verdict `AUTHENTIC_TARGET → SUBSTITUTE` at every Tier-D-inclusive
configuration, and changes nothing in the two default-deployment arms.

### The defect in one line

> The contract defined a **binary** predicate — "was it authored this episode?" — so the
> recorder had **no vocabulary in which to say "I did not watch"**, and absence of
> observation was laundered into a positive provenance claim before any rule ran.

This is why abstain-by-default did not protect 13b. R1 fires on a **missing field**. The
field was never missing.

### Absence is handled inconsistently *within the same contract*

This is the sharpest evidence that the policy was never stated, because two fields in one
contract resolve absence in opposite directions:

| Field | What happens when the observation fails | Effect |
|---|---|---|
| `ACTIVE_PID` | `Recorder._fail()` records `None` **plus a reason** in `field_observation_failures`; R1 then abstains | absence ⇒ **not observed** ✅ |
| `DISPLAYED_RESOURCE_LINEAGE` | silently becomes `pre_existing` | absence ⇒ **did not happen** ❌ |

The asymmetry is perverse in its consequences: a **missing file** is closer to producing an
abstention than a **missed write** is. The recorder is scrupulous about one plane and
credulous about another, and the contract text distinguishes them nowhere.

### The schema an observation policy must fill, per security-relevant field

Six declarations. Anything less is not evaluable.

1. **Observer** — which plane, named, not "the OS".
2. **Collection mechanism** — the actual syscall/protocol/API. `HARNESS_OBSERVED` is a
   plane; `inotify` and "writes through helper `journal_write()`" are mechanisms, and they
   have different coverage.
3. **Coverage boundary** — the exact set of events the mechanism can see.
4. **Known blind spots** — enumerated, with the consequence attached. The frozen contract
   *names* "write via a child process" as a lineage evasion and attaches **no consequence**;
   13b then used exactly that. Naming a blind spot without a consequence is documentation,
   not policy.
5. **Missed-event semantics** — the value emitted when the mechanism did not observe.
   **A third token is mandatory.** Two-valued provenance predicates are unsafe by
   construction.
6. **Is absence evidence?** — explicit yes/no. Default must be **no**.

### The frozen contract, audited against that schema

Status of each security-relevant field as actually implemented in the tested X11 lab.
`mechanism` is what `infra/recorder.py` really did, not what the contract implies.

| Field | Observer (as implemented) | Mechanism | Coverage boundary | Missed-event semantics | Absence = evidence? |
|---|---|---|---|---|---|
| `WINDOW_TITLE`, `WM_CLASS` | `APPLICATION_ASSERTED` | `xdotool getwindowname`, `xprop WM_CLASS` | value is app-supplied | `_fail` → None + reason | no (and presence proves nothing — R3) |
| `ACTIVE_PID` | `COMPOSITOR/DISPLAY_SERVER` (**not** kernel, per IC-1) | `XResQueryClientIds`, `LocalClientPIDMask` | **local** X clients only; server-attributable resources only | `_fail` → None + reason | **no** ✅ |
| `PROCESS_START_IDENTITY`, `EXECUTABLE_PATH`, `COMMAND_LINE` | `KERNEL/RUNTIME` | `/proc/<pid>/{stat,exe,cmdline}` | live process only; argv as the process left it | `_fail` → None + reason | no ✅ |
| `AGENT_WRITTEN_CODE_LINEAGE` | `HARNESS_OBSERVED` | **any whitespace token of argv ∈ journal keys** | write-API-keyed journal | **none** — silently `not_agent_authored` | **yes** ❌ (and conflates data writes with code lineage — CF-2) |
| `CONTENT_HASH` | `TRUSTED_RECORDER` | `sha256` of capture bytes | the delivered image only | n/a | **never consumed by any rule** |
| `DISPLAYED_RESOURCE_LINEAGE` — *identity* | reconstructed, **not observed** | last argv token containing `/` with an extension (`recorder.py:249-253`) | viewers that name the resource in argv | none | — |
| `DISPLAYED_RESOURCE_LINEAGE` — *provenance* | `HARNESS_OBSERVED` | `journal.get(path)` | **writes through `journal_write()` only**; blind to `cp`, child processes, pre-staging, network- and pipe-sourced content | **none** — silently `pre_existing` | **yes** ❌ **← the 13b defect** |
| `VISIBLE_WINDOW_SET`, `Z_ORDER`, `WINDOW_GEOMETRY` | `COMPOSITOR/DISPLAY_SERVER` | `wmctrl -lpG`, `xwininfo -root -children` | managed windows on the observed display; **blind through a nested X server** (S2) | `_fail` → None + reason | no ✅ |
| `CAPTURE_REGION` | `TRUSTED_RECORDER` | **declared string**, not measured from the image | — | none | no |
| `ACTIVE_WINDOW_IDENTITY` | `COMPOSITOR/DISPLAY_SERVER` | `xdotool getactivewindow` | focused window at sample time | `_fail` → None + reason | no ✅ |
| *atomicity* | — | **not a field**; sequential shell-outs | 105–170 ms skew; **120/120 invariant violations in each of two runs** | none | — |

Note the pattern: every field whose mechanism is a **query** ("what is true now?") handles
absence correctly, and every field whose mechanism is an **event journal** ("what happened?")
handles it incorrectly. A query that fails is visibly a failure. An event that never arrives
looks exactly like an event that never happened. **Event-based observation therefore requires
an explicit coverage guarantee in a way query-based observation does not.**

---

## 3. The candidate thesis

> **A provenance claim is meaningful only relative to both a declared observation policy and
> a declared inference policy.**

**Classification: INFERENCE / candidate thesis. Not a theorem, not proven.**

### What supports it

| Witness | What it shows | Class |
|---|---|---|
| Lookback sweep (455 cases) | with observations fixed, varying only the inference rule moves apparent resolution 11×, while well-supported attribution stays nearly flat | MEASURED |
| Case 13b + static trace | with the inference rules fixed and unmodified, varying only whether one write was observed flips `AUTHENTIC_TARGET` ↔ `SUBSTITUTE` | MEASURED |
| Absence asymmetry within the frozen contract | two fields in one contract resolve "not observed" in opposite directions, and the text distinguishes them nowhere | MEASURED (code + trace) |

The first two are a genuine double dissociation: each policy was varied with the other held
fixed, and each alone moved the verdict. That is the strongest form the current evidence
takes.

### What does NOT support it, and must not be claimed

- **Not** that the two policies are jointly sufficient. Nothing here shows that declaring
  both yields a sound provenance claim. 13b's boundary — `path identity ≠ content identity` —
  survives any observation policy that binds paths and write events rather than rendered
  bytes.
- **Not** a general result about provenance systems. Two witnesses, one contract, one
  corpus, one substrate (X11).
- **Not** a claim that better policy would have saved the frozen contract. The rule-property
  probe shows the opposite: the observation that repairs 13b turns the honest control into a
  **false reject**, because the contract has no field distinguishing a task-mandated write
  from an adversarial one.

### The consequence that matters for this project

A successor contract cannot be evaluated as "sufficient" or "insufficient" until both
policies are written down. Phase I's kill criterion fired against a contract whose observation
policy was never stated — which is why 13b classifies as **CONTRACT_UNDERSPECIFICATION** and
not as a clean contract falsification. The kill criterion still fired on its own predeclared
terms; what this document establishes is what a successor would have to declare *before* its
own criterion could mean anything.

---

## 4. Minimum declaration for any successor

Non-negotiable, derived from the failures above and from nothing else:

1. **A third lineage token.** `observed_authored` / `observed_not_authored` /
   **`not_observed`**. Binary provenance predicates are unsafe by construction.
2. **Absence is never evidence.** `not_observed` must reach the abstention rule, and that
   must be mechanically tested, not asserted in prose.
3. **Mechanism, not plane.** Every field declares its actual collection mechanism and the
   event set that mechanism can see.
4. **Blind spots carry consequences.** A named blind spot that changes no verdict is
   documentation. If "write via a child process" is admissible, every field derived from the
   journal must degrade to `not_observed` whenever a child process could have written the
   resource.
5. **Identity and provenance are separate fields.** Fusing them (finding C′) let identity be
   sourced from Tier B while the Tier C provenance requirement silently evaporated.
6. **Declare whether the agent may legitimately author the target.** Without it, "the target
   was written this episode" cannot distinguish fabrication from doing the task.
7. **Publish the inference sensitivity curve** with every coverage number, always.
