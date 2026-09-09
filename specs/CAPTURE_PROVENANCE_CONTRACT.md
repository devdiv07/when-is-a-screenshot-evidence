# Candidate Capture-Provenance Contract

**Status: CANDIDATE. Not validated. Not sufficient.**

Every field below satisfies at least one of:

1. it addresses a **measured** information deficit from Phase C
   (`outputs/information_deficits.csv`, `outputs/field_set_analysis.md`); or
2. it is **explicitly required by the threat model** (`research/THREAT_MODEL.md`), in which
   case its historical-deficit column reads `0 — threat model only`.

Fields that meet neither test are not in this contract.

**Trust planes** are defined in `research/THREAT_MODEL.md` §3. "OS-observed" is not one
fact, so the planes separate who actually observes what:

| Plane | Observer | Covers |
|---|---|---|
| `EVALUATOR/TASK_SPECIFIED` | the task/evaluator, not telemetry | Tier 0 claim + target context |
| `AGENT_ASSERTED` | the agent | narrative, filenames |
| `APPLICATION_ASSERTED` | a process the agent may have written | window title, WM_CLASS, document identity |
| `HARNESS_OBSERVED` | the agent runtime / tool layer | tool calls, episode file-writes |
| `KERNEL/RUNTIME_OBSERVED` | kernel + runtime | pid, process start identity, executable, ppid, file/runtime events |
| `COMPOSITOR/DISPLAY_SERVER_OBSERVED` | display server / compositor | visible window set, geometry, stacking/z-order, active surface |
| `PRIVILEGED_APPLICATION_OBSERVER` | protected CDP / extension channel | browser tab or target id, URL/origin, app document identity |
| `TRUSTED_RECORDER_OBSERVED` | the recorder itself | capture bytes, region, timestamp, atomic correlation across the other planes |
| `HARDWARE/TEE_ATTESTED` | attestation root | integrity measurement of recorder/runtime |

The distinction matters because these planes fail independently: a compositor observation is
not protected by kernel integrity, and a privileged-application observation depends on a
channel the agent must not be able to call.

Recall the central principle, unchanged:
**truthfully observed state can still be adversarially arranged.** Moving a field to a
higher plane buys integrity of the *report*, never integrity of the *claim*.

This is an **attestation ladder**, not one schema. Each tier is separately collectable,
separately costed, and separately falsifiable in Phase I. **No claim is made that the top
tier is sufficient** — that is precisely what the experiment must test.

---

## Tier 0 — Evidence claim / target context

**Not attestation. Not telemetry.** This is evaluator/task specification, on the
`EVALUATOR/TASK_SPECIFIED` plane. It is a *prerequisite* for the tiers below, not a
defence against them.

Historical basis: **98 cases** in the frozen corpus where target/substitute adjudication is
impossible for any capture-side field set, because the task never declared a target
(`outputs/field_set_analysis.md` §2). Those cases are why this tier exists.

| Field | Description | Notes |
|---|---|---|
| `task_id` | which task the evidence belongs to | |
| `evidence_claim_id` | which specific claim this artifact is offered as evidence for | one artifact may support several claims |
| `target_kind` | application / document / service / system state / other | |
| `target_application` | the substrate, **when the task specifies one** | |
| `target_resource` | document, file or record, **when specified** | |
| `evidence_modality` | screenshot / synthesised render / derived image / log | |
| `capture_scope` | full screen / window / region, as the claim requires | |
| `expected_renderer_identity` | allowed application identity, **where meaningful** | often absent, and that is data |
| `state_predicate` / `evaluator_reference` | the checkable condition, where one exists | |

**Rules**

1. **Do not invent target semantics the task does not provide.** An absent field is
   recorded absent, never inferred from a filename, a window title, or a task's prose.
2. **When the target is undefined, TARGET/SUBSTITUTE adjudication is `UNKNOWN`.** It is not
   a failure of the capture tiers and must not be scored as one.
3. **Tier 0 is not trusted telemetry.** It is a declaration by the evaluator. It says what
   was *asked for*, never what *happened*. It cannot be used as evidence about the scene.
4. Tier 0 being complete is necessary and nowhere near sufficient: it makes adjudication
   *possible*, and Tiers B–E decide it.

## Tier A — Human-readable window metadata

Cheap, portable, and **evidentially weak**. Included because it is what everyone proposes
first and because Phase I needs it as the baseline that fails.

