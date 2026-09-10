# Visual Evidence Provenance for Computer-Using Agents

**A measurement study of where provenance for agent-produced visual evidence terminates —
and why the answer depends on policies that are usually left unstated.**

---

## The problem

A computer-using agent is asked to do something in a GUI and to prove it with a screenshot.

It produces a screenshot. The file was written by a real capture tool. The window was real.
The process was a genuine, unmodified, distribution-packaged binary. Every field a recorder
can collect is **true**.

And the thing on screen is something the agent made.

> **Visual evidence can be a valid screenshot of the wrong thing.**

File provenance answers *which action wrote this file*. Capture provenance answers *was this
produced by a real capture*. Neither answers *what was on the screen, and was it the task's
actual state*. Those are different properties with different failure modes, and collapsing
them is the category error this work exists to measure. `[C1, C4]`

## Main result

**Post-hoc visual provenance collapses when traces fail to record the binding that matters,
and apparent recoverability depends heavily on inference policy.**

Over 394 capture-based delivered artifacts from a real agent benchmark, scene source reached
EXACT or STRONG confidence in 6.6% of cases — with **EXACT in zero cases**. Meanwhile
artifact provenance was recovered for **453/453**. The easy link is solved; the load-bearing
one is not. `[C3, C4]`

Worse, "how recoverable is it?" turns out to be partly a question about the analyst. Holding
the observations fixed and varying only how much temporal speculation the resolver is
permitted moved apparent resolution from **4.8% to 54.9%** — while well-supported
(EXACT/STRONG) attribution moved only **2.4% to 11.9%**.

> More permissive inference produced substantially more answers without a commensurate
> increase in strong evidence. `[C2]`

## Deeper result

The obvious response is to stop reconstructing after the fact and *record* the right fields
prospectively. So we specified a capture-provenance contract, predeclared a kill criterion,
and attacked it in a real X11 lab with an unprivileged adversary.

The criterion fired. `[C23]`

A legitimate image viewer was opened on the **declared target file**, and that file's
**bytes** were replaced with attacker-authored content. Every contract field was collected.
Every field was truthful. **Zero field observation failures.** The verdict was
`AUTHENTIC_TARGET`. `[C6]`

Tracing that failure statically through the frozen rules produced the result that reframes
the project:

> **Even prospective provenance schemas are underspecified unless they declare what the
> recorder must observe and how absence and ambiguity are handled.**

The contract defined resource lineage as a *binary* predicate — "was it authored this
episode?" — so a faithful recorder had **no vocabulary in which to say "I did not watch."**
Absence of observation was emitted as the positive claim `pre_existing`, and abstain-by
-default could never fire because the field was never missing. `[C7]`

And the obvious fix is not a fix: injecting the missed observation does flip 13b to
`SUBSTITUTE` — and simultaneously turns the *honest* control into a false reject, because the
schema cannot distinguish a task-mandated write from an adversarial substitution. `[C8]`

## System implication

**Fail-closed UNKNOWN reduces exposure, but cannot protect against incorrectly authenticated
evidence.**

Refusing automatic credit for UNKNOWN moved effective exposure from **100.0% → 0.0%** below
the display tier and **27.3% → 9.1%** at the strongest tier — the largest single effect
measured anywhere in this work, and it is a *policy* decision rather than a field.

It has a hard ceiling. Case 13b survives fail-closed UNKNOWN because 13b was never UNKNOWN —
it was **accepted**. No abstention policy reaches an accepted fabrication. `[C15]`

## Does a better desktop architecture fix it?

We ran one narrow comparison: the same two cases on X11 and on a Wayland stack with a
compositor-mediated capture path (sway/wlroots + `xdg-desktop-portal-wlr` + PipeWire).

**Zero of twelve comparable provenance bindings changed evidence level.** `[C9]`

The tested stack genuinely improved *trust architecture*: only the compositor can produce a
frame, and it reports the owning client pid as a first-class field. It did not improve
*attribution*. The tested portal advertised `AvailableSourceTypes = 1` — **MONITOR only, no
window source** — so capture stayed output-scoped, exactly as on X11. And `app_id` proved to
be client-asserted: an attacker's GTK process obtained `app_id = "eog"`, byte-identical to the
genuine viewer's. `[C10, C11, C13]`

> The tested Wayland stack changed the trust architecture but did not export additional
> provenance sufficient to improve the tested binding matrix.

This is a result about **the tested backend**, not about Wayland. GNOME and KDE portal
backends implement window sources and were **not tested**; such a backend could change the
`capture → surface` cell. It would not, by itself, establish displayed-resource provenance.

## The thesis

> **Provenance claims for computer-using agents are meaningful only relative to an explicit
> epistemic policy: what the recorder is obligated to observe, what may be inferred from
> those observations, where assurance terminates across opaque boundaries, and when the
> evaluator must abstain.**

Classified **INFERENCE / research thesis — not a theorem.** `[C19]`

It rests on a double dissociation: varying the *inference* policy with observations fixed
moved apparent resolution ~11×; varying a *single observation* with the decision rules frozen
and unmodified flipped a verdict between `AUTHENTIC_TARGET` and `SUBSTITUTE`.

It is a **necessary-condition** claim. Declaring both policies does not make provenance sound
— C8 is the counter-example from inside our own data.

## The assurance chain

```
artifact ──► capture ──► process/surface ──► displayed resource ──► app state ──► claim
   ✅          ✅              ✅                    ❌               untested     untested
 solved      solved      solved in lab         BOUNDARY          not reached   not reached
                                          same on BOTH platforms
```

Links 1–3 hold in the tested labs. **Link 4 is where assurance fails**, identically on X11
and on the tested Wayland stack. Links 5 and 6 were never reached, and nothing here is
progress on them. `[C14]`

## What this is not

This work claims **no novel mechanism**. Explicitly not claimed as novel: provenance graphs
over agent traces, process/file/runtime telemetry, eBPF collection, screen recording,
tamper-evident logs, content provenance, Wayland's capture mediation, or trusted display.
All are occupied prior art. `[C20]`

The contribution is narrower and is a measurement:

> which visual-evidence provenance bindings survive or fail under different observation
> policies, inference policies, and desktop trust architectures.

The primary results are **negative**, with a precisely located boundary. That is the
deliverable.

## Read next

| If you want | Read |
|---|---|
| the full argument | [`TECHNICAL_REPORT.md`](TECHNICAL_REPORT.md) |
| what every claim is allowed to say | [`CLAIM_TABLE.md`](CLAIM_TABLE.md) |
| how it was measured | [`METHODOLOGY.md`](METHODOLOGY.md) |
| the numbers | [`RESULTS.md`](RESULTS.md) |
| why you should doubt it | [`LIMITATIONS.md`](LIMITATIONS.md) · [`HOSTILE_REVIEW.md`](HOSTILE_REVIEW.md) |
| how to re-run it | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |
| where it sits in the literature | [`RELATED_WORK.md`](RELATED_WORK.md) |
| every artifact | [`ARTIFACT_INDEX.md`](ARTIFACT_INDEX.md) · [`PACKAGE_MANIFEST.md`](PACKAGE_MANIFEST.md) |

---

**Status:** closed for technical expansion at tag `phaseJ-epistemic-boundary-v1`. Every
number in this package is quoted from a frozen artifact and is regenerable by the commands in
`REPRODUCIBILITY.md`. Bracketed `[C…]` markers refer to rows in `CLAIM_TABLE.md`; a sentence
without a licensing row does not belong here.
