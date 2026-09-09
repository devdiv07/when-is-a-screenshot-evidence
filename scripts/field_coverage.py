"""Phase D — what candidate field sets would have achieved on the historical cases.

Set cover over outputs/information_deficits.csv, respecting conjunctive bundles: a case
counts for a field set S only if S contains EVERY field of at least one qualifying bundle.

THREE NESTED OUTCOMES are computed separately (preflight correction 1). The earlier single
"resolved" number conflated them and overstated the result:

  closure      INFORMATION_DEFICIT_CLOSURE      the missing fields are no longer missing
  resolution   SCENE_SOURCE_RESOLUTION          which surface contributed the pixels
  adjudication TARGET_SUBSTITUTE_ADJUDICATION   whether that surface is the declared target

Adjudication additionally requires a declared target (Tier 0). Cases with no declared
target are excluded from its universe and stay UNKNOWN, never counted as failures.

HISTORICAL only. Nothing here says a field survives a contract-aware adversary; that is the
white-box adversarial case evaluation.

Exact minimum set cover is NP-hard and the bundle verdicts carry real ambiguity, so exact
minimality would be false precision. Bundle-greedy is used and labelled an approximation;
brute force to size 7 reports the gap.
"""
from __future__ import annotations

import collections
import csv
import itertools
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

OUTCOMES = [
    ("closure", "closes_information_deficit", {"yes"}),
    ("resolution", "enables_scene_source_resolution", {"yes"}),
    ("resolution_lenient", "enables_scene_source_resolution", {"yes", "uncertain"}),
    ("adjudication", "enables_target_substitute_adjudication", {"yes"}),
]


def load():
    rows = list(csv.DictReader(open(os.path.join(OUT, "information_deficits.csv"), encoding="utf-8")))
    per_outcome = {name: collections.defaultdict(set) for name, _c, _ok in OUTCOMES}
    eligible, declared = {}, {}
    for r in rows:
        fs = frozenset(r["bundle_fields"].split("+"))
        for name, col, ok in OUTCOMES:
            if r[col] in ok:
                per_outcome[name][r["case_id"]].add(fs)
        eligible[r["case_id"]] = r["eligible"]
        declared[r["case_id"]] = r["target_declared"] == "True"
    return rows, per_outcome, eligible, declared


def covered(sel, bundles, universe):
    s = set(sel)
    return {c for c in universe if any(f <= s for f in bundles.get(c, ()))}


def greedy(bundles, universe, limit=16):
    """Greedy over BUNDLES: single-field marginal gain is normally zero."""
    cand = sorted({f for c in universe for f in bundles.get(c, ())},
                  key=lambda b: (len(b), sorted(b)))
    sel, order = [], []
    while len(sel) < limit:
        cur = covered(sel, bundles, universe)
        if len(cur) == len(universe):
            break
        best, best_score, best_gain = None, 0.0, 0
        for b in cand:
            new = b - set(sel)
            if not new:
                continue
            gain = len(covered(sel + list(new), bundles, universe) - cur)
            if gain <= 0:
                continue
            score = gain / len(new)
            if score > best_score:
                best, best_score, best_gain = b, score, gain
        if best is None:
            break
        added = sorted(best - set(sel))
        sel.extend(added)
        order.append(("+".join(added), best_gain,
                      len(covered(sel, bundles, universe)), list(sel)))
    return sel, order


