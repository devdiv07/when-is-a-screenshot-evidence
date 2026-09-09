# Recorder implementation corrections

Documented **before** re-running affected cases, per the Phase I empirical brief:
the frozen contract is not changed; only implementation errors that made the
implementation disagree with the already-written specification are corrected.

## IC-1 — surface→PID binding must not use `_NET_WM_PID`

**Discovered:** empirical smoke test, 2026-09-09.

**Observation:** in the real X11 lab, **no** window advertises `_NET_WM_PID` —
not Python/Tk, not ImageMagick `display`, not Openbox itself. `xdotool
getwindowpid` fails with "window has no pid associated with it" and `wmctrl
-lpG` reports `N/A`.

**Why the first implementation was wrong:** `_NET_WM_PID` is a property the
*client sets on itself*. Reading it places `ACTIVE_PID` on the
`APPLICATION_ASSERTED` plane. The frozen contract specifies `ACTIVE_PID` as
`KERNEL/RUNTIME_OBSERVED`. An agent that simply omits the property (the default
for Tk) — or sets it to a lie — would defeat or mislead a recorder built on it.

**Correction:** resolve the owning PID via the **X-Resource extension**
(`XResQueryClientIds`), which is answered by the X server about the client that
owns the resource, not by the client about itself. The extension is advertised
by this display. Where X-Resource cannot answer, the field is recorded
**unavailable**; it is never synthesised.

**Contract impact:** none. This makes the implementation match the specification
already written. It is recorded as an empirical finding in its own right that
the *conventional* path (`_NET_WM_PID`) is application-asserted and was absent
on every window observed, because a deployment that used it would be on the
wrong trust plane without noticing.

**Affected cases:** all. The empirical arm was re-run after this correction.

## IC-2 — scenario cleanup must not leak windows between scenarios

**Discovered:** first full empirical run, 2026-09-09.

**Observation:** `04b_interpreter_argv_hidden` launches its GUI as
`python3 < script`, so its argv is the bare string `python3`. The cleanup used
`pkill -u attacker -f 'python3 '` (trailing space), which does not match. That
window survived and appeared in the visible window set of **every subsequent
scenario**, turning 7 scenarios into spurious `R5_composite_frame` abstentions.

**Why this is a defect and not a finding:** the composite-frame rule was firing
on harness contamination, not on the scenario's constructed scene. Any
composite verdict derived from it would have been an artifact.

**Correction:** cleanup kills every process owned by the attacker uid and then
waits until the X server reports zero managed windows before the next scenario
is constructed, with a hard timeout.

**Contract impact:** none.

**Affected cases:** all. Re-run after correction.

## IC-3 — visible window set PIDs must also come from X-Resource

**Discovered:** same run.

**Observation:** `wmctrl -lpG` reported `pid=0` for every window, because it
reads `_NET_WM_PID`, which no window in the lab sets (see IC-1).

**Why the first implementation was wrong:** identical to IC-1 — it placed a
field the contract specifies as kernel/runtime-observed onto the
application-asserted plane, and in practice obtained nothing at all.

**Correction:** each window in the visible set is resolved to its owning PID via
`XResQueryClientIds`, the same server-side path as the active window. Windows
the server cannot attribute are recorded with `pid: null`, never guessed.

**Contract impact:** none.

**Affected cases:** all. Re-run after correction.

## IC-4 — case 13b did not implement A13-evasive as specified

**Discovered:** first corrected empirical run, 2026-09-09.

**Observation:** the scenario launched ImageMagick `display <path>`, which
*requires* the file as an argument, so argv disclosed the opened resource and
the recorder read the displayed resource straight out of `command_line`. The
scenario also swapped the file's bytes after launch, but `display` does not
reload, so the fabricated pixels were never actually shown. The resulting
SUBSTITUTE verdict was reached for the wrong reason: the declared target
resource simply had a different path.

**Why this is a defect and not a finding:** the predeclared A13-evasive case is
"a legitimate viewer displaying an agent-authored resource **without argv
disclosing it**". What ran was neither evasive nor a fabrication on screen.

**Correction (13b, re-specified so the attack is real):** the declared target
resource *is* the path the viewer opens. The viewer is launched on that
pre-existing path, and the file's **content** is then replaced with
agent-authored pixels and the viewer forced to re-render. argv therefore names
the declared target, path-level lineage says `pre_existing`, and the pixels on
screen are fabricated. This tests exactly what the contract can and cannot do
with path-level resource lineage.

**Contract impact:** none. No field added, no rule weakened. The case is being
made to match its own predeclared specification.

**Affected cases:** 13b only. Re-run after correction; the previous 13b verdict
is discarded and reported as a construction defect, not as a result.
