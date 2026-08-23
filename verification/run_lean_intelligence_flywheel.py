#!/usr/bin/env python3
"""Build and source-bind the intelligence-flywheel Lean kernel."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROOF_ROOT = REPO_ROOT / "proofs" / "intelligence_flywheel"
PROOF_FILES = (
    "IntelligenceFlywheel.lean",
    "AxiomAudit.lean",
    "lakefile.lean",
    "lake-manifest.json",
    "lean-toolchain",
)
COMPATIBILITY_SHIM_SOURCE = REPO_ROOT / "verification" / "compat" / "lean_proc_self_compat.c"
PLACEHOLDER = re.compile(r"\b(?:sorry|admit|axiom|unsafe)\b|sorryAx")
EXPECTED_LEAN_VERSION_PREFIX = "Lean (version 4.33.0,"
EXPECTED_THEOREMS = (
    "IntelligenceFlywheel.alignment_of_geometric_bounds",
    "IntelligenceFlywheel.fixed_deviation_doubling_witness",
    "IntelligenceFlywheel.intelligence_growth_alone_insufficient",
    "IntelligenceFlywheel.bounded_reward_blocks_alignment",
    "IntelligenceFlywheel.equality_is_not_strict_alignment",
    "IntelligenceFlywheel.dac_admission_implies_every_fact",
    "IntelligenceFlywheel.non_treasury_sender_is_unaffected",
    "IntelligenceFlywheel.treasury_admission_implies_gate",
)
AXIOM_LINE = re.compile(
    r"^'(?P<name>[^']+)' (?:depends on axioms: \[(?P<axioms>[^]]*)\]|"
    r"does not depend on any axioms)$",
    re.MULTILINE,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bundle_sha256(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative, file_hash in sorted(files.items()):
        name = relative.encode()
        value = file_hash.encode()
        digest.update(len(name).to_bytes(8, "big"))
        digest.update(name)
        digest.update(value)
    return digest.hexdigest()


def _parse_axioms(output: str) -> dict[str, list[str]]:
    reports = {}
    for match in AXIOM_LINE.finditer(output):
        rendered = match.group("axioms") or ""
        reports[match.group("name")] = [
            item.strip() for item in rendered.split(",") if item.strip()
        ]
    return reports


def _preload_receipt() -> list[dict[str, str]]:
    entries = []
    for raw in os.environ.get("LD_PRELOAD", "").split(":"):
        if raw:
            path = Path(raw)
            entries.append(
                {
                    "basename": path.name,
                    "sha256": _sha256(path) if path.is_file() else "UNREADABLE_OR_MISSING",
                }
            )
    return entries


def run() -> dict[str, object]:
    files = {relative: _sha256(PROOF_ROOT / relative) for relative in PROOF_FILES}
    source = (PROOF_ROOT / "IntelligenceFlywheel.lean").read_text()
    placeholders = sorted(set(PLACEHOLDER.findall(source)))
    version = subprocess.run(
        ["lake", "env", "lean", "--version"],
        cwd=PROOF_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    build = subprocess.run(
        ["lake", "build"], cwd=PROOF_ROOT, capture_output=True, text=True, timeout=180
    )
    audit = subprocess.run(
        ["lake", "env", "lean", "AxiomAudit.lean"],
        cwd=PROOF_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = audit.stdout + audit.stderr
    reports = _parse_axioms(output)
    expected_set = set(EXPECTED_THEOREMS)
    passed = (
        build.returncode == 0
        and audit.returncode == 0
        and set(reports) == expected_set
        and all("Classical.choice" not in axioms for axioms in reports.values())
        and not placeholders
        and (version.stdout + version.stderr).strip().startswith(EXPECTED_LEAN_VERSION_PREFIX)
    )
    return {
        "schema": "alignment-theorem-intelligence-flywheel-lean-build-v1",
        "checker_sha256": _sha256(Path(__file__)),
        "lean_version": (version.stdout + version.stderr).strip(),
        "source_files_sha256": files,
        "source_bundle_sha256": _bundle_sha256(files),
        "compatibility_shim_source_sha256": _sha256(COMPATIBILITY_SHIM_SOURCE),
        "ld_preload": _preload_receipt(),
        "execution_environment_status": "HOST_KERNEL_LIBRARIES_AND_SANDBOX_NOT_HERMETICALLY_ATTESTED",
        "source_to_executable_status": "LEAN_VERSION_REPORTED_BINARY_BUILD_PROVENANCE_NOT_ATTESTED",
        "placeholders": placeholders,
        "build_returncode": build.returncode,
        "axiom_audit_returncode": audit.returncode,
        "axiom_reports": reports,
        "passed": passed,
        "error": "" if passed else build.stdout + build.stderr + output,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    if args.json:
        print(rendered, end="")
    else:
        print("PASS" if report["passed"] else "FAIL")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
