# Claim Table

Every headline sentence in `README.md` and `TECHNICAL_REPORT.md` maps to a row here. If a
sentence is not licensed by a row, it does not appear in the package.

**Classification vocabulary**

| Class | Meaning |
|---|---|
| **VERIFIED FACT** | directly supported by a pinned primary source or inspected artifact |
| **MEASURED FACT** | produced by a reproducible command or analysis in this repository |
| **INFERENCE** | reasoned conclusion from facts/measurements |
| **HYPOTHESIS** | empirical proposition that can fail |
| **SCOPE STATEMENT** | a statement about what was and was not tested |

**Counter-evidence** is the strongest thing known that cuts against the claim. Where it is
"none known", that is itself a claim and can be falsified.

---

## C1 — The problem

| | |
|---|---|
| **Claim** | A screenshot can be a genuine capture, produced by a real capture tool, of a scene the agent fabricated. File-level and capture-level provenance cannot distinguish this from honest evidence. |
| **Class** | MEASURED FACT |
| **Evidence** | `research/OBSERVABILITY_BOUNDARY.md` §2.4; case `DOC_task_3_okular_annotate_fact` (`proof.png` is a capture of an agent-authored Tk window); Phase I case 13b; platform Case R |
| **Scope** | Observed in one benchmark corpus and reproduced in two constructed labs. |
| **Counter-evidence** | None known. The distinction is structural, not statistical. |
| **Safe wording** | "A valid screenshot of the wrong thing." "Capture provenance and scene provenance are different properties." |
| **Prohibited** | "Screenshots are worthless as evidence." "Most agent screenshots are fabricated." (No base rate was measured.) |

## C2 — Inference-policy sensitivity (F1)

| | |
|---|---|
| **Claim** | With observations held fixed, varying only the permitted temporal lookback moved apparent scene-source resolution from 4.8% to 54.9%, while EXACT/STRONG attribution moved only 2.4% → 11.9%. |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/recoverability_report.md` §5.2 over 455 capture-based cases; E020, E029; Figure 3 |
| **Scope** | One corpus (WeaveBench GPT-5.4 low), one resolver, one parameter family. |
| **Counter-evidence** | The figures are a *corrected* recomputation; an earlier draft reported 5.5%→72.7% from a pre-correction resolver (E029). The corrected swing is ~11× rather than ~13×. |
| **Safe wording** | "More permissive inference produced substantially more answers without a commensurate increase in strong evidence." "Apparent recoverability is a property of the inference policy as much as of the traces." |
| **Prohibited** | "The additional answers were wrong." "54.9% of attributions are false." **Individual high-lookback attributions were never adjudicated; they are unsupported, not disproven.** |

## C3 — Scene provenance was not recoverable in this corpus

| | |
|---|---|
| **Claim** | Over 394 capture-based delivered artifacts, scene source reached EXACT or STRONG in 26 cases (6.6%), with **EXACT = 0**. |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/audit_metrics.json` `R3`; Figure 2 |
| **Scope** | One corpus; benign (non-adversarial) agent traces. |
| **Counter-evidence** | This measures *this* runtime's recording, not an intrinsic limit. A runtime that logged active-window identity at capture time would score differently — that is the stated reopening condition in the frozen decision log. |
| **Safe wording** | "Not recoverable from these traces at useful confidence." |
| **Prohibited** | "Scene provenance is impossible to recover." "No trace format could recover this." |

## C4 — Artifact provenance *is* recoverable

