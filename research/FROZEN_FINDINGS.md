# Frozen Findings

**Frozen 2026-09-10 at tag `phaseJ-epistemic-boundary-v1`. These are the research package.**

Seven findings. Each carries its evidence class, its supporting evidence IDs, and — the part
that must not be dropped in any writeup — its **scope and explicit non-claims**.

Nothing below licenses a broader statement than the row it sits in. Where a finding is one
measured instance, it says so. Where it is an inference from measurement, it says so.

**Status: the research is CLOSED for technical expansion. H-RB is NOT opened.**

---

## F1 — Post-hoc scene attribution is highly inference-policy-sensitive

**Class: MEASURED FACT** (one corpus, 455 capture-based delivered-evidence cases).

Holding the observations fixed and varying only the permitted temporal lookback:

| Lookback (events) | source resolved | of which EXACT/STRONG |
|---|---|---|
| 2 | 4.8% | 2.4% |
| 16 (used) | 30.8% | 7.5% |
| unbounded | 54.9% | 11.9% |

Apparent resolution moves **~11×**. Well-supported attribution moves from 2.4% to 11.9% and
is nearly flat across the sweep. At unbounded lookback, roughly **43 of every 55 resolved
cases** are resolved by nothing but a willingness to look further back.

> **An answer created by temporal permissiveness is not equivalent to new evidence.**

**Scope:** the WeaveBench GPT-5.4 low corpus, one resolver, one parameter family.
**Non-claim:** not a general result about attribution methods. It shows that *this* metric is
parameter-driven above the STRONG tier, which is why any recoverability number quoted without
its sensitivity curve is treated here as unusable.

Evidence: **E020**, E029 · `outputs/recoverability_report.md` §5.2

---

## F2 — A provenance schema without an explicit observation policy can silently interpret "not observed" as "did not happen"

**Class: MEASURED FACT** (code + static trace over the frozen adjudicator).

The frozen contract defines displayed-resource lineage as a **binary** predicate — "was it
authored this episode?" — so a faithful implementation has two tokens and **no vocabulary in
which to say "I did not watch"**:

```python
rec = journal.get(path)
if rec:                    return f"{path}:agent_authored_this_episode"
if os.path.exists(path):   return f"{path}:pre_existing"   # <- absence of an OBSERVATION
```

Absence of observation is emitted as a **positive provenance claim** before any rule runs.
The contract's entire safety mechanism — abstain-by-default — fires on a *missing field*, and
the field is never missing.

The inconsistency is visible **within one contract**: every *query*-based field
(`ACTIVE_PID`, geometry, z-order) records a failure and reason and correctly abstains, while
every *event-journal*-based field silently converts "not observed" into a value. A query that
fails is visibly a failure; an event that never arrives looks exactly like an event that never
happened.

**Consequence for any successor:** a third token (`not_observed`) is mandatory, and it must
reach the abstention rule.

**Scope:** one contract, one recorder. **Non-claim:** not a claim that all provenance schemas
do this — a claim that this one did, structurally, and that the mechanism is general enough
to check for.

Evidence: **E076**, **E078**, E072, E073 · `research/13B_STATIC_CLASSIFICATION.md`,
`research/EPISTEMIC_POLICY.md`

---

## F3 — System/display facts can all be truthful while describing adversarially arranged state

**Class: MEASURED FACT** (empirical, X11 and Wayland).

Case 13b: a genuine unmodified `/usr/bin/display-im6.q16`, real pid 297 at uid 1000, a real
X11 window, argv naming the **declared target path**, lineage reading `pre_existing`, and
**zero field observation failures** — with attacker-authored bytes on screen. Every field was
obtained and every field was true.

Case P, both platforms: an unprivileged GTK3 process calling `GLib.set_prgname("eog")`
obtained `WM_CLASS = "eog"` on X11 and **`app_id = "eog"` on Wayland**, byte-identical to the
genuine viewer's, with an identical window title. The platform reported it faithfully. Only
the pid separated impostor from viewer.

> Moving a field to a higher trust plane buys integrity of the **report**, never integrity of
> the **claim**. The observer is not lying; it is faithfully describing a world the agent
> arranged.

**Scope:** constructed cases, unprivileged attacker, no recorder/kernel/compositor
compromise. **Non-claim:** says nothing about how often real agents do this.

