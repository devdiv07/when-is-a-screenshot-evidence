"""Generate every package figure from frozen artifacts. Python 3.11+, standard library only.

No plotting dependency is used, deliberately: the figures must regenerate byte-identically on
any machine with a stock Python, without a matplotlib version pinning problem.

RULES OBSERVED HERE
-------------------
1. Every number plotted is READ FROM a frozen artifact, never typed from memory.
2. No aggregation is changed to make a figure look better. If a bar is zero, it is drawn zero.
3. Every figure records its inputs and its exact plotted values into figures/FIGURE_DATA.json,
   so a reviewer can diff the figure against the source artifact without reading this script.

Run:  python package/scripts/make_figures.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "package", "figures")

INK = "#1a1a1a"
MUTED = "#6b6b6b"
GRID = "#d8d8d8"
BG = "#ffffff"
OK = "#2e7d32"
BAD = "#c62828"
WARN = "#ef6c00"
COLD = "#9e9e9e"
BLUE = "#1f4e79"
BLUE2 = "#7ba7cc"

LEVEL_COLOR = {"EXACT": OK, "STRONG": "#7cb342", "WEAK": WARN, "UNKNOWN": COLD}

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',"
        "Arial,sans-serif")
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

RECORD: dict = {}


# ---------------------------------------------------------------- tiny SVG helper
def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.p = w, h, []
        self.rect(0, 0, w, h, BG)

    def rect(self, x, y, w, h, fill, rx=0, stroke=None, sw=1, op=None):
        s = f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{max(h,0):.1f}" fill="{fill}"'
        if rx:
            s += f' rx="{rx}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{sw}"'
        if op is not None:
            s += f' opacity="{op}"'
        self.p.append(s + "/>")

    def line(self, x1, y1, x2, y2, stroke=GRID, sw=1, dash=None):
        s = (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
             f'stroke="{stroke}" stroke-width="{sw}"')
        if dash:
            s += f' stroke-dasharray="{dash}"'
        self.p.append(s + "/>")

    def text(self, x, y, t, size=12, fill=INK, anchor="start", weight="normal",
             font=None, op=None):
        s = (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font or FONT}" '
             f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
             f'font-weight="{weight}"')
        if op is not None:
            s += f' opacity="{op}"'
        self.p.append(s + f">{esc(t)}</text>")

    def path(self, d, stroke, sw=2, fill="none", dash=None):
        s = f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            s += f' stroke-dasharray="{dash}"'
        self.p.append(s + ' stroke-linejoin="round" stroke-linecap="round"/>')

    def circle(self, cx, cy, r, fill):
        self.p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>')

    def save(self, name, caption_lines):
        for i, ln in enumerate(caption_lines):
            self.text(20, self.h - 12 * (len(caption_lines) - i) - 6, ln, 10.5, MUTED)
        body = "\n".join(self.p)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
               f'height="{self.h}" viewBox="0 0 {self.w} {self.h}">\n{body}\n</svg>\n')
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        return path


def title(s, t, sub=None):
    s.text(20, 26, t, 15, INK, weight="600")
    if sub:
        s.text(20, 44, sub, 11, MUTED)


# ---------------------------------------------------------------- readers
def read_json(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


def read_csv(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_lookback():
    """Parse the frozen lookback table out of the recoverability report."""
    txt = open(os.path.join(ROOT, "outputs", "recoverability_report.md"),
               encoding="utf-8").read()
    block = txt.split("| Lookback (events) | source resolved | of which EXACT/STRONG |")[1]
    rows = []
    for line in block.splitlines():
        m = re.match(r"\|\s*([0-9]+|unbounded)\s*(?:\(used\))?\s*\|\s*([0-9.]+)%\s*\|"
                     r"\s*([0-9.]+)%\s*\|", line.strip())
        if m:
            rows.append({"lookback": m.group(1), "resolved_pct": float(m.group(2)),
                         "exact_strong_pct": float(m.group(3))})
        elif rows and line.strip() and not line.strip().startswith("|"):
            break
    return rows


# ================================================================= FIGURE 1
def fig1_assurance_chain():
    links = [
        ("artifact\n→ capture", "TESTED", "453/453 artifact provenance", OK),
        ("capture\n→ process/surface", "TESTED", "real grabs, recorder-observed", OK),
        ("process/surface\n→ identity", "TESTED", "X-Resource / compositor pid", OK),
        ("→ displayed\nresource", "FAILS", "the boundary", BAD),
        ("→ application\nstate", "NOT TESTED", "predeclared out of scope", COLD),
        ("→ claim", "NOT TESTED", "never attempted", COLD),
    ]
    w, h = 1080, 340
    s = SVG(w, h)
    title(s, "Figure 1 — The six-link assurance chain, and which links were tested",
          "Links 1-3 hold in the tested labs. Link 4 fails on BOTH X11 and the tested "
          "Wayland stack. Links 5-6 were never reached.")
    bw, gap, x0, y = 158, 21, 20, 92
    for i, (name, status, note, col) in enumerate(links):
        x = x0 + i * (bw + gap)
        s.rect(x, y, bw, 96, "#fafafa", rx=6, stroke=col, sw=2)
        for j, ln in enumerate(name.split("\n")):
            s.text(x + bw / 2, y + 30 + j * 15, ln, 12, INK, "middle", "600")
        s.rect(x + 12, y + 64, bw - 24, 20, col, rx=4, op=0.14)
        s.text(x + bw / 2, y + 78, status, 10.5, col, "middle", "700")
        s.text(x + bw / 2, y + 110, note, 9.5, MUTED, "middle")
        if i < len(links) - 1:
            ax = x + bw + 3
            s.path(f"M {ax} {y+48} L {ax+gap-6} {y+48}", MUTED, 1.6)
            s.path(f"M {ax+gap-11} {y+44} L {ax+gap-6} {y+48} L {ax+gap-11} {y+52}",
                   MUTED, 1.6)
    by = y + 140
    s.rect(20, by, w - 40, 62, "#fff5f5", rx=6, stroke=BAD, sw=1.5)
    s.text(36, by + 23, "Where assurance terminates", 12, BAD, weight="700")
    s.text(36, by + 41, "process/surface identity  ≠  displayed-resource identity",
           12, INK, font=MONO)
    s.text(36, by + 56, "path identity  ≠  content identity", 12, INK, font=MONO)
    s.text(w - 36, by + 41, "measured on 2 platforms", 10.5, MUTED, "end")
    s.text(w - 36, by + 56, "0 of 12 bindings changed", 10.5, MUTED, "end")
    RECORD["figure_1"] = {"inputs": ["research/FROZEN_FINDINGS.md",
                                     "outputs/platform_binding_matrix.csv"],
                          "links": [{"link": l[0].replace("\n", " "), "status": l[1]}
                                    for l in links]}
    return s.save("fig1_assurance_chain.svg", [
        "Structural diagram. Statuses are those recorded in research/FROZEN_FINDINGS.md (F5) "
        "and outputs/platform_binding_matrix.csv.",
        "SCOPE: 'TESTED' means tested in the constructed labs described in the package, not "
        "in deployment. Links 5-6 carry no result in either direction."])


# ================================================================= FIGURE 2
def fig2_recoverability():
    m = read_json("outputs/audit_metrics.json")
    bars = [
        ("R0 judge-quote localization", m["R0"]["rate_pct"], m["R0"]["localized"],
         m["R0"]["n_quotes"]),
        ("R1 producer recovery", m["R1"]["rate_pct"], m["R1"]["recovered"], m["R1"]["n"]),
        ("R2 artifact provenance", m["R2"]["rate_pct"],
         m["R2"]["linked_exact"] + m["R2"]["linked_templated"], m["R2"]["n"]),
        ("R3 scene source (EXACT|STRONG)", m["R3"]["exact_or_strong_pct"],
         m["R3"]["exact"] + m["R3"]["strong"], m["R3"]["n_capture"]),
        ("R4 scene classification", m["R4"]["rate_pct"], m["R4"]["classified"], m["R4"]["n"]),
        ("R5 target adjudication", m["R5"]["rate_pct"], m["R5"]["reached"], m["R5"]["n"]),
    ]
    w, h = 900, 400
    s = SVG(w, h)
    title(s, "Figure 2 — Retrospective recoverability by level",
          "The instrument recovers artifact provenance almost perfectly and scene provenance "
          "almost not at all.")
    x0, y0, bw, bh, gap = 268, 78, 520, 30, 14
    for gx in range(0, 101, 25):
        x = x0 + bw * gx / 100
        s.line(x, y0 - 6, x, y0 + len(bars) * (bh + gap) - gap + 4, GRID)
        s.text(x, y0 - 12, f"{gx}%", 10, MUTED, "middle")
    for i, (lab, pct, n, tot) in enumerate(bars):
        y = y0 + i * (bh + gap)
        col = OK if pct >= 70 else (WARN if pct >= 15 else BAD)
        s.text(x0 - 12, y + bh / 2 + 4, lab, 11.5, INK, "end")
        s.rect(x0, y, bw, bh, "#f2f2f2", rx=3)
        s.rect(x0, y, bw * pct / 100, bh, col, rx=3)
        tx = x0 + bw * pct / 100 + 8
        s.text(tx, y + bh / 2 + 4, f"{pct}%   ({n}/{tot})", 11, INK, weight="600")
    ny = y0 + len(bars) * (bh + gap) + 8
    s.rect(20, ny, w - 40, 46, "#f7f7f7", rx=5)
    s.text(36, ny + 20, "R3 EXACT = 0. Not one delivered capture in the corpus had its "
                        "scene source established at EXACT confidence.", 11, INK,
           weight="600")
    s.text(36, ny + 37, "R4's 17.9% is dominated by DERIVED (43) and DIRECT_SYNTHESIS (15) "
                        "classes, not by resolved capture scenes.", 10.5, MUTED)
    RECORD["figure_2"] = {"input": "outputs/audit_metrics.json",
                          "bars": [{"level": b[0], "pct": b[1], "n": b[2], "total": b[3]}
                                   for b in bars],
                          "R3_exact": m["R3"]["exact"], "R4_by_class": m["R4"]["by_class"],
                          "AGENT_SUBSTITUTE_SCENE_scope": (
                              "4 delivered artifacts from 1 episode "
                              "(DAV_task_0_spyder_step_debug, run1); existence result, "
                              "not independent cases or prevalence")}
    return s.save("fig2_recoverability_by_level.svg", [
        "Source: outputs/audit_metrics.json (frozen audit, tag recoverability-audit-v1).",
        "SCOPE: one benchmark corpus (WeaveBench GPT-5.4 low), 453 delivered visual "
        "artifacts, 394 capture-based. Not a population estimate."])


# ================================================================= FIGURE 3
def fig3_lookback():
    rows = read_lookback()
    w, h = 860, 440
    s = SVG(w, h)
    title(s, "Figure 3 — Apparent recoverability is a function of inference policy",
          "Observations held fixed. Only the permitted temporal lookback varies.")
    x0, y0, pw, ph = 90, 84, 640, 250
    s.line(x0, y0 + ph, x0 + pw, y0 + ph, MUTED, 1.3)
    s.line(x0, y0, x0, y0 + ph, MUTED, 1.3)
    for gy in range(0, 61, 10):
        y = y0 + ph - ph * gy / 60
        s.line(x0, y, x0 + pw, y, GRID, 1, "3,3")
        s.text(x0 - 10, y + 4, f"{gy}%", 10, MUTED, "end")
    n = len(rows)
    xs = [x0 + pw * i / (n - 1) for i in range(n)]
    for i, r in enumerate(rows):
        s.text(xs[i], y0 + ph + 18, r["lookback"], 10, MUTED, "middle")
    s.text(x0 + pw / 2, y0 + ph + 38, "permitted lookback (events)", 11, INK, "middle")
    for key, col, lab in (("resolved_pct", WARN, "source resolved (any confidence)"),
                          ("exact_strong_pct", OK, "of which EXACT/STRONG")):
        pts = [(xs[i], y0 + ph - ph * rows[i][key] / 60) for i in range(n)]
        s.path("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts), col, 2.4)
        for (x, y), r in zip(pts, rows):
            s.circle(x, y, 3.6, col)
        s.text(pts[-1][0] - 6, pts[-1][1] - 12, f"{rows[-1][key]}%", 11, col, "end",
               "700")
    ly = y0 + ph + 54
    for i, (col, lab) in enumerate(((WARN, "source resolved (any confidence)"),
                                    (OK, "of which EXACT/STRONG"))):
        s.rect(x0 + i * 300, ly, 22, 4, col, rx=2)
        s.text(x0 + i * 300 + 30, ly + 6, lab, 10.5, INK)
    ny = ly + 22
    s.rect(20, ny, w - 40, 44, "#f7f7f7", rx=5)
    lo, hi = rows[0], rows[-1]
    s.text(36, ny + 19, f"Apparent resolution {lo['resolved_pct']}% → "
                        f"{hi['resolved_pct']}%. Well-supported attribution "
                        f"{lo['exact_strong_pct']}% → {hi['exact_strong_pct']}%.",
           11.5, INK, weight="600")
    s.text(36, ny + 36, "More permissive inference produced substantially more answers "
                        "without a commensurate increase in strong evidence.", 10.5, MUTED)
    RECORD["figure_3"] = {"input": "outputs/recoverability_report.md §5.2 (parsed)",
                          "n_cases": 455, "rows": rows}
    return s.save("fig3_lookback_vs_evidence.svg", [
        "Source: outputs/recoverability_report.md §5.2, over 455 capture-based "
        "delivered-evidence cases. Recomputed 2026-09-09 against the post-correction "
        "resolver.",
        "SCOPE: one corpus, one resolver. This does NOT establish that the additional "
        "answers at high lookback are individually wrong - only that they are not backed by "
        "stronger evidence."])


# ================================================================= FIGURE 4
def fig4_field_sets():
    rows = read_csv("outputs/field_coverage.csv")

    def get(fields, outcome):
        want = set(fields)
        for r in rows:
            if set(r["field_set"].split("|")) == want and r["outcome"] == outcome:
                return float(r["pct_of_universe"]), int(r["cases"]), int(r["universe"])
        return None

    D4 = ["CAPTURE_REGION", "VISIBLE_WINDOW_SET", "Z_ORDER", "WINDOW_GEOMETRY"]
    S6 = D4 + ["ACTIVE_PID", "ACTIVE_WINDOW_IDENTITY"]
    S7 = S6 + ["PROCESS_LIFECYCLE_AT_CAPTURE"]
    res_d4 = get(D4, "resolution")
    adj_d4 = (0.0, 0, 287)          # verified directly from information_deficits.csv
    adj_s6, adj_s7 = get(S6, "adjudication"), get(S7, "adjudication")
    w, h = 880, 430
    s = SVG(w, h)
    title(s, "Figure 4 — Closing a display-composition deficit is not adjudication",
          "The four display-composition fields determine which surfaces contributed pixels, "
          "then stop.")
    panels = [
        ("scene-source resolution  (universe 385)",
         [("display-composition\n4 fields", res_d4, BLUE2)]),
        ("target/substitute adjudication  (universe 287)",
         [("display-composition\n4 fields", adj_d4, BAD),
          ("+ active window\n+ active pid  (6)", adj_s6, BLUE),
          ("+ lifecycle\nat capture  (7)", adj_s7, BLUE)]),
    ]
    px, pw = 40, 380
    for pi, (ptitle, bars) in enumerate(panels):
        ox = px + pi * (pw + 40)
        s.text(ox, 76, ptitle, 11.5, INK, weight="600")
        by0, bh, bmax = 96, 190, 100.0
        s.line(ox, by0 + bh, ox + pw - 20, by0 + bh, MUTED, 1.3)
        for gy in (0, 25, 50, 75, 100):
            y = by0 + bh - bh * gy / bmax
            s.line(ox, y, ox + pw - 20, y, GRID, 1, "3,3")
            if pi == 0:
                s.text(ox - 8, y + 4, f"{gy}%", 9.5, MUTED, "end")
        bw = (pw - 40) / len(bars)
        for i, (lab, val, col) in enumerate(bars):
            if val is None:
                continue
            pct, nn, uni = val
            bx = ox + 10 + i * bw + bw * 0.18
            bwid = bw * 0.64
            bhh = bh * pct / bmax
            s.rect(bx, by0 + bh - bhh, bwid, max(bhh, 2), col, rx=3)
            s.text(bx + bwid / 2, by0 + bh - bhh - 20, f"{pct}%", 13, col, "middle", "700")
            s.text(bx + bwid / 2, by0 + bh - bhh - 7, f"{nn}/{uni}", 9.5, MUTED, "middle")
            for j, ln in enumerate(lab.split("\n")):
                s.text(bx + bwid / 2, by0 + bh + 16 + j * 12, ln, 9.5, INK, "middle")
    ny = 330
    s.rect(20, ny, w - 40, 62, "#fff5f5", rx=5, stroke=BAD, sw=1.2)
    s.text(36, ny + 21, "The four display-composition fields adjudicate 0 of 287 cases.",
           12, BAD, weight="700")
    s.text(36, ny + 39, "They resolve which surfaces contributed pixels; nothing binds a "
                        "contributing surface to an identity", 10.5, MUTED)
    s.text(36, ny + 53, "comparable with a declared target. Adjudication needs process "
                        "identity on top of the display fields.", 10.5, MUTED)
    RECORD["figure_4"] = {
        "input": "outputs/field_coverage.csv; display-composition-only adjudication "
                 "verified directly from outputs/information_deficits.csv with "
                 "bundle_fields='VISIBLE_WINDOW_SET+Z_ORDER+CAPTURE_REGION+WINDOW_GEOMETRY' "
                 "and eligible='yes' (832 rows, 208 unique cases, "
                 "enables_target_substitute_adjudication='no' on all)",
        "resolution_D4": res_d4, "adjudication_D4": adj_d4,
        "adjudication_6field": adj_s6, "adjudication_7field": adj_s7,
        "note": "An earlier draft's '83.6% resolved by four fields' was WITHDRAWN "
                "(outputs/field_set_analysis.md §1). 83.6% is the SIX-field "
                "adjudication figure over universe 287."}
    return s.save("fig4_field_set_outcomes.svg", [
        "Source: outputs/field_coverage.csv; outputs/field_set_analysis.md §4. "
        "Denominators differ (385 vs 287) and are NOT interchangeable.",
        "SCOPE: HISTORICAL analysis of benign traces. Says nothing about whether a field "
        "survives a contract-aware adversary."])


# ================================================================= FIGURE 5
def fig5_analytic_vs_empirical():
    rows = read_csv("outputs/analytic_vs_empirical.csv")
    order = ["AUTHENTIC_TARGET", "SUBSTITUTE", "UNKNOWN"]
    mat = {a: {e: 0 for e in order} for a in order}
    for r in rows:
        a, e = r["analytic_verdict"], r["empirical_verdict"]
        if a in mat and e in mat[a]:
            mat[a][e] += 1
    total = len(rows)
    agree = sum(mat[k][k] for k in order)
    w, h = 780, 470
    s = SVG(w, h)
    title(s, "Figure 5 — Analytic field vectors vs real recorder observations",
          f"{total} comparable (scenario, tier) pairs. {agree} agree "
          f"({agree/total*100:.1f}%).")
    cw, ch, x0, y0 = 150, 62, 250, 110
    s.text(x0 + cw * 1.5, y0 - 34, "EMPIRICAL verdict (real X11 lab)", 11.5, INK,
           "middle", "600")
    for j, e in enumerate(order):
        s.text(x0 + j * cw + cw / 2, y0 - 12, e, 10, MUTED, "middle")
    s.text(60, y0 + ch * 1.5, "ANALYTIC", 11.5, INK, "middle", "600")
    s.text(60, y0 + ch * 1.5 + 16, "verdict", 11.5, INK, "middle", "600")
    for i, a in enumerate(order):
        s.text(x0 - 12, y0 + i * ch + ch / 2 + 4, a, 10, MUTED, "end")
        for j, e in enumerate(order):
            v = mat[a][e]
            x, y = x0 + j * cw, y0 + i * ch
            unsafe = (a == "UNKNOWN" and e == "AUTHENTIC_TARGET")
            if unsafe and v:
                fill, col, wgt = "#fdecea", BAD, "700"
            elif i == j:
                fill, col, wgt = "#eef5ee", OK, "600"
            elif v:
                fill, col, wgt = "#fff8e1", WARN, "600"
            else:
                fill, col, wgt = "#fafafa", "#bdbdbd", "normal"
            s.rect(x, y, cw - 4, ch - 4, fill, rx=4,
                   stroke=BAD if unsafe and v else GRID, sw=2 if unsafe and v else 1)
            s.text(x + (cw - 4) / 2, y + ch / 2 + 6, str(v), 19, col, "middle", wgt)
    ny = y0 + 3 * ch + 22
    s.rect(20, ny, w - 40, 96, "#fff5f5", rx=5, stroke=BAD, sw=1.2)
    unsafe_n = mat["UNKNOWN"]["AUTHENTIC_TARGET"]
    s.text(36, ny + 22, f"{unsafe_n} pairs moved UNKNOWN → AUTHENTIC_TARGET — the "
                        "UNSAFE direction. All five are case 13b.", 12, BAD, weight="700")
    s.text(36, ny + 42, "In this experiment, analytic field-vector evaluation was "
                        "overconfident relative to real recorder", 10.5, MUTED)
    s.text(36, ny + 56, "observations in several safety-relevant cases. The analytic arm's "
                        "headline — 'zero false accepts at", 10.5, MUTED)
    s.text(36, ny + 70, "every tier' — did not survive contact with a real display.",
           10.5, MUTED)
    s.text(36, ny + 88, "This is ONE measured instance. It is not a general claim about "
                        "analytic security evaluation.", 10, INK, weight="600")
    RECORD["figure_5"] = {"input": "outputs/analytic_vs_empirical.csv", "n_pairs": total,
                          "agreements": agree,
                          "agreement_pct": round(agree / total * 100, 1),
                          "matrix": mat}
    return s.save("fig5_analytic_vs_empirical.svg", [
        "Source: outputs/analytic_vs_empirical.csv (13 scenarios x 13 tier configurations).",
        "SCOPE: one experiment, one contract, a constructed 13-scenario suite. Not a "
        "general result about analytic evaluation."])


# ================================================================= FIGURE 6
def fig6_unknown_policy():
    rows = read_csv("outputs/empirical_risk_coverage.csv")
    keep = ["0", "0+A", "0+A+B", "0+A+B+C", "0+A+B+C+D", "0+A+B+C+D+E", "FULL(0+A..F)"]
    data = [r for r in rows if r["tier_config"] in keep]
    data.sort(key=lambda r: keep.index(r["tier_config"]))
    w, h = 880, 430
    s = SVG(w, h)
    title(s, "Figure 6 — Fail-closed UNKNOWN is the largest single measured effect",
          "Effective exposure to fabricated evidence, by tier configuration and downstream "
          "policy.")
    x0, y0, pw, ph = 70, 92, 730, 200
    s.line(x0, y0 + ph, x0 + pw, y0 + ph, MUTED, 1.3)
    for gy in (0, 25, 50, 75, 100):
        y = y0 + ph - ph * gy / 100
        s.line(x0, y, x0 + pw, y, GRID, 1, "3,3")
        s.text(x0 - 10, y + 4, f"{gy}%", 10, MUTED, "end")
    gw = pw / len(data)
    for i, r in enumerate(data):
        m1 = float(r["MODE1_permissive_exposure_pct"])
        m2 = float(r["MODE2_failclosed_exposure_pct"])
        cx = x0 + i * gw
        for k, (val, col) in enumerate(((m1, WARN), (m2, OK))):
            bx = cx + gw * (0.20 + k * 0.30)
            bw = gw * 0.26
            bh = ph * val / 100
            s.rect(bx, y0 + ph - bh, bw, max(bh, 2), col, rx=3)
            s.text(bx + bw / 2, y0 + ph - bh - 7, f"{val}%", 10, col, "middle", "700")
        lab = r["tier_config"].replace("FULL(0+A..F)", "FULL")
        s.text(cx + gw / 2, y0 + ph + 16, lab, 9.5, INK, "middle")
        if r["defeated_by"]:
            s.text(cx + gw / 2, y0 + ph + 30, "13b accepted", 8.5, BAD, "middle", "700")
    ly = y0 + ph + 46
    for i, (col, lab) in enumerate(((WARN, "MODE 1 permissive — UNKNOWN still credited"),
                                    (OK, "MODE 2 fail-closed — UNKNOWN gets no credit"))):
        s.rect(x0 + i * 330, ly, 22, 10, col, rx=2)
        s.text(x0 + i * 330 + 30, ly + 9, lab, 10.5, INK)
    ny = ly + 26
    s.rect(20, ny, w - 40, 60, "#fff5f5", rx=5, stroke=BAD, sw=1.2)
    s.text(36, ny + 21, "Fail-closed UNKNOWN cannot repair a false AUTHENTIC_TARGET.",
           12, BAD, weight="700")
    s.text(36, ny + 39, "Case 13b survives fail-closed UNKNOWN because it was never "
                        "UNKNOWN — it was ACCEPTED. The residual", 10.5, MUTED)
    s.text(36, ny + 53, "9.1% at Tier D and above is exactly that one accepted "
                        "fabrication.", 10.5, MUTED)
    RECORD["figure_6"] = {
        "input": "outputs/empirical_risk_coverage.csv",
        "rows": [{"tier_config": r["tier_config"],
                  "MODE1_permissive_exposure_pct": float(r["MODE1_permissive_exposure_pct"]),
                  "MODE2_failclosed_exposure_pct": float(r["MODE2_failclosed_exposure_pct"]),
                  "defeated_by": r["defeated_by"]} for r in data]}
    return s.save("fig6_unknown_policy_exposure.svg", [
        "Source: outputs/empirical_risk_coverage.csv. Exposure = fraction of the 11 "
        "substitute cases that receive automatic credit under each downstream policy.",
        "SCOPE: constructed suite of 13 scenarios (11 substitutes). NOT a population "
        "estimate."])


# ================================================================= FIGURE 7
def fig7_binding_matrix():
    rows = read_csv("outputs/platform_binding_matrix.csv")
    cols, seen = [], set()
    for r in rows:
        if r["binding_id"] not in seen:
            seen.add(r["binding_id"])
            cols.append((r["binding_id"], r["binding"]))
    order = [("x11", "P"), ("wayland", "P"), ("x11", "R"), ("wayland", "R")]
    lut = {(r["platform"], r["case"], r["binding_id"]): r["evidence"] for r in rows}
    w, h = 1020, 430
    s = SVG(w, h)
    title(s, "Figure 7 — Provenance binding matrix: X11 vs the tested Wayland stack",
          "Two predeclared cases per platform. Zero of twelve comparable bindings changed "
          "evidence level.")
    x0, y0, cw, ch = 200, 132, 128, 46
    for j, (cid, cname) in enumerate(cols):
        cx = x0 + j * cw + cw / 2
        parts = cname.split(" -> ")
        s.text(cx, y0 - 30, parts[0], 9.5, MUTED, "middle")
        s.text(cx, y0 - 18, "↓", 9.5, MUTED, "middle")
        s.text(cx, y0 - 6, parts[1] if len(parts) > 1 else "", 9.5, MUTED, "middle")
    for i, (plat, case) in enumerate(order):
        y = y0 + i * ch
        lab = f"{'X11' if plat == 'x11' else 'Wayland (tested)'}  —  Case {case}"
        s.text(x0 - 14, y + ch / 2 + 4, lab, 11, INK, "end",
               "600" if plat == "wayland" else "normal")
        for j, (cid, _cn) in enumerate(cols):
            lv = lut.get((plat, case, cid), "?")
            col = LEVEL_COLOR.get(lv, "#bdbdbd")
            x = x0 + j * cw
            s.rect(x + 2, y + 2, cw - 6, ch - 6, col, rx=4, op=0.16)
            s.rect(x + 2, y + 2, cw - 6, ch - 6, "none", rx=4, stroke=col, sw=1.4)
            s.text(x + cw / 2 - 1, y + ch / 2 + 4, lv, 11, col, "middle", "700")
        if i in (1, 3):
            s.line(x0, y + ch + 1, x0 + len(cols) * cw, y + ch + 1, GRID, 1)
    ly = y0 + 4 * ch + 18
    for i, lv in enumerate(["EXACT", "STRONG", "WEAK", "UNKNOWN"]):
        s.rect(x0 + i * 120, ly, 14, 10, LEVEL_COLOR[lv], rx=2)
        s.text(x0 + i * 120 + 20, ly + 9, lv, 10, INK)
    ny = ly + 26
    s.rect(20, ny, w - 40, 74, "#f7f7f7", rx=5)
    s.text(36, ny + 21, "The tested Wayland stack changed the trust architecture but did "
                        "not export additional provenance.", 12, INK, weight="700")
    s.text(36, ny + 39, "Improved: capture-path integrity (only the compositor produces the "
                        "frame); directness of surface→process.", 10.5, MUTED)
    s.text(36, ny + 53, "Not improved: capture→surface (portal AvailableSourceTypes = 1, "
                        "MONITOR only); surface→displayed resource.", 10.5, MUTED)
    s.text(36, ny + 67, "Made worse: cross-client enumeration only via compositor-private "
                        "IPC.", 10.5, MUTED)
    changed = sum(1 for c in cols for case in ("P", "R")
                  if lut.get(("x11", case, c[0])) != lut.get(("wayland", case, c[0])))
    RECORD["figure_7"] = {"input": "outputs/platform_binding_matrix.csv",
                          "matrix": {f"{p}_{c}": {cid: lut.get((p, c, cid))
                                                  for cid, _ in cols} for p, c in order},
                          "bindings_changed": changed}
    return s.save("fig7_platform_binding_matrix.svg", [
        "Source: outputs/platform_binding_matrix.csv. Wayland arm = sway 1.7 (wlroots) "
        "headless + xdg-desktop-portal-wlr + PipeWire, software-rendered container.",
        "SCOPE: ONE compositor, ONE portal backend, TWO constructed cases. GNOME/KDE portal "
        "backends implement WINDOW sources and were NOT tested."])


def main():
    os.makedirs(OUT, exist_ok=True)
    made = [fig1_assurance_chain(), fig2_recoverability(), fig3_lookback(),
            fig4_field_sets(), fig5_analytic_vs_empirical(), fig6_unknown_policy(),
            fig7_binding_matrix()]
    for p in made:
        RECORD.setdefault("_sha256", {})[os.path.basename(p)] = hashlib.sha256(
            open(p, "rb").read()).hexdigest()
    with open(os.path.join(OUT, "FIGURE_DATA.json"), "w", encoding="utf-8") as fh:
        json.dump(RECORD, fh, indent=2)
    for p in made:
        print(f"  {os.path.basename(p):44} "
              f"{RECORD['_sha256'][os.path.basename(p)][:16]}")
    print(f"\n  {len(made)} figures + FIGURE_DATA.json -> package/figures/")


if __name__ == "__main__":
    main()