| | |
|---|---|
| **Claim** | Artifact provenance (which action wrote this file) was recovered for 453/453 delivered visual artifacts. |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/audit_metrics.json` `R2`; Figure 2 |
| **Scope** | Same corpus. |
| **Counter-evidence** | None known. |
| **Safe wording** | "File-level provenance is solved in this setting and is not the hard part." |
| **Prohibited** | Presenting this as visual/scene provenance. That conflation is the specific category error the work exists to prevent. |

## C5 — Display-composition fields adjudicate nothing

| | |
|---|---|
| **Claim** | The four display-composition fields (capture region, visible window set, z-order, geometry) achieve 70.6% scene-source resolution (272/385) and **0.0% target/substitute adjudication (0/287)**. Six fields — adding active window and active pid — adjudicate 83.6% (240/287). |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/field_coverage.csv`; `outputs/field_set_analysis.md` §4; D4 adjudication re-verified directly from `outputs/information_deficits.csv` (832 D4 rows, all `enables_target_substitute_adjudication = no`); Figure 4 |
| **Scope** | HISTORICAL analysis of benign traces. Denominators 385 and 287 are **not** interchangeable. |
| **Counter-evidence** | An earlier draft reported "83.6% of cases resolved by four fields". **That claim was withdrawn** (`field_set_analysis.md` §1) as an artifact of scoring fields independently. |
| **Safe wording** | "Closure of a display-composition deficit is not adjudication." "83.6% is the six-field adjudication figure over 287 cases." |
| **Prohibited** | "Four fields resolve 83.6% of cases." "Tier D adjudicates 83.6%." (Two of the six fields are not Tier D.) |

## C6 — Truthful facts, adversarially arranged state (F3)

| | |
|---|---|
| **Claim** | Every field in the frozen contract can be obtained and be truthful while the pixels on screen are attacker-authored. Case 13b: genuine unmodified viewer binary, real pid at uid 1000, real window, argv naming the declared target, **zero field observation failures** — and fabricated content displayed. |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/empirical_raw/empirical_records.json`; `outputs/phase1_final_metrics.json` `BOUNDARY_1_RESOURCE`; E064 |
| **Scope** | Constructed case; unprivileged attacker; no recorder/kernel/compositor compromise. |
| **Counter-evidence** | The episode journal was write-API-keyed and did not observe the mutating `cp` — see C7, which is the honest qualification of the mechanism. |
| **Safe wording** | "Moving a field to a higher trust plane buys integrity of the report, never integrity of the claim." |
| **Prohibited** | "The recorder was lying." "The telemetry was wrong." Every field was correct. |

## C7 — 13b classifies as CONTRACT_UNDERSPECIFICATION

| | |
|---|---|
| **Claim** | 13b is not cleanly reducible to a recorder bug or a decision-rule failure. The provenance concept lacked an explicit observation policy: the contract defined lineage as a binary predicate, so the recorder had no way to express "not observed", and absence of observation was emitted as the positive value `pre_existing`. |
| **Class** | MEASURED FACT (code + static trace) + INFERENCE (the classification) |
| **Evidence** | `research/13B_STATIC_CLASSIFICATION.md`; `outputs/13b_static_trace/`; `infra/recorder.py:193-202`; `infra/adjudicator.py:212-218`; E072–E077 |
| **Scope** | One contract, one recorder, one adjudicator. |
| **Counter-evidence** | **Secondary finding B′:** inside the optimistic configurations the adjudicator already had the correct rule and supplying the missed write alone flips the verdict to SUBSTITUTE — so *within that configuration* it is an observation gap. **Secondary finding C′:** with the Tier C field dropped, the adjudicator sources identity from argv and skips the provenance requirement, contradicting the contract's own "absence ⇒ UNKNOWN" cell. Both are recorded, not resolved away. |
| **Safe wording** | "The result is not cleanly reducible to recorder bug versus decision-rule failure." "The concept lacked a sufficiently explicit observation policy." |
| **Prohibited** | "13b proves the contract is insufficient." (Superseded framing.) "13b was just a recorder bug." Both are licensed only inside a stated configuration. |

## C8 — The repair is not a repair

| | |
|---|---|
| **Claim** | The single injected observation that flips 13b to SUBSTITUTE also flips the honest control `01_genuine_target` to SUBSTITUTE, because the rule is a pure function of "was the declared target path written this episode" and the contract has no field distinguishing a task-mandated write from an adversarial one. |
| **Class** | MEASURED FACT (property of the frozen rule) |
| **Evidence** | `outputs/13b_static_trace/rule_property_probe.md`; E075 |
| **Scope** | Measures the frozen **rule**, applied uniformly. |
| **Counter-evidence** | The honest control did not in fact perform such a write; the probe applies the observation uniformly to expose the rule's behaviour. This is stated in the artifact itself. |
| **Safe wording** | "Applying the mutation interpretation uniformly creates an honest-case false reject." |
| **Prohibited** | "The honest case was misclassified by the real recorder." It was not; this is a counterfactual probe. |

## C9 — Tested Wayland stack: no binding improved (F4)

| | |
|---|---|
| **Claim** | Across two predeclared cases on both platforms, **zero of twelve** comparable provenance bindings changed evidence level between X11 and the tested Wayland stack. |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/platform_binding_matrix.csv`; `outputs/platform_comparison_metrics.json`; Figure 7; E079 |
| **Scope** | **One** compositor (sway 1.7/wlroots headless), **one** portal backend (`xdg-desktop-portal-wlr`), software-rendered container, **two** constructed cases. |
| **Counter-evidence** | The xdg-desktop-portal specification supports WINDOW sources where a backend implements them. GNOME and KDE backends do implement window capture and were **not tested**; such a backend may change the `capture → surface` cell. |
| **Safe wording** | "The tested Wayland stack changed the trust architecture but did not export additional provenance sufficient to improve the tested binding matrix." |
| **Prohibited** | "Wayland does not help provenance." "Wayland is no better than X11." Both overreach past one backend, and the second is false — see C10. |