Evidence: **E064**, **E081**, E060 · `research/THREAT_MODEL.md` §3,
`outputs/x11_wayland_comparison.md`

---

## F4 — The tested Wayland backend improved architecture and isolation but exported no additional useful provenance binding for these cases

**Class: MEASURED FACT** (2 predeclared cases × 2 platforms; zero observation failures;
capture hashes byte-identical across independent runs).

> **Zero of twelve comparable bindings changed evidence level between X11 and Wayland.**

| Improved | Not improved | Made worse |
|---|---|---|
| capture-path integrity — only the compositor can produce the frame (on X11 any client with display access can grab the root window) | `capture → surface`: the standard portal offers **no window source at all** — `AvailableSourceTypes = 1`, MONITOR only; `Screenshot` interface absent on the backend | cross-client enumeration exists **only** via compositor-private IPC, so the standardised API exposes strictly **less** than X11 |
| directness of `surface → process` — the compositor reports client pid as a first-class field, no `_NET_WM_PID` trap | `surface → displayed resource`: no such field on either platform | a recorder built on `swaymsg` is a *sway* recorder, not a *Wayland* recorder |
| | identity trustworthiness — `app_id` is client-asserted (F3) | |

The predeclared expectation that Wayland would strengthen `capture → surface` is **REFUTED
for the standard path**, and the refutation is measured, not argued.

**Scope — load-bearing:** **one** compositor (sway 1.7/wlroots), **one** portal backend
(`xdg-desktop-portal-wlr`), headless software-rendered container, **two** constructed cases.
**GNOME's and KDE's portals implement window capture and were NOT tested.** Portal
*stream metadata* was never observed — `Start` failed on PipeWire format negotiation
(`unable to receive a valid format from wlr_screencopy`, no DRM device) and is recorded
**BLOCKED**, not inferred from documentation.

**Non-claim:** *not* "Wayland is no better than X11" — it is better in the ways listed, and
those matter for the recorder's integrity. It is not better at the thing measured here.

Evidence: **E079**, **E080**, **E083**, E084, E088 · `outputs/platform_binding_matrix.csv`,
`outputs/x11_wayland_comparison.md`

---

## F5 — Process/surface identity does not establish displayed-resource identity

**Class: MEASURED FACT** (empirical, now on two desktop trust architectures).

```
process/surface identity  ≠  displayed-resource identity
path identity             ≠  content identity
```

This is the edge where assurance fails, and Phase J measured it failing **identically on both
platforms**. Neither X11 nor Wayland has a concept of "the resource this surface is showing",
so neither reports one. The binding rests entirely on argv — a string the attacker chooses,
which is not evidence that those bytes were the pixels rendered.

Phase J added an empirical bound on the obvious next move: **open file descriptors at the
capture instant reveal nothing.** `eog` decodes the image and closes the descriptor;
`holds_declared_target_open = false` on both arms.

> Whatever binds pixels to bytes must be recorded **when the read happens**, not when the
> capture happens. A recorder sampling at capture time samples after the binding has ceased
> to exist in kernel-visible form.

```
artifact ─► capture ─► process/surface ─► displayed resource ─► app state ─► claim
   ✅         ✅             ✅                   ❌              untested    untested
                                          SAME EDGE, BOTH PLATFORMS
```

**Scope:** one viewer (`eog`), two platforms, constructed cases. Links 5 and 6 were never
reached and nothing here is progress on them.

Evidence: **E064**, **E065**, **E082**, E079 · `research/PHASE1_EMPIRICAL_CONCLUSIONS.md` §2

---

## F6 — UNKNOWN protects you only when downstream policy refuses automatic credit, and it cannot repair a false AUTHENTIC_TARGET

**Class: MEASURED FACT** (empirical, 13-scenario constructed suite).

| Tier config | MODE 1 permissive exposure | MODE 2 fail-closed exposure |
|---|---|---|
| `0` → `0+A+B+C` | **100.0%** | **0.0%** |
| `0+A+B+C+D` and above | 27.3% | **9.1%** |

Fail-closed UNKNOWN is the **largest single effect measured in the whole project** — larger
than any field's contribution — and it is a **policy** decision, not a field.

And it has a hard ceiling: **case 13b survives fail-closed UNKNOWN**, because 13b was never
UNKNOWN. It was **accepted**. No UNKNOWN policy touches an accepted fabrication.