| | `WINDOW_TITLE` | `WM_CLASS` |
|---|---|---|
| description | title string of the relevant window | window-manager class / app id |
| historical cases addressed | 0 as a resolving bundle (272 cases as a **verdict-`no`** bundle) | 0 as resolving |
| trust source | `APPLICATION_ASSERTED` | `APPLICATION_ASSERTED` |
| agent spoofability | **total** — `root.title(...)` (observed, C4) | **total** where the toolkit permits (C5) |
| application spoofability | total | total |
| OS/kernel observability | readable via X11/Wayland properties, but the value is app-supplied | same |
| collection cost | negligible | negligible |
| privacy | titles leak document names, URLs, user content — **highest privacy risk in the contract** | low |
| portability | X11 yes; Wayland restricted; macOS/Windows equivalents exist | X11/`app_id` on Wayland |
| failure modes | A2 (title spoofing) defeats it completely | A2 |
| absence ⇒ UNKNOWN? | **no** — absence changes nothing, since presence proves nothing | no |
| required? | **optional, context only** | **optional, context only** |

**Empirical grounding for the `no` verdict:** both fields were already available in the 12
traces carrying `xwininfo`, and did not resolve those cases (report §5.1). Title and class
narrow a candidate set; they never bind a scene.

> Tier A must never be used as positive evidence of authenticity. It is admissible only to
> *contradict* a claim (a window titled "Krita" backed by `python foo.py` is a signal), and
> even then the contradiction comes from Tier B.

## Tier B — Runtime process identity

| | `ACTIVE_PID` | `PROCESS_START_IDENTITY` | `EXECUTABLE_PATH` | `COMMAND_LINE` | `PARENT_PROCESS_LINEAGE` |
|---|---|---|---|---|---|
| description | pid owning the relevant window | pid + start time / generation | resolved exe behind that pid | argv | ppid chain |
| historical cases | 35 (with active window), 41 (with lifecycle) | 36 (with lifecycle) | 0 directly | **14** | 0 — threat model only |
| trust source | `KERNEL/RUNTIME_OBSERVED` | `KERNEL/RUNTIME_OBSERVED` | `KERNEL/RUNTIME` | `KERNEL/RUNTIME` | `KERNEL/RUNTIME` |
| agent spoofability | cannot forge the value; **fully controls which process owns the window** | cannot forge; controls | cannot forge; controls by choosing what to launch | cannot forge; **chooses argv** | controls by choosing the launcher |
| application spoofability | no | no | no | no | no |
| OS observability | high | high | high | high | high |
| cost | low | low | low | low | low |
| privacy | low | low | medium (paths) | **medium-high — argv leaks file paths and secrets** | low |
| portability | universal | universal (start time is per-OS) | universal | universal | universal |
| failure modes | **A3, A4**: `/usr/bin/python3` and Chrome are genuine in both honest and fake cases | stale-liveness only | **A3/A4 defeat it outright** | A4 (a real browser with a real URL arg) | A3/A4 |
| absence ⇒ UNKNOWN? | **yes** | yes, where liveness matters | no (argv usually suffices) | **yes** for interpreter cases | no |
| required? | **required** | **required** | optional | **required** | optional |

**Why `COMMAND_LINE` is required and `EXECUTABLE_PATH` is not:** capability C13. When the
agent runs `python /tmp/inspect_stages.py`, the executable is a genuine unmodified
interpreter. Only argv exposes the script. This is a direct consequence of the measured
`nearest_launch_is_non_gui_script` failure (39 cases) and its fix.

**`PROCESS_START_IDENTITY` exists because the audit made this exact error**: it treated
`Command still running (session …, pid …)` as liveness for a process that had already
exited (report §8; observability boundary §2.1). pid alone is reusable and stale.

## Tier C — Code, content and displayed-resource lineage

| | `AGENT_WRITTEN_CODE_LINEAGE` | `CONTENT_HASH` | `DISPLAYED_RESOURCE_LINEAGE` |
|---|---|---|---|
| description | was the owning executable/script authored during this episode? | hash of captured bytes and of any source image | provenance of the **resource the surface is displaying** — the file, document or URL opened, and whether *it* was authored this episode |
| historical cases | 14 | **43** (every derivation chain) | **38** (browser/viewer-mediated captures) |
| trust source | `HARNESS_OBSERVED` (the harness sees the writes) | `HARNESS_OBSERVED` / `TRUSTED_RECORDER_OBSERVED` | `HARNESS_OBSERVED` + `PRIVILEGED_APPLICATION_OBSERVER` (to learn *what* is open) |
| agent spoofability | **partial**: cannot hide a write the harness saw, but *can* pre-stage content, write via a child process, or fetch code authored earlier/elsewhere | cannot forge a hash; **can choose what to hash** | same pre-staging weakness; also requires the viewer to disclose what it has open, which many applications do not |
| application spoofability | n/a | n/a | total for an agent-authored "viewer" |
| OS observability | needs harness file-write tracking | high | **not OS-observable** — needs harness lineage joined to app-reported resource identity |
| cost | medium | low | **high** — join across two planes |
| privacy | medium (file contents) | low | **high** (documents opened) |
| portability | harness-specific | universal | per-application |
| failure modes | **A3**; pre-staging (S3) | derivation root may be a synthesised image, so chaining terminates without resolving (30 cases) | **A13 if absent**; pre-staging if the resource predates the episode |
| absence ⇒ UNKNOWN? | yes, for interpreter-mediated scenes | **yes**, for any derived artifact | **yes**, for any viewer- or browser-mediated scene |
| required? | **required** | **required** | **required for viewer/browser captures** |

