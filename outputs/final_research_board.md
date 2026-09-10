# Final Research Board

**Date: 2026-09-10. Status: TECHNICAL EXPANSION STOPPED. PACKAGE.**

Phase J had exactly two objectives — classify 13b statically, and measure what a Wayland
trust architecture actually changes. Both resolved. Both point the same way. Neither
reopens the board.

Nothing frozen was modified. `infra/adjudicator.py`, `infra/recorder.py` and
`specs/CAPTURE_PROVENANCE_CONTRACT.md` are unchanged, and their hashes are recorded with the
trace that used them.

---

## 1. What exactly did 13b classify as?

**C. CONTRACT_UNDERSPECIFICATION.**

The frozen contract cannot be judged sufficient or insufficient independently of an
observation policy it never stated. Specifically it leaves undefined: what events must be
observed, which observer is authoritative, what completeness guarantee exists, and — fatally
— how a missed event is represented.

The mechanism, precisely: the contract defines displayed-resource lineage as a **binary**
predicate ("was it authored this episode?"). A faithful implementation therefore has two
tokens and no way to say *"I did not watch"*. The frozen recorder emits `pre_existing` on
`journal.get(path)` returning falsy — converting **absence of observation** into a
**positive provenance claim** before any rule runs. The contract's entire safety mechanism,
abstain-by-default, fires on a *missing field*; the field was never missing.

Evidence: E076, E078 · `research/13B_STATIC_CLASSIFICATION.md`

---

## 2. Contract failure, recorder defect, underspecification, or mixed?

**Primary: underspecification.** Two secondary findings are recorded rather than collapsed
into the headline, because 13b's classification genuinely depends on which deployment
configuration is being asked about — and the contract never fixed that either.

| | Finding | Where it holds |
|---|---|---|
| **Primary — C** | the contract never stated an observation policy, so neither "contract failure" nor "implementation defect" is well-defined | everywhere |
| **Secondary B′** | recorder observation gap: the adjudicator already had the right rule (`R4_displayed_resource_agent_authored`), and supplying the missed write alone flips the verdict to `SUBSTITUTE` | the **optimistic** configurations (`0+A+B+C+D`, `+E`, `FULL`) |
| **Secondary C′** | identity and provenance are fused into one field; with it dropped the adjudicator takes identity from argv and silently skips the Tier C provenance requirement, contradicting the contract's own "absence ⇒ UNKNOWN" cell and Composition Rule 1 | the **default** deployment (both `SENS` arms) |

Three structural facts decided this, all measured:

1. The mutation fact has **exactly one consumer** in the frozen adjudicator — a substring
   test on `displayed_resource_lineage` at `adjudicator.py:216`. `agent_written_code_lineage`
   is never read on the resource-claim path; `content_hash` is never read by any rule.
2. That one consumer is the contract's own **least-deployable** field, which the contract
   itself calls "not OS-observable" and which the frozen decision log treats as absent in
   the **default** deployment.
3. The observation that "repairs" 13b **breaks the honest control**: applied uniformly, it
   flips `01_genuine_target` from `AUTHENTIC_TARGET` to `SUBSTITUTE`. The rule is a pure
   function of *"was the declared target path written this episode"*, and the contract has no
   field distinguishing a task-mandated write from an adversarial one.

**Category D (mixed/unresolved) was considered and rejected as the primary label.** The
"authored" vs "written" ambiguity is real, but under both readings the adjudicator behaves
identically once the token is present. The ambiguity governs the recorder's *obligation*, not
the adjudication *semantics* — which is category C, not D.

**The Phase I kill criterion still fired on its predeclared terms.** Nothing here
reinterprets it. What Phase J adds is a correction to the *scope* of one frozen sentence:
"13b is not a missing field in the frozen contract" is confirmed for the default deployment
and too strong for the optimistic one.

Evidence: E073, E074, E075, E076, E077

---

## 3. What did Wayland improve, if anything?

**Zero of twelve comparable bindings changed evidence level.**

| Row | artifact→capture | capture→surface | surface→process | process→resource | resource→state | state→claim |
|---|---|---|---|---|---|---|
| X11 Case P | EXACT | WEAK | EXACT | UNKNOWN | UNKNOWN | UNKNOWN |
| Wayland Case P | EXACT | WEAK | EXACT | UNKNOWN | UNKNOWN | UNKNOWN |
| X11 Case R | EXACT | STRONG | EXACT | WEAK | UNKNOWN | UNKNOWN |
| Wayland Case R | EXACT | STRONG | EXACT | WEAK | UNKNOWN | UNKNOWN |

Both arms used the **same application**: `/usr/bin/eog`, started as a native client of each
platform, zero fallbacks taken. No result rests on an XWayland surface being presented as
native Wayland (E088).

**Improved (measured, and real):**
- **Capture-path integrity.** Only the compositor can produce the frame. On X11 any client
  with display access can grab the root window. This removes a whole attack class against
  the *recorder*.