> Abstention is a mechanism. Refusing automatic credit is enforcement. A contract whose entire
> safety margin is abstention is worth nothing until the evaluator actions UNKNOWN — and even
> then it does not reach a false accept.

**Scope:** constructed suite of 13 scenarios, 11 substitutes. **Not a population estimate.**

Evidence: **E062**, **E069** · `outputs/empirical_risk_coverage.csv`

---

## F7 — Analytic field-vector evaluations can be dangerously cleaner than real recorder observations

**Class: INFERENCE from one measured experiment.** The measurement is a fact; the
generalisation to "can be, in general" is an inference and is labelled as such.

169 comparable (scenario, tier) pairs; **127 agree — 75.1%**.

| Direction | n | Reading |
|---|---|---|
| `SUBSTITUTE → UNKNOWN` | 34 | analytic over-confident |
| `AUTHENTIC_TARGET → UNKNOWN` | 3 | analytic over-confident |
| **`UNKNOWN → AUTHENTIC_TARGET`** | **5** | **analytic wrong in the UNSAFE direction** |

All five unsafe transitions are **case 13b** — the headline case. The analytic arm scored it
UNKNOWN; the real lab returned `AUTHENTIC_TARGET`. The analytic arm's headline, *"zero false
accepts at every tier"*, did not survive contact with a real display.

Mechanism: the analyst-derived vectors encoded resource lineage as **content-aware**, which no
real recorder in the lab could produce. Derived vectors supply semantic cleanliness and
bindings that are unavailable in practice.

**Scope:** one experiment, one contract. **Non-claim:** not a universal benchmark claim about
analytic evaluation. It is one measured instance, and it happened to fall on the unsafe side —
which is precisely why it is worth recording.

Evidence: **E061** · `outputs/analytic_vs_empirical.csv`

---

## The cross-cutting thesis

> **A provenance claim is meaningful only relative to both a declared observation policy and
> a declared inference policy.**

**Class: INFERENCE / candidate thesis. Not a theorem.**

Supported by a genuine **double dissociation** — each policy varied with the other held
fixed, and each alone moved the verdict:

| | varied | held fixed | effect |
|---|---|---|---|
| **F1** | inference policy | observations | apparent resolution ×11 |
| **F2** | one observation | the rules (frozen, unmodified) | verdict flips `AUTHENTIC_TARGET` ↔ `SUBSTITUTE` |

**Explicitly NOT claimed: that the two policies are jointly sufficient.** The rule-property
probe shows the opposite — declaring them does not repair 13b. The single observation that
fixes 13b turns the honest control into a **false reject**, because the contract has no field
distinguishing a task-mandated write from an adversarial one (E075).

### The renderer-boundary hypothesis

> Every opaque transition in a visual-evidence provenance chain requires a trusted binding
> recorded at or across that boundary; when no trusted observer records the binding where it
> occurs, reliable post-hoc reconstruction is generally unavailable.

**Class: HYPOTHESIS.** Four measured witnesses — retrospective WeaveBench scene-source
failure; 13b's observation-policy case; the Xephyr nested-renderer boundary; and Phase J's
fd-at-capture-time result. The Wayland comparison was the designed test of whether a **trusted
compositor** changes one of these bindings. **It does not** — the compositor stands at the
`capture → surface` boundary, improves the integrity of what it reports there, and is not
standing where the failure occurs.

**Still open:** that no trusted observer *could* be placed at that boundary. Only that neither
tested platform places one there.

---

## Candidate contribution, as frozen

> **Measurement of which visual-evidence provenance bindings survive or fail under different
> observation policies, inference policies, and desktop trust architectures.**

Not a mechanism. Explicit non-novelty for: provenance graphs over agent traces; process/file/
runtime telemetry; eBPF; window or screen recording; tamper-evident logs; content provenance
or signed media; Wayland's capture mediation; trusted display or anti-spoofing UI.

## Not opened

**H-RB is NOT opened.** It remains registered with its falsification condition and unexecuted,
and Phase J has already bounded its naive form (F5). Also not opened: application-state
attestation, adaptive red-teaming, additional operating systems, additional compositors,
further benchmark tasks, ProcGrep modifications, another provenance framework.

The one result that would justify reopening anything is specific and cheap: a compositor whose
portal implements **window-source** capture *and* reports the selected source's client
identity to the caller — i.e. the GNOME or KDE backend, untested. It would change one cell of
the matrix and would **not** touch F5.
