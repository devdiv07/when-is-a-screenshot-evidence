# Post-Gate Summary

State after the provenance-recoverability gate resolved and was converted into an
observability boundary, threat model, and candidate contract.

Frozen audit: commit `f8e23a5`, tag `recoverability-audit-v1`.

---

## 1. What the original hypothesis was

**E011 / H-R:** for a substantial fraction of judge-localized fabrication cases, the raw
WeaveBench trace contains enough exact structural evidence to reconstruct the critical
producer/scene lineage — distinguishing visual evidence descended from the task's target
application state from evidence descended from agent-created substitute state — **without**
a VLM or LLM semantic judgment.

The motivating asymmetry (`RESEARCH_QUESTION.md`): file-level provenance separates
"screenshot" from "PIL synthesis", but misclassifies the third case — a *genuine* screenshot
of an *agent-authored* fake renderer — as authentic.

## 2. Exactly why it failed

It failed at one specific edge. Over 453 delivered visual artifacts in 117 traces:

| Level | Result |
|---|---|
| R1 producer recovered | **40/40 = 100%** |
| R2 artifact linked to delivered file | **453/453** |
| R3 capture source | **EXACT 0**, STRONG 26/394 = **6.6%** |
| R4 scene lineage classified | **81/453 = 17.9%** |
| R5 target reachability | **38/453 = 8.4%** |

Split by channel: direct-write artifacts classify at **98.3%**, shell-routed
`gnome-screenshot` captures at **5.9%**.

The cause is not parsing difficulty. **The scene-source edge is absent from the recording.**

- `wmctrl` and `xdotool` are not installed; agents invoke them and get `command not found`.
- `xwininfo` output appears in **12/117** traces; explicit focus control in **4/117**.
- **125 of 145** sampled `gnome-screenshot` invocations capture the full screen; 5 use `-w`.
- **Zero** delivered captures have unambiguous single-window scene identity.

And the recoverability figure is not a property of the data. Holding the traces fixed and
varying only the temporal-lookback parameter moves source resolution from **4.8% to 54.9%**
— while the EXACT/STRONG sub-curve stays nearly flat at **2.4% → 11.9%**. More permissive
inference buys guesses, not evidence. Audit kill criteria **2, 3 and 5** fired.

## 3. What survived

1. **Artifact / file lineage** — 453/453, 308 EXACT edges. Which action wrote which
   delivered file is fully recoverable.
2. **Direct-synthesis provenance** — 98.3% classified. When no capture exists in an
   artifact's lineage, the pixels provably cannot descend from any application scene.
   Guarded by a task-spec-derived capture-vs-synthesis obligation, since a diff map *should*
   be synthesised.
3. **Bracketed substitute detection** — the `DAV_task_0` pattern (agent authors Tk script →
   launches → captures → alt+F4 → delivers) reconstructs end-to-end with EXACT authorship
   and STRONG capture edges.
4. **Precision** — 0/99 and 0/73 false attributions on negative controls; 23/453 = 5.1% of
   artifacts receive a target-vs-substitute verdict. High precision, ~5% recall.
5. **Independence from the judge** — the strongest substitute case carries `is_hack = False`.
   The instrument disagrees with the judge's binary flag on structural grounds, so it is not
   merely reproducing judge output (kill criterion 6 not triggered).

## 4. Which missing information dominates the failure

From 287 eligible unresolved cases, with fields recorded as **conjunctive bundles** — no
single field resolves any case:

| Deficit | eligible cases | bundle required |
|---|---|---|
| **composite scene unresolvable** | **240 (83.6%)** | capture region + visible window set + z-order + geometry |
| target running but capture unbindable | 41 | active pid + active window + lifecycle at capture |
| stale / approximated liveness | 36 | lifecycle at capture + process start identity |
| owner not nameable | 35 | active pid + active window |
| competing candidates | 32 | active window + z-order |
| browser tab/URL at capture time | 25 | tab id + URL + active window |
| interpreter hides the script | 14 | active pid + command line |

**Display composition dominates**, because the dominant capture is a full-screen grab whose
scene is a *set* of windows, not one process.

Two further deficits are not runtime problems at all: **98 cases** where the benchmark task
never names a target application, and **30 derivation chains** whose lineage recurses into a
prior image.

## 5. Which proposed fields derive from observed deficits

Every field in `specs/CAPTURE_PROVENANCE_CONTRACT.md` traces to a measured deficit or is
marked threat-model-only:

| Tier | Fields | Historical basis |
|---|---|---|
| A window labels | title, WM_CLASS | **0 resolving cases** — kept only as the baseline that fails |
| B process identity | pid, start identity, argv, exe, ppid | 35 + 36 + 14 cases |
| C code/content lineage | agent-written lineage, content hash | 14 cases + all 30 derivation chains |
| D display composition | capture region, visible set, z-order, geometry, active window | **240 cases — dominant** |
| E application state | browser tab, URL, document identity | 25 + 41 cases |
| F record integrity | signature, privileged recorder, TEE | **0 — threat model only** |