- **Directness of `surface → process`.** The compositor reports the owning client pid as a
  first-class field — no `_NET_WM_PID` trap, no X-Resource correlation needed.

**Not improved (measured):**
- `capture → surface`. The standard portal offers **no window source at all**:
  `AvailableSourceTypes = 1` (MONITOR only), and `org.freedesktop.portal.Screenshot` does not
  exist on that backend. `SelectSources` accepted `types=MONITOR|WINDOW` and the backend
  enumerated **outputs**.
- `surface → displayed resource`. No such field exists on either platform.
- Identity trustworthiness. **`app_id` is client-asserted and spoofable exactly as
  `WM_CLASS` is** — an attacker's GTK3 process obtained `app_id = "eog"`, byte-identical to
  the genuine viewer's, with an identical title. Only the pid separated them.

**Made worse (measured):**
- Cross-client enumeration exists **only** through compositor-private IPC. The
  standardised API exposes strictly less than X11. A recorder built on `swaymsg` is a *sway*
  recorder, not a *Wayland* recorder.

> **Wayland changes who may capture and who reports identity. It does not change what can be
> bound.**

The predeclared expectation (RESULT A) is **refuted in its first half**. The outcome is
**RESULT B**, with the portal *stream-metadata* sub-arm **BLOCKED** (RESULT D) for a stated
environmental reason — PipeWire format negotiation on a headless, no-DRM container. Stream
contents were never observed and are **not** inferred from documentation.

Evidence: E079, E080, E081, E083, E084 · `outputs/x11_wayland_comparison.md`

---

## 4. Which provenance edge remains unresolved?

**Link 4: `process/client → displayed resource`.** Unchanged, and now measured to fail
identically on two different desktop trust architectures.

```
artifact ─► capture ─► process/surface ─► displayed resource ─► app state ─► claim
   ✅         ✅             ✅                   ❌              untested    untested
                                          SAME EDGE, BOTH PLATFORMS
```

Phase J added one new empirical bound on how that edge might be closed. Open file
descriptors at the capture instant are the closest platform-native resource binding
available — and they returned nothing on either platform. `eog` decodes the image and
**closes the descriptor** before the capture happens; `holds_declared_target_open = false` on
both arms.

**Consequence:** whatever binds pixels to bytes must be recorded **when the read happens**,
not when the capture happens. A recorder that samples state at capture time is sampling after
the binding has ceased to exist in kernel-visible form. This bounds the naive form of H-RB
before H-RB is ever executed.

Links 5 and 6 were never reached. Nothing in Phase J is progress on them.

Evidence: E082

---

## 5. Which results are X11-specific?

Narrowly scoped; do not generalise:

| Result | Scope |
|---|---|
| S1 atomicity — 120/120 invariant violations, both runs | **one recorder implementation** on X11. Not a claim that atomic provenance is impossible. |
| S2 nested display — provenance terminates at `/usr/bin/Xephyr` | **the tested outer recorder** on X11. The Wayland analogue was **not tested**. |
| `_NET_WM_PID` absent on every window | the frozen Debian/Xvfb/Openbox lab with Tk and ImageMagick. **Phase J contradicts it in the other direction**: GTK/`eog` *did* set it here. The transferable point survives both: it cannot be relied on, and is client-asserted whenever present. |
| X-Resource correlation required to obtain a pid at all | X11 with toolkits that omit `_NET_WM_PID`. |
| `capture → surface` STRONG "by elimination" | contingent on enumeration completeness — **already falsified for X11 by S2**, and untested on Wayland. |

---

## 6. Which results generalise beyond X11?

As **evidence-policy and inference-policy findings**, not as platform facts:

1. **The observation/inference distinction, and the double dissociation supporting it.**
   Holding observations fixed and loosening inference moved apparent resolution ~11×
   (4.8% → 54.9%) while well-supported attribution stayed nearly flat (2.4% → 11.9%).
   Holding the rules fixed and supplying one missed observation flipped a verdict. Each
   policy alone moves the answer.
2. **Absence-of-observation must be a first-class value.** Binary provenance predicates are
   unsafe by construction: they have no way to express "not observed", so abstention cannot
   fire. Measured *within one contract* — query-based fields handle absence correctly, event
   -journal-based fields do not, because a query that fails is visibly a failure while an
   event that never arrives looks exactly like an event that never happened.
3. **Client-asserted identity strings are not a trust plane.** `WM_CLASS` and `app_id` are
   the same fact wearing different names, measured on both platforms.
4. **`process/surface identity ≠ displayed-resource identity`; `path identity ≠ content
   identity`.** Now measured on two trust architectures rather than one.
5. **A binding must be recorded at the boundary where it occurs.** Post-hoc reconstruction
   fails when no trusted observer recorded the transition — three independent witnesses.

**Candidate thesis, classified INFERENCE — not a theorem:**

> A provenance claim is meaningful only relative to both a declared observation policy and a
> declared inference policy.

Explicitly **not** claimed: that the two policies are jointly *sufficient*. The rule-property
probe shows the opposite — declaring them does not repair 13b, it converts a false-accept
problem into a false-reject problem.

