"""Phase D — which candidate field sets would have resolved the historical cases.

Set cover over outputs/information_deficits.csv, respecting conjunctive bundles:
a case is covered by a field set S only if S contains EVERY field of at least
one of that case's bundles.

HISTORICAL COVERAGE ONLY. Nothing here says a field survives an adversarial
evidence generator; that is Phase I and is not evaluated.

Two models are reported because the honest answer differs:
  STRICT   only bundles marked would_resolve = yes count
  LENIENT  bundles marked uncertain also count

Exact minimum set cover is NP-hard, and the yes/uncertain mapping carries real
ambiguity, so exact minimality would be false precision. Greedy is used and
labelled as an approximation; brute force up to size 5 reports the gap.
"""
from __future__ import annotations

import collections
import csv
import itertools
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")


def load():
    rows = list(csv.DictReader(open(os.path.join(OUT, "information_deficits.csv"), encoding="utf-8")))
    # case -> list of (frozenset(fields), verdict)
    bundles = collections.defaultdict(set)
    eligible = {}
    for r in rows:
        bundles[r["case_id"]].add((frozenset(r["bundle_fields"].split("+")),
                                   r["would_field_resolve_historical_case"]))
        eligible[r["case_id"]] = r["eligible"]
    return rows, {k: list(v) for k, v in bundles.items()}, eligible


def covered(sel, bundles, universe, lenient):
    ok = {"yes", "uncertain"} if lenient else {"yes"}
    s = set(sel)
    return {c for c in universe
            if any(v in ok and f <= s for f, v in bundles[c])}


def greedy(bundles, universe, lenient, all_fields, limit=14):
    """Greedy over BUNDLES, not single fields.

    Bundles are conjunctive, so the marginal gain of any single field is
    normally zero and field-wise greedy stalls immediately. At each step pick
    the bundle maximising (newly covered cases) / (number of NEW fields it
    costs), then add that whole bundle's fields.
    """
    ok = {"yes", "uncertain"} if lenient else {"yes"}
    cand = []
    for c in universe:
        for f, v in bundles[c]:
            if v in ok:
                cand.append(f)
    # deterministic candidate order: ties in greedy must not depend on set order
    cand = sorted({frozenset(f) for f in cand}, key=lambda b: (len(b), sorted(b)))

    sel, order = [], []
    while len(sel) < limit:
        cur = covered(sel, bundles, universe, lenient)
        if len(cur) == len(universe):
            break
        best, best_score, best_new = None, 0.0, 0
        for b in cand:
            new_fields = b - set(sel)
            if not new_fields:
                continue
            gain = len(covered(sel + list(new_fields), bundles, universe, lenient) - cur)
            if gain <= 0:
                continue
            score = gain / len(new_fields)
            if score > best_score:
                best, best_score, best_new = b, score, gain
        if best is None:
            break
        added = sorted(best - set(sel))
        sel.extend(added)
        order.append(("+".join(added), best_new,
                      len(covered(sel, bundles, universe, lenient)), list(sel)))
    return sel, order