This tier decides `DAV_task_0`: the deciding fact is not that a Tk window existed, but that
**the code drawing it was written 3 events earlier by the agent**.

`DISPLAYED_RESOURCE_LINEAGE` is the answer to **A13** (legitimate viewer displaying
agent-authored content) and its browser special case A4. Without it, the contract stops at
"a genuine viewer process owned a genuine window" — which is *true* and *worthless*, because
the agent chose what that viewer opened. With it, the question becomes the provenance of the
opened resource, which is the question that was actually being asked.

It is also the most expensive and least portable field in the contract: it requires joining
harness file-write lineage to an application's own report of what it has open, and most
applications do not report that at all.

## Tier D — Display composition

**The dominant tier: 240 of 287 eligible cases (83.6%).** These four fields are conjunctive;
none is useful alone (Phase D §2).

| | `CAPTURE_REGION` | `VISIBLE_WINDOW_SET` | `Z_ORDER` | `WINDOW_GEOMETRY` | `ACTIVE_WINDOW_IDENTITY` |
|---|---|---|---|---|---|
| description | rectangle actually captured | every mapped window at the capture instant | stacking order | per-window position/size | which window held focus |
| historical cases | 240 (bundle) | 240 | 240 | 240 | 35/41/32 (bundles) |
| trust source | `TRUSTED_RECORDER_OBSERVED` | `COMPOSITOR/DISPLAY_SERVER` | `COMPOSITOR/DISPLAY_SERVER` | `COMPOSITOR/DISPLAY_SERVER` | `COMPOSITOR/DISPLAY_SERVER` |
| agent spoofability | cannot forge; chooses full-screen vs window-scoped | cannot forge; **fully controls which windows exist** | cannot forge; **fully controls stacking** (C8) | cannot forge; controls | cannot forge; controls focus |
| application spoofability | no | no | no | no | no |
| OS observability | high | high on X11; **Wayland restricts cross-client enumeration** | same restriction | same | same |
| cost | negligible | low | low | low | negligible |
| privacy | low | **high — enumerates every open window, i.e. the user's whole session** | low | low | medium (via title) |
| portability | universal | **X11 good; Wayland poor — a real deployment blocker** | X11 good; Wayland poor | X11 good | varies |
| failure modes | **A6/A7**: correctly reporting a composite frame does not adjudicate it. **A12**: racing between snapshot and capture | A6/A7/A12 | A6/A7/A12 | A7 | A6 |
| absence ⇒ UNKNOWN? | **yes — mandatory** | **yes — mandatory** | **yes — mandatory** | yes | yes |
| required? | **required** | **required** | **required** | **required** | **required** |

**Atomicity is a property of this tier, not a field.** All five must be sampled *at the
capture instant*, not near it, or A12 defeats the tier. A contract that samples display
state before or after the grab is racing an adversary who controls the window-manager queue.

**Honest limitation:** this tier resolves *what was on screen*. For A7 (a frame genuinely
containing both target and substitute) the correct output may remain UNKNOWN even with all
five fields, because the frame really is ambiguous. Perfect Tier D data yields a correct
description of an ambiguous scene, not a verdict.

## Tier E — Application-specific state

