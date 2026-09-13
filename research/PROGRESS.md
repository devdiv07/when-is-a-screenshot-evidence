# Progress

## Current status — 2026-09-09 — SUPERSEDED by the 2026-09-10 section at the end of this file

> **This section is retained unrewritten for provenance. Phase I's conclusions stand;
> its "next step" list at the end of this section does NOT — see Phase J.**

**PHASE I CLOSED AND FROZEN. Kill criterion FIRED. Contract branch CLOSED / INSUFFICIENT.**

Read first: `outputs/phase1_final_summary.md`, then
`research/PHASE1_EMPIRICAL_CONCLUSIONS.md`. Machine-readable:
`outputs/phase1_final_metrics.json`.

**Frozen decision:** capture-time system/display provenance is **insufficient** for visual
claim integrity under the tested white-box adversary. Primary falsifier **case 13b**.
Assurance boundary: `process/surface identity != displayed-resource identity`;
`path identity != content identity`.

**Do not add displayed-resource fields to the frozen contract.** 13b is not a missing
field. A successor contract must be predeclared separately before testing. The successor
hypothesis **H-RB** is registered and **not executed**.

The assurance chain, with what was actually established:

```
artifact ──► capture ──► process/surface ──► displayed resource ──► application state ──► claim
   OK          OK             OK                  FAILED                untested         untested
```

Three evidence classes must never be merged: **ANALYTIC** (derived vectors, criterion did
not fire), **EMPIRICAL** (real lab, criterion **FIRED**), **BLOCKED/UNRUN** (Wayland,
adaptive red-team, A9). Where the arms disagree the empirical arm governs — and they
disagreed on 13b in the **unsafe** direction.

---

**Phase I EMPIRICAL arm — detail.**

| Freeze | |
|---|---|
| analytic arm | tag `phase1-analytic-v1`, commit `fa78c2d` — preserved unrewritten |
| empirical arm | see `outputs/phase1_empirical_report.md` |

Headline: case `13b` produced a **FALSE ACCEPT** (`AUTHENTIC_TARGET`) at the strongest
practically collectable field set and at the full ladder, from an **unprivileged**
attacker, with **no compromise** of the recorder/kernel/compositor boundary. A legitimate
viewer was opened on the **declared target path** and that file's **bytes were swapped**
for agent-authored pixels. The contract's resource lineage is **path-level**; the attack is
**content-level**. No field was added in response.

Two further boundaries, both empirically demonstrated:
- **S1 atomicity**: the invariant was violated in **120/120 trials** (113 hard
  pixel/metadata mismatches; 118–170 ms skew). Tier D's precondition does not hold as
  implemented.
- **S2 nested display**: provenance terminates at `/usr/bin/Xephyr`; the inner scene is
  invisible to the outer recorder, with zero field observation failures.

**The analytic arm was falsified in the unsafe direction**: 127/169 agreement (75.1%), with
**5 pairs moving UNKNOWN → AUTHENTIC_TARGET**, including the headline case.

**Largest single measured effect is policy, not mechanism**: crediting UNKNOWN (MODE 1)
gives 100% exposure below Tier D and 27.3% at the strongest tier; refusing to credit it
(MODE 2) gives 0% and 9.1%.

**Wayland arm NOT run** — external validity to Wayland unknown.

---

**Earlier: Phase I analytic arm (contract-logic). Kill criterion did NOT fire there.**

### Phase I result in one paragraph

Zero false accepts and zero false rejects at every tier configuration, including the
strongest practically collectable set. The contract never *accepts* fabricated evidence.
But `13b` — a legitimate image viewer opened bare and pointed at an agent-authored file
through the GUI rather than argv — is **undetected at every configuration including the
full ladder**, by abstention. **The assurance ceiling is the displayed RESOURCE, not the
displaying PROCESS.** The contract's entire safety margin is abstention, which is worth
nothing unless the evaluator actions UNKNOWN.