def main():
    rows, bundles, eligible = load()
    universe = {c for c, e in eligible.items() if e == "yes"}
    all_fields = {r["missing_field_category"] for r in rows} - {"UNKNOWN_OTHER"}
    print(f"total unresolved cases        : {len(bundles)}")
    print(f"eligible (capture-addressable): {len(universe)}")
    for k, v in sorted(collections.Counter(eligible.values()).items()):
        print(f"   eligible={k:20s} {v}")

    out_rows, summary = [], {"universe_eligible": len(universe),
                             "universe_all": len(bundles), "models": {}}

    for lenient in (False, True):
        model = "LENIENT" if lenient else "STRICT"
        print(f"\n================ {model} coverage model ================")
        print(f"  {'single field alone':34s} {'covers':>7s} {'%elig':>7s}")
        singles = sorted(((f, len(covered([f], bundles, universe, lenient)))
                          for f in sorted(all_fields)),
                         key=lambda x: (-x[1], x[0]))
        for f, n in singles:
            if n:
                print(f"  {f:34s} {n:7d} {100*n/len(universe):6.1f}%")
            out_rows.append({"model": model, "analysis": "single_field", "field_set": f,
                             "set_size": 1, "cases_covered": n,
                             "pct_of_eligible": round(100 * n / len(universe), 1)})
        if not any(n for _f, n in singles):
            print("    (no single field resolves any case on its own — all bundles are conjunctive)")

        sel, order = greedy(bundles, universe, lenient, all_fields)
        print("")
        print(f"  greedy cumulative ({model}) - bundle-greedy approximation, not proven minimal:")
        thresholds = {}
        for i, (fadded, gain, tot, running) in enumerate(order, 1):
            pct = 100 * tot / len(universe)
            print(f"    step {i}: +{fadded:46s} gain={gain:4d}  |S|={len(running):2d}  "
                  f"cumulative={tot:4d} ({pct:5.1f}%)")
            out_rows.append({"model": model, "analysis": "greedy_cumulative",
                             "field_set": "|".join(running), "set_size": len(running),
                             "cases_covered": tot, "pct_of_eligible": round(pct, 1)})
            for t in (50, 75, 90):
                if pct >= t and t not in thresholds:
                    thresholds[t] = {"n_fields": len(running), "fields": list(running),
                                     "pct": round(pct, 1)}
        if thresholds:
            for t in sorted(thresholds):
                v = thresholds[t]
                print(f"    >= {t}% of eligible reached with {v['n_fields']} fields "
                      f"({v['pct']}%): {'+'.join(v['fields'])}")
        else:
            print("    no threshold reached")

        best_by_size = {}
        fields_l = sorted(all_fields)
        for k in (1, 2, 3, 4, 5, 6, 7):
            b, bn = None, -1
            for combo in itertools.combinations(fields_l, k):
                n = len(covered(list(combo), bundles, universe, lenient))
                if n > bn:
                    b, bn = combo, n
            g = len(covered(sel[:k], bundles, universe, lenient))
            best_by_size[k] = {"fields": list(b), "covered": bn,
                               "pct": round(100 * bn / len(universe), 1)}
            print(f"  size {k}: optimal={bn:4d} ({100*bn/len(universe):5.1f}%)  "
                  f"greedy={g:4d}  gap={bn-g}   optimal set = {'+'.join(b)}")
            out_rows.append({"model": model, "analysis": "optimal_bruteforce",
                             "field_set": "|".join(b), "set_size": k, "cases_covered": bn,
                             "pct_of_eligible": round(100 * bn / len(universe), 1)})
        summary["models"][model] = {
            "greedy_order": [{"fields_added": f, "gain": g, "cumulative": t,
                              "set_size": len(run), "set": run} for f, g, t, run in order],
            "thresholds": {str(k): v for k, v in thresholds.items()},
            "optimal_by_size": {str(k): v for k, v in best_by_size.items()},
        }

    p = os.path.join(OUT, "field_coverage.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["model", "analysis", "field_set", "set_size",
                                           "cases_covered", "pct_of_eligible"])
        w.writeheader()
        w.writerows(out_rows)
    os.makedirs(os.path.join(OUT, "cache"), exist_ok=True)
    json.dump(summary, open(os.path.join(OUT, "cache", "field_coverage_summary.json"), "w"), indent=2)
    print(f"\nwrote {p}: {len(out_rows)} rows")

    print("\n=== bundle frequency (yes-marked only, by case) ===")
    bf = collections.Counter()
    for c in universe:
        for f, v in bundles[c]:
            if v == "yes":
                bf["+".join(sorted(f))] += 1
    for k, n in bf.most_common(12):
        print(f"  {n:4d}  {k}")


if __name__ == "__main__":
    main()
