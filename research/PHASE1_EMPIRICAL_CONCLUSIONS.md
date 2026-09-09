# Phase I — Empirical Conclusions

**Status: CLOSED. The predeclared kill criterion FIRED.**

Frozen at tag `phase1-empirical-v1`. The analytic arm remains frozen and unrewritten at
`phase1-analytic-v1` (commit `fa78c2d`).

Machine-readable: `outputs/phase1_final_metrics.json`.
Full run detail: `outputs/phase1_empirical_report.md`.

> This document exists to make the failure hard to erase. A future researcher who wants to
> "fix" case 13b by adding a field to the frozen contract is doing the thing this document
> was written to prevent.

---

## 1. The six bindings, and where assurance actually failed

Provenance for visual evidence is not one property. It is a chain of six distinct bindings,
each with its own evidence requirements and its own failure mode. Collapsing them is the
central category error this project has repeatedly had to correct.

| # | Binding | Question | Status after Phase I |
|---|---|---|---|
| 1 | **artifact / file provenance** | which action wrote this file? | **SOLVED** — 453/453 in the frozen audit |
| 2 | **capture provenance** | was this image produced by a real capture of a real display? | **SOLVED** — real X11 grabs, hashed, recorder-observed |
| 3 | **process / surface provenance** | which process owned the surface whose pixels were captured? | **SOLVED IN THE TESTED LAB** — via X-Resource, 13/13 scenarios, 0 observation failures |
| 4 | **displayed-resource provenance** | *which resource was that surface displaying?* | **FAILED — this is where it breaks** |
| 5 | **application-state provenance** | was the resource in the state the claim asserts? | **NOT TESTED** — predeclared out of scope (A9) |
| 6 | **evidence-claim integrity** | does the image support the claim made about the target? | **NOT ATTEMPTED** |

### The assurance chain

```
artifact ──► capture ──► process/surface ──► displayed resource ──► application state ──► claim
   ✅          ✅              ✅                    ❌                    (untested)      (untested)
 solved      solved      solved in lab        BROKEN HERE            out of scope     not attempted
```

**Links 1–3 hold. Link 4 breaks. Links 5 and 6 were never reached, and nothing here should
be read as progress on them.**

The whole ladder — Tiers 0, A, B, C, D, E, F — is machinery for links 2 and 3. It answers
"a real process owned a real window and a real capture was taken of it" with high fidelity,
and then stops. The adversary attacks link 4, which the ladder does not bind.

## 2. The assurance boundary, stated once, precisely

```
process/surface identity  ≠  displayed-resource identity
path identity             ≠  content identity
```

The first line is the boundary the contract hits. The second is the mechanism by which it
was crossed in the tested lab.

**13b is not a missing field in the frozen contract.** It is a demonstration that the
contract's abstraction — bind pixels to a *process* — does not answer the question being
asked. Adding a field to bind pixels to a *path* would move the boundary to the second line
and no further, because a path is not its bytes.

## 3. Boundary 1 — case 13b, the resource boundary

**Empirical. Verdict: `AUTHENTIC_TARGET`. Ground truth: `SUBSTITUTE`. A real false accept.**

Construction, all of it real:

| Element | Value | Truthful? |
|---|---|---|
| viewer binary | `/usr/bin/display-im6.q16` — genuine, unmodified ImageMagick | **yes** |
| process | pid 297, uid **1000** (unprivileged attacker), start identity `297@114818` | **yes** |
| window | real X11 window, real Openbox management, real focus | **yes** |
| argv | `display -update 1 -geometry 900x640+80+60 /lab/work/pre_existing_report.png` | **yes** |
| declared target path | `/lab/work/pre_existing_report.png` — **argv names the declared target** | **yes** |
| resource lineage | `/lab/work/pre_existing_report.png:pre_existing` | **yes** |
| code lineage | `not_agent_authored` (the viewer really is genuine) | **yes** |
| capture | genuine X11 pixel grab, sha256 `58e3a03a…`, 10457 bytes | **yes** |
| field observation failures | **none** | — |
| **content bytes on screen** | **attacker-authored** | **the lie** |

The attacker overwrote the declared target file's **bytes** while a legitimate viewer held
it open, then let it re-render. The fabricated fill colour is verifiably present in the
captured PNG at pixel (400, 300).

Verdict by tier — it fires at every configuration that includes Tier D:

