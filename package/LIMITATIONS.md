# Limitations

Ordered by how much they should change your reading, most material first. Nothing here is
deferred to a footnote, because several of these bound the headline results directly.

---

## 1. One benchmark and one model family for all retrospective work

**What.** Every retrospective number — R0–R5, the lookback sweep, the field-set analysis —
comes from **one** corpus: WeaveBench GPT-5.4 low, 114 hybrid GUI+CLI tasks, two runs, 453
delivered visual artifacts.

**Why it matters.** Capture practice is a property of the *runtime*, not of agents in general.
The dominant reason scene provenance is unrecoverable here is that 125 of 145 sampled
`gnome-screenshot` invocations captured the whole screen and the runtime logged no window
identity. **A different harness that recorded active-window identity at capture time would
produce different numbers**, and that is the stated reopening condition in our own decision
log.

**Do not read** any recoverability figure as a property of agent traces in general.

## 2. Manual validation is single-reviewer, with no inter-rater statistic

**What.** One reviewer manually checked automated claims. It **refuted 4 of the first 7** and
drove three rule corrections (GUI-capability test, process-exit invalidation, composite-scene
demotion).

**Why it matters.** That validation is load-bearing — it is why substitute claims dropped from
9 to 4, and why the lookback curve had to be recomputed. A single reviewer who was also the
system's author has an obvious failure mode, and **no inter-rater agreement statistic exists**.

**Never describe this as completed two-reviewer validation.** The corrections it produced are
better evidence of its value than its own reliability is.

## 3. The judge is not independent ground truth

**What.** WeaveBench's judge emits `is_hack`, `hack_confidence`, `hack_patterns`,
`hack_evidence_quotes`, `dimensions.evidence_authenticity` and per-artifact `fake_signal` —
all from the *same* trajectory and deliverables.

**Why it matters.** These are correlated outputs of one evaluator apparatus. Agreement between
our structural instrument and the judge would not validate the instrument. We used judge
output only for **candidate localisation and validation sampling**, and the comparison in
`audit_metrics.json` is explicitly annotated *"comparison against a coupled LLM judge, NOT a
ground-truth evaluation"*.

**Residual risk.** R0 (quote localisation, 70.4%) is computed *against judge quotes*, so it
inherits whatever the judge chose to quote. It is a tractability measure, not a correctness
measure.

## 4. The empirical environment is X11-heavy, and containerised

**What.** The prospective arm ran on Xvfb + Openbox in Docker, with Tk and ImageMagick
windows. The frozen scoping note (`_NET_WM_PID` absent everywhere) is a property of *that*
environment — and our own Phase J lab, with GTK/`eog`, **contradicts it**.

**Why it matters.** Two of our own environments disagree about a field's availability. That is
the transferable point (it cannot be relied on either way), but it also means environment
-specific findings should not be lifted out of their environment. Headless, software-rendered
containers are also not desktops: no GPU, no DRM device, no real compositor scheduling.

## 5. Exactly one Wayland backend was tested

**What.** sway 1.7 (wlroots), headless, `WLR_RENDERER=pixman`, with
`xdg-desktop-portal-wlr` and PipeWire.

**Why it matters — this bounds the headline platform result.** The measured fact is that the
tested portal advertised `AvailableSourceTypes = 1` (MONITOR only) and had no `Screenshot`
interface. **The xdg-desktop-portal specification supports WINDOW sources where a backend
implements them, and GNOME and KDE backends do.** Those were **not tested**.

A backend offering window-source capture could change the `capture → surface` cell of the
binding matrix. It would **not**, by itself, establish displayed-resource provenance — neither
platform has any concept of "the resource this surface is showing" — but the zero-of-twelve
headline is a statement about **the tested stack**, and must always be written that way.

## 6. Portal stream metadata was never observed

**What.** The full `ScreenCast` session reached `Start` and failed (response_code 2) with the
backend's own trace: `wlroots: unable to receive a valid format from wlr_screencopy` —
PipeWire buffer-format negotiation in a container with no DRM device.

**Why it matters.** We therefore **do not know** what identity metadata a portal stream carries
in practice. That question is **BLOCKED**, not answered negatively, and no sentence in this
package infers stream contents from the specification.

**Mitigating:** the decisive Case P finding comes from `AvailableSourceTypes`, a property read
directly off the running portal with no session required, so it does not depend on the block.

## 7. Attacks are hand-constructed and predeclared, not an adaptive red team

**What.** A white-box adversarial **case evaluation**: the adversary knows the contract, but
the 13 scenarios plus stretch cases were written in advance and never adapted to results.

