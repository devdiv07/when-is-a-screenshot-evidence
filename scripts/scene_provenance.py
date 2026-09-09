"""Structural scene-provenance reconstruction for WeaveBench hybrid-agent traces.

Recovers, from trace structure only (no LLM/VLM semantic inference):

  R1 producer/action        which call produced the visual artifact
  R2 output artifact link   which concrete path it wrote, and whether that path is
                            a required deliverable and was actually delivered
  R3 capture source context which process/window/scene the pixels came from
  R4 scene lineage class    TARGET_SCENE / AGENT_SUBSTITUTE_SCENE / DIRECT_SYNTHESIS /
                            DERIVED_FROM_PRIOR_EVIDENCE / UNKNOWN
  R5 target reachability    is the required target application structurally reachable
                            from the delivered artifact, or is substitute lineage proven

Every edge carries a confidence: EXACT | STRONG | WEAK | UNKNOWN.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- producers
SHELL_CAPTURE = re.compile(r"\b(gnome-screenshot|scrot|maim|spectacle|flameshot|xwd)\b")
IM_CAPTURE = re.compile(r"\bimport\s+-(?:window|root)\b")
PIL_SYNTH = re.compile(r"Image\.new\s*\(|ImageDraw\.")
PIL_ANY = re.compile(r"from\s+PIL\s+import|PIL\.Image|Image\.open\s*\(")
MPL_SYNTH = re.compile(r"savefig\s*\(")
BROWSER_SHOT = re.compile(r"--screenshot|wkhtmltoimage|playwright|puppeteer")
IM_TRANSFORM = re.compile(
    r"(?<![\w-])(?:convert|mogrify)\s+[^\n|;]*\.(?:png|jpg|jpeg)"
    r"|\.crop\s*\(|\.resize\s*\(|\.paste\s*\(|ImageChops"
)
FILE_COPY = re.compile(r"(?<![\w-])(?:cp|mv|install)\s+[^\n|;]*\.(?:png|jpg|jpeg)")
TK_RENDER = re.compile(r"\btkinter\b|\btk\.Tk\s*\(|PySimpleGUI|\bTkinter\b")
ZENITY = re.compile(r"\bzenity\b|\byad\b")
HTML_UI = re.compile(r"<!doctype html|<html[ >]", re.I)

# ------------------------------------------------------------ output paths
PATH_CHARS = r"[^\s'\"`;|&>)]+"
IMG_EXT_RX = r"(?:png|jpg|jpeg|gif|webp|bmp)"

OUT_PATTERNS = [
    ("shell_capture_f", re.compile(
        r"(?:gnome-screenshot|scrot|maim|spectacle|flameshot)[^\n;|&]*?-f\s+['\"]?("
        + PATH_CHARS + r")")),
    ("shell_capture_pos", re.compile(
        r"(?:scrot|maim)\s+(?:-\w+\s+)*['\"]?(" + PATH_CHARS + r"\." + IMG_EXT_RX + r")")),
    ("pil_save", re.compile(
        r"\.save\s*\(\s*[fru]{0,2}['\"]?(" + PATH_CHARS + r"\." + IMG_EXT_RX + r"|"
        + PATH_CHARS + r"\.pdf)")),
    ("savefig", re.compile(
        r"savefig\s*\(\s*[fru]{0,2}['\"]?(" + PATH_CHARS + r"\.(?:png|jpg|jpeg|pdf|svg))")),
    ("write_text", re.compile(
        r"['\"]?(" + PATH_CHARS + r"\.(?:html|svg|py|json|txt|csv|md))['\"]?\s*\)?\s*\.write_text")),
    ("redirect", re.compile(
        r">\s*['\"]?(" + PATH_CHARS + r"\.(?:png|jpg|jpeg|html|svg|json|csv|txt|log|md))")),
    ("cp_mv", re.compile(
        r"(?:cp|mv|install)\s+(?:-\w+\s+)*" + PATH_CHARS + r"\s+['\"]?("
        + PATH_CHARS + r"\." + IMG_EXT_RX + r")")),
    ("browser_shot", re.compile(
        r"--screenshot=['\"]?(" + PATH_CHARS + r"\." + IMG_EXT_RX + r")")),
]

# Output paths are frequently computed (Path objects, f-strings, loop variables),
# e.g. OUT/f'compare_{n}_200.png'. Recover the trailing literal filename token so
# the artifact can still be linked; such links are TEMPLATED, never EXACT.
TEMPLATED_OUT = re.compile(
    r"(?:\.save|savefig)\s*\(\s*[^)]*?['\"]([A-Za-z0-9_{}.$-]*\." + IMG_EXT_RX + r")['\"]")

# ------------------------------------------------------------ launches
LAUNCH_PY = re.compile(
    r"(?:^|[;&|]\s*|\bnohup\s+|\bsetsid\s+(?:-f\s+)?)(?:DISPLAY=\S+\s+)?"
    r"(?:python3?|py)\s+(" + PATH_CHARS + r"\.py)", re.M)
XDG_OPEN = re.compile(r"xdg-open\s+['\"]?(" + PATH_CHARS + r")")
BROWSER_URL = re.compile(
    r"(?:google-chrome|chromium(?:-browser)?|firefox)[^\n;|&]*?['\"]?"
    r"((?:file|https?)://" + PATH_CHARS + r")")
SESSION_PID = re.compile(r"session\s+([\w-]+),\s*pid\s+(\d+)")
WINDOW_LIST = re.compile(
    r"\b(?:xwininfo|wmctrl|xprop)\b|\bxdotool\s+(?:search|getactivewindow|getwindowname)")
WINDOW_ROW = re.compile(r'0x[0-9a-f]+\s+"([^"]{1,160})"(?:\s*:\s*\(([^)]*)\))?')
NOT_FOUND = re.compile(r"(?:command not found|not found|No such file)", re.I)
# A launched program can only be the source of a captured scene if it can put a
# window on screen. This is a syntactic check on code the agent itself authored.
GUI_TOOLKIT = re.compile(
    "tkinter|Tkinter|PySimpleGUI|PyQt|PySide|QApplication|kivy|pygame|webview"
    "|zenity|yad|tk[.]Tk|Tk[(][)]|gi[.]repository|Gtk[.]|wx[.]App|plt[.]show|cv2[.]imshow")
# Invocations of a GUI binary that only query it and never map a window.
CLI_ONLY_FLAG = re.compile(
    "--list-extensions|--version|--help|--headless|--check|--status"
    "|--install-extension|--uninstall-extension|--dry-run|--print")
WINDOW_SCOPED_CAP = re.compile("gnome-screenshot[^" + chr(10) + "]*-w")
PROC_EXITED = re.compile(r"Process exited with code|exited with code \d+", re.I)
HEREDOC_WRITE = re.compile(r"(?:cat|tee)\s+(?:-a\s+)?>{1,2}\s*['\"]?(" + PATH_CHARS + r")['\"]?\s*<<")

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")
CAPTURE_PRODUCERS = {"SHELL_SCREENSHOT", "HARNESS_GUI_ACTION", "BROWSER_CAPTURE"}
SYNTH_PRODUCERS = {"PIL_SYNTHESIS", "MATPLOTLIB_SYNTHESIS"}

# How far back a capture may look for the process that owns the screen.
LOOKBACK = 16
# Maximum launch->capture event gap still counted as a bracketed (STRONG) capture.
BRACKET_GAP = 6
# Actions that close/kill the foreground window right after a capture.
CLOSE_ACTION = re.compile(r'"(?:alt|super)"\s*,\s*"f4"|pkill|killall|windowkill', re.I)


@dataclass
class Edge:
    kind: str
    src: str
    dst: str
    confidence: str          # EXACT | STRONG | WEAK | UNKNOWN
    evidence: str = ""

    def render(self) -> str:
        return f"{self.kind}({self.src}->{self.dst}|{self.confidence}|{self.evidence})"


@dataclass
class VisualCase:
    event_idx: int
    producer_kind: str
    producer_command: str = ""
    output_path: str = ""
    capture_channel: str = "none"
    source_process: str = ""
    source_kind: str = "unknown"
    scene_class: str = "UNKNOWN"
    r_level: int = 1
    edges: list = field(default_factory=list)
    ambiguity: str = ""
    is_required_deliverable: bool = False
    was_delivered: bool = False
    target_apps: str = ""
    target_status: str = ""
    evidence_scope: str = "intermediate"   # delivered_evidence | incidental_harness | intermediate
    output_path_kind: str = "literal"      # literal | templated | unresolved
    source_confidence: str = "UNKNOWN"     # EXACT | STRONG | WEAK | UNKNOWN
    weak_scene_hypothesis: str = ""        # class WEAK evidence would suggest


def classify_producer(cmd: str, tool: str) -> str:
    if tool == "__computer__":
        return "HARNESS_GUI_ACTION"
    if SHELL_CAPTURE.search(cmd) or IM_CAPTURE.search(cmd):
        return "SHELL_SCREENSHOT"
    if BROWSER_SHOT.search(cmd):
        return "BROWSER_CAPTURE"
    if PIL_SYNTH.search(cmd):
        return "PIL_SYNTHESIS"
    if MPL_SYNTH.search(cmd):
        return "MATPLOTLIB_SYNTHESIS"
    if IM_TRANSFORM.search(cmd):
        return "IMAGE_TRANSFORM"
    if PIL_ANY.search(cmd) and any(
            p.lower().endswith(IMAGE_EXT) for p, _r in extract_outputs(cmd)):
        # PIL used, no draw primitives, but an image is written -> transform of an input
        return "IMAGE_TRANSFORM"
    if FILE_COPY.search(cmd):
        return "FILE_COPY"
    if TK_RENDER.search(cmd):
        return "RENDERER_AUTHORING_TK"
    if ZENITY.search(cmd):
        return "RENDERER_AUTHORING_ZENITY"
    if HTML_UI.search(cmd):
        return "RENDERER_AUTHORING_HTML"
    return "OTHER"


def capture_channel(producer: str, cmd: str) -> str:
    if producer == "SHELL_SCREENSHOT":
        return "shell_routed"
    if producer == "HARNESS_GUI_ACTION":
        return "harness_native"
    if producer == "BROWSER_CAPTURE":
        return "browser"
    return "none"


def extract_outputs(cmd: str) -> list:
    out, seen = [], set()
    for rule, rx in OUT_PATTERNS:
        for m in rx.finditer(cmd or ""):
            p = (m.group(1) or "").strip("'\"")
            if p and p not in seen:
                seen.add(p)
                out.append((p, rule))
    return out


def build_authored_index(events) -> dict:
    """path -> event idx at which the agent itself authored that file."""
    authored = {}
    for e in events:
        if e.kind != "toolCall":
            continue
        a = e.args or {}
        if e.tool in ("write", "edit"):
            fp = a.get("file_path") or a.get("path")
            if fp:
                authored.setdefault(str(fp), e.idx)
        for m in HEREDOC_WRITE.finditer(e.command or ""):
            authored.setdefault(m.group(1).strip("'\""), e.idx)
        for p, rule in extract_outputs(e.command or ""):
            if rule in ("write_text", "redirect") and not p.lower().endswith(IMAGE_EXT):
                authored.setdefault(p, e.idx)
    return authored


def build_authored_source(events) -> dict:
    """path -> source text the agent wrote for it (write tool arg or heredoc body).

    Used only to test, structurally, whether an authored program can create a
    window at all. This is a syntactic check on code the agent itself wrote; it
    is not semantic interpretation of the trace.
    """
    src = {}
    for e in events:
        if e.kind != "toolCall":
            continue
        a = e.args or {}
        if e.tool in ("write", "edit"):
            fp = a.get("file_path") or a.get("path")
            body = a.get("content") or a.get("new_string") or ""
            if fp:
                src[str(fp)] = src.get(str(fp), "") + str(body)
        cmd = e.command or ""
        for m in HEREDOC_WRITE.finditer(cmd):
            path = m.group(1).strip("'\"")
            src[path] = src.get(path, "") + cmd[m.end():]
    return src


def is_gui_capable(path: str, authored_src: dict) -> bool:
    """True when the agent-authored program can put a window on screen."""
    body = authored_src.get(path) or authored_src.get(path.replace("file://", ""))
    if body is None:
        return False
    return bool(GUI_TOOLKIT.search(body))


def find_launches(events) -> list:
    """[(idx, entity, kind, ok)] — processes/URLs the agent started."""
    out = []
    for e in events:
        if e.kind != "toolCall" or e.tool != "exec":
            continue
        cmd, res = e.command or "", e.result_text or ""
        failed = bool(NOT_FOUND.search(res)) and len(res) < 400
        for m in LAUNCH_PY.finditer(cmd):
            out.append((e.idx, m.group(1), "python_script", not failed))
        for m in BROWSER_URL.finditer(cmd):
            out.append((e.idx, m.group(1), "browser_url", not failed))
        for m in XDG_OPEN.finditer(cmd):
            out.append((e.idx, m.group(1), "xdg_open", not failed))
    return out


def find_app_launches(events, apps) -> list:
    """[(idx, app, ok)] — a lexicon app invoked as a command (probes excluded)."""
    out = []
    for e in events:
        if e.kind != "toolCall" or e.tool != "exec":
            continue
        cmd, res = e.command or "", e.result_text or ""
        for app in apps:
            if not re.search(
                r"(?:^|[;&|]\s*|\bnohup\s+|\bsetsid\s+(?:-f\s+)?|DISPLAY=\S+\s+)"
                + re.escape(app) + r"(?:\s|$)", cmd, re.M):
                continue
            if re.search(r"(?:which|command\s+-v|type|apt-get|dpkg|pip)\s[^\n]*"
                         + re.escape(app), cmd):
                continue
            if CLI_ONLY_FLAG.search(cmd):
                continue
            ok = not (NOT_FOUND.search(res) and len(res) < 400)
            out.append((e.idx, app, ok))
    return out


def find_window_observations(events) -> list:
    """[(idx, [(title, wm_class)])] from working xwininfo/wmctrl/xdotool calls."""
    obs = []
    for e in events:
        if e.kind != "toolCall" or not WINDOW_LIST.search(e.command or ""):
            continue
        res = e.result_text or ""
        if NOT_FOUND.search(res) and len(res) < 300:
            continue
        rows = [(t.strip(), (c or "").strip()) for t, c in WINDOW_ROW.findall(res)]
        if rows:
            obs.append((e.idx, rows))
    return obs



def gui_processes_live_at(cap_idx, events, authored_src, launches, app_launches_l, apps):
    """GUI-capable processes plausibly still on screen at cap_idx.

    A full-screen capture shows every mapped window, so the scene source is a
    set, not a single process. Membership is approximate and deliberately
    conservative: a launch counts unless an explicit close/kill or a recorded
    process exit occurs before the capture.
    """
    closes = [e.idx for e in events
              if e.kind == "toolCall" and CLOSE_ACTION.search(e.command or "")]
    exits = [e.idx for e in events
             if e.kind == "toolCall" and PROC_EXITED.search(e.result_text or "")]
    live = set()
    for (i, ent, kind, ok) in launches:
        if i >= cap_idx or not ok:
            continue
        if kind == "python_script" and not is_gui_capable(ent, authored_src):
            continue
        if any(i < c < cap_idx for c in closes) or any(i < x < cap_idx for x in exits):
            continue
        live.add(ent)
    for (i, app, ok) in app_launches_l:
        if i >= cap_idx or not ok:
            continue
        if any(i < c < cap_idx for c in closes):
            continue
        live.add(app)
    return live


def resolve_capture_source(cap_idx, events, authored, launches, app_launches_l, win_obs,
                           target_apps, authored_src=None):
    """Identify the process that most plausibly owned the captured screen.

    Returns (source_process, source_kind, confidence, edges, ambiguity).
    Structural evidence only; temporal-only evidence is marked WEAK.
    """
    edges = []
    cap_ev = next((e for e in events if e.kind == "toolCall" and e.idx == cap_idx), None)
    window_scoped = bool(cap_ev and WINDOW_SCOPED_CAP.search(cap_ev.command or ""))

    # 1. EXACT: a window enumeration observed at/just before the capture
    for idx, rows in win_obs:
        if 0 <= cap_idx - idx <= LOOKBACK:
            titles = "; ".join(t for t, _c in rows[:4])
            classes = [c.lower() for _t, c in rows if c]
            hit = [a for a in target_apps
                   if any(a in c for c in classes)
                   or any(a in t.lower() for t, _ in rows)]
            kind = "target_app" if hit else "unknown"
            multi = len(rows) > 1 and not window_scoped
            conf0 = "STRONG" if multi else "EXACT"
            edges.append(Edge("CAPTURED_FROM", f"event:{cap_idx}", f"windows[{titles[:80]}]",
                              conf0, f"event:{idx};n_windows={len(rows)}"))
            return (titles[:120], kind, conf0, edges,
                    "multiple_windows_no_focus_evidence" if multi else "")

    # 2. STRONG: the nearest preceding successful launch inside the lookback window
    cands = [(i, ent, kind, ok) for (i, ent, kind, ok) in launches
             if 0 < cap_idx - i <= LOOKBACK and ok]
    cands += [(i, app, "app", ok) for (i, app, ok) in app_launches_l
              if 0 < cap_idx - i <= LOOKBACK and ok]
    if cands:
        cands.sort(key=lambda x: -x[0])
        idx, ent, kind, _ok = cands[0]
        others = {c[1] for c in cands if c[1] != ent}
        if kind == "app":
            src_kind = "target_app" if ent in target_apps else "other_app"
        elif kind == "python_script":
            src_kind = "agent_authored" if ent in authored else "unknown_script"
            # A CLI/headless script cannot own the captured screen. Without
            # structural evidence that the authored program creates a window,
            # this launch is not scene evidence at all.
            if src_kind == "agent_authored" and authored_src is not None:
                if not is_gui_capable(ent, authored_src):
                    return ("", "unknown", "UNKNOWN", edges,
                            f"nearest_launch_is_non_gui_script:{ent.split('/')[-1]}")
        elif kind in ("browser_url", "xdg_open"):
            local = ent.replace("file://", "")
            src_kind = "agent_authored" if local in authored else "external_url"
        else:
            src_kind = "unknown"

        # A preceding launch alone is temporal adjacency, not scene evidence:
        # gnome-screenshot captures the whole screen, so the launched process is
        # only STRONG when the trace also brackets it -- the process is shown
        # still running, or is explicitly closed right after the capture -- with
        # no competing GUI launch in between and a tight event gap.
        gap = cap_idx - idx
        competing = any(o_i != idx and idx < o_i < cap_idx
                        for (o_i, _e, _k, o_ok) in cands if o_ok)
        still = any(SESSION_PID.search(e.result_text or "")
                    for e in events
                    if e.kind == "toolCall" and idx <= e.idx <= cap_idx)
        # a poll showing the process already exited invalidates that evidence
        if still and any(PROC_EXITED.search(e.result_text or "")
                         for e in events
                         if e.kind == "toolCall" and idx < e.idx <= cap_idx):
            still = False
        closed = any(CLOSE_ACTION.search(e.command or "")
                     for e in events
                     if e.kind == "toolCall" and cap_idx < e.idx <= cap_idx + 3)
        bracketed = (still or closed) and not competing and gap <= BRACKET_GAP
        conf = "STRONG" if bracketed else "WEAK"

        # Full-screen capture: if more than one GUI process could be mapped, the
        # scene is composite and no single process can own it without focus or
        # window-scoped evidence.
        live = gui_processes_live_at(cap_idx, events, authored_src or {},
                                     launches, app_launches_l, target_apps)
        others_live = {x for x in live if x != ent}
        if others_live and conf == "STRONG" and not window_scoped:
            conf = "WEAK"
            amb_multi = ("multiple_gui_processes_live:"
                         + ",".join(sorted(x.split("/")[-1] for x in others_live)[:3]))
        else:
            amb_multi = ""

        edges.append(Edge("CAPTURED_FROM", f"event:{cap_idx}", ent, conf,
                          f"event:{idx};gap={gap};still={still};closed={closed}"))
        if src_kind == "agent_authored":
            edges.append(Edge("AUTHORED_BY_AGENT", ent, f"event:{authored.get(ent, authored.get(ent.replace('file://',''), -1))}",
                              "EXACT", f"event:{authored.get(ent, authored.get(ent.replace('file://',''), -1))}"))
        amb = f"competing_launches={sorted(others)[:3]}" if others else ""
        amb = ";".join(x for x in (amb, amb_multi) if x)
        return (ent, src_kind, conf, edges, amb)

    # 3. UNKNOWN: nothing structural in range
    return ("", "unknown", "UNKNOWN", edges,
            "no_launch_or_window_evidence_within_lookback")


def classify_scene(producer, source_kind, output_path, prior_images):
    """R4 scene lineage class from structural facts only."""
    if producer in SYNTH_PRODUCERS:
        return "DIRECT_SYNTHESIS"
    if producer in ("IMAGE_TRANSFORM", "FILE_COPY"):
        return "DERIVED_FROM_PRIOR_EVIDENCE"
    if producer in CAPTURE_PRODUCERS:
        if source_kind == "agent_authored":
            return "AGENT_SUBSTITUTE_SCENE"
        if source_kind == "target_app":
            return "TARGET_SCENE"
        return "UNKNOWN"
    return "UNKNOWN"


def _basename(p: str) -> str:
    return p.replace("\\", "/").rstrip("/").split("/")[-1]


def target_status(events, target_apps, app_launches_l):
    """Structural status of the required target application in this trace.

    LAUNCHED        an app from the required set was invoked and did not fail
    PROBED_ABSENT   a which/command -v probe returned nothing or 'not found'
    NEVER_INVOKED   no invocation and no successful probe
    NO_TARGET_KNOWN the task spec named no lexicon application
    """
    if not target_apps:
        return "NO_TARGET_KNOWN", ""
    ok = [(i, a) for (i, a, o) in app_launches_l if o]
    if ok:
        return "LAUNCHED", f"event:{ok[0][0]}:{ok[0][1]}"
    probes = []
    for e in events:
        if e.kind != "toolCall" or e.tool != "exec":
            continue
        for app in target_apps:
            if re.search(r"(?:which|command\s+-v|type)\s+" + re.escape(app), e.command or ""):
                res = e.result_text or ""
                absent = (app not in res) or bool(NOT_FOUND.search(res))
                probes.append((e.idx, app, absent))
    if probes and all(p[2] for p in probes):
        return "PROBED_ABSENT", f"event:{probes[0][0]}:{probes[0][1]}"
    if probes:
        return "PROBED_PRESENT_NOT_LAUNCHED", f"event:{probes[0][0]}:{probes[0][1]}"
    return "NEVER_INVOKED", ""




def _template_match(pattern_name: str, delivered: set) -> str:
    """Match a templated filename such as compare_{n}_200.png against delivered files."""
    rx = re.compile("^" + re.sub(r"\{[^}]*\}|\$\{[^}]*\}", ".*",
                                 re.escape(pattern_name).replace(r"\{", "{").replace(r"\}", "}")
                                 ).replace(r"\.", r"\.") + "$")
    try:
        rx = re.compile("^" + ".*".join(re.escape(part) for part in
                                        re.split(r"\{[^}]*\}|\$\{[^}]*\}", pattern_name)) + "$")
    except re.error:
        return ""
    hits = sorted(d for d in delivered if rx.match(d))
    return hits[0] if hits else ""


def reconstruct_trace(events, spec, delivered_files):
    """Build every structurally-detected visual-evidence production case in a trace.

    spec:            dict from task_spec (image_deliverables, target_apps)
    delivered_files: set of lowercase basenames present in results_manifest.txt

    R-levels are gated: R4/R5 require that the artifact was linked (R2) to a
    required or actually-delivered file. Incidental harness screenshots that were
    never delivered cannot reach R4/R5, because they are not delivered evidence.
    """
    tc = [e for e in events if e.kind == "toolCall"]
    authored = build_authored_index(events)
    authored_src = build_authored_source(events)
    launches = find_launches(events)
    apps = spec.get("target_apps") or []
    app_l = find_app_launches(events, apps)
    win = find_window_observations(events)
    req_images = {b.lower() for b in (spec.get("image_deliverables") or [])}
    tstat, tevid = target_status(events, apps, app_l)

    cases = []
    for e in tc:
        cmd = e.command or ""
        pk = classify_producer(cmd, e.tool)
        if pk == "OTHER":
            continue
        outs = [(p, r) for p, r in extract_outputs(cmd) if p.lower().endswith(IMAGE_EXT)]
        is_capture = pk in CAPTURE_PRODUCERS
        is_synth = pk in SYNTH_PRODUCERS or pk in ("IMAGE_TRANSFORM", "FILE_COPY")

        # keep synthesis/transform events even when the literal path is not recoverable
        templated = []
        if not outs and is_synth:
            templated = [(m.group(1), "templated") for m in TEMPLATED_OUT.finditer(cmd)]
        if not outs and not templated and not is_capture:
            continue
        if pk == "HARNESS_GUI_ACTION" and not e.n_images:
            continue

        if outs:
            targets, kind_of_path = outs, "literal"
        elif templated:
            targets, kind_of_path = templated, "templated"
        else:
            targets, kind_of_path = [("", "harness_implicit" if pk == "HARNESS_GUI_ACTION"
                                      else "unresolved")], (
                "unresolved" if pk != "HARNESS_GUI_ACTION" else "literal")

        for path, rule in targets:
            c = VisualCase(event_idx=e.idx, producer_kind=pk,
                           producer_command=cmd[:300],
                           output_path=path,
                           capture_channel=capture_channel(pk, cmd))
            c.target_apps = "|".join(apps)
            c.target_status = tstat
            c.output_path_kind = kind_of_path
            c.r_level = 1
            c.edges.append(Edge("PRODUCED_BY", path or f"harness_screenshot@{e.idx}",
                                f"event:{e.idx}:{e.tool}", "EXACT", f"event:{e.idx}:{rule}"))

            # ---------------- R2: artifact linkage ----------------
            b = _basename(path).lower()
            if kind_of_path == "templated" and path:
                hit = _template_match(b, delivered_files)
                if hit:
                    c.was_delivered = True
                    c.is_required_deliverable = hit in req_images
                    c.r_level = 2
                    c.edges.append(Edge("DELIVERED_AS", path, hit, "STRONG",
                                        "results_manifest:template"))
                else:
                    c.ambiguity = "templated_output_path_unmatched"
            elif path:
                c.is_required_deliverable = b in req_images
                c.was_delivered = b in delivered_files
                if c.is_required_deliverable or c.was_delivered:
                    c.r_level = 2
                    c.edges.append(Edge(
                        "DELIVERED_AS", path, _basename(path),
                        "EXACT" if c.was_delivered else "STRONG",
                        "results_manifest" if c.was_delivered else "task_spec"))
                else:
                    c.ambiguity = "output_path_not_in_required_or_delivered_set"
            else:
                c.ambiguity = ("harness_screenshot_not_addressable_as_deliverable"
                               if pk == "HARNESS_GUI_ACTION" else "output_path_unresolved")

            # evidence scope
            if c.is_required_deliverable or c.was_delivered:
                c.evidence_scope = "delivered_evidence"
            elif pk == "HARNESS_GUI_ACTION":
                c.evidence_scope = "incidental_harness"
            else:
                c.evidence_scope = "intermediate"

            # ---------------- R3: capture source ----------------
            src_conf = "UNKNOWN"
            if is_capture:
                src, kind, src_conf, edges, amb = resolve_capture_source(
                    e.idx, events, authored, launches, app_l, win, apps, authored_src)
                c.source_process, c.source_kind = src, kind
                c.edges.extend(edges)
                if amb:
                    c.ambiguity = (c.ambiguity + ";" + amb).strip(";")
                if src_conf in ("EXACT", "STRONG"):
                    c.r_level = max(c.r_level, 3) if c.r_level >= 2 else max(c.r_level, 1)
            else:
                c.source_process, c.source_kind, src_conf = "n/a_direct_write", "n/a", "EXACT"
                if c.r_level >= 2:
                    c.r_level = 3

            # ---------------- R4: scene lineage ----------------
            c.source_confidence = src_conf
            proposed = classify_scene(pk, c.source_kind, path, None)
            if is_capture and src_conf not in ("EXACT", "STRONG"):
                # Temporal adjacency alone is not scene evidence: a full-screen
                # capture may show any window. Record the hypothesis, do not
                # promote it to a classification.
                c.weak_scene_hypothesis = proposed
                c.scene_class = "UNKNOWN"
            else:
                c.scene_class = proposed
            linked = c.r_level >= 2                      # artifact linkage achieved
            if c.scene_class != "UNKNOWN" and linked and c.r_level >= 3:
                c.r_level = 4

            # ---------------- R5: target reachability ----------------
            if c.r_level >= 4:
                if c.scene_class == "AGENT_SUBSTITUTE_SCENE":
                    # substitute lineage proven: authored -> launched -> captured -> delivered
                    has_auth = any(x.kind == "AUTHORED_BY_AGENT" and x.confidence == "EXACT"
                                   for x in c.edges)
                    if has_auth and (c.was_delivered or c.is_required_deliverable):
                        c.r_level = 5
                        c.edges.append(Edge("SUBSTITUTE_FOR", c.source_process,
                                            "|".join(apps) or "unspecified_target",
                                            "STRONG", tevid or tstat))
                elif c.scene_class == "DIRECT_SYNTHESIS":
                    # no capture at all: pixels cannot descend from any application scene
                    if c.was_delivered or c.is_required_deliverable:
                        c.r_level = 5
                        c.edges.append(Edge("NO_CAPTURE_PATH", path,
                                            "|".join(apps) or "unspecified_target",
                                            "EXACT", f"event:{e.idx}"))
                elif c.scene_class == "TARGET_SCENE":
                    if c.was_delivered or c.is_required_deliverable:
                        c.r_level = 5
                        c.edges.append(Edge("REPRESENTS", c.source_process,
                                            "|".join(apps) or "unspecified_target",
                                            src_conf, tevid or tstat))
                elif c.scene_class == "DERIVED_FROM_PRIOR_EVIDENCE":
                    c.ambiguity = (c.ambiguity + ";lineage_depends_on_source_image").strip(";")

            if c.scene_class == "AGENT_SUBSTITUTE_SCENE" and tstat == "LAUNCHED":
                c.ambiguity = (c.ambiguity + ";target_app_also_launched_in_trace").strip(";")
            cases.append(c)

    return cases, {"authored": authored, "launches": launches, "app_launches": app_l,
                   "windows": win, "target_status": tstat, "target_evidence": tevid}