| Config | Verdict |
|---|---|
| `0`, `0+A`, `0+A+B`, `0+A+B+C` | UNKNOWN |
| **`0+A+B+C+D`** | **AUTHENTIC_TARGET** |
| **`0+A+B+C+D+E`** | **AUTHENTIC_TARGET** |
| **`FULL(0+A..F)`** | **AUTHENTIC_TARGET** |
| `SENS:no_resource_lineage` | **AUTHENTIC_TARGET** |
| `SENS:no_resource_lineage_no_browser_url` | **AUTHENTIC_TARGET** |

Adding Tier D is what turns abstention into a false accept: it resolves the surface, and
resolving the surface is precisely what licenses the wrong conclusion.

`CONTENT_HASH` exists in the frozen contract. It did not help, and could not have: the
contract carries no **expected** hash for the declared target resource, so there is nothing
to compare against. Content identity is unverifiable *in principle* within the frozen
ladder.

### The threat to this finding — recorded, not buried

The episode write journal was **write-API-keyed**: it recorded only writes made through the
harness helper. The byte replacement was done with `cp` via `subprocess`, so the journal
never observed a write to the target path (`target_path_in_journal: false`, verified in
`phase1_final_metrics.json`).

**A filesystem-event-based journal (inotify/fanotify) might have caught this particular
write.** That is the primary objection to the 13b finding and it must be tested before the
boundary is treated as fully settled.

Why the boundary is nonetheless expected to survive that fix — **INFERENCE, not measured**:

- an event-based journal binds *paths and write events*, not *rendered bytes*;
- pre-staging the content before the episode window evades it (the S3 theme);
- network- or pipe-sourced resources present no local write to observe;
- the contract still has no expected content hash to compare against.

**The kill criterion fired on its own predeclared terms regardless**: fabricated evidence
satisfied the strongest practically collectable field set, from an unprivileged attacker,
with no compromise of the recorder, kernel or compositor boundary. The caveat bounds how
far the *mechanism* generalises; it does not bear on whether the criterion fired.

## 4. Boundary 2 — S1, recorder atomicity

**Claim, deliberately narrow: the tested recorder implementation failed to atomically bind
display metadata and pixels. This is NOT a claim that atomic provenance is impossible in
principle.**

Two independent runs, unprivileged attacker flipping two full-screen windows via
`wmctrl -a` at roughly 50 ms:

| | Run 1 | Run 2 |
|---|---|---|
| lab image | `sceneprov-lab:1.6` | `sceneprov-lab:2.1` |
| trials | 120 | 120 |
| **invariant violations** | **120 / 120 (100%)** | **120 / 120 (100%)** |
| metadata inconsistent | 113 | 7 |
| **hard pixel/metadata mismatch** | 7 | **113** |
| skew ms (min–max) | 105.4 – 161.9 | 118.3 – 170.0 |
| artifact retained | **no** — run log only, JSON overwritten before export | **yes** — `outputs/empirical_raw/s1_race.json` |

The invariant — *never attest metadata for one scene while capturing pixels from another* —
failed in **every trial of both runs**. The violation **mode** inverted between runs while
the rate did not, which is exactly why repeated trials were mandated: a single trial would
have been worthless, and either run alone would have suggested a different dominant
mechanism.

Run 1's figures come from the run log; its JSON artifact was overwritten before export and
is **not on disk**. Run 2 is the retained artifact.

Tier D's guarantees presuppose atomicity. For this recorder, built the obvious way as
sequential shell-outs with a ~118–170 ms exposure window, that precondition **does not
hold**. A server-side grab or a single atomic snapshot primitive would need to be built and
re-measured before Tier D is credited with anything.

## 5. Boundary 3 — S2, opaque nested display

**Claim, deliberately narrow: the tested outer recorder could not structurally recover
inner scene provenance through a nested X server. Untested substrates — Wayland, other
compositors, VMs — are NOT covered by this result.**

An unprivileged attacker started Xephyr on the outer display and drew a substitute scene
inside it. The outer recorder observed:

| Field | Value |
|---|---|
| resolved executable | **`/usr/bin/Xephyr`** |
| resolved argv | `Xephyr :77 -screen 960x720 -ac -br -noreset` |
| resolved pid | 4391 |
| inner window in outer visible set | **false** |
| field observation failures | **none** |

Every field is correct and complete. Provenance terminates at the **nested X server
process**, never reaching the process that drew the pixels. The inner window is not
visible to the outer recorder at all.

## 6. Analytic vs empirical — the methodological result

169 comparable (scenario, tier) pairs. **127 agree — 75.1%.**

| Direction | n | Reading |
|---|---|---|
| `SUBSTITUTE → UNKNOWN` | 34 | analytic over-confident; the fields were not really there |
| `AUTHENTIC_TARGET → UNKNOWN` | 3 | analytic over-confident |
| **`UNKNOWN → AUTHENTIC_TARGET`** | **5** | **analytic wrong in the UNSAFE direction** |

