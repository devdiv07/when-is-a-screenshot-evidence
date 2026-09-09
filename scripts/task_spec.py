"""Deterministic extraction of required deliverables and required target apps
from WeaveBench task specification .md files.

These come from the benchmark task definition, NOT from judge output, so they can
be used as an independent statement of what the task's actual target was.
"""
from __future__ import annotations

import os
import re

# Applications that can plausibly own an on-screen scene in this benchmark.
# Built from task ids / Warmup install lines actually observed in the corpus.
APP_LEXICON = [
    "spyder", "inkscape", "gimp", "krita", "darktable", "blender", "okular", "evince",
    "libreoffice", "loffice", "soffice", "localc", "lowriter", "loimpress", "xmind",
    "drawio", "dia", "scribus", "thunderbird", "firefox", "google-chrome", "chromium",
    "vlc", "audacity", "kdenlive", "obs", "shotcut", "handbrake", "jupyter", "jupyterlab",
    "spyder3", "code", "gedit", "kate", "nautilus", "gnome-terminal", "meld", "kompare",
    "grafana", "prometheus", "superset", "streamlit", "tensorboard", "jaeger", "kibana",
    "mysql-workbench", "pgadmin", "dbeaver", "wireshark", "virt-manager", "gparted",
    "baobab", "gnome-system-monitor", "gnome-disks", "seahorse", "dconf-editor",
    "quadrapassel", "gnome-mines", "gnome-sudoku", "aisleriot", "supertux", "0ad",
    "joplin", "obsidian", "zotero", "calibre", "sigil", "gnucash", "planner",
    "qgis", "freecad", "openscad", "kicad", "audacity", "rhythmbox", "totem",
    "eog", "shotwell", "digikam", "rawtherapee", "colmap", "meshlab", "cloudcompare",
    "spotify", "slack", "telegram", "postman", "insomnia", "filezilla", "remmina",
]

DELIV_HEADING = re.compile(r"^#{2,4}\s*Deliverables?\b.*$", re.M | re.I)
PROMPT_SEC = re.compile(r"^##\s*Prompt\s*$", re.M | re.I)
GRADING_SEC = re.compile(r"^##\s*Grading Criteria\s*$", re.M | re.I)
FILENAME = re.compile(r"(?<![\w/.-])([A-Za-z0-9][A-Za-z0-9_.-]*\.[A-Za-z0-9]{1,6})(?![\w/])")
NEXT_HEADING = re.compile(r"^#{2,4}\s+", re.M)
BACKTICK_FILE = re.compile(r"`([A-Za-z0-9_./-]+\.[A-Za-z0-9]{1,6})`")
WARMUP_BLOCK = re.compile(r"##\s*Warmup\s*\n+```(?:bash|sh)?\n(.*?)```", re.S | re.I)
APT_INSTALL = re.compile(r"apt-get\s+install[^\n]*?((?:\s+-{1,2}[\w-]+)*)\s+([a-z0-9][\w.+-]*(?:\s+[a-z0-9][\w.+-]*)*)")
WHICH_CMD = re.compile(r"\bwhich\s+([a-z0-9][\w.+-]*)")
COMMAND_V = re.compile(r"\bcommand\s+-v\s+([a-z0-9][\w.+-]*)")


def _section(text: str, heading_re: re.Pattern, level: int = 2) -> str:
    """Text under a heading, up to the next heading of the same or higher level.

    Deliverable contracts often live under ### sub-headings inside ## Prompt, so
    the Prompt section must not stop at the first ###.
    """
    m = heading_re.search(text)
    if not m:
        return ""
    start = m.end()
    boundary = re.compile(r"^#{1," + str(level) + r"}\s+", re.M)
    n = boundary.search(text, start)
    return text[start: n.start() if n else len(text)]


def required_deliverables(spec_text: str) -> list[str]:
    """Filenames named in the agent-visible deliverable contract.

    The contract is stated in the Prompt section (sometimes under a Deliverables
    heading, sometimes as a bolded list inside the prompt), and restated in
    Grading Criteria. Both are part of the benchmark task definition, not judge
    output. Filenames are taken whether backticked, quoted, or bare.
    """
    secs = [_section(spec_text, DELIV_HEADING, level=3),
            _section(spec_text, PROMPT_SEC, level=2),
            _section(spec_text, GRADING_SEC, level=2)]
    out, seen = [], set()
    for sec in secs:
        for f in FILENAME.findall(sec):
            b = f.split("/")[-1]
            if b.lower() in ("e.g", "i.e", "etc") or b in seen:
                continue
            seen.add(b)
            out.append(b)
    return out


