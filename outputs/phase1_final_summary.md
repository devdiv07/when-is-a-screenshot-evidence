# Phase I — Final Summary

**CLOSED. Kill criterion FIRED. Capture-provenance contract branch: INSUFFICIENT.**

Tags: `phase1-analytic-v1` (`fa78c2d`) · `phase1-empirical-v1`
Detail: `research/PHASE1_EMPIRICAL_CONCLUSIONS.md` · `outputs/phase1_final_metrics.json`

---

## Result in one line

A legitimate viewer, opened on the **declared target path**, displaying **attacker-swapped
bytes**, was accepted as **`AUTHENTIC_TARGET`** at the full attestation ladder — from an
unprivileged attacker, with no recorder, kernel or compositor compromise.

## Three evidence classes — never merge these

| Class | What it is | Kill criterion |
|---|---|---|
| **ANALYTIC** | contract logic over **analyst-derived** field vectors. No process launched, no pixel captured. | did **not** fire |
| **EMPIRICAL** | real Xvfb X11, Openbox, real Tk/ImageMagick windows, real pixel grabs, unprivileged attacker (uid 1000), independent privileged recorder (root + `CAP_SYS_PTRACE`) | **FIRED** |
| **BLOCKED / UNRUN** | Wayland arm; adaptive red-teaming; A9 application-state attack | not evaluated |

Where the two arms disagree, **the empirical arm governs**.

## Final empirical numbers — `0+A+B+C+D+E`

| Metric | Value |
|---|---|
| scenarios | 13 (1 authentic, 11 substitute, 1 ambiguous) |
| **false accepts** | **1 — `13b_viewer_agent_image_hidden`** |
| false rejects | 0 |
| coverage | 76.9% |
| secure coverage | 69.2% |
| abstention rate | 23.1% |
| MODE 1 permissive exposure | 27.3% |
| MODE 2 fail-closed exposure | 9.1% |

Constructed suite. **Not a population estimate.**

## Three boundaries, each scoped narrowly

**1 — Resource boundary (13b).** Genuine viewer binary, genuine pid/uid 1000, genuine
window, argv naming the declared target, lineage reading `pre_existing`, zero field
observation failures — and attacker-authored content bytes on screen.
`process/surface identity ≠ displayed-resource identity`; `path identity ≠ content identity`.
Fires at every Tier-D-inclusive config.
*Threat to this finding, recorded:* the journal was write-API-keyed and never saw the `cp`;
an inotify-based journal might have caught this instance. The criterion still fired on its
predeclared terms.

**2 — Atomicity (S1).** *The tested recorder implementation* failed to atomically bind
metadata and pixels — **120/120 violations in both of two runs**, skew 105–170 ms. Violation
mode inverted between runs (113/7 vs 7/113); the rate did not. **Not** a claim that atomic
provenance is impossible in principle. Run 1's JSON artifact was not retained; run 2's is.

**3 — Nested display (S2).** *The tested outer recorder* could not recover inner scene
provenance through Xephyr: it resolved the pixels to `/usr/bin/Xephyr` (pid 4391), inner
window invisible, zero observation failures. Untested substrates are not covered.

## The assurance chain

```
artifact ──► capture ──► process/surface ──► displayed resource ──► application state ──► claim
   ✅          ✅              ✅                    ❌                    untested        untested
```

Links 1–3 hold. **Link 4 is where assurance fails.** Links 5–6 were never reached; nothing
here is progress on them.

## Analytic vs empirical

127/169 agree (**75.1%**). Disagreements: 34 `SUBSTITUTE→UNKNOWN`, 3
`AUTHENTIC→UNKNOWN`, and **5 `UNKNOWN→AUTHENTIC_TARGET`** — all of them 13b, all unsafe.

**INFERENCE:** derived field vectors can overstate assurance by supplying semantic
cleanliness and bindings a real recorder cannot obtain. One instance, not a universal
benchmark claim.

## UNKNOWN policy — mechanism ≠ enforcement

Fail-closed UNKNOWN cuts exposure from 100%→0% below Tier D and 27.3%→9.1% at the strongest
tier: the **largest single measured effect**, and it is policy, not a field.

**It does not repair a false `AUTHENTIC_TARGET`. Case 13b survives fail-closed UNKNOWN**,
because 13b was never UNKNOWN — it was accepted.

| Verdict | Handling |
|---|---|
| `AUTHENTIC_TARGET` | may be automatically considered |
| `SUBSTITUTE` | reject / flag |
| `UNKNOWN` | no automatic credit; review or independent verification |

## Discarded runs — excluded from all figures

| Discarded | Invalidated by | Superseded by |
|---|---|---|
| empirical suite on `≤1.6` | **IC-2** — cleanup missed `python3 < script`; a window leaked into 7 scenarios | run on `2.0+` |
| case 13b on `≤2.0` | **IC-4** — 13b put the path in argv and never rendered the fabrication | 13b on `2.1` |
| visible-set PIDs pre-IC-3 | **IC-3** — `wmctrl` returned `pid=0` throughout | X-Resource on `2.0+` |

Four implementation corrections (IC-1…IC-4) are documented in
`infra/IMPLEMENTATION_CORRECTIONS.md`, all written **before** re-running affected cases.
**None changed the frozen contract.**

## Scope note

In the tested Debian/Xvfb/Openbox environment `_NET_WM_PID` was absent on every window and
`wmctrl` returned `pid=0`, requiring X-Resource correlation. **Not claimed universal for
X11** — GTK/Qt commonly set it. The transferable point: it cannot be relied upon, and it is
application-asserted either way.

## Direction

**CLOSED / INSUFFICIENT.** Do not add displayed-resource fields to the frozen contract to
rescue it. Any successor must be predeclared before testing.

**H-RB (documented option, NOT executed):** can application-independent system telemetry
bind displayed pixels to the actual resource bytes consumed by a legitimate renderer?
*Falsifies if* legitimate viewers can display attacker-controlled resources whose
rendered-byte identity cannot be reconstructed from system telemetry — escalating to
application-specific state attestation or an independent outcome oracle.
