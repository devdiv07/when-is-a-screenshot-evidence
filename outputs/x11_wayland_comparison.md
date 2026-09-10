# X11 vs Wayland — which provenance binding does compositor mediation actually improve?

**Two predeclared cases. Not a benchmark. Constructed suite; no population claims.**

Reproduce: `docker build -t sceneprov-wl:1.5 infra/wayland_lab/` then
`docker run --rm --cap-add=SYS_PTRACE sceneprov-wl:1.5 python3 /lab/run_platform.py`,
then `python scripts/platform_matrix.py`.

Raw: `outputs/platform_raw/` · Matrix: `outputs/platform_binding_matrix.csv` ·
Cases: `outputs/platform_comparison_cases.csv` · Metrics:
`outputs/platform_comparison_metrics.json`

---

## Headline

> **Zero of twelve comparable bindings changed evidence level between X11 and Wayland.**

Wayland changes **who may capture** and **who reports surface identity**. It does not change
**what can be bound**. The assurance chain terminates at exactly the same edge on both
platforms, and it is the same edge Phase I identified: `process/client → displayed resource`.

The predeclared prediction was **RESULT A** — that Wayland would materially improve
`capture → surface` while failing to reach the displayed resource. The second half is
**confirmed**. The first half is **REFUTED for the standard capture path**, and the
refutation is measured, not argued.

Primary outcome: **RESULT B**, with the portal *stream-metadata* sub-arm **BLOCKED**
(RESULT D) for a stated environmental reason.

---

## Apparatus

| | X11 arm | Wayland arm |
|---|---|---|
| display server | Xvfb + Openbox (matches the frozen Phase I lab) | **sway 1.7 (wlroots), headless backend, `WLR_RENDERER=pixman`** |
| capture | ImageMagick `import`, root-window grab | **`grim` via `wlr-screencopy-unstable-v1`** (compositor copies its own output buffer) |
| standard capture API | n/a | **`xdg-desktop-portal` + `xdg-desktop-portal-wlr`**, PipeWire |
| surface enumeration | `wmctrl -lpG` + `xwininfo -root -children` | **`swaymsg -t get_tree`** (compositor IPC) |
| surface → pid | `XResQueryClientIds` (X-Resource extension) | **compositor's own `pid` field** |
| legitimate viewer | `/usr/bin/eog` — **native X11** | `/usr/bin/eog` — **native Wayland** (`shell=xdg_shell`) |
| substitute surface | GTK3, `GDK_BACKEND=x11` | GTK3, `GDK_BACKEND=wayland` — **native Wayland** |

**Same application on both arms.** eog ran as a native client of each platform; no result
here rests on an XWayland surface being presented as native Wayland. XWayland was left
enabled precisely so that nativeness was measurable rather than assumed.

**Three trust domains**, one more than the Phase I lab: compositor session (uid 1001),
unprivileged attacker (uid 1000), trusted recorder (root + `CAP_SYS_PTRACE`).

**Zero field observation failures** on all four runs. Capture hashes reproduce
byte-identically across independent container runs. `eog` was used on every arm with **zero
fallbacks taken**.

**Two implementation corrections, documented before re-running**
(`infra/wayland_lab/IMPLEMENTATION_CORRECTIONS.md`). IC-5: `shell=True` forked the client, so
the Wayland surface check matched the shell's pid and recorded `viewer_binary: null` while
the recorder independently observed genuine `/usr/bin/eog` running — a defect in the
**ground-truth record**, not in the measurement, caught precisely because the recorder
observes independently of the constructor. IC-6: Debian ships `imv` as
`imv-wayland`/`imv-x11`, so the fallback probe could never have fired.

**The result is stable across the correction:** all four capture sha256 values are identical
before and after, and the binding matrix is unchanged at **0/12**. Only the ground-truth
`viewer_binary` field changed. Checked, not assumed — per the IC-2/IC-4 precedent that a
construction defect can invalidate a verdict.

### Construction verified at the pixel level

The frozen IC-4 lesson — a case can look correctly built and render nothing — was applied.
Pixel counts in the captured PNGs:

| capture | `#ffd6d6` (fabricated) | white | verdict |
|---|---|---|---|
| `x11_R.png` | **501,867** | 823 | fabrication genuinely on screen |
| `wayland_R.png` | **501,867** | 826 | fabrication genuinely on screen |
| `x11_P.png` | 33 (antialias noise) | 789,060 | substitute surface genuinely on top |
| `wayland_P.png` | 33 (antialias noise) | 586,302 | substitute surface genuinely on top |

---

## The binding matrix