**Scope limit that governs every Phase I number:** this was a CONTRACT-LOGIC evaluation.
The analysis host has no X11, compositor, `gnome-screenshot` or privileged recorder, so
**no process was launched and no pixel was captured**; field vectors are analyst-derived.
Cases S1 (recorder atomicity race) and S2 (nested compositor) are **BLOCKED/unrun**, and
the Wayland arm is unrun. Recorder atomicity is **assumed, not demonstrated**.

Key numbers: coverage 86.7% at `0+A+B+C+D+E`; Tier A alone **0.0%**; Tier D alone 6.7%;
Tier B alone 66.7%; without a privileged browser channel coverage falls to 80.0% and case
05 joins 13b as undetected. Predictions 10/15 matched, all 5 misses in the same direction
(predicted false accepts, got abstentions).

---

**Earlier: gate RESOLVED (negative), converted into an observability boundary, threat
model, and candidate capture-provenance contract.**

Read in this order:
1. `outputs/post_gate_summary.md` — the nine-point state of the project
2. `research/OBSERVABILITY_BOUNDARY.md` — the research result
3. `research/THREAT_MODEL.md` — the adversary
4. `specs/CAPTURE_PROVENANCE_CONTRACT.md` — candidate fields
5. `outputs/adversarial_experiment_report.md` — Phase I result (contract-logic arm)

### Frozen audit

| | |
|---|---|
| commit | `f8e23a57e37a55306f77280e7cc453d0b64d4be4` |
| tag | `recoverability-audit-v1` |
| repo root | this repository root (historically nested inside a separate, uncommitted parent workspace) |
| contents | 35 files, 1.0 MB; `outputs/raw/` (1.7 GB) and `outputs/cache/` gitignored |

Phase-A reproduction before freezing: **10/10 headline figures re-derived exactly** from
`outputs/recoverability_cases.csv`. **One correction (E029):** the lookback sweep in report
§5.2 had been computed with the pre-correction resolver and read 5.5%→72.7%; recomputed
against the final resolver it is **4.8%→54.9%**, with the EXACT/STRONG sub-curve nearly flat
at 2.4%→11.9%. That strengthens the conclusion.

### Headline (MEASURED FACT, 117 traces, 453 delivered visual artifacts)

- R0 quote localization 181/257 = 70.4%
- R1 producer recovery 40/40 = 100%
- R2 artifact linkage 453/453
- R3 capture-source **EXACT 0**, STRONG 26/394 = 6.6%
- R4 scene lineage 81/453 = 17.9%
- R5 target reachability 38/453 = 8.4%
- direct-write 58/59 = 98.3% vs shell-routed capture 23/388 = 5.9% (23/394 = 5.8% of all captures)
- negative-control false attribution 0/99, 0/73

Audit kill criteria **2, 3, 5** triggered. **E011 REJECTED.**

### Post-gate result (Phases C–I)

- 415 of 453 artifacts unresolved; **287 capture-addressable**, 98 no task-defined target,
  30 derivation chains.
- Deficits are **conjunctive**: in the strict model **no single field resolves any case**
  (E031 — an independent-field encoding wrongly reported 83.6% for one field and was
  discarded).
- Coverage is reported as three nested outcomes (preflight): the four display-composition
  fields give 70.6% scene-source resolution and **0.0% target/substitute adjudication**;
  six fields adjudicate 83.6%, seven 93.0% (E041). The old "83.6% resolved by four fields"
  is **withdrawn**.
- `CAPTURE_TRIGGER_ACTION_ID` alone closes 81% of deficits and adjudicates 0% (E042).
- **Display composition dominates** the deficits (240/287) but adjudicates nothing alone.
- `WINDOW_TITLE` / `WM_CLASS` resolve **zero** cases and are agent-choosable (E034, E049).
- **13 of 14** adversary capabilities were observed in the benign corpus; C5 (WM_CLASS
  spoofing) is derived, not observed (E037).

## What exists on disk