| | `BROWSER_TAB_ID` | `BROWSER_URL` | `DOCUMENT_INSTANCE_ID` |
|---|---|---|---|
| description | foreground tab at capture time | URL/origin in that tab at capture time | app-specific open document / session identity |
| historical cases | **25** | **25** | 41 (uncertain bundle) |
| trust source | `APPLICATION_ASSERTED`, promotable to T4 via a privileged browser extension / CDP over a channel the agent cannot call | promotable as above | `APPLICATION_ASSERTED` — asserted by an app the agent may have written |
| agent spoofability | cannot forge if read out-of-band; **fully controls what the URL points at** | same — a `file:///tmp/fake.html` URL is a *true* answer | **total when the app is agent-authored** |
| application spoofability | a real browser will not lie; an agent-authored "browser" will | same | total |
| OS observability | **not OS-observable** — requires app cooperation | not OS-observable | not OS-observable |
| cost | medium — needs an extension or debug channel | medium | high, and per-application |
| privacy | **high — full browsing URLs** | **high** | high |
| portability | per-browser | per-browser | per-application; realistically unbounded work |
| failure modes | **A4 is only *partly* addressed**: the URL is truthfully reported and points at agent-authored content, so the field must be combined with Tier C lineage on that file | A4, A9 | **A9 defeats it entirely** — a real document with agent-corrupted contents |
| absence ⇒ UNKNOWN? | yes, for browser-mediated captures | yes | yes, where the claim is about document state |
| required? | required **for browser captures**; otherwise n/a | required for browser captures | **optional — aspirational, not deployable generally** |

Tier E is the only tier that addresses A4, and it addresses it **only in combination with
Tier C**: knowing the URL is `file:///tmp_workspace/results/screens/01_full.html` is
worthless unless we also know that file was written by the agent this episode.

`DOCUMENT_INSTANCE_ID` is marked optional deliberately. Making it real means per-application
integration work with no general solution, and it still does not survive A9.

## Tier F — Record integrity

**Historical cases addressed: 0. Threat-model only.** No case in the corpus failed because
the record was tampered with; they failed because the record was never made.

| | `RECORD_SIGNATURE` / hash chain | `PRIVILEGED_RECORDER` | `TEE_BACKING` |
|---|---|---|---|
| description | signed, hash-chained event record | recorder the agent cannot call, race, or read | hardware-rooted attestation of the recorder |
| historical cases | **0 — threat model only** | **0 — threat model only** | **0 — threat model only** |
| trust source | `TRUSTED_RECORDER_OBSERVED` | `TRUSTED_RECORDER_OBSERVED` | `HARDWARE/TEE_ATTESTED` |
| agent spoofability | negligible under the stated boundary | negligible under the boundary | negligible |
| cost | low | **high — privileged deployment** | very high |
| privacy | neutral | neutral | neutral |
| portability | universal | OS-dependent | hardware-dependent |
| failure modes | **does not address any attack A1–A11** | enables Tier D atomicity (A12) | none of A1–A11 |
| absence ⇒ UNKNOWN? | no | no, but downgrades every other tier's assurance | no |
| required? | recommended | **required for the atomicity property** | out of scope for the first experiment |

**Prior art:** hash-chained tamper-evident agent event logs are occupied by Agent Flight
Recorder (arXiv:2609.01931), which we must not claim as novel. AFR's own threat model
assumes the recorder faithfully observes honest actions — the assumption this contract
exists to stress.

> A cryptographically perfect, TEE-attested record of "the agent's fake window was on top"
> is a perfect record of a fabrication. Tier F protects the recorder. It does not protect
> the claim.

---

## Composition rules

1. **Abstain by default.** Any required field missing ⇒ `UNKNOWN`. Never infer a missing
   field from an adjacent one.
2. **No temporal substitution.** A field sampled at any time other than the capture instant
   is not that field. This is the audit's central lesson (`OBSERVABILITY_BOUNDARY.md` §1).
3. **Tier A is never positive evidence.** It may contradict, never confirm.
4. **Tier C gates Tiers B, D and E for interpreter- and browser-mediated scenes.** A genuine
   process rendering agent-authored content is the common case (C6, C13), not the exception.
5. **Composite frames may stay UNKNOWN** even with complete Tier D. That is correct behaviour.
6. **Claim integrity is out of scope.** This contract addresses scene provenance only. A9
   (a genuine target displaying agent-manipulated state) is not detectable at this layer by
   construction — see `THREAT_MODEL.md` §4.

## What this contract is not

- Not validated. Zero adversarial cases have been run against it.
- Not minimal. Phase D reports the historical-coverage frontier; some fields here are
  threat-model-driven and carry no historical coverage at all.
- Not sufficient. P6 in the threat model predicts that no tier combination detects A9, and
  the Phase I kill criterion is written to fire if fabricated evidence satisfies the
  strongest practically collectable set.
- Not privacy-cleared. `VISIBLE_WINDOW_SET`, `WINDOW_TITLE`, `COMMAND_LINE` and `BROWSER_URL`
  together reconstruct a user's entire desktop session. Any real deployment needs a
  minimisation and retention story that does not exist yet.
- Not portable as written. Tier D leans on X11 window enumeration; Wayland deliberately
  restricts exactly these queries. This is a deployment blocker, not a detail.