| Row | 1 artifact→capture | 2 capture→surface | 3 surface→process | 4 process→resource | 5 resource→app state | 6 app state→claim |
|---|---|---|---|---|---|---|
| **X11 Case P** | EXACT | **WEAK** | EXACT | UNKNOWN | UNKNOWN | UNKNOWN |
| **Wayland Case P** | EXACT | **WEAK** | EXACT | UNKNOWN | UNKNOWN | UNKNOWN |
| **X11 Case R** | EXACT | STRONG | EXACT | **WEAK** | UNKNOWN | UNKNOWN |
| **Wayland Case R** | EXACT | STRONG | EXACT | **WEAK** | UNKNOWN | UNKNOWN |

Per-cell observer, mechanism, supporting evidence, platform-native-vs-reconstructed, and
attacker control are in `outputs/platform_binding_matrix.csv`.

`STRONG` in column 2 is **by elimination** — exactly one surface was enumerated, so the
frame can only be its pixels. It is contingent on the enumeration being *complete*, and the
frozen S2 result already falsified that assumption for X11 (a nested Xephyr server hides
inner surfaces). **The analogous nested-compositor attack was not tested on Wayland**, so
that contingency is open on both arms.

---

## Case P — can the trusted capture path bind pixels to the originating client?

**Measured answer: no, and not because of a lab limitation.**

Both arms produced a frame containing **two** clients' pixels: a genuine `eog` showing the
genuine target, and an agent-created GTK surface in front of it. On neither platform does
the capture carry any per-pixel or per-region attribution.

The decisive Wayland fact was read directly off the running portal, and needed no session:

```
org.freedesktop.portal.ScreenCast  version = 4
AvailableSourceTypes = 1   ->  MONITOR: true   WINDOW: false   VIRTUAL: false
org.freedesktop.portal.Screenshot  ->  interface does not exist on this backend
```

**The standard Wayland capture API does not offer window-scoped capture at all** on this
backend. `SelectSources` was called with `types = MONITOR|WINDOW` (bitmask 3) and returned
success — the WINDOW bit was accepted and silently ignored; the backend's own trace shows it
enumerating **outputs**:

```
[INFO] - dbus: option types:3
[INFO] - wlroots: capturable output: headless model: headless: id: 38 name: HEADLESS-1
```

So the selectable unit of the standard API is a **monitor**, exactly as on X11. A capture
taken through it is output-scoped, and `capture → surface` must be reconstructed from
enumeration and geometry on both platforms. `WEAK` on both.

### What Wayland *does* change here — and it is not nothing

| Property | X11 | Wayland |
|---|---|---|
| who can produce the frame | **any client with display access** can grab the root window | **only the compositor** — no client can read another client's buffer |
| who reports surface identity | X server, to any client | compositor, only via its own IPC |
| per-pixel attribution in the capture | none | none |

This is a real improvement in the **integrity of the capture path** — it removes an entire
class of attack in which the agent itself forges or intercepts the frame. It is *not* an
improvement in **attribution**. Recording both is the point: the platform hardened the
observer without extending what the observer can see.

### Identity strings are client-asserted on both platforms

Measured, both arms, same GTK3 substitute calling `GLib.set_prgname("eog")`:

| | substitute (attacker, `python3.11`) | genuine `eog` |
|---|---|---|
| X11 `WM_CLASS` | `eog` | `Eog` |
| **Wayland `app_id`** | **`eog`** | **`eog`** |
| window title | `quarterly_report.png` | `quarterly_report.png` |

**Wayland's `app_id` is exactly as client-asserted, and exactly as spoofable, as X11's
`WM_CLASS`.** On the Wayland arm the two strings are byte-identical; only the pid separates a
genuine viewer from an impostor.

*Honest caveat:* on X11 the genuine app reported `Eog` and the substitute `eog`, because GTK
derives the X11 class name differently from `prgname`. That is an accident of toolkit
convention, **not a defence** — the attacker can set either string — and it is recorded so
the asymmetry in the raw data is not mistaken for a security property.

---

## Case R — does compositor mediation establish anything about the displayed resource?

**Predeclared prediction: it should not. Result: CONFIRMED, on both platforms, identically.**

A genuine unmodified `/usr/bin/eog`, a genuine surface, attacker-authored bytes at the
declared target path — the direct platform analogue of frozen case 13b.

What each platform reported about **which resource was on screen**:

| Observation | X11 | Wayland |
|---|---|---|
| compositor/display server reports the displayed resource | **no such field** | **no such field** |
| window title | `quarterly_report.png` (APPLICATION_ASSERTED) | `quarterly_report.png` (APPLICATION_ASSERTED) |
| argv | `eog /lab/work/quarterly_report.png` | `eog /lab/work/quarterly_report.png` |
| **open regular file descriptors at the capture instant** | **`[]`** | **`["/memfd:wayland-cursor (deleted)"]`** |
| holds the declared target open | **false** | **false** |

The compositor's job is surfaces and buffers. Neither platform has a concept of "the resource
this surface is showing", so neither reports one. `process/client → displayed resource` is
`WEAK` on both, resting entirely on argv — a string the attacker chooses, which does not
establish that those bytes were the pixels rendered.

