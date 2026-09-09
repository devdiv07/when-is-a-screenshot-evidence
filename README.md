# Scene Provenance Lab

Evidence-first research workspace for auditing visual evidence provenance in hybrid computer-use agent traces.

## Current target

The immediate research question is **not** "can we detect reward hacking with screenshots?" and not "should agents render more?"

The current gate is narrower:

> Can the provenance of delivered visual evidence be reconstructed structurally from a hybrid-agent trace strongly enough to distinguish evidence that descends from the task's target application state from evidence that descends from agent-created substitute state?

This is a **recoverability question** before it is a modeling question.

## First execution

1. Read `CLAUDE.md`.
2. Read `CURRENT_STATE.md`.
3. Read `specs/RECOVERABILITY_AUDIT.md`.
4. Read `research/PRIOR_ART.md`.
5. Invoke `/provenance-recoverability` or paste `PROMPT_FIRST_RUN.md`.
6. Work only on the recoverability audit until its gate is resolved.
7. Do not build a general framework, ProcGrep extension, paper, or fellowship application yet.

## Hard stop

If scene provenance cannot be recovered from trace-derived structural evidence at useful coverage and only an LLM semantic judge can decide it, record that as a negative result. Do not manufacture a more complex system to save the thesis.

## Data already included

`data/weavebench_gpt54_low_joined.csv` contains the joined score-level reconnaissance for GPT-5.4 low run1/run2.

Raw `chat.jsonl` traces are intentionally not included yet. The first operational task is to retrieve the relevant trace members efficiently, preferably using HTTP range access / selective ZIP member extraction rather than full multi-GB archive download when technically reliable.
