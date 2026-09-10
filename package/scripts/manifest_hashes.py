"""Compute SHA-256 for package files and key frozen artifacts.

Used to generate the hash tables in package/PACKAGE_MANIFEST.md, and to re-verify them.

Run:  python package/scripts/manifest_hashes.py [--check]
"""
from __future__ import annotations

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

KEY_FROZEN = [
    "outputs/audit_metrics.json",
    "outputs/field_coverage.csv",
    "outputs/information_deficits.csv",
    "outputs/analytic_vs_empirical.csv",
    "outputs/empirical_risk_coverage.csv",
    "outputs/phase1_final_metrics.json",
    "outputs/platform_binding_matrix.csv",
    "outputs/platform_comparison_cases.csv",
    "outputs/platform_comparison_metrics.json",
    "outputs/13b_static_trace/trace_summary.json",
    "outputs/platform_raw/portal_probe.json",
    "outputs/empirical_raw/empirical_records.json",
    "research/FROZEN_FINDINGS.md",
    "infra/adjudicator.py",
    "infra/recorder.py",
]


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def package_files():
    out = []
    base = os.path.join(ROOT, "package")
    for r, _d, fs in os.walk(base):
        for f in sorted(fs):
            p = os.path.join(r, f)
            out.append(os.path.relpath(p, ROOT).replace(os.sep, "/"))
    return sorted(out)


def main():
    print("PACKAGE FILES")
    for rel in package_files():
        print(f"  {sha(os.path.join(ROOT, rel))}  {rel}")
    print("\nKEY FROZEN ARTIFACTS")
    for rel in KEY_FROZEN:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            print(f"  {sha(p)}  {rel}")
        else:
            print(f"  {'MISSING':64}  {rel}")


if __name__ == "__main__":
    main()