## C10 — What the tested Wayland stack *did* improve

| | |
|---|---|
| **Claim** | It improved capture-path integrity (only the compositor can produce the frame; on X11 any client with display access can grab the root window) and the directness of `surface → process` (the compositor reports client pid as a first-class field). It made standardisation worse: cross-client enumeration was available only via compositor-private IPC. |
| **Class** | MEASURED FACT (the mechanisms) + INFERENCE (the "integrity improvement" reading) |
| **Evidence** | `outputs/x11_wayland_comparison.md`; `outputs/platform_raw/raw/*.json`; E083 |
| **Scope** | Same single-backend scope as C9. |
| **Counter-evidence** | None known; but note this improvement protects the *recorder*, not the *claim*. |
| **Safe wording** | "It changes who may capture and who reports identity, not what can be bound." |
| **Prohibited** | "Wayland solves capture provenance." |

## C11 — Portal source types (measured)

| | |
|---|---|
| **Claim** | The tested portal advertised `AvailableSourceTypes = 1` — MONITOR only; WINDOW and VIRTUAL not offered — and `org.freedesktop.portal.Screenshot` was absent on that backend. `SelectSources` accepted `types = MONITOR\|WINDOW` and the backend enumerated outputs. |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/platform_raw/portal_probe.json`; `outputs/platform_raw/portal_start_diagnostic.log`; E080 |
| **Scope** | `xdg-desktop-portal-wlr` at the tested version, one machine. |
| **Counter-evidence** | This is a backend property, not a specification property. The spec permits WINDOW sources. |
| **Safe wording** | "The tested portal advertised MONITOR only." |
| **Prohibited** | "The xdg-desktop-portal API cannot capture windows." False — it is backend-dependent. |

## C12 — Portal stream metadata is BLOCKED, not negative

| | |
|---|---|
| **Claim** | A full ScreenCast session was attempted; `CreateSession` and `SelectSources` succeeded and `Start` failed (response_code 2) with backend trace `wlroots: unable to receive a valid format from wlr_screencopy` — PipeWire format negotiation in a headless container with no DRM device. Stream property contents were **never observed**. |
| **Class** | MEASURED FACT (the block) + SCOPE STATEMENT |
| **Evidence** | `outputs/platform_raw/portal_start_diagnostic.log`; E084 |
| **Scope** | Environment limitation, not an API limitation. |
| **Counter-evidence** | `grim` captures succeeded throughout, so the compositor's screencopy protocol works here; only the portal→PipeWire pipeline is blocked. |
| **Safe wording** | "BLOCKED. Not observed, and not inferred from documentation." |
| **Prohibited** | Any statement about what portal stream properties do or do not contain. |

## C13 — `app_id` is client-asserted

| | |
|---|---|
| **Claim** | An unprivileged attacker's GTK3 process calling `GLib.set_prgname("eog")` obtained `app_id = "eog"` on Wayland and `WM_CLASS = "eog"` on X11, with a window title identical to the genuine viewer's. Only the pid separated them. |
| **Class** | MEASURED FACT (both arms) |
| **Evidence** | `outputs/platform_comparison_metrics.json` `identity_spoofing`; E081 |
| **Scope** | One toolkit (GTK3), one compositor. |
| **Counter-evidence** | On X11 the genuine app reported `Eog` and the substitute `eog`. **This is toolkit convention, not a defence** — the attacker can set either string; on Wayland the two are byte-identical. |
| **Safe wording** | "`app_id` did not provide trustworthy application identity in the tested case." |
| **Prohibited** | "The case difference on X11 detects impostors." |

## C14 — Process/surface identity ≠ displayed-resource identity (F5)

| | |
|---|---|
| **Claim** | Neither platform has a field reporting which resource a surface is displaying. The binding rests on argv, which the attacker chooses. Additionally, open file descriptors at the capture instant revealed nothing: the viewer had already closed the file. |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/platform_comparison_cases.csv` (`holds_declared_target_open = false`, both arms); Phase I 13b; E082, E064 |
| **Scope** | One viewer (`eog`), two platforms, constructed cases. |
| **Counter-evidence** | A viewer that holds its file open (e.g. a memory-mapped document editor) could yield a different fd result. Only one viewer was tested. |
| **Safe wording** | "Whatever binds pixels to bytes must be recorded when the read happens, not when the capture happens." |
| **Prohibited** | "No kernel telemetry can ever bind pixels to bytes." Not tested; H-RB was not executed. |