| File | Role |
|---|---|
| `scripts/remote_zip.py` | selective ZIP member reads over HTTP range requests |
| `scripts/fetch_members.py` | fetch archive members + source manifest with SHA-256 |
| `scripts/fetch_tasks.py` | fetch WeaveBench task specs (judge-independent targets) |
| `scripts/trace_model.py` | `chat.jsonl` → ordered Event list; canonical tool renderings |
| `scripts/quote_locator.py` | deterministic L0–L6 match ladder |
| `scripts/task_spec.py` | deliverables, target apps, capture-vs-synthesis obligation |
| `scripts/scene_provenance.py` | R1–R5 reconstruction, edge confidences |
| `scripts/run_audit.py` | → `recoverability_cases.csv` |
| `scripts/audit_metrics.py` | → `audit_metrics.json` |
| `scripts/information_deficits.py` | Phase C → `information_deficits.csv` (bundles) |
| `scripts/field_coverage.py` | Phase D → `field_coverage.csv` (3 outcomes, bundle-aware set cover) |
| `scripts/adversarial_cases.py` | Phase I predeclared cases + observed field vectors |
| `scripts/adjudicator.py` | contract rules, deterministic, no LLM |
| `scripts/run_adversarial.py` | Phase I analytic matrix → 4 output files |
| `scripts/score_empirical.py` | Phase I empirical scoring → 5 output files |
| `scripts/freeze_phase1.py` | Phase I closure → `phase1_final_metrics.json` |
| `infra/Dockerfile` + `entrypoint.sh` | reproducible headless X11 lab (Xvfb + Openbox) |
| `infra/recorder.py` | trusted recorder; derives every field from live state |
| `infra/scenarios.py` | attack constructors, run unprivileged |
| `infra/race_s1.py`, `infra/nested_s2.py` | S1 atomicity race, S2 nested display |
| `infra/test_isolation.py` | proves the adjudicator cannot read ground truth |
| `infra/IMPLEMENTATION_CORRECTIONS.md` | IC-1..IC-4, documented before re-running |

Outputs: `source_manifest.csv` (697), `recoverability_cases.csv` (825 rows),
`recoverability_report.md`, `audit_metrics.json`, `information_deficits.csv`,
`field_coverage.csv`, `field_set_analysis.md`, `post_gate_summary.md`,
`adversarial_cases.csv`, `tier_results.csv`, `risk_coverage.csv`,
`adversarial_metrics.json`, `adversarial_experiment_report.md`.
Raw data `outputs/raw/`, caches `outputs/cache/` — both gitignored.

## Key facts a fresh session must not re-derive

- Trace schema: `{id,parentId,timestamp,type,message}`; `message.role` ∈
  assistant/toolResult/user; assistant content carries `toolCall` parts; `toolCallId` links
  call↔result **exactly**.
- Tools: `exec`, `read`, `write`, `edit`, `__computer__`, `process`, `image`, `browser`,
  `web_fetch`, `memory_search`.
- `__computer__` has **no screenshot action** — a screenshot is a side effect of every GUI
  action (2,118 across 115 traces), stored under `_screenshots/`, not addressable as a
  deliverable.
- The `image` tool is an **agent-side VLM call**. Never used for provenance decisions.
- `browser` tool is disabled in this runtime.
- `wmctrl`/`xdotool` absent; `xwininfo` in 12/117 traces; focus control in 4/117;
  125/145 captures full-screen.
- Judge quotes are not verbatim: 28% contain `...`; tool calls cited as `read <path>`,
  `write <path> <content>`, `edit new_string: …`.

## Do not repeat these mistakes

1. A preceding `python x.py` launch is **not** a scene source unless the authored file is
   GUI-capable — three claims refuted by headless CLI scripts and a web server.
2. `Command still running (session …, pid …)` goes stale; a later `Process exited with
   code 0` invalidates it.
3. Full-screen capture makes the scene a **set**, not one process.
4. `DIRECT_SYNTHESIS` is not fabrication — check the capture-vs-synthesis obligation.
5. Harness screenshots are not delivered evidence; including them inflates R5.
6. `code --list-extensions` is not a GUI launch.
7. **Do not score deficit fields independently** — they are conjunctive (E031).
8. **Do not quote a recoverability number without the lookback sensitivity curve** (E020).
9. **A field is not secure because it comes from the OS** — kernel- and compositor-observed
   fields are truthfully reported and adversarially chosen (`THREAT_MODEL.md` §3).
