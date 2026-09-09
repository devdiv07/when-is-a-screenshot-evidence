"""Deterministic localization of judge `hack_evidence_quotes` inside a trace.

No LLM/embedding/fuzzy-semantic matching. Every level is a documented,
reproducible string transform. The level that succeeded is always recorded.

Ladder (first success wins):
  L0_EXACT     raw quote is a substring of the event's searchable text
  L1_WS        whitespace-collapsed quote inside whitespace-collapsed text
  L2_UNESCAPE  as L1 after decoding literal \n \t \\" \' sequences
  L3_ELIDED    quote split on elision markers ("...", "…"); ALL fragments
               present, in order, within one event
  L4_BACKTICK  judge-prose quote: only the `backticked` fragments are matched
               (all of them, in order, within one event)
  P5_PARTIAL   only some fragments matched (>=1, longest >= MIN_FRAG) -> PARTIAL
  NO_MATCH     nothing matched anywhere
"""
from __future__ import annotations

import re
from dataclasses import dataclass

MIN_FRAG = 24
MIN_NOWS = 40
ELISION = re.compile(r"\s*(?:\.\.\.+|…)\s*")
WS = re.compile(r"\s+")
BACKTICK = re.compile(r"`([^`]+)`")


def norm_ws(s: str) -> str:
    return WS.sub(" ", s).strip()


def unescape(s: str) -> str:
    return (s.replace("\n", "\n").replace("\t", "\t")
             .replace('\\"', '"').replace("\'", "'").replace("\\\\", "\\"))


def _ordered_in(hay: str, frags: list[str]) -> bool:
    pos = 0
    for fr in frags:
        i = hay.find(fr, pos)
        if i < 0:
            return False
        pos = i + len(fr)
    return True


def _found_frags(hay: str, frags: list[str]) -> list[str]:
    return [f for f in frags if f and f in hay]


@dataclass
class Match:
    level: str
    event_idx: int | None
    n_frags: int = 0
    n_frags_found: int = 0
    detail: str = ""

    @property
    def localized(self) -> bool:
        return self.level.startswith(("L0", "L1", "L2", "L3", "L4", "L5", "L6"))


def locate(quote: str, events) -> Match:
    """Return the best (earliest-ladder) match across events."""
    if not quote or not quote.strip():
        return Match("EMPTY_QUOTE", None)

    hays = [(e.idx, e.searchable()) for e in events]
    hays_ws = [(i, norm_ws(h)) for i, h in hays]
    hays_un = [(i, norm_ws(unescape(h))) for i, h in hays]

    # L0 raw substring
    for i, h in hays:
        if quote in h:
            return Match("L0_EXACT", i)
    # L1 whitespace-collapsed
    q1 = norm_ws(quote)
    for i, h in hays_ws:
        if q1 and q1 in h:
            return Match("L1_WS", i)
    # L2 unescaped
    q2 = norm_ws(unescape(quote))
    for i, h in hays_un:
        if q2 and q2 in h:
            return Match("L2_UNESCAPE", i)
    # L3 elision-split
    frags3 = [norm_ws(unescape(f)) for f in ELISION.split(quote)]
    frags3 = [f for f in frags3 if len(f) >= 3]
    if len(frags3) > 1:
        for i, h in hays_un:
            if _ordered_in(h, frags3):
                return Match("L3_ELIDED", i, len(frags3), len(frags3))
    # L4 backticked fragments (judge prose)
    bt = []
    for f in BACKTICK.findall(quote):
        bt.extend(norm_ws(unescape(x)) for x in ELISION.split(f))
    bt = [f for f in bt if len(f) >= 3]
    if bt:
        for i, h in hays_un:
            if _ordered_in(h, bt):
                return Match("L4_BACKTICK", i, len(bt), len(bt))
    # L5 whitespace-free (judge sometimes drops newlines entirely at token joins)
    def squeeze(x: str) -> str:
        return WS.sub("", unescape(x))
    qsq = squeeze(quote)
    if len(qsq) >= MIN_NOWS:
        for i, h in hays:
            if qsq in squeeze(h):
                return Match("L5_NOWS", i)
    # L6 elided fragments, whitespace-free
    cand6 = frags3 if len(frags3) > 1 else bt
    cand6 = [c for c in cand6 if len(squeeze(c)) >= 12]
    if cand6:
        for i, h in hays:
            if _ordered_in(squeeze(h), [squeeze(c) for c in cand6]):
                return Match("L6_ELIDED_NOWS", i, len(cand6), len(cand6))
    # P5 partial
    cand = frags3 if len(frags3) > 1 else (bt if bt else [q2])
    best = (0, None, [])
    for i, h in hays_un:
        got = _found_frags(h, cand)
        if got and len(got) > best[0]:
            best = (len(got), i, got)
    if best[1] is not None and max((len(x) for x in best[2]), default=0) >= MIN_FRAG:
        return Match("P5_PARTIAL", best[1], len(cand), best[0],
                     detail=f"longest_frag={max(len(x) for x in best[2])}")
    return Match("NO_MATCH", None, len(cand), 0)