Historical coverage (STRICT, eligible universe): **4 fields → 83.6%**, **6 → 90.2%**,
**8 → 99.7%**. Against all 415 unresolved cases: 4 fields → 75.2%, 8 fields → 89.4%.
Greedy is optimal at sizes 4 and 6 (brute-force verified).

## 6. Which fields are spoofable

The uncomfortable part, and the reason §5 is not a solution:

| Field group | Trust | Agent control |
|---|---|---|
| window title, WM_CLASS | T2 app-asserted | **total** — `root.title(...)`, observed in corpus |
| exe path | T4 OS-observed | **defeated by design**: `/usr/bin/python3` and Chrome are genuine in both honest and fabricated cases |
| pid, argv, geometry, z-order, visible set | T4 OS-observed | **cannot forge the value; fully controls the state being reported** |
| browser tab / URL | T2→T4 | truthfully reports a URL pointing at agent-authored content |
| document instance id | T2 | **total** when the app is agent-authored |
| record signature, TEE | T5/T6 | negligible — but protects the *record*, not the *claim* |

The central trap, stated in `THREAT_MODEL.md` §3: **a field is not secure because it comes
from the OS.** When the kernel reports "focused window is pid 3725, argv
`python /tmp/inspect_stages.py`, top of stack", every word is true and every word describes
a state the agent deliberately created. Raising a field's tier buys integrity of the report,
never integrity of the claim.

## 7. What remains unknown

- **Whether any practically collectable field set survives an adaptive adversary.** Zero
  adversarial cases have been run. All coverage is measured on agents that were not trying
  to defeat a recorder — several made attribution possible by accident.
- **Whether Tier D is deployable.** It leans on X11 window enumeration; Wayland restricts
  exactly these queries. A real blocker, not a detail.
- **Whether "written during the episode" survives pre-staging**, indirection, or fetching
  code authored earlier. Tier C's weakest definition.
- **Inter-rater reliability.** Manual validation was **single-reviewer**. It refuted 4 of the
  first 7 automated claims and drove three rule corrections, but **no agreement statistic
  exists** and this must never be described as completed two-reviewer validation.
- **Whether composite frames are ever adjudicable.** Case 8 / A7 may be irreducibly UNKNOWN.
- **Claim integrity.** Never attempted. Distinct from scene provenance and strictly harder.
- **Privacy viability.** Visible window set + titles + argv + URLs reconstruct a user's whole
  session. No minimisation story exists.

## 8. What the adversarial experiment can falsify

`specs/ADVERSARIAL_SUFFICIENCY_EXPERIMENT.md` — designed, **not run**. 12 predeclared cases
plus 4 stretch cases, each with construction-time ground truth (the independent label the
audit lacked), evaluated per attestation tier for false accept / false reject / abstention /
coverage.

It can falsify:

- **P1–P5**, that each tier stops the attacks it is supposed to (A2 vs Tier A, A3/A4 vs
  Tier B, A11 vs Tier C, A6/A7 vs Tier D, A4 vs Tier E);
- **P6**, that no tier detects a genuine target displaying agent-manipulated state (case 10);
- **P7**, that every guarantee is bounded by recorder atomicity (S1, the race case);
- the display-server trust assumption (S2, nested compositor);
- Tier C's episode-scoping definition (S3, pre-staged renderer).

Predeclared kill criterion: if fabricated evidence satisfies Tiers A–E plus a privileged
atomic recorder **without** breaching the recorder/kernel boundary, capture metadata is
insufficient for claim integrity and the project escalates to application-state attestation,
trusted display, an independent outcome oracle, or concludes the layer is wrong. A clean
sweep is predeclared as **suspicious** — evidence of a weak adversary, not a strong contract.

## 9. Direction: **MODIFY**

Not GO — the original construct is rejected and must not be revived.
Not NO-GO — the failure localised to a **specific, named, addressable** missing edge, and
the surviving capability is real if narrow.

**MODIFY** means:

- The research object changes from *"reconstruct scene provenance post-hoc"* to
  *"what capture-time evidence binds agent visual evidence to intended task state under an
  adversarial evidence generator?"*
- The deliverable changes from a classifier to a **falsifiable systems hypothesis** plus a
  measurement of where the boundary lies.
- The next executable step is the Phase I experiment, whose kill criterion can end the
  direction outright.

Honest odds, stated in advance: threat-model P6 predicts the kill criterion fires at least
partially, because capabilities C6 (real browser, fake local content) and C13 (real
interpreter, agent-written script) make several tiers report truthfully about an
adversarially arranged world. **If it fires, that is the result.** The failure mode to avoid
is adding fields until it stops firing — the same error, in a new register, that the
recoverability gate was built to catch.

### Explicitly not done this run

No adversarial experiment executed. No recorder built. No classifier built. ProcGrep
untouched. No application prose. No novelty claim beyond a HYPOTHESIS that survived a
prior-art sweep against Agent Flight Recorder, AgentTrails, PROV-AGENT, CHIEF, C2PA,
OpenAdapt Capture, WeaveBench, and the trusted-path literature.
