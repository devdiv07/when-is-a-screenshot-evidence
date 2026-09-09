# Candidate Capture-Provenance Contract

**Status: CANDIDATE. Not validated. Not sufficient.**

Every field below satisfies at least one of:

1. it addresses a **measured** information deficit from Phase C
   (`outputs/information_deficits.csv`, `outputs/field_set_analysis.md`); or
2. it is **explicitly required by the threat model** (`research/THREAT_MODEL.md`), in which
   case its historical-deficit column reads `0 — threat model only`.

Fields that meet neither test are not in this contract.

Trust tiers T1–T6 are defined in `research/THREAT_MODEL.md` §3. Recall the tier fallacy
stated there: **a T4 (OS-observed) field is truthfully reported and adversarially chosen.**
Raising a field's tier buys integrity of the *report*, not integrity of the *claim*.

This is an **attestation ladder**, not one schema. Each tier is separately collectable,
separately costed, and separately falsifiable in Phase I. **No claim is made that the top
tier is sufficient** — that is precisely what the experiment must test.

---

## Tier A — Human-readable window metadata

Cheap, portable, and **evidentially weak**. Included because it is what everyone proposes
first and because Phase I needs it as the baseline that fails.

| | `WINDOW_TITLE` | `WM_CLASS` |
|---|---|---|
| description | title string of the relevant window | window-manager class / app id |
| historical cases addressed | 0 as a resolving bundle (272 cases as a **verdict-`no`** bundle) | 0 as resolving |
| trust source | **T2 APPLICATION_ASSERTED** | **T2 APPLICATION_ASSERTED** |
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
| trust source | **T4 OS_OBSERVED** | **T4/T5** | T4 | T4 | T4 |
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

## Tier C — Code and content lineage

| | `AGENT_WRITTEN_CODE_LINEAGE` | `CONTENT_HASH` |
|---|---|---|
| description | was the owning executable/script authored during this episode? | hash of captured bytes and of any source image |
| historical cases | 14 | **43** (every derivation chain) |
| trust source | **T3 HARNESS_OBSERVED** (the harness sees the writes) | T3/T5 depending on who hashes |
| agent spoofability | **partial and important**: cannot hide a write the harness saw, but *can* pre-stage content, write via a child process, or fetch code written earlier/elsewhere | cannot forge a hash; **can choose what to hash** |
| application spoofability | n/a | n/a |
| OS observability | needs harness file-write tracking, not just OS | high |
| cost | medium — requires episode-scoped write tracking | low |
| privacy | medium (file contents) | low |
| portability | harness-specific | universal |
| failure modes | **A4** — the *browser* is not agent-written; the HTML it renders is. Lineage must follow the **content**, not the binary | derivation root may be a synthesised image, so chaining terminates without resolving (30 cases) |
| absence ⇒ UNKNOWN? | yes, for interpreter/browser-mediated scenes | **yes**, for any derived artifact |
| required? | **required** | **required** |

This tier is where the `DAV_task_0` case is actually decided: the deciding fact is not that
a Tk window existed, but that **the code drawing it was written 3 events earlier by the
agent**. It is also the tier most likely to be under-specified — "written during the
episode" needs a precise definition covering pre-staging and indirection.

## Tier D — Display composition

**The dominant tier: 240 of 287 eligible cases (83.6%).** These four fields are conjunctive;
none is useful alone (Phase D §2).

| | `CAPTURE_REGION` | `VISIBLE_WINDOW_SET` | `Z_ORDER` | `WINDOW_GEOMETRY` | `ACTIVE_WINDOW_IDENTITY` |
|---|---|---|---|---|---|
| description | rectangle actually captured | every mapped window at the capture instant | stacking order | per-window position/size | which window held focus |
| historical cases | 240 (bundle) | 240 | 240 | 240 | 35/41/32 (bundles) |
| trust source | **T3/T4** — depends whether the harness or the compositor reports it | **T4** | **T4** | **T4** | **T4** |
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
| trust source | **T2 APPLICATION_ASSERTED**, promotable to T4 via a privileged browser extension / CDP over a channel the agent cannot call | T2→T4 as above | **T2** — asserted by an app the agent may have written |
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
| trust source | T5 | T5 | **T6** |
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
