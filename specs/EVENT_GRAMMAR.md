# Event Grammar — Later Extractor

Do not implement the full grammar before the recoverability audit passes.

Candidate coarse events:

- M — target artifact mutation
- P — target artifact / application presented or observed
- V — explicit verification or comparison
- R — corrective mutation after observation
- G — genuine capture action
- F — synthetic visual evidence generation
- T — transformation/derivation of prior evidence
- H — premature halt
- S — submit/finalize

## Provenance channel annotations

Every visual-producing event should also record:

- native GUI tool
- shell screenshot
- browser capture
- PIL / graphics synthesis
- Tk/HTML/custom renderer
- ImageMagick transform
- copy/move/stage
- unknown

## Do not infer cognition

P means a relevant state was structurally presented/available in the trace, not that the model internally attended to or understood it.

V requires stronger evidence than a returned screenshot. Examples may include:
- explicit comparison action;
- use of a visual diff/evaluator;
- subsequent corrective action clearly keyed to the presented state.

Definitions must be validated on real traces before freezing.
