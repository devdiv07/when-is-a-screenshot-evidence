# Progress

## Current status — 2026-09-09

**Gate RESOLVED (negative). Negative result converted into an observability boundary,
threat model, and candidate capture-provenance contract. Direction = MODIFY.**

Read in this order:
1. `outputs/post_gate_summary.md` — the nine-point state of the project
2. `research/OBSERVABILITY_BOUNDARY.md` — the research result
3. `research/THREAT_MODEL.md` — the adversary
4. `specs/CAPTURE_PROVENANCE_CONTRACT.md` — candidate fields
5. `specs/ADVERSARIAL_SUFFICIENCY_EXPERIMENT.md` — the falsification test (**not run**)

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
- Historical coverage, STRICT: **4 display-composition fields → 83.6%**, 6 → 90.2%,
  8 → 99.7%. Greedy optimal at sizes 4 and 6 by brute force.
- **Display composition dominates** (240/287), because a full-screen grab's scene is a
  *set* of windows.
- `WINDOW_TITLE` / `WM_CLASS` resolve **zero** cases and are agent-choosable (E034).
- All 14 adversary capabilities in the threat model were **observed in the benign corpus**
  (E037).

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
| `scripts/field_coverage.py` | Phase D → `field_coverage.csv` (bundle-aware set cover) |

Outputs: `source_manifest.csv` (697), `recoverability_cases.csv` (825 rows),
`recoverability_report.md`, `audit_metrics.json`, `information_deficits.csv`,
`field_coverage.csv`, `field_set_analysis.md`, `post_gate_summary.md`.
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
9. **A field is not secure because it comes from the OS** — T4 fields are truthfully
   reported and adversarially chosen (`THREAT_MODEL.md` §3).

## Next actions

1. Run `specs/ADVERSARIAL_SUFFICIENCY_EXPERIMENT.md` — 12 predeclared cases + 4 stretch,
   construction-time ground truth, per-tier false accept / false reject / abstention /
   coverage. **Requires building the instrumented environment and recorder first.**
2. Honour the predeclared kill criterion. P6 predicts it fires on case 10. **If it fires,
   that is the result** — do not add fields until it stops.
3. Treat a clean sweep as suspicious (weak adversary) before believing it.

## Blocked / not done

- **Two independent annotators.** Manual validation is single-reviewer; it refuted 4 of the
  first 7 automated claims and drove three rule corrections, but **no inter-rater statistic
  exists**. Never describe it as completed two-reviewer validation.
- Adversarial experiment **not run**; no recorder built; no classifier built.
- ProcGrep untouched. No BPE. No application prose.
- Tier D portability to Wayland unresolved (a real deployment blocker).
- No privacy-minimisation story for visible-window-set + titles + argv + URLs.
