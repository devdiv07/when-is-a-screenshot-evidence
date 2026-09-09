---
name: evidence-first-research
description: Evidence-led research protocol for this project. Use when evaluating claims, changing the research thesis, interpreting experiments, reviewing literature, or deciding whether a result supports a public/application claim.
---

# Evidence-First Research

## Before analysis

Read:
- `CLAUDE.md`
- `research/EVIDENCE_LEDGER.md`
- `research/DECISION_LOG.md`
- `research/PRIOR_ART.md`

## Claim discipline

Label every material claim as:
- VERIFIED FACT
- MEASURED FACT
- INFERENCE
- HYPOTHESIS
- UNKNOWN

A filename, benchmark label, LLM-judge output, or plausible interpretation is not ground truth by default.

## Counter-research

For every proposed gap, search:
1. exact mechanism;
2. adjacent terminology;
3. prior systems with different naming;
4. newest papers after the current board;
5. counterexamples that would make the claim less novel.

Do not use "first", "novel", "nobody", or equivalent language without targeted prior-art evidence.

## Measurement audit

Before trusting an effect:
- audit how both predictor and outcome are produced;
- identify shared evaluator/apparatus coupling;
- inspect missingness;
- check task/model/harness confounds;
- add negative controls;
- distinguish rerun instability from label unreliability;
- preserve null/invalid results.

## Decision rule

Only change the project thesis when new evidence changes the board.

Record the decision and what would reopen it.

## Output

Update the Evidence Ledger and Decision Log before finishing a research-changing task.
