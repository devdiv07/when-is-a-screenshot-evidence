"""Compute SHA-256 for package files and key frozen artifacts.

Used to generate the hash tables in package/PACKAGE_MANIFEST.md, and to re-verify them.

Run:  python package/scripts/manifest_hashes.py [--check]
"""
from __future__ import annotations

import hashlib
import os
import re
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
    for r, dirs, fs in os.walk(base):
        dirs[:] = [directory for directory in dirs if directory != "__pycache__"]
        for f in sorted(fs):
            if f.endswith((".pyc", ".pyo")):
                continue
            p = os.path.join(r, f)
            out.append(os.path.relpath(p, ROOT).replace(os.sep, "/"))
    return sorted(out)


def check_manifest():
    manifest_rel = "package/PACKAGE_MANIFEST.md"
    manifest_path = os.path.join(ROOT, manifest_rel)
    text = open(manifest_path, encoding="utf-8").read()
    entries = re.findall(r"\| `([0-9a-f]{64})` \| `([^`]+)`", text)
    expected = {path: digest for digest, path in entries}

    failures = []
    for rel, digest in sorted(expected.items()):
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            failures.append(f"missing: {rel}")
        elif sha(path) != digest:
            failures.append(f"digest mismatch: {rel}")

    actual_package = set(package_files()) - {manifest_rel}
    listed_package = {rel for rel in expected if rel.startswith("package/")}
    for rel in sorted(actual_package - listed_package):
        failures.append(f"unlisted package file: {rel}")
    for rel in sorted(listed_package - actual_package):
        failures.append(f"manifest-only package file: {rel}")

    if failures:
        print("MANIFEST CHECK FAILED")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print(f"manifest check: {len(expected)} files OK; manifest self-digest excluded")
    return 0


def main():
    if "--check" in sys.argv[1:]:
        return check_manifest()
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
