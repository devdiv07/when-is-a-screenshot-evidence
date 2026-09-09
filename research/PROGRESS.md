# Progress

## Current status — 2026-09-09

**Phase I executed (contract-logic arm). Kill criterion did NOT fire. Assurance ceiling
identified. Direction = MODIFY, unchanged.**

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
| repo root | `C:/Users/ASUS/Desktop/scene-provenance-lab/scene-provenance-lab` (nested; the parent repo at `Desktop/scene-provenance-lab` was deliberately NOT committed into) |
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
- direct-write 98.3% vs shell-routed capture 5.9%
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
| `scripts/run_adversarial.py` | Phase I matrix → 4 output files |

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

**Do NOT add fields to catch 13b.** The ceiling is a result, not a defect list.

1. **Build the empirical arm.** An instrumented X11 host with a privileged recorder, then
   re-run the 17 evaluable cases against real observations to test whether a real recorder
   sees what the contract-logic arm assumed.
2. **Run the two blocked cases.** S1 (recorder atomicity, with repeated trials as the spec
   requires) and S2 (nested compositor). Either could invalidate Tier D wholesale.
3. **Run the Wayland arm** — Tier D leans on X11 enumeration that Wayland restricts.
4. **Determine whether an evaluator can action UNKNOWN.** The contract's whole safety
   margin is abstention; if unadjudicated evidence is accepted by default, the margin is
   zero. This is an evaluator-design question, not a contract question.
5. Adaptive red-teaming only after the empirical arm exists. The suite is not saturated:
   `13b` was found only because the spec asked for an evasive variant.

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
