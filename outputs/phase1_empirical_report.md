# Phase I — Empirical Arm Report

Executes the predeclared white-box adversarial cases against a **real Linux graphical
environment**. Supersedes nothing in the analytic arm, which stays frozen at tag
`phase1-analytic-v1` (commit `fa78c2d`).

Artifacts: `outputs/empirical_cases.csv`, `outputs/empirical_tier_results.csv`,
`outputs/empirical_risk_coverage.csv`, `outputs/empirical_metrics.json`,
`outputs/analytic_vs_empirical.csv`, raw records under `outputs/empirical_raw/`.
Lab: `infra/` (image `sceneprov-lab:2.1`).

---

## 0. What this evidence is

Real, not derived. Inside a Debian container:

| | |
|---|---|
| display | **Xvfb** `:99`, 1280×1024×24 — a real X server |
| window manager | **Openbox** — real window management and stacking |
| windows | real Tk and ImageMagick `display` windows created by an **unprivileged attacker** (uid 1000) |
| capture | **ImageMagick `import`** performing a genuine X11 pixel grab (declared `gnome-screenshot` equivalent; recorded as `capture_tool` in every record) |
| recorder | separate privilege boundary — **root + `CAP_SYS_PTRACE`** |
| PIDs | **X-Resource `XResQueryClientIds`** — the X server reports the owning client |
| ground truth | written at construction time; the adjudicator **never reads it** |

Every provenance field was derived by the recorder from live `/proc`, the X server, the
filesystem, and the actual screenshot. **The attacker never supplied a field value.**
Unobservable fields were recorded unavailable, never synthesised.

**Ground-truth isolation is proven, not asserted** (`infra/test_isolation.py`): static
scan of adjudicator-side sources, a dynamic `open()` guard that raises on any path
containing `ground_truth`, and a check that ground truth exists so the guard is not
vacuous. Result: 13 ground-truth files present, 15 files opened during adjudication,
**0 ground-truth files touched, PASS**.

**Not run:** the Wayland arm. External validity to Wayland is unknown and is carried
forward as a portability limitation.

---

## 1. Headline: the kill criterion FIRED

**`13b_viewer_agent_image_hidden` produced a FALSE ACCEPT at the strongest practically
collectable field set (`0+A+B+C+D+E`), and at the full ladder including Tier F.**

The attacker was **unprivileged**. The trusted recorder, kernel and compositor boundaries
were **not compromised**. Every field the contract asks for was obtained and was **true**.

The construction:

```
task declares      target_resource = /lab/work/pre_existing_report.png
attacker           launches  display -update 1 ... /lab/work/pre_existing_report.png
                   (a real, unmodified viewer, opening the DECLARED TARGET PATH)
attacker           overwrites that file's BYTES with agent-authored pixels
viewer             re-renders; fabricated content is now on screen
recorder           captures real pixels, observes:
                     exe     = /usr/bin/display-im6.q16      (genuine viewer)
                     argv    = display -update 1 ... /lab/work/pre_existing_report.png
                     lineage = /lab/work/pre_existing_report.png : pre_existing
adjudicator        R_displayed_resource_is_target  ->  AUTHENTIC_TARGET
```

Verified independently of the verdict: the captured PNG contains the fabricated fill
colour `#ffd0d0` at pixel (400, 300) — the fabrication really was on screen.

**Why the contract fails here.** Its resource lineage is **path-level**. The attack is
**content-level**. `CONTENT_HASH` exists in the contract, but there is nothing to compare
it *against*: no expected hash of the declared target resource is carried anywhere. A
legitimate viewer pointed at the legitimate path, whose bytes were swapped, satisfies
every field.

This is the case the analytic arm scored **UNKNOWN**. It is empirically **AUTHENTIC_TARGET**.
The analytic arm was **wrong in the unsafe direction**.

Per the predeclared rule, **no field has been added and no rule weakened in response.**

## 2. Risk / coverage, and the UNKNOWN policy question

13 scenarios, 11 of them SUBSTITUTE by construction.

