# Field-Set Coverage Analysis

Phase D. Derived from `outputs/information_deficits.csv` by `scripts/field_coverage.py`.
Machine-readable results: `outputs/field_coverage.csv`.

> **Scope warning, applies to every number below.**
> This is **HISTORICAL** analysis of benign traces already collected. It says nothing about
> whether a field survives a contract-aware adversary. That is the
> **white-box adversarial case evaluation** (`specs/ADVERSARIAL_SUFFICIENCY_EXPERIMENT.md`).

---

## 1. Three outcomes, not one

Earlier drafts said a field bundle "resolved" a case and reported *83.6% of cases resolved
by four fields*. **That claim is withdrawn.** It conflated three separate things, and the
strongest of them was never measured. The contract itself states that complete
display-composition metadata can leave a composite scene genuinely UNKNOWN, so "resolved"
was never the right word.

The three are now scored separately and are strictly nested:

| | Concept | What it means |
|---|---|---|
| 1 | **INFORMATION_DEFICIT_CLOSURE** | the historically missing fields would no longer be missing |
| 2 | **SCENE_SOURCE_RESOLUTION** | the evidence identifies which process / resource / display surface contributed the relevant captured pixels |
| 3 | **TARGET/SUBSTITUTE_ADJUDICATION** | the evidence decides whether that scene corresponds to the **declared** task target |

Closure is necessary for resolution; resolution is necessary for adjudication.
Adjudication additionally requires a **declared target** (Tier 0). Where no target is
declared, adjudication is **UNKNOWN** — never "failed".

### Why the split matters immediately

`CAPTURE_TRIGGER_ACTION_ID` — a single field that binds an image file to the action that
produced it — **closes 81.0% of information deficits on its own** and **adjudicates 0%**.
It is artifact provenance, which the frozen audit already recovers at 453/453. A "coverage"
metric on which that field scores 81% is measuring the wrong thing. That is the clearest
demonstration that closure is a weak concept and adjudication is the one that answers the
project's question.

## 2. Populations

| Universe | n | Excludes |
|---|---|---|
| unresolved cases | 415 | — |
| **scene-source universe** | **385** | 30 derivation chains (lineage recurses out of the capture layer) |
| **adjudication universe** | **287** | additionally the 98 cases with no declared target |

The 98 no-declared-target cases are not a rounding detail. They are the empirical
demonstration behind **Tier 0** in the contract: provenance cannot adjudicate
target-vs-substitute without a declared target, no matter how good the telemetry.

## 3. Fields are conjunctive

**No single field achieves resolution or adjudication alone.** `Z_ORDER` without
`VISIBLE_WINDOW_SET` is "stacking order of what?", and neither intersects the image without
`CAPTURE_REGION`. An earlier encoding scored fields independently and produced an 83.6%
single-field figure that was an artifact of the encoding; it was discarded. Deficits are
recorded as conjunctive **bundles**, and a case counts only when a whole bundle is supplied.

## 4. The headline correction

| Field set | closure (of 385) | scene-source resolution (of 385) | **adjudication (of 287)** |
|---|---|---|---|
| **D4 display-composition** — capture region, visible set, geometry, z-order | 272 / **70.6%** | 272 / **70.6%** | **0 / 0.0%** |
| D4 + active window + active pid (6) | 312 / 81.0% | 312 / 81.0% | 240 / **83.6%** |
| + lifecycle + start identity (8) | 371 / 96.4% | 339 / 88.1% | 267 / **93.0%** |

**The four display-composition fields adjudicate nothing.** They determine which surfaces
contributed pixels, and then stop: nothing binds a contributing surface to an identity
comparable with a declared target. Adjudication needs process identity
(`ACTIVE_PID`, and in interpreter cases `COMMAND_LINE`) on top of the display fields.

So the corrected statement of the old headline is:

> **83.6% of eligible cases had their recorded display-composition information deficit
> closed by four fields** — and of those, **0%** could be adjudicated target-vs-substitute
> without also binding surface to process identity. Six fields adjudicate 83.6% of the
> adjudication universe; seven reach 93.0%.