### The renderer-boundary hypothesis, after the experiment

> **Every opaque transition in a visual-evidence provenance chain requires a trusted binding
> recorded at or across that boundary; when no trusted observer records the binding where it
> occurs, reliable post-hoc reconstruction is generally unavailable.**

**Classification: HYPOTHESIS**, promoted from a two-witness conjecture to a
three-and-a-half-witness one, and still not a theorem.

| Witness | Boundary | Status |
|---|---|---|
| Retrospective WeaveBench scene-source failure | capture → scene source, reconstructed from traces | MEASURED |
| 13b resource/observation-policy case | write event → displayed bytes, unobserved | MEASURED |
| Xephyr nested renderer (S2) | outer recorder → inner scene, opaque | MEASURED |
| **Phase J addition** — fd inspection at capture time (E082) | read event → rendered pixels; the binding has already dissolved | MEASURED |

The Wayland comparison was the designed test of whether a **trusted compositor** changes one
of these bindings. **It does not.** The compositor is a trusted observer standing at the
`capture → surface` boundary; it demonstrably improves the integrity of what it reports, and
it is not standing at the boundary where the failure occurs. That is consistent with the
hypothesis and is the closest thing Phase J produced to a positive test of it.

Still not established: that no trusted observer *could* be placed at that boundary. Only
that neither of the two tested platforms places one there.

---

## 7. Is further technical work justified?

**No — with exactly one specific, cheap exception, and it does not change link 4.**

| Candidate | Verdict |
|---|---|
| Filesystem telemetry ladder (J0/J1/J2), eBPF, fanotify, inotify | **No.** Occupied prior art for the runtime layer; the static trace showed observing the write does not bind rendered bytes and breaks the honest case; E082 showed capture-time fd inspection reaches nothing. |
| H-RB | **No.** Registered, unexecuted, and now bounded before execution by E082. |
| Application-state attestation | **No.** Link 5, never reached; opening it would absorb an unpackaged negative result. |
| Adaptive red-teaming | **No.** Would grow the suite, not resolve the edge. |
| More operating systems / benchmark tasks / ProcGrep / another framework | **No.** Explicitly excluded by the stop rule. |
| **GNOME or KDE portal backend** | **The one exception.** They implement window-source capture and were not tested. It is a single measurement and would change one cell (`capture → surface`, Case P). It would **not** touch link 4. |

The stop rule asks whether this board contains a specific new result that materially changes
the decision. It does not. Both Phase J results sharpen the same negative finding and neither
contradicts it.

---

## 8. Should the project now STOP AND PACKAGE?

# YES.

The two questions this run existed to answer are answered, and they converge:

- **13b was epistemically ambiguous because the contract never stated an observation
  policy** — not because the contract was subtly wrong, and not because the recorder was
  merely buggy.
- **Wayland does not move the assurance boundary.** Changing the desktop trust architecture
  moved zero of twelve binding evidence levels. The platform closes an attack surface around
  the *recorder* and leaves the *claim* exactly where it was.

The defensible result is a **negative one with a precisely located boundary**, three
measured witnesses for the renderer-boundary hypothesis, and a methodological finding
(observation policy vs inference policy) that is independent of X11, of Wayland, and of this
particular contract.

Per `CLAUDE.md`: *a smaller negative result that is defensible is preferable to a larger
system with ambiguous claims.* That is what exists on disk.

**Do not open a new technical phase. Do not write the Taste application yet — it was not
requested.** The next action is packaging.

---

## Artifact index

| Artifact | What it is |
|---|---|
| **`research/FROZEN_FINDINGS.md`** | **the seven frozen findings — the research package** |
| `research/13B_STATIC_CLASSIFICATION.md` | the classification, with the frozen-semantics trace |
| `research/EPISTEMIC_POLICY.md` | observation policy vs inference policy; the candidate thesis |
| `outputs/13b_static_trace/` | original + counterfactual records, both decision traces, rule-property probe |
| `outputs/x11_wayland_comparison.md` | the platform comparison writeup |
| `outputs/platform_binding_matrix.csv` | the binding matrix — the main experimental output |
| `outputs/platform_comparison_cases.csv` | per-case observed facts |
| `outputs/platform_comparison_metrics.json` | machine-readable metrics |
| `outputs/platform_raw/` | raw recorder output, ground truth, captures, portal probe + diagnostic |
| `infra/wayland_lab/` | the reproducible dual-stack lab |
| `infra/wayland_lab/IMPLEMENTATION_CORRECTIONS.md` | IC-5, IC-6 — documented before re-running; result verified stable across them |
| `scripts/static_13b_trace.py`, `scripts/platform_matrix.py` | the two analyses, rerunnable |

### Reproduce

```
python scripts/static_13b_trace.py
docker build -t sceneprov-wl:1.5 infra/wayland_lab/
docker run --rm --cap-add=SYS_PTRACE sceneprov-wl:1.5 python3 /lab/run_platform.py
python scripts/platform_matrix.py
```
