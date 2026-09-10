# Phase J lab — implementation corrections

Separate from `infra/IMPLEMENTATION_CORRECTIONS.md`, which documents IC-1…IC-4 for the
**frozen** Phase I lab and must not be edited. Numbering continues so the two files read as
one sequence.

Same discipline as Phase I: corrections are documented **before** re-running affected cases,
and none of them changes a contract, a rule, or a measurement.

---

## IC-5 — a launched client's surface must be matched by process *tree*, not by `Popen.pid`

**Discovered:** during final verification of the platform run, 2026-09-10, by comparing the
construction-time ground truth against the recorder's independent observation.

**Observation:** the Wayland ground-truth records read

```json
"viewer_binary": null,
"fallbacks_tried": [{"binary": "eog", "result": "no surface within 10s"}],
"result": "NO LEGITIMATE VIEWER COULD BE STARTED"
```

while the trusted recorder, observing the same moment independently, reported
`executable_path = /usr/bin/eog`, `command_line = eog /lab/work/quarterly_report.png`,
`app_id = eog`, `shell = xdg_shell`, `parent_pid = 1`.

**Why the first implementation was wrong.** Two compounding defects:

1. `spawn()` used `subprocess.Popen(cmd, shell=True)`. `/bin/sh` **forks** the target rather
   than exec'ing it, so `Popen.pid` is the shell's pid and the application's pid is
   different.
2. `wait_for_surface()` on the Wayland arm matched a surface's compositor-reported pid
   against `Popen.pid` **exactly**. It therefore never matched, timed out, and killed the
   shell — leaving the already-mapped `eog` reparented to init (`parent_pid = 1`) and
   still running.

The X11 arm did not exhibit this because its `surface_count()` counts `wmctrl -l` lines and
ignores pid entirely. That asymmetry is what made the defect visible: the same construction
produced `viewer=eog` on one arm and `null` on the other.

**What was and was not affected.**

- **The scene was constructed correctly on both arms.** The recorder observed a genuine,
  unmodified `/usr/bin/eog` holding a genuine native surface, and the captured pixels contain
  the intended content (501,867 fabricated pixels in Case R on both platforms).
- **The construction-time ground truth was inaccurate on the Wayland arm.** Ground truth is
  the independent label for this experiment, so an inaccurate one is a defect even when the
  measurement is right.
- No spurious surface was introduced. The fallback probed `imv`, which does not exist as a
  binary name (see IC-6), so nothing else was launched or mapped. This is **not** an IC-2
  class window leak, and that was checked rather than assumed: Case R enumerated exactly one
  surface.

**Correction:**

1. `spawn()` now issues `exec <cmd>`, so the shell **becomes** the binary and `Popen.pid` is
   the application's pid.
2. `wait_for_surface()` accepts the launched pid **or any descendant of it**, walking the
   `/proc/<pid>/stat` ppid chain, so a client that forks a helper still counts.

**Contract impact:** none. No contract, rule, adjudicator or recorder field was touched.

**Affected cases:** ground-truth metadata for the two Wayland cases. Both arms were re-run
after the correction.

**Result stability across the correction — checked, not assumed:**

| | before IC-5 | after IC-5 |
|---|---|---|
| `x11_P` capture sha256 | `314f00e1c77c…` | `314f00e1c77c…` |
| `x11_R` capture sha256 | `c4d0da448283…` | `c4d0da448283…` |
| `wayland_P` capture sha256 | `91650fa2ad55…` | `91650fa2ad55…` |
| `wayland_R` capture sha256 | `b73fe5968318…` | `b73fe5968318…` |
| bindings changed X11→Wayland | 0 / 12 | **0 / 12** |
| ground truth `viewer_binary` (Wayland) | `null` **(wrong)** | `eog` **(correct)** |

The correction changed the accuracy of the record and **nothing** about the measurement.

---

## IC-6 — Debian ships `imv` as `imv-wayland` / `imv-x11`

**Discovered:** same verification pass.

**Observation:** the viewer fallback list probed `which imv`, which fails. The `imv` package
**is** installed (`ii imv 4.3.0-1.1+b3`) but provides `/usr/bin/imv-wayland` and
`/usr/bin/imv-x11`, not a plain `imv`.

**Why it matters:** the fallback was recorded as `"result": "not installed"`, which is
misleading — the viewer was installed and merely misnamed in the probe. Had `eog` genuinely
failed, the arm would have reported no viewer available when one was.

**Correction:** the fallback lists now name `imv-wayland` and `imv-x11` (and `display` on
X11).

**Contract impact:** none.

**Affected cases:** none in practice. `eog` is first on both lists and started natively on
both platforms in every run, so no fallback was ever taken. Recorded because a latent
fallback that cannot fire is a defect waiting for the run where it is needed.