10. **Do not conflate abstention with detection.** Phase I's zero false accepts come from
    abstain-by-default; `13b` is undetected, not caught (E047, E048).
11. **Do not add fields to catch `13b`.** The ceiling is a result.

## Next actions

**Phase I is closed. Do NOT patch the contract to catch 13b — the failure IS the result.**

The single highest-value next step is to test the recorded threat to the 13b mechanism:

1. **Build a filesystem-EVENT-based journal (inotify/fanotify) and re-run 13b.** The
   current journal was write-API-keyed and never saw the `cp` (E066). If an event-based
   journal catches it, the mechanism is narrower than stated — the criterion still fired,
   but the boundary claim must be re-scoped. If it does not, the boundary hardens.
2. **Decide the escalation** from the predeclared options: application-specific state
   attestation, trusted-display mechanisms, an independent outcome oracle, or that this
   layer cannot establish the property.
3. **Fail-closed UNKNOWN is actionable now and independent of the contract** (E069) — but
   note it does not touch 13b.
4. **Atomicity is an engineering question.** S1 measured one naive recorder; a server-side
   grab or atomic snapshot primitive must be built and re-measured before Tier D is
   credited with anything.
5. **Wayland arm** still unrun. **Adaptive red-teaming** still unrun; the suite is nowhere
   near saturated — 13b only became a real attack after IC-4 corrected its construction.

H-RB is registered as a documented option and must **not** be executed until Phase I
closure is committed and a successor contract is predeclared.

## Blocked / not done

- **Two independent annotators.** Manual validation is single-reviewer; it refuted 4 of the
  first 7 automated claims and drove three rule corrections, but **no inter-rater statistic
  exists**. Never describe it as completed two-reviewer validation.
- **Empirical arm of the adversarial evaluation not run**; no recorder built; no
  classifier built. The contract-logic arm ran (17 of 19 cases; 2 blocked).
- **Recorder atomicity assumed, not demonstrated** (S1 blocked; repeated-trial requirement
  unmet).
- ProcGrep untouched. No BPE. No application prose.
- Tier D portability to Wayland unresolved (a real deployment blocker).
- No privacy-minimisation story for visible-window-set + titles + argv + URLs.

---

# Current status — 2026-09-10 (supersedes the 2026-09-09 "next step" list above)

**PHASE J COMPLETE. TECHNICAL EXPANSION STOPPED. THE PROJECT IS IN PACKAGING.**

**Read first: `research/FROZEN_FINDINGS.md`** — the seven frozen findings, each with its
evidence class, evidence IDs, scope and explicit non-claims. That file is the research
package. Then `outputs/final_research_board.md`, `research/13B_STATIC_CLASSIFICATION.md`,
`research/EPISTEMIC_POLICY.md`, `outputs/x11_wayland_comparison.md`.

**H-RB is NOT opened**, and its naive form is already bounded by E082.

Phase J had exactly two objectives. Both resolved, and both in the same direction.

## 1. 13b is classified — CONTRACT_UNDERSPECIFICATION

Resolved **statically**, over the frozen adjudicator, with nothing frozen modified. The
replay reproduces the Phase I verdicts at all 13 configurations rule-for-rule (E072).

- Injecting the single missed write flips 13b to `SUBSTITUTE` at every Tier-D-inclusive
  configuration (E073) — so the adjudicator already had a correct rule and the recorder
  simply did not observe the fact.
- But that fact has **exactly one consumer**, and it is the contract's own least-deployable
  field. In the default deployment the fact is unrepresentable and changes nothing (E074).
- And the same fact turns the **honest control into a false reject** (E075), because the
  contract has no field distinguishing a task-mandated write from an adversarial one.
- The decisive defect: the contract defines lineage as a **binary** predicate, so absence of
  observation is emitted as the positive claim `pre_existing`, and abstain-by-default
  **cannot fire** because the field is never missing (E076).

Secondary findings recorded, not discarded: **B′** (within the optimistic configuration it
is a recorder observation gap) and **C′** (identity and provenance are fused into one field;
the adjudicator sources identity from argv and silently drops the provenance requirement —
E077).

