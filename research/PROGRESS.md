# Progress

## Current status — 2026-09-09

**The provenance-recoverability gate is RESOLVED, with a negative result for the general construct.**

### Frozen

| | |
|---|---|
| commit | `2e197064f4c2a91de8bd0a4844ea147974ef9237` |
| tag | `recoverability-audit-v1` |
| repo root | `C:/Users/ASUS/Desktop/scene-provenance-lab/scene-provenance-lab` (nested; the parent repo at `Desktop/scene-provenance-lab` was deliberately NOT committed into) |
| contents | 35 files, 1.0 MB; `outputs/raw/` (1.7 GB) and `outputs/cache/` gitignored |

Phase-A reproduction check before freezing: 10/10 headline figures re-derived exactly from `outputs/recoverability_cases.csv`. **One correction**: the lookback sweep in report §5.2 had been computed with the pre-correction resolver and read 5.5%→72.7%; recomputed against the final resolver it is **4.8%→54.9%** (E029). The EXACT/STRONG sub-curve is nearly flat across the sweep (2.4%→11.9%), which strengthens rather than weakens the conclusion.

Read `outputs/recoverability_report.md` first. It is the deliverable.

Headline (MEASURED FACT, 117 traces, 453 delivered visual artifacts):

- R0 quote localization 181/257 = 70.4%
- R1 producer recovery 40/40 = 100% on visual-linked quotes
- R2 artifact linkage 453/453 (444 exact path, 9 templated)
- R3 capture-source: **EXACT 0**, STRONG 26/394 = 6.6%, WEAK 96, UNKNOWN 272
- R4 scene lineage classified 81/453 = 17.9%
- R5 target reachability 38/453 = 8.4%
- shell-routed captures classify at 5.9%; direct-write artifacts at 98.3%
- negative-control false attribution 0/99 (NC-A), 0/73 (NC-B)

Audit kill criteria **2, 3 and 5 are triggered**. E011 is REJECTED.

The result is the boundary itself: **structural artifact/file lineage is recoverable; structural scene lineage is not**, because the WeaveBench desktop never records which window owned the screen at capture time (`wmctrl`/`xdotool` absent; `xwininfo` in 12/117 traces; 125/145 captures full-screen).

## What exists on disk

Pipeline (stdlib + deterministic, no LLM/VLM anywhere):

| File | Role |
|---|---|
| `scripts/remote_zip.py` | selective ZIP member reads over HTTP range requests |
| `scripts/fetch_members.py` | fetch archive members, record source manifest with SHA-256 |
| `scripts/fetch_tasks.py` | fetch WeaveBench task specs (independent target definitions) |
| `scripts/trace_model.py` | `chat.jsonl` → ordered Event list; canonical tool renderings |
| `scripts/quote_locator.py` | deterministic L0–L6 match ladder for judge quotes |
| `scripts/task_spec.py` | required deliverables, target apps, capture-vs-synthesis obligation |
| `scripts/scene_provenance.py` | R1–R5 reconstruction, edge confidences |
| `scripts/run_audit.py` | drives the audit → `recoverability_cases.csv` |
| `scripts/audit_metrics.py` | → `audit_metrics.json` |

Outputs: `outputs/source_manifest.csv` (697 records), `outputs/recoverability_cases.csv` (825 rows), `outputs/recoverability_report.md`, `outputs/audit_metrics.json`.
Raw data under `outputs/raw/` and caches under `outputs/cache/` (both gitignored).

## Key facts a fresh session must not re-derive

- Trace schema: `chat.jsonl` lines are `{id,parentId,timestamp,type,message}`; `message.role` ∈ assistant/toolResult/user; assistant content carries `toolCall` parts; `toolCallId` links call↔result **exactly**.
- Tool vocabulary: `exec`, `read`, `write`, `edit`, `__computer__`, `process`, `image`, `browser`, `web_fetch`, `memory_search`.
- `__computer__` has **no screenshot action** — wait/click/keypress/type/scroll/double_click/move/drag. A screenshot is returned as a side effect of every action (2,118 across 115 traces) and is not addressable as a deliverable.
- The `image` tool is an **agent-side VLM call** (`{image, prompt}` → natural-language answer). Its text was never used to decide provenance; doing so would violate the gate.
- `browser` tool is disabled in this runtime.
- Judge quotes are not verbatim: 28% contain `...` elisions; tool calls are cited as `read <path>`, `write <path> <content>`, `edit new_string: …`, `toolCall: …`.

## Do not repeat these mistakes

Each was caught by manual validation and cost a re-measurement (report Sect. 8):

1. A preceding `python x.py` launch is **not** a scene source unless the authored file is GUI-capable — three claims were refuted by headless CLI scripts and a web server.
2. `Command still running (session …, pid …)` goes stale; a later `Process exited with code 0` invalidates it.
3. Full-screen capture makes the scene a **set**, not one process.
4. `DIRECT_SYNTHESIS` is not fabrication — check the task's capture-vs-synthesis obligation first.
5. Harness screenshots must not be scored as delivered evidence; they cap at R1 and inflate R5 if included.
6. `code --list-extensions` is not a GUI launch.

## Next actions (gate resolved; these are the reframing options)

Per `outputs/recoverability_report.md` §12, in preference order:

1. Write up the boundary as a measurement/limits result with the instrumentation ask.
2. Specify the minimal capture-time provenance record (active window title, WM_CLASS, PID, geometry) and demonstrate UNKNOWN→EXACT conversion on the 12 traces that carry `xwininfo`.
3. Keep the narrow high-precision instrument, always reporting its ~5% recall.

Blocked / not done:

- **Two independent human annotators.** The audit requires them; only single-annotator validation was performed, so no agreement/adjudication statistic exists. Any writeup must say so.
- No full extractor, no ProcGrep change, no BPE, no application prose — all still correctly not started.