Note the denominators differ (385 vs 287) and are not interchangeable.

## 5. Curves

### Adjudication — the operative one

| fields | set | of 287 |
|---|---|---|
| 6 | capture region + visible set + geometry + z-order + active window + active pid | **83.6%** |
| 7 | + process lifecycle at capture | **93.0%** |
| 9 | + agent-written code lineage + command line | 95.1% |

Thresholds: 50% and 75% both first crossed at **6 fields**; 90% at **7**.
Brute force to size 7 confirms greedy is optimal at sizes 6 and 7 (gap 0); sizes 1–5
adjudicate **0.0%**, because no subset that small contains both a display bundle and a
process binding.

### Scene-source resolution

| fields | set | of 385 |
|---|---|---|
| 4 | D4 display-composition | 70.6% |
| 6 | + active window + active pid | 81.0% |
| 8 | + lifecycle + start identity | 88.1% |

A lenient variant (counting `uncertain` bundles, chiefly the assumption that focus identity
settles a full-screen grab) reaches 70.6% with **three** cheap fields. The audit refuted
that assumption on real data (`view_dashboard_and_editor.png`). **Quote the strict column.**

### Closure — reported for completeness, not for decisions

81.0% from one field; 91.7% from four. Closure says the recorder wrote something down. It
does not say the something was useful.

## 6. Bundle inventory

| eligible cases | bundle (all fields required together) | resolution | adjudication |
|---|---|---|---|
| 240 | capture region + visible set + geometry + z-order + active window + active pid | yes | yes |
| 272 | capture region + visible set + geometry + z-order | yes | **no** — no identity binding |
| 41 | active window + active pid + lifecycle at capture | uncertain | no |
| 38 | tab id + URL + active window + **displayed-resource lineage** | yes | yes |
| 36 | lifecycle at capture + process start identity | no | no |
| 25 | active pid + command line | uncertain | no |
| 272 | window title + WM_CLASS | **no** | no |
| 312 | capture trigger action id | **no** | no |

`DISPLAYED_RESOURCE_LINEAGE` is new in this pass. It exists because a legitimate viewer
showing agent-authored content (threat-model **A13**, the generic form of A4) is not
addressed by tab id and URL alone: those fields truthfully report a resource whose own
provenance is the actual question.

## 7. What this licenses

**Supported (MEASURED FACT, historical):**

- Six fields would have adjudicated 83.6% of the adjudication universe; seven, 93.0%.
- Display composition alone adjudicates **nothing**.
- No single field achieves resolution or adjudication.
- `WINDOW_TITLE` / `WM_CLASS` achieve neither, in any combination. They were already present
  in the 12 traces carrying `xwininfo` and did not resolve those cases.
- Adjudication is impossible without a declared target, for 98 cases in this corpus.

**Not supported:**

- That these fields make visual evidence trustworthy. Coverage was measured on agents not
  trying to defeat a recorder; several made attribution possible by accident.
- Any false-accept rate. There are no adversarial cases in this analysis.
- Practical deployability. Display composition leans on X11 enumeration; Wayland restricts
  exactly these queries.

## 8. Input to the contract

| Contract tier | Fields | Historical basis |
|---|---|---|
| **0 claim / target context** | task id, evidence claim id, target kind/application/resource, modality, capture scope | **98 cases** where adjudication is impossible without it |
| A window labels | title, WM_CLASS | **0** for every outcome — baseline that fails |
| B process identity | pid, start identity, argv, exe, ppid | required for **all** adjudication; +25 for interpreter cases |
| C code/resource lineage | agent-written lineage, content hash, displayed-resource lineage | 14 + 30 chains + 38 browser/viewer cases |
| D display composition | capture region, visible set, z-order, geometry, active window | **240 — dominant, but adjudicates 0 alone** |
| E application state | browser tab, URL, document identity | 38 + 41 |
| F record integrity | signature, privileged recorder, TEE | **0 — threat model only** |