**Why it matters.** This measures whether a contract **can** be defeated, never how often it
**would** be. And the suite is demonstrably **not saturated**: case 13b — the case that fired
the kill criterion — only became a real attack after IC-4 corrected its construction. A case
we nearly got wrong turned out to be the whole result, which is direct evidence that an
adaptive adversary would find more.

## 8. Constructed suites carry no base rates

**What.** 13 scenarios (11 substitutes) in Phase I; 2 cases per platform in Phase J.

**Why it matters.** Every rate — coverage 76.9%, exposure 27.3%/9.1%, agreement 75.1% —
describes **these suites and nothing else**. None is a population estimate, and the
substitute-heavy mix was chosen to stress the contract, not to resemble real agent behaviour.

## 9. No application-state attestation; H-RB not executed

**What.** Links 5 and 6 of the assurance chain — application-state provenance and
evidence-claim integrity — were **never reached**. The A9 attack (a genuine target displaying
agent-manipulated state) was predeclared out of scope and never exercised. The successor
hypothesis H-RB is registered and **not executed**.

**Why it matters.** Nothing in this package is evidence for or against whether those links can
be closed. We do have one empirical bound obtained in passing: open file descriptors at the
capture instant revealed nothing, because the viewer had already closed the file — but that is
**one viewer on two platforms**, not a general result about kernel telemetry.

## 10. Provenance is not correctness

**What.** Even a perfect result on links 1–4 would establish *what was on screen and where it
came from*. It would not establish that the task was **done**.

**Why it matters.** A genuine target application, in focus, displaying a document the agent
corrupted, satisfies every display-layer field correctly. This is predeclared as out of reach
for a display-layer contract, and no sentence here should be read as progress on semantic task
correctness.

## 11. Scoped negatives that are easy to over-read

Each of these is narrow by construction, and the broad version is false or unestablished:

| Measured, narrow | The over-reading to avoid |
|---|---|
| the **tested outer recorder's** provenance terminated at `/usr/bin/Xephyr` | "all nested compositors are opaque" — the Wayland analogue was **not tested** |
| **the tested recorder implementation** violated its atomicity invariant 120/120 in each of two runs | "atomic provenance is impossible" — a server-side grab was never built |
| **in this experiment** analytic vectors were overconfident in several safety-relevant cases | "analytic security evaluation is unreliable" — and note 34 of 42 disagreements ran the *safe* direction |
| **no generic visual-display/scene provenance mechanism was found in the inspected pinned surface** of AgentProvenance | "AgentProvenance cannot capture screenshots" — never established |
| scene provenance was **not recoverable from these traces** | "scene provenance is impossible to recover" |

## 12. Known apparatus defects, and what they cost

Six implementation corrections were found and documented **before** re-running affected cases.
Two were serious:

- **IC-2** — cleanup missed `python3 < script`; a leaked window contaminated 7 scenarios and
  produced spurious composite abstentions. **The whole suite was re-run**; the earlier run is
  discarded.
- **IC-4** — case 13b disclosed the path in argv and **never rendered the fabrication**. Its
  SUBSTITUTE verdict was correct for the wrong reason. **13b was re-specified and re-run**;
  the earlier verdict is discarded.

**IC-5** was caught only because the trusted recorder observes independently of the case
constructor: the two disagreed about whether a viewer had started, and the disagreement was
the signal. The affected artifact was the **ground-truth record**, not the measurement, and
the result was verified stable across the fix (all four capture hashes byte-identical, binding
matrix unchanged at 0/12).

**What this implies:** an apparatus that produced four material defects in this many runs has
probably not produced its last. Runs invalidated by IC-2, IC-4 and IC-3 are excluded from
every figure in this package and are listed in [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

## 13. One withdrawn claim, recorded rather than deleted

The comparative **recorder-skew** figure (Wayland lower than X11) is **withdrawn as not
reproducible**: the ranges moved materially between re-runs of the same image. Skew here is a
property of recorder architecture and machine load, not of the platform. No result in this
package rests on it. See [`HOSTILE_REVIEW.md`](HOSTILE_REVIEW.md) H-3.

## 14. Prior-art search is not exhaustive

Sources are pinned where possible and read directly. AgentProvenance was verified at a specific
commit, but **the software was not executed** and the search was term-based over one revision;
forks, issues, PRs and roadmap items outside that tree were not considered. A capability
implemented without any searched term would not have been found.

Novelty claims in this package are correspondingly narrow, and one prior system
(AgentProvenance) is recorded as **reducing** our claim to novelty on trust-plane separation
and graded-confidence correlation, because it independently enforces both.