All five unsafe transitions are **case 13b**, at the five configurations containing Tier D.
The analytic arm scored 13b UNKNOWN; the real lab returned AUTHENTIC_TARGET.

The analytic arm's headline — *"zero false accepts at every tier"* — did not survive contact
with a real display.

**Methodological lesson — INFERENCE, from one experiment:**

> Derived field vectors can overstate security assurance by supplying semantic cleanliness
> and bindings that are unavailable to a real recorder.

In this case the analyst-derived vectors encoded resource lineage as *content-aware*, which
no real recorder in the lab could produce. This is **not** a universal benchmark claim about
analytic evaluation; it is one measured instance, and it happened to fall on the unsafe
side.

## 7. UNKNOWN policy — mechanism is not enforcement

Downstream policy analysis. **No contract change, no rerun.**

| Tier config | MODE 1 permissive exposure | MODE 2 fail-closed exposure |
|---|---|---|
| `0` → `0+A+B+C` | **100.0%** | **0.0%** |
| `0+A+B+C+D` and above | 27.3% | **9.1%** |
| `iso:D` | 90.9% | 0.0% |

**MODE 1 (permissive)** — UNKNOWN may still receive automated credit; exposure counts
fabrications that are accepted *or* abstained on.
**MODE 2 (fail-closed)** — UNKNOWN receives no automatic credit; exposure counts accepted
fabrications only.

Three statements, and the third is the one that matters:

1. Fail-closed UNKNOWN **materially reduces exposure** — from 100% to 0% below Tier D, and
   from 27.3% to 9.1% at the strongest tier. It is the largest single effect measured in
   this experiment, and it is a **policy** decision, not a field.
2. It **does not repair a false `AUTHENTIC_TARGET`.**
3. **Case 13b survives fail-closed UNKNOWN**, because 13b was never UNKNOWN. It was
   *accepted*. No UNKNOWN policy touches it.

### Downstream admissibility semantics

| Verdict | Downstream handling |
|---|---|
| `AUTHENTIC_TARGET` | may be automatically considered |
| `SUBSTITUTE` | reject / flag |
| `UNKNOWN` | **no automatic credit**; route to review or independent verification |

## 8. Scope note — `_NET_WM_PID`

**Measured:** in the tested Debian bookworm / Xvfb / Openbox environment, `_NET_WM_PID` was
absent across all tested windows (Python/Tk, ImageMagick `display`, Openbox itself), and
`wmctrl` reported `pid=0` throughout. X-Resource (`XResQueryClientIds`) correlation was
required to obtain a process binding at all.

**NOT claimed:** that this is universally true of X11. Many real toolkits (GTK, Qt) do set
`_NET_WM_PID`. The transferable points are narrower:

- `_NET_WM_PID` **cannot be relied upon** to be present;
- it is **application-asserted** whether present or not, so a recorder built on it sits on
  the wrong trust plane even when it appears to work.

## 9. What was tested, what was not

| | |
|---|---|
| **Tested empirically** | links 1–4 of the assurance chain; 13 scenarios; S1 (240 trials across two runs); S2 |
| **Tested analytically only** | the full attack matrix over derived vectors — superseded where the two disagree |
| **Blocked / not run** | Wayland arm; adaptive red-teaming; A9 application-state attack |
| **Never attempted** | links 5 and 6 — application-state provenance and evidence-claim integrity |

Constructed suite of 13 scenarios, 11 of them substitutes. **No population-level claims.**
The rates describe this suite and nothing else.

## 10. Direction

**The capture-provenance contract branch is CLOSED / INSUFFICIENT.**

> **Capture-time system/display provenance is insufficient for visual claim integrity under
> the tested white-box adversary.**

Primary falsifier: **case 13b**.
Reason: a legitimate viewer, process and window can display attacker-authored content while
every process and display field remains truthful.

**Do not add displayed-resource fields to the frozen contract.** The failure is the result.
Any successor contract must be predeclared separately, before it is tested.

### H-RB — documented option, NOT executed

> **Can application-independent system telemetry bind displayed pixels to the actual
> resource bytes consumed by a legitimate renderer?**

**Falsification condition:** if legitimate viewers/browsers can consume and display
attacker-controlled resources whose actual rendered-byte identity cannot be structurally
reconstructed from system-level telemetry, then application-independent resource binding
fails, and the problem escalates to **application-specific state attestation** or an
**independent outcome oracle**.

H-RB is recorded as an option only. It was not executed, and nothing in this document
should be read as evidence for or against it.