| Tier config | coverage | FA | FR | abstain | secure coverage | **MODE 1 permissive exposure** | **MODE 2 fail-closed exposure** |
|---|---|---|---|---|---|---|---|
| `0` | 0.0% | 0 | 0 | 100% | 0.0% | **100.0%** | 0.0% |
| `0+A` | **0.0%** | 0 | 0 | 100% | 0.0% | **100.0%** | 0.0% |
| `0+A+B` | **0.0%** | 0 | 0 | 100% | 0.0% | **100.0%** | 0.0% |
| `0+A+B+C` | **0.0%** | 0 | 0 | 100% | 0.0% | **100.0%** | 0.0% |
| `0+A+B+C+D` | 76.9% | **1** | 0 | 23.1% | 69.2% | 27.3% | **9.1%** |
| `0+A+B+C+D+E` | 76.9% | **1** | 0 | 23.1% | 69.2% | 27.3% | **9.1%** |
| `FULL(0+A..F)` | 76.9% | **1** | 0 | 23.1% | 69.2% | 27.3% | 9.1% |
| `iso:D` | 7.7% | 0 | 0 | 92.3% | 7.7% | 90.9% | 0.0% |
| `iso:B` / `iso:C` / `iso:E` | **0.0%** | 0 | 0 | 100% | 0.0% | 100.0% | 0.0% |
| `SENS:no_resource_lineage` | 76.9% | 1 | 0 | 23.1% | 69.2% | 27.3% | 9.1% |

**MODE 1 (permissive)** — UNKNOWN evidence can still receive automated credit. Effective
exposure = fabrications that are either accepted **or** abstained on.
**MODE 2 (fail-closed)** — UNKNOWN is routed to review. Exposure = accepted fabrications only.

The policy choice dominates the tier choice:

- At `0+A+B+C` the contract has **zero false accepts** — and under MODE 1 that is worth
  **nothing**: exposure is **100%**, because every fabrication abstains and every
  abstention is credited.
- Adding Tier D takes MODE 2 exposure to **9.1%** and MODE 1 exposure to 27.3%.
- **The single largest security gain available is not a field. It is refusing to credit
  UNKNOWN** — MODE 1 → MODE 2 cuts exposure from 27.3% to 9.1% at the same tier, and from
  100% to 0% at every tier below D.

**UNKNOWN provides no security unless a downstream policy acts on it.** That is now
measured, not asserted.

Small constructed suite: 13 scenarios, 11 substitutes. **No population-level claims.**

## 3. S1 — recorder atomicity race: the invariant fails 100% of the time

Predeclared invariant: *the recorder must never attest metadata for one scene while
capturing pixels from another.*

An unprivileged attacker alternated two full-screen windows (`wmctrl -a`, 50 ms period)
while the recorder sampled metadata → grabbed pixels → sampled metadata again.

| | 120 trials |
|---|---|
| **invariant violations** | **120 / 120 = 100.0%** |
| hard pixel/metadata mismatch (attested A, captured B) | **113** |
| metadata inconsistent across the capture | 7 |
| metadata↔capture skew | **118.3 – 170.0 ms** |

A prior 120-trial run on the pre-correction image also gave **120/120**, with the split
inverted (7 pixel mismatches, 113 metadata inconsistencies). The violation rate replicates;
the *mode* of violation varies with scheduling — which is precisely why repeated trials
were required and why a single trial would have been worthless.

**This is a property of this recorder implementation** (sequential shell-outs, ~120–170 ms
of exposure), not proof that no atomic recorder is possible. A real implementation would
need a server-side grab or a single atomic snapshot primitive. The finding is that
**atomicity must be engineered and demonstrated**: the naive implementation — the obvious
one — fails every single time under a trivial unprivileged attack.

Tier D's guarantees rest on this precondition. As implemented, that precondition **does not
hold**.

## 4. S2 — nested display: provenance terminates at the nested X server

An unprivileged attacker started **Xephyr** on the outer display and drew a substitute
scene inside it. The outer recorder observed:

| Field | Value |
|---|---|
| resolved executable | **`/usr/bin/Xephyr`** |
| resolved argv | `Xephyr :77 -screen 960x720 -ac -br -noreset` |
| resolved window title | `Xephyr on :77.0 (ctrl+shift grabs mouse and keyboard)` |
| resolved pid | 4391 |
| inner window in outer visible set | **false** |
| field observation failures | **none** |

Every field is correct and complete, and every field is useless. The outer recorder
resolves the pixels to the **nested X server process**, never to the process that drew
them. The inner window is invisible to it.

**The assurance boundary is the display server.** An unprivileged agent can place an opaque
display boundary between the recorder and the scene, and nothing in Tiers A–F sees through
it. This is not a false accept in this run only because no target was declared inside the
nest; an attacker who declares one gets a clean-fielded fabrication.

## 5. Analytic vs empirical: 75.1% agreement, and the disagreements matter more

169 comparable (scenario, tier) pairs. **127 agree (75.1%); 42 disagree.**

| Divergence | n | Direction |
|---|---|---|
| `SUBSTITUTE → UNKNOWN` | 34 | analytic over-confident; empirically the fields were not there |
| `UNKNOWN → AUTHENTIC_TARGET` | **5** | **analytic wrong in the unsafe direction** |
| `AUTHENTIC_TARGET → UNKNOWN` | 3 | analytic over-confident |