**The Phase I kill criterion still fired on its own predeclared terms. Nothing was
reinterpreted, and the frozen contract was not touched.**

## 2. Wayland changes who observes, not what can be bound

Two predeclared cases, both platforms, zero field observation failures, capture hashes
reproducible byte-identically across container runs.

> **Zero of twelve comparable bindings changed evidence level between X11 and Wayland**
> (E079).

- The standard portal offers **no window source at all**: `AvailableSourceTypes = 1`
  (MONITOR only), and the `Screenshot` interface is absent on that backend (E080). The
  predeclared expectation that Wayland would strengthen `capture → surface` is **REFUTED**
  for the standard path.
- `app_id` is client-asserted and spoofable exactly as `WM_CLASS` is (E081).
- Open file descriptors at the capture instant reveal **nothing** about the displayed
  resource — `eog` had already closed the file (E082).
- Wayland *does* improve capture-path integrity and the directness of `surface → process`,
  and it *worsens* standardisation: cross-client enumeration exists only through
  compositor-private IPC (E083).
- Portal **stream metadata is BLOCKED**, not negative — PipeWire format negotiation failed
  on a headless no-DRM container. Not inferred from documentation (E084).

## Implementation corrections in the Phase J lab

**IC-5** and **IC-6**, documented before re-running affected cases
(`infra/wayland_lab/IMPLEMENTATION_CORRECTIONS.md`). IC-5 was a defect in the
**construction-time ground truth**, not in the measurement: `shell=True` forked the client so
the Wayland surface check matched the shell's pid, recording `viewer_binary: null` while the
recorder independently observed genuine `/usr/bin/eog` running. It was caught only because
the recorder observes independently of the constructor.

**The result is stable across both corrections** — all four capture sha256 values identical
before and after, binding matrix unchanged at 0/12 (E086, E087). The frozen Phase I
corrections file was not edited.

## The assurance chain, after Phase J

```
artifact ─► capture ─► process/surface ─► displayed resource ─► app state ─► claim
   ✅         ✅             ✅                   ❌               untested    untested
                                          SAME EDGE ON BOTH
                                          X11 AND WAYLAND
```

Links 1–3 hold on both platforms. **Link 4 fails identically on both.** Links 5–6 were never
reached, and nothing in Phase J is progress on them.

## What Phase J deliberately did NOT do

- **No filesystem telemetry ladder** (J0/J1/J2). No eBPF recorder, no fanotify framework, no
  inotify study. Process/file/runtime provenance is occupied prior art, and E082 measured
  that even fd inspection at the capture instant does not reach the displayed resource.
- **No contract modification.** The frozen contract, adjudicator and recorder are untouched;
  their sha256 values are recorded with the trace.
- **No new phase opened.** H-RB remains registered and unexecuted.

## STOP RULE — in force

Per the predeclared stop rule, technical expansion **stops here**. Do not open H-RB,
application-state attestation, adaptive red-teaming, more operating systems, more
compositors, more benchmark tasks, ProcGrep modifications, or another provenance framework.

The single result that would justify reopening is specific and cheap to check:

> a compositor whose portal implements **window-source** capture **and** reports the
> selected source's client identity to the caller — i.e. GNOME's or KDE's portal backend,
> which were **not tested**.

That would change the Case P cell and only that cell. It does not change link 4.

## Blocked / not done — carried forward, still true

- Two independent annotators: still single-reviewer; **no inter-rater statistic exists**.
- Portal ScreenCast stream metadata: **BLOCKED** (E084).
- Nested-compositor analogue of S2 on Wayland: **not tested**.
- GNOME/KDE portal backends: **not tested**.
- A9 application-state attack: never exercised.
- Adaptive red-teaming: never run; the suite is not saturated.
- Atomicity remains a recorder-architecture question, not a platform property. The lower
  Wayland skew comparison is **WITHDRAWN as not reproducible** — the ranges moved materially
  between re-runs of the same image. Skew is a property of recorder architecture and machine
  load, not of the platform.
- ProcGrep untouched. No BPE. No application prose.
- No privacy-minimisation story for visible-window-set + titles + argv + URLs.