def main():
    rows, per_outcome, eligible, declared = load()
    all_cases = set(eligible)
    scene_universe = {c for c, e in eligible.items() if e in ("yes", "no_target_defined")}
    adj_universe = {c for c in scene_universe if declared[c]}
    all_fields = sorted({r["missing_field_category"] for r in rows} - {"UNKNOWN_OTHER"})

    print(f"unresolved cases                       : {len(all_cases)}")
    print(f"scene-source universe (capture-layer)  : {len(scene_universe)}")
    print(f"adjudication universe (target declared): {len(adj_universe)}")
    for k, v in sorted(collections.Counter(eligible.values()).items()):
        print(f"   eligible={k:20s} {v}")

    out_rows = []
    summary = {"universes": {"all_unresolved": len(all_cases),
                             "scene_source": len(scene_universe),
                             "adjudication": len(adj_universe)},
               "outcomes": {}}

    for name, _col, _ok in OUTCOMES:
        bundles = per_outcome[name]
        universe = adj_universe if name == "adjudication" else scene_universe
        print(f"\n================ {name.upper()} ================")
        print(f"  universe = {len(universe)}")
        singles = sorted(((f, len(covered([f], bundles, universe))) for f in all_fields),
                         key=lambda x: (-x[1], x[0]))
        top = [s for s in singles if s[1]]
        if top:
            for f, n in top[:6]:
                print(f"    single {f:32s} {n:5d} ({100*n/len(universe):5.1f}%)")
        else:
            print("    no single field achieves this outcome alone (bundles are conjunctive)")
        for f, n in singles:
            out_rows.append({"outcome": name, "analysis": "single_field", "field_set": f,
                             "set_size": 1, "cases": n, "universe": len(universe),
                             "pct_of_universe": round(100 * n / len(universe), 1)})

        sel, order = greedy(bundles, universe)
        print("  bundle-greedy (approximation, not proven minimal):")
        thresholds = {}
        for i, (added, gain, tot, run) in enumerate(order, 1):
            pct = 100 * tot / len(universe)
            print(f"    step {i}: +{added:46s} |S|={len(run):2d}  {tot:4d} ({pct:5.1f}%)")
            out_rows.append({"outcome": name, "analysis": "greedy_cumulative",
                             "field_set": "|".join(run), "set_size": len(run),
                             "cases": tot, "universe": len(universe),
                             "pct_of_universe": round(pct, 1)})
            for t in (50, 75, 90):
                if pct >= t and t not in thresholds:
                    thresholds[t] = {"n_fields": len(run), "fields": list(run),
                                     "pct": round(pct, 1)}
        if not order:
            print("    (nothing achievable with any bundle)")
        for t in sorted(thresholds):
            v = thresholds[t]
            print(f"    >= {t}% with {v['n_fields']} fields ({v['pct']}%): {'+'.join(v['fields'])}")

        best_by_size = {}
        for k in (1, 2, 3, 4, 5, 6, 7):
            b, bn = None, -1
            for combo in itertools.combinations(all_fields, k):
                n = len(covered(list(combo), bundles, universe))
                if n > bn:
                    b, bn = combo, n
            g = len(covered(sel[:k], bundles, universe))
            best_by_size[k] = {"fields": list(b), "cases": bn,
                               "pct": round(100 * bn / len(universe), 1)}
            out_rows.append({"outcome": name, "analysis": "optimal_bruteforce",
                             "field_set": "|".join(b), "set_size": k, "cases": bn,
                             "universe": len(universe),
                             "pct_of_universe": round(100 * bn / len(universe), 1)})
            print(f"    size {k}: optimal={bn:4d} ({100*bn/len(universe):5.1f}%) greedy={g:4d} "
                  f"gap={bn-g}  {'+'.join(b)}")
        summary["outcomes"][name] = {
            "universe": len(universe),
            "greedy_order": [{"added": a, "gain": g, "cumulative": t, "set_size": len(run),
                              "set": run} for a, g, t, run in order],
            "thresholds": {str(k): v for k, v in thresholds.items()},
            "optimal_by_size": {str(k): v for k, v in best_by_size.items()},
        }

    p = os.path.join(OUT, "field_coverage.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["outcome", "analysis", "field_set", "set_size",
                                           "cases", "universe", "pct_of_universe"])
        w.writeheader()
        w.writerows(out_rows)
    os.makedirs(os.path.join(OUT, "cache"), exist_ok=True)
    json.dump(summary, open(os.path.join(OUT, "cache", "field_coverage_summary.json"), "w"),
              indent=2)
    print(f"\nwrote {p}: {len(out_rows)} rows")

    print("\n=== canonical field sets across the three outcomes ===")
    sets = {
        "D4 display-composition": ["CAPTURE_REGION", "VISIBLE_WINDOW_SET",
                                   "WINDOW_GEOMETRY", "Z_ORDER"],
        "D4 + focus + pid": ["CAPTURE_REGION", "VISIBLE_WINDOW_SET", "WINDOW_GEOMETRY",
                             "Z_ORDER", "ACTIVE_WINDOW_IDENTITY", "ACTIVE_PID"],
        "D4 + focus + pid + lifecycle": ["CAPTURE_REGION", "VISIBLE_WINDOW_SET",
                                         "WINDOW_GEOMETRY", "Z_ORDER",
                                         "ACTIVE_WINDOW_IDENTITY", "ACTIVE_PID",
                                         "PROCESS_LIFECYCLE_AT_CAPTURE",
                                         "PROCESS_START_IDENTITY"],
    }
    print(f"  {'set':32s} {'closure':>14s} {'resolution':>14s} {'adjudication':>14s}")
    for label, s in sets.items():
        cells = []
        for name in ("closure", "resolution", "adjudication"):
            u = adj_universe if name == "adjudication" else scene_universe
            n = len(covered(s, per_outcome[name], u))
            cells.append(f"{n}/{len(u)} {100*n/len(u):.1f}%")
        print(f"  {label:32s} {cells[0]:>14s} {cells[1]:>14s} {cells[2]:>14s}")
        out_rows.append({})


if __name__ == "__main__":
    main()