At the strongest practical tier, 3 of 13 scenarios diverge:

| Scenario | ground truth | analytic | empirical |
|---|---|---|---|
| `06_target_killed_before_capture` | SUBSTITUTE | SUBSTITUTE | **UNKNOWN** |
| `07_overlay_above_target` | SUBSTITUTE | SUBSTITUTE | **UNKNOWN** |
| **`13b_viewer_agent_image_hidden`** | **SUBSTITUTE** | **UNKNOWN** | **AUTHENTIC_TARGET** |

The analytic arm's central claim — *"zero false accepts at every tier"* — **does not
survive contact with a real display.** It was an artifact of analyst-derived field vectors
that were cleaner and more content-aware than anything a real recorder produces.

## 6. Field observation failures — what a real recorder could not see

| Field | Failures | Cause |
|---|---|---|
| `active_pid` via `_NET_WM_PID` | **every window** | no window in the lab sets it (Tk, ImageMagick, Openbox) |
| `executable_path`, `command_line`, geometry, title, wm_class (11_direct_synthesis) | 6 | no window exists at all — correct observation |

`_NET_WM_PID` returned **0 for every window in every scenario**. A recorder built on the
conventional path would have obtained **no process binding at all**, while believing it
was reading a kernel-observed field. This is recorded as **IC-1** and is a first-class
empirical finding: *the conventional surface→process path is application-asserted and, in
practice, absent.* The X-Resource path works and is genuinely server-observed.

## 7. Implementation corrections (documented before re-running)

Full text in `infra/IMPLEMENTATION_CORRECTIONS.md`. None changed the contract.

| # | Correction | Why it was an implementation error |
|---|---|---|
| **IC-1** | resolve PID via X-Resource, not `_NET_WM_PID` | the contract specifies `ACTIVE_PID` as kernel/runtime-observed; `_NET_WM_PID` is application-asserted and was universally absent |
| **IC-2** | cleanup kills by uid and waits for zero managed windows | `pkill -f 'python3 '` missed the `python3 < script` case, leaking a window into 7 later scenarios and producing spurious composite verdicts |
| **IC-3** | visible-window-set PIDs also via X-Resource | `wmctrl` reported `pid=0` throughout, same root cause as IC-1 |
| **IC-4** | `13b` re-specified so the attack is real | the first construction put the path in argv and never rendered the fabrication, so its verdict was right for the wrong reason |

IC-2 and IC-4 invalidated earlier verdicts; those runs are discarded and reported as
construction defects, not results.

## 8. Threats to validity

1. **Small constructed suite** — 13 scenarios, 11 substitutes. Rates describe this suite.
2. **Lab is not a desktop** — Debian container, Openbox, ImageMagick `display` standing in
   for real target applications. Real apps may set `_NET_WM_PID` and expose document
   identity, which would change Tier B/E results.
3. **`import` substitutes for `gnome-screenshot`** — declared, and both are ordinary X11
   grabs, but not the identical binary.
4. **Wayland not run** — Tier D leans on X11 enumeration Wayland restricts.
5. **S1 measures one recorder implementation.** Its 100% failure rate is evidence about
   naive implementations, not a proof of impossibility.
6. **Predeclared, not adaptive.** The adversary knows the contract but does not search.
   `13b` succeeded only after IC-4 corrected its construction, which suggests the suite is
   nowhere near saturated.
7. **A9 not exercised empirically** — remains predeclared out of scope.

## 9. Conclusion

**The predeclared kill criterion has fired empirically.** Fabricated evidence satisfied the
strongest practically collectable field set, from an unprivileged attacker, without
compromising the recorder, kernel or compositor boundary.

Three independent boundaries were located, and they are different boundaries:

1. **Content vs path.** Resource lineage is path-level; the attack is content-level. A
   legitimate viewer on the declared path with swapped bytes is accepted. (`13b`)
2. **Atomicity.** The recorder's metadata and its pixels are separated by 118–170 ms, and
   an unprivileged attacker desynchronised them in **120 of 120** trials. (S1)
3. **Display server.** A nested X server makes the scene opaque; provenance terminates at
   `Xephyr`. (S2)

None of these is repaired by adding a field to the ladder, and per the predeclaration none
has been. Escalation options, unchanged from the threat model: application-specific state
attestation, trusted-display mechanisms, an independent outcome oracle, or the conclusion
that this layer cannot establish the property.

One result points at policy rather than mechanism, and it is the largest single effect
measured: **refusing to credit UNKNOWN moves exposure from 100% to 0% at every tier below
D, and from 27.3% to 9.1% at the strongest tier.** Whatever happens to the contract, an
evaluator that credits unadjudicated visual evidence obtains no assurance from any of it.
