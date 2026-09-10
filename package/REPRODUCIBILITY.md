# Reproducibility

**This is not a one-command reproduction, and this document does not pretend otherwise.**
Three of the four arms reproduce fully from what is in the repository. One is blocked by a
hardware/backend condition, and the raw benchmark corpus is not redistributed here.

---

## 1. Pinned states

| Tag | Commit | What it froze |
|---|---|---|
| `recoverability-audit-v1` | `f8e23a5` | retrospective audit; general post-hoc scene provenance **NO-GO** |
| `phase1-analytic-v1` | `fa78c2d` | contract-logic arm over analyst-derived vectors; empirical arm **not run** |
| `phase1-empirical-v1` | `a444f0d` | real X11 arm; kill criterion **fired**; S1 and S2 |
| `phase1-closed-v1` | `c74cd36` | Phase I closed / INSUFFICIENT |
| **`phaseJ-epistemic-boundary-v1`** | **`58f0eeb`** | **13b static classification + X11-vs-Wayland comparison. This package.** |

All tags except the last are annotated; `git rev-parse --short <tag>^{commit}` gives the
commits above.

**External source, pinned:** `ByteYellow/AgentProvenance` @
`fc2e62647dc64b6d23144b88e0e0ac101b4f2793` (HEAD of `main` at inspection, 2026-08-18).

## 2. Environment actually used

| | |
|---|---|
| Host OS | Windows 11 (26100), Docker Desktop 4.90.0, engine 29.7.2 |
| Analysis Python | **3.13.5** (project declares 3.11+) |
| Analysis dependencies | **none** — standard library only, including the figure generator |
| Container base | `debian:bookworm-slim` |
| X11 lab image | `sceneprov-lab:2.1` (`infra/Dockerfile`) |
| Dual-stack lab image | `sceneprov-wl:1.5` (`infra/wayland_lab/Dockerfile`) |
| Required capability | **`--cap-add=SYS_PTRACE`** |

**`SYS_PTRACE` is not optional.** Docker drops it by default; without it the recorder cannot
`readlink /proc/<pid>/exe` or read `/proc/<pid>/fd` for another user's process, and every run
silently reports `executable_path: null` with a permission-denied observation failure. The
frozen Phase I lab ran with it, so the Phase J lab must too or the arms are not comparable.

## 3. What is NOT in git

`.gitignore` excludes the raw corpus and derived caches:

| Path | Present locally | Redistributed |
|---|---|---|
| `outputs/raw/` | 697 files | **no** |
| `outputs/cache/` | 8 files | **no** |
| `*.zip`, `*.tar.gz`, `*.qcow2` | — | no |

Everything the package cites — `audit_metrics.json`, `information_deficits.csv`,
`field_coverage.csv`, `analytic_vs_empirical.csv`, `empirical_risk_coverage.csv`,
`empirical_raw/`, `platform_raw/` — **is committed**, so every figure and every number
regenerates without the raw corpus. Only re-deriving the audit *from source traces* needs §4.

## 4. How the corpus was retrieved (selective ZIP-over-HTTP)

The WeaveBench archives total ~9.6 GB, dominated by 2,048 screenshot PNGs that this study
never needed.

`scripts/remote_zip.py` reads each archive's **central directory** over HTTP range requests,
selects only the text members (`chat.jsonl`, `score.json`, task `.md` specs), and fetches
just those byte ranges.

- **1.79 GB** of text members fetched
- **0** image members downloaded
- every member **CRC-verified** against the archive's own directory entry
- source URL, archive member path, size and content hash recorded per member

This depends on the CDN honouring `Accept-Ranges`. If it stops doing so, the fallback is a
full archive download — the analysis is unaffected, only the retrieval cost.

## 5. Regenerating each result

### 5.1 Figures — always reproducible, no dependencies

```bash
python package/scripts/make_figures.py
```

Reads frozen artifacts, writes 7 SVGs plus `package/figures/FIGURE_DATA.json` containing every
plotted value and its source artifact. Deterministic: same inputs → byte-identical SVGs.
Verify with the SHA-256 list in [`PACKAGE_MANIFEST.md`](PACKAGE_MANIFEST.md).

### 5.2 The 13b static classification — fully reproducible

```bash
python scripts/static_13b_trace.py
```

Requires nothing but the repository. It:

- copies the frozen 13b record (never modifies Phase I artifacts),
- injects one journal entry and derives the Tier C value with **frozen recorder code**,
- runs the **unchanged** adjudicator,
- **self-checks** that replaying the original reproduces the Phase I verdicts at all 13
  configurations (`replay_matches_frozen_phase1: true`) — if this prints `False`, the frozen
  apparatus has drifted and nothing downstream should be trusted,
- records sha256 of `adjudicator.py`, `recorder.py`, `adjudicate_empirical.py` and
  `adversarial_cases.py` with the run.

### 5.3 The platform comparison — reproducible except the portal stream arm

```bash
docker build -t sceneprov-wl:1.5 infra/wayland_lab/
docker run --rm --cap-add=SYS_PTRACE \
  -v "$PWD/outputs/platform_raw:/lab/hostout" sceneprov-wl:1.5 \
  bash -c 'python3 /lab/run_platform.py && cp -r /lab/out/raw /lab/out/ground_truth \
           /lab/out/shots /lab/out/portal_probe.json /lab/hostout/'
python scripts/platform_matrix.py
```

**Expected, and stable across our re-runs:**

