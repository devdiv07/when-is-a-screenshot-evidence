# Research Question

## Candidate thesis — NOT YET CONFIRMED

Hybrid computer-use agent traces may contain enough structural evidence to distinguish visual evidence that is causally descended from the task's target application state from evidence that is synthesized or captured from agent-created substitute state.

## Core research question

Can scene/evidence provenance be reconstructed from hybrid-agent trajectories with sufficient coverage, precision, and auditability to support evaluation without requiring an LLM judge to semantically infer authenticity?

## Why file provenance is insufficient

These cases differ:

A. target application -> rendered target state -> screenshot -> delivered PNG

B. Python/PIL -> PNG

C. agent-created Tk/HTML/fake renderer -> rendered fake scene -> genuine screenshot -> delivered PNG

File-level provenance can separate A/B but may misclassify C as genuine capture.

The candidate instrument must reason about **scene lineage**, not only file generation.

## Recoverability hypothesis

H-R:

> For a substantial fraction of judge-localized fabrication cases, the raw trace contains enough exact structural evidence to reconstruct the critical producer/scene lineage without a VLM or LLM semantic judgment.

### Falsification

H-R fails if:
- producer commands cannot be linked reliably to delivered artifacts;
- captured images cannot be associated with an identifiable displayed process/scene;
- target application identity cannot be distinguished from agent-created substitute renderers;
- the necessary dependency edges require semantic inference unavailable from structural trace evidence;
- or recoverability is too selective to support a useful instrument.

If H-R fails, do not rescue the project by substituting an LLM judge and calling it structural provenance.

## Later mechanism hypothesis — NOT FOR THE FIRST GATE

Only if H-R survives:

> Authentic vs fabricated visual evidence differs in the structure of artifact mutation, scene observation, verification, correction, and evidence production, beyond simple observation volume and runtime.

This later question must use independent human/mechanical labels and must challenge generic execution-discipline explanations.