## C15 — UNKNOWN policy (F6)

| | |
|---|---|
| **Claim** | Fail-closed UNKNOWN moved effective exposure from 100.0% → 0.0% below Tier D and 27.3% → 9.1% at Tier D and above — the largest single measured effect. It did **not** repair the false accept: case 13b survives fail-closed UNKNOWN because it was classified `AUTHENTIC_TARGET`, never UNKNOWN. |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/empirical_risk_coverage.csv`; Figure 6; E062, E069 |
| **Scope** | Constructed suite of 13 scenarios, 11 substitutes. Not a population estimate. |
| **Counter-evidence** | None known. |
| **Safe wording** | "Abstention is a mechanism; refusing automatic credit is enforcement. Neither reaches an accepted fabrication." |
| **Prohibited** | "Fail-closed UNKNOWN makes the system safe." The residual 9.1% is exactly the accepted fabrication. |

## C16 — Analytic vs empirical (F7)

| | |
|---|---|
| **Claim** | Of 169 comparable (scenario, tier) pairs, 127 agreed (75.1%). Five pairs moved `UNKNOWN → AUTHENTIC_TARGET`, the unsafe direction; all five are case 13b. |
| **Class** | MEASURED FACT |
| **Evidence** | `outputs/analytic_vs_empirical.csv`; Figure 5; E061 |
| **Scope** | One experiment, one contract, a constructed 13-scenario suite. |
| **Counter-evidence** | The majority of disagreements (34) run the *safe* direction (`SUBSTITUTE → UNKNOWN`), i.e. analytic over-confidence that produced abstention rather than acceptance. |
| **Safe wording** | "In this experiment, analytic field-vector evaluation was overconfident relative to real recorder observations in several safety-relevant cases." |
| **Prohibited** | "Analytic security evaluation is unreliable." "Paper evaluations cannot be trusted." One instance does not license a universal claim. |

## C17 — Opaque rendering boundary (Xephyr)

| | |
|---|---|
| **Claim** | An unprivileged attacker running Xephyr made the inner scene opaque to the tested outer recorder, which resolved the captured pixels to `/usr/bin/Xephyr` (pid 4391) with zero field observation failures; the inner window did not appear in the outer visible set. |
| **Class** | MEASURED FACT, narrowly scoped |
| **Evidence** | `outputs/empirical_raw/s2_nested.json`; E059, E068 |
| **Scope** | **The tested outer recorder**, one nested X server. |
| **Counter-evidence** | The analogous nested-compositor attack was **not** tested on Wayland. |
| **Safe wording** | "The tested outer recorder's provenance terminated at `/usr/bin/Xephyr`." |
| **Prohibited** | "All nested compositors are opaque." "Nested displays defeat provenance generally." |

## C18 — Renderer-boundary principle

| | |
|---|---|
| **Claim** | Opaque rendering boundaries require some trusted binding recorded at or across the boundary if inner provenance is to remain auditable; where no trusted observer records the binding where it occurs, reliable post-hoc reconstruction is generally unavailable. |
| **Class** | **INFERENCE / candidate general principle. Not a theorem.** |
| **Evidence** | Four measured witnesses: retrospective scene-source failure (C3); 13b's observation-policy case (C7); the Xephyr boundary (C17); fd-at-capture-time (C14) |
| **Scope** | Four witnesses, two substrates, one corpus. |
| **Counter-evidence** | The Wayland comparison was the designed test of whether a *trusted compositor* changes one of these bindings, and it did not — consistent with the principle, but a single non-refutation is weak support. Nothing establishes that a trusted observer *could not* be placed at that boundary. |
| **Safe wording** | "Candidate general principle, classified INFERENCE." |
| **Prohibited** | "It is impossible to reconstruct provenance across a rendering boundary." "We proved…" |

## C19 — The epistemic-policy thesis

| | |
|---|---|
| **Claim** | Provenance claims for computer-using agents are meaningful only relative to an explicit epistemic policy: what the recorder is obligated to observe, what may be inferred, where assurance terminates, and when the evaluator must abstain. |
| **Class** | **INFERENCE / research thesis. Not a theorem.** |
| **Evidence** | Double dissociation: C2 varies inference with observations fixed and moves apparent resolution ~11×; C7 varies one observation with the rules frozen and flips the verdict |
| **Scope** | Two witnesses, one contract, one corpus, two substrates. |
| **Counter-evidence** | **Declaring both policies is not sufficient.** C8 shows the observation that repairs 13b converts a false-accept problem into a false-reject problem. The thesis identifies a necessary condition, not a solution. |
| **Safe wording** | "Meaningful only relative to…" — a necessary-condition claim. |
| **Prohibited** | "Declaring an epistemic policy makes provenance sound." "We solved provenance semantics." |

## C20 — Novelty position

| | |
|---|---|
| **Claim** | The contribution is the measurement of which visual-evidence provenance bindings survive or fail under different observation policies, inference policies, and desktop trust architectures — not a mechanism. |
| **Class** | SCOPE STATEMENT + INFERENCE |
| **Evidence** | `research/PRIOR_ART.md`; the pinned AgentProvenance inspection (C21) |
| **Scope** | Prior-art search is not exhaustive. |
| **Counter-evidence** | AgentProvenance independently enforces the same trust-plane separation and the same graded-confidence discipline, which **reduces** this project's claim to novelty on those two ideas. Recorded deliberately. |
| **Safe wording** | Explicit non-novelty for: provenance graphs, process/file/runtime telemetry, eBPF, screen recording, tamper-evident logs, content provenance, Wayland capture mediation, trusted display. |
| **Prohibited** | "First work to…" for any mechanism listed above. |

## C21 — AgentProvenance, pinned

| | |
|---|---|
| **Claim** | At `ByteYellow/AgentProvenance` commit `fc2e62647dc64b6d23144b88e0e0ac101b4f2793`, all six checked claims are supported: three-axis evidence graph; process/file/network/runtime event families; native eBPF sensor marked IMPLEMENTED with compiled BPF objects; pid/tgid/ppid/cgroup/container correlation with graded confidences; content-addressed evidence via SHA-256 subject digests; and an ingest-enforced separation of runtime identity from application-asserted context. |
| **Class** | VERIFIED FACT (pinned primary source) |
| **Evidence** | `research/PRIOR_ART.md` "AgentProvenance" section; E089 |
| **Scope** | Source and documentation at one revision. **The software was not executed.** |
| **Counter-evidence** | None known. |
| **Safe wording** | Quote the pinned SHA with every use. |
| **Prohibited** | Any claim about runtime behaviour, performance, or deployment. |

## C22 — AgentProvenance display surface (the narrow negative)

| | |
|---|---|
| **Claim** | **No generic visual-display/scene provenance mechanism was found in the inspected pinned repository surface.** `compositor` and `wayland` return zero hits; `screen capture`, `display server`, `window manager` return zero in source and docs; the two `screenshot` hits describe the project's own dashboard documentation images; all four `x11` hits are false positives. |
| **Class** | MEASURED FACT (a search over a pinned tree) |
| **Evidence** | `git grep` over 379 tracked files at `fc2e6264`; E090 |
| **Scope** | Term-based search at one commit; binaries not decoded; six files read in full; software not executed. |
| **Counter-evidence** | A display capability implemented without any searched term would not be found. Forks, issues, PRs and roadmap items outside the pinned tree were not considered. |
| **Safe wording** | Exactly the sentence above, including "in the inspected pinned repository surface". |
| **Prohibited** | **"AgentProvenance cannot capture screenshots."** **"AgentProvenance has no display support."** Neither was established. |

## C23 — Phase I kill criterion

| | |
|---|---|
| **Claim** | The predeclared kill criterion fired: fabricated evidence satisfied the strongest practically collectable field set, from an unprivileged attacker, with no recorder, kernel or compositor compromise. The capture-provenance contract branch is CLOSED / INSUFFICIENT. |
| **Class** | MEASURED FACT (empirical arm) |
| **Evidence** | `outputs/phase1_final_metrics.json`; `research/PHASE1_EMPIRICAL_CONCLUSIONS.md`; E064 |
| **Scope** | The tested white-box adversary and the tested field set. |
| **Counter-evidence** | The 13b classification (C7) sharpens *why* it fired: the contract's observation policy was unstated. The criterion still fired on its own predeclared terms. |
| **Safe wording** | "Capture-time system/display provenance is insufficient for visual claim integrity under the tested white-box adversary." |
| **Prohibited** | "Provenance for agent visual evidence is impossible." |

## C24 — Recorder atomicity (S1)

| | |
|---|---|
| **Claim** | *The tested recorder implementation* failed to atomically bind display metadata and pixels: 120/120 invariant violations in each of two independent 120-trial runs, skew 105–170 ms. The violation *mode* inverted between runs (113/7 vs 7/113); the *rate* did not. |
| **Class** | MEASURED FACT, narrowly scoped |
| **Evidence** | `outputs/empirical_raw/s1_race.json` (run 2); E058, E067 |
| **Scope** | One naive recorder built as sequential shell-outs. |
| **Counter-evidence** | Run 1's JSON artifact was **not retained** (run log only). Run 2 is the artifact on disk. |
| **Safe wording** | "For this recorder, built the obvious way, the atomicity precondition does not hold." |
| **Prohibited** | "Atomic provenance is impossible." A server-side grab was never built or measured. |

## C25 — `_NET_WM_PID`

| | |
|---|---|
| **Claim** | In the frozen Debian/Xvfb/Openbox lab, `_NET_WM_PID` was absent on every window tested (Tk, ImageMagick `display`, Openbox) and `wmctrl` reported `pid=0`, requiring X-Resource correlation. In the Phase J lab, GTK/`eog` **did** set it. |
| **Class** | MEASURED FACT (two environments, opposite results) |
| **Evidence** | E060, E070; `outputs/platform_comparison_metrics.json` `net_wm_pid_corroboration` |
| **Scope** | Two constructed environments. |
| **Counter-evidence** | The two results contradict each other in the direction of "it depends on the toolkit" — which is the transferable point. |
| **Safe wording** | "It cannot be relied upon in either direction, and it is application-asserted whenever present." |
| **Prohibited** | "`_NET_WM_PID` is absent on X11." Falsified by our own Phase J data. |