| Check | Expected |
|---|---|
| bindings changed X11 → Wayland | **0 of 12** |
| `AvailableSourceTypes` | **1** (MONITOR only) |
| field observation failures | **0** on all four runs |
| `x11_P` / `x11_R` / `wayland_P` / `wayland_R` capture sha256 | `314f00e1…` / `c4d0da44…` / `91650fa2…` / `b73fe596…` |

Capture hashes reproduced byte-identically across independent container runs, including across
the IC-5 correction. **Recorder skew does not reproduce stably** and no claim rests on it
(see `HOSTILE_REVIEW.md` H-3).

### 5.4 The X11 empirical lab (Phase I)

```bash
docker build -t sceneprov-lab:2.1 infra/
docker run --rm --cap-add=SYS_PTRACE sceneprov-lab:2.1 python3 /lab/run_empirical.py
docker run --rm --cap-add=SYS_PTRACE sceneprov-lab:2.1 python3 /lab/adjudicate_empirical.py
```

Ground-truth isolation is enforced and tested, not asserted: `/lab/test_isolation.py` performs
a static check, a dynamic `open()` guard, and a non-vacuity check over the 13 ground-truth
files.

**S1 (atomicity) is a timing experiment.** 120 trials per run; the violation *rate* reproduced
(120/120 in both runs) but the violation *mode* inverted between runs. Expect the rate, not the
mode.

### 5.5 The retrospective audit

```bash
python scripts/run_audit.py        # R0-R5 -> outputs/audit_metrics.json
python scripts/field_coverage.py   # -> outputs/field_coverage.csv
```

Deterministic given the manifest. Two parameters materially affect results and are recorded in
`scripts/scene_provenance.py`: `LOOKBACK = 16`, `BRACKET_GAP = 6`. **Any single-parameter
recoverability number is meaningless without the sensitivity curve** (`RESULTS.md` §2).

Re-deriving from source traces additionally requires the corpus (§4).

## 6. What cannot currently be reproduced

| Blocked | Why | What would unblock it |
|---|---|---|
| **Portal ScreenCast stream metadata** | `Start` fails with `wlroots: unable to receive a valid format from wlr_screencopy` — PipeWire buffer-format negotiation in a headless container with **no DRM device** (`drmGetDevices2 failed`), software `pixman` renderer | a host with a real GPU/DRM node, or a portal backend whose stream path works headless |
| **GNOME / KDE portal backends** | not tested; out of scope for this run | running the same two cases against `xdg-desktop-portal-gnome` or `-kde`, which implement WINDOW sources |
| **Nested-compositor analogue of S2 on Wayland** | not tested | a nested Wayland compositor case |
| **S1 run 1 JSON artifact** | overwritten before export; **only the run log survives** | nothing — it is gone, and run 1's figures are quoted from the log with that stated |
| Application-state attestation, H-RB, adaptive red-team | never executed | out of scope; deliberately not opened |

`grim` captures succeed throughout, so the compositor's screencopy protocol works in this
environment. It is specifically the portal→PipeWire pipeline that is blocked.

## 7. Discarded runs — must NOT be included

These were invalidated by a documented defect and are excluded from every figure and number in
this package. If you re-run and find these artifacts, they are not results:

| Discarded run | Invalidated by | Defect | Superseded by |
|---|---|---|---|
| empirical suite on `sceneprov-lab:≤1.6` | **IC-2** | cleanup used `pkill -f 'python3 '` and missed `python3 < script`; a leaked window entered the visible set of 7 later scenarios and produced spurious `R5_composite_frame` abstentions | run on `2.0+` |
| case 13b on `sceneprov-lab:≤2.0` | **IC-4** | 13b put the resource path in argv and **never rendered the fabrication**; its SUBSTITUTE verdict was right for the wrong reason | 13b on `2.1` |
| visible-set PIDs before IC-3 | **IC-3** | `wmctrl` reads `_NET_WM_PID` and returned `pid=0` throughout | X-Resource resolution on `2.0+` |
| Wayland ground truth before IC-5 | **IC-5** | `viewer_binary: null` recorded while `eog` was in fact running | re-run on `sceneprov-wl:1.5` |
| lookback sweep 5.5% → 72.7% | pre-correction resolver | computed before the GUI-capability test, process-exit invalidation and composite demotion | 4.8% → 54.9% |

All corrections are documented in `infra/IMPLEMENTATION_CORRECTIONS.md` (IC-1…IC-4) and
`infra/wayland_lab/IMPLEMENTATION_CORRECTIONS.md` (IC-5, IC-6), each **written before** the
affected cases were re-run.

## 8. Determinism boundaries

| Reproduces exactly | Reproduces qualitatively | Does not reproduce |
|---|---|---|
| all audit metrics, field coverage, adjudication verdicts, the 13b static trace, all 7 figures, platform capture hashes and the binding matrix | S1 violation **rate** (120/120), Phase J case construction | S1 violation **mode**; recorder skew ranges; pids and X11 window ids |

Process ids, window ids and timestamps differ every run by construction and are never load
-bearing in any claim.

## 9. Verifying the package itself

```bash
python package/scripts/make_figures.py          # regenerate figures
python scripts/static_13b_trace.py              # regenerate the static trace
python scripts/platform_matrix.py               # regenerate matrix + metrics
git status --porcelain                          # expect: no unexpected diffs
```

A clean `git status` after regeneration is the strongest available check that the numbers in
this package are the numbers its scripts produce.