def required_image_deliverables(spec_text: str) -> list[str]:
    return [d for d in required_deliverables(spec_text)
            if d.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"))]


def target_apps(spec_text: str, task_id: str) -> list[str]:
    """Applications the task requires/recommends operating on.

    Sources (all structural, none judge-derived):
      1. tokens of the task id that appear in the app lexicon
      2. packages the Warmup block installs / probes
      3. lexicon apps named in the Prompt + Expected Behavior text
    """
    found: list[str] = []

    def add(x: str) -> None:
        x = x.strip().lower()
        if x and x in APP_LEXICON and x not in found:
            found.append(x)

    for tok in re.split(r"[_\-.]", task_id.lower()):
        add(tok)
    wm = WARMUP_BLOCK.search(spec_text)
    if wm:
        blk = wm.group(1)
        for m in APT_INSTALL.finditer(blk):
            for pkg in m.group(2).split():
                add(pkg)
        for rx in (WHICH_CMD, COMMAND_V):
            for m in rx.finditer(blk):
                add(m.group(1))
    body = spec_text.lower()
    for app in APP_LEXICON:
        if re.search(r"(?<![\w-])" + re.escape(app) + r"(?![\w-])", body):
            add(app)
    return found


def load_specs(tasks_dir: str) -> dict[str, dict]:
    specs = {}
    for root, _dirs, files in os.walk(tasks_dir):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(root, fn)
            txt = open(p, encoding="utf-8", errors="replace").read()
            tid = fn[:-3]
            imgs = required_image_deliverables(txt)
            specs[tid] = {
                "task_id": tid,
                "path": p,
                "deliverables": required_deliverables(txt),
                "image_deliverables": imgs,
                "target_apps": target_apps(txt, tid),
                "obligation": capture_required_images(txt, imgs),
                "text": txt,
            }
    return specs


# Keywords that make a named deliverable a *capture* obligation (a picture of an
# application scene) rather than a synthesis obligation (a computed image such as
# a diff map, chart or plot). English + the Chinese used in these specs.
CAPTURE_WORDS = [
    "screenshot", "screen shot", "screen capture", "capture of", "capture the",
    "截图", "屏幕截图", "截屏", "抓图",
    "window", "窗口", "gui", "ide", "must genuinely show", "genuinely show",
    "visible in the", "shows the ", "showing the ",
]
SYNTH_WORDS = [
    "diff map", "difference map", "heatmap", "chart", "plot", "graph of",
    "histogram", "diff image", "差异图", "图表", "曲线", "直方图", "render of",
]


def capture_required_images(spec_text: str, image_deliverables: list) -> dict:
    """For each required image, whether the task text demands a screen capture.

    Returns {filename: "capture" | "synthesis" | "capture_or_synthesis" | "unspecified"}.

    Scope is the defining bullet/line for that filename (plus indented
    continuation lines), not a fixed character window, so that neighbouring
    deliverable descriptions do not bleed in. Decided only from the task
    specification text, never from judge output.
    """
    lines = spec_text.split(chr(10))
    out = {}
    for name in image_deliverables:
        n = name.lower()
        blob_parts = []
        for i, ln in enumerate(lines):
            if n not in ln.lower():
                continue
            chunk = [ln]
            for j in range(i + 1, min(i + 4, len(lines))):
                nxt = lines[j]
                if not nxt.strip():
                    break
                if nxt[:1] in (" ", "	") or not nxt.lstrip()[:1] in ("-", "*", "#", "|"):
                    chunk.append(nxt)
                else:
                    break
            blob_parts.append(" ".join(chunk))
        blob = " ".join(blob_parts).lower()
        has_cap = any(w in blob for w in CAPTURE_WORDS)
        has_syn = any(w in blob for w in SYNTH_WORDS)
        if has_cap and not has_syn:
            out[name] = "capture"
        elif has_syn and not has_cap:
            out[name] = "synthesis"
        elif has_cap and has_syn:
            out[name] = "capture_or_synthesis"
        else:
            out[name] = "unspecified"
    return out