### The strongest platform-native resource binding available, measured

Open file descriptors at the capture instant are the closest thing either platform offers to
a kernel-observed resource binding — and they returned **nothing useful on either arm**.
`eog` reads the image, decodes it, and closes the descriptor. At the moment the pixels were
captured, the rendering process held **no** handle to the file it was displaying.

**MEASURED FACT**, both platforms. This bounds the naive form of the successor hypothesis
H-RB: a recorder that samples open file descriptors at the capture instant cannot recover the
displayed resource for an ordinary image viewer, because the binding no longer exists in
kernel-visible state by then. Whatever binds pixels to bytes must be recorded **when the read
happens**, not when the capture happens.

That is the renderer-boundary pattern showing up again, in a third place.

---

## Portal stream metadata — BLOCKED, and why

A full `ScreenCast` session was attempted so that the returned stream properties could be
inspected for any client/surface identity. It did not complete:

| Step | Result |
|---|---|
| `CreateSession` | **SUCCEEDED** (response_code 0) |
| `SelectSources` (`types=MONITOR\|WINDOW`) | **SUCCEEDED** (response_code 0) |
| `Start` | **FAILED** (response_code 2) |

Cause, from the backend's own TRACE log
(`outputs/platform_raw/portal_start_diagnostic.log`):

```
[TRACE] - wlroots: callbacks registered
[INFO]  - wlroots: unable to receive a valid format from wlr_screencopy
```

PipeWire buffer-format negotiation failed in a headless container with no DRM device
(`drmGetDevices2 failed: No such file or directory`, pixman software renderer). **This is an
environment limitation, not a portal API limitation.**

Consequently: **the contents of the returned stream properties were NOT observed, and are NOT
inferred from documentation.** Recorded BLOCKED per RESULT D.

What this does *not* undermine: the decisive Case P finding comes from
`AvailableSourceTypes`, a property read directly off the running portal without any session.
`grim`'s own captures succeeded throughout — the compositor's screencopy protocol works
here; it is the portal→PipeWire pipeline that is blocked.

One further measured detail: the only identity the portal logged is
`dbus: app_id: ` *(empty)* — and that field identifies the **requesting** application, never
the captured content. The standard API's identity concept points the wrong way for this
problem.

---

## What changed, what did not

**Improved by Wayland (measured):**
1. Capture-path integrity — only the compositor can produce the frame.
2. Directness of `surface → process` — the compositor reports the client pid as a
   first-class field, with no `_NET_WM_PID` trap. (Corroborating E070's scoping: in *this*
   lab GTK/eog **did** set `_NET_WM_PID`, unlike the Tk/ImageMagick windows of the frozen
   lab. It cannot be relied on either way, and is client-asserted whenever present.)
3. Recorder skew was observed lower on the Wayland arm, but the **comparative claim is
   WITHDRAWN as not reproducible**: the ranges moved materially between re-runs of the same
   image (X11 137–208 ms, Wayland 80–100 ms in the final run). Skew here is a property of
   recorder architecture and machine load, not of the platform, and no platform claim rests
   on it.

**Not improved (measured):**
1. `capture → surface` — output-scoped on both; the standard portal offers **no** window
   source type.
2. `surface → displayed resource` — no such field on either platform.
3. Identity-string trustworthiness — `app_id` is as client-asserted as `WM_CLASS`.
4. `displayed resource → application state` and `application state → claim` — untouched.

**Made worse by Wayland (measured):**
- Cross-client enumeration exists **only** through compositor-private IPC. The binding that
  is available is available through a **non-standard, per-compositor channel**; the
  standardised API exposes strictly less than X11 does. A provenance recorder built on
  `swaymsg` is a sway recorder, not a Wayland recorder.

---

## Interpretation, bounded

**RESULT B holds:** trusted mediation genuinely exists on Wayland, and the generic exported
API is insufficient for the provenance claim being asked about. The compositor knows which
client owns every pixel it composites. It simply does not export that, and the standardised
capture interface cannot even be asked for a window.

**RESULT A is refuted in its first half**, on the standard path. It would survive only for a
compositor whose portal implements window-source capture *and* reports the selected source's
client identity to the caller — a combination not present here and not verified anywhere by
this experiment.

**Do not read this as "Wayland is no better than X11."** It is better in the ways listed
above, and those matter for the *recorder's* integrity. It is not better at the thing this
project is measuring.

### Scope — what this does not establish

- One compositor (sway/wlroots), one portal backend (`xdg-desktop-portal-wlr`), one
  environment (headless, software-rendered, containerised). **GNOME's and KDE's portals
  implement window capture** and were **not tested**; a compositor that offers a WINDOW
  source could change the Case P result. That is a specific, cheap, falsifiable follow-up,
  and it is deliberately not run here.
- Two constructed cases. No rates, no population claims.
- The nested-compositor analogue of S2 was not tested on Wayland.
- Portal stream metadata was never observed.
