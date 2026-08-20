"""Build and grade the V1.1 Lean theorem with deterministic evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROOF_ROOT = REPO_ROOT / "proofs" / "v1_1"
PROOF_FILES = (
    "AlignmentTheoremV1_1.lean",
    "AxiomAudit.lean",
    "lakefile.lean",
    "lake-manifest.json",
    "lean-toolchain",
)
PLACEHOLDER = re.compile(r"\b(?:sorry|admit|axiom|unsafe)\b|sorryAx")
EXPECTED_LEAN_VERSION_PREFIX = "Lean (version 4.33.0,"
EXPECTED_AXIOMS = {
    "AlignmentTheoremV1_1.minimum_scarcity_multiplier_is_strict": ["propext"],
    "AlignmentTheoremV1_1.strict_margin_at_or_above_minimum": ["propext"],
    "AlignmentTheoremV1_1.strict_margin_forces_epsilon_optimal_choice_ethical": [
        "propext",
        "Quot.sound",
    ],
    "AlignmentTheoremV1_1.finite_hyperdeflationary_alignment": [
        "propext",
        "Quot.sound",
    ],
    "AlignmentTheoremV1_1.hyperdeflation_eventually_aligns_bounded_deviations": [
        "propext",
        "Quot.sound",
    ],
    "AlignmentTheoremV1_1.relative_growth_eventually_has_strict_margin": [
        "propext"
    ],
}
AXIOM_LINE = re.compile(
    r"^'(?P<name>[^']+)' (?:depends on axioms: \[(?P<axioms>[^]]*)\]|"
    r"does not depend on any axioms)$",
    re.MULTILINE,
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _bundle_sha256(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative, file_hash in sorted(files.items()):
        name = relative.encode("utf-8")
        value = file_hash.encode("ascii")
        digest.update(len(name).to_bytes(8, "big"))
        digest.update(name)
        digest.update(value)
    return digest.hexdigest()


def _parse_axiom_report(output: str) -> dict[str, list[str]]:
    reports = {}
    for match in AXIOM_LINE.finditer(output):
        rendered = match.group("axioms") or ""
        reports[match.group("name")] = [
            item.strip() for item in rendered.split(",") if item.strip()
        ]
    return reports


def run() -> dict[str, object]:
    files = {
        relative: _sha256((PROOF_ROOT / relative).read_bytes())
        for relative in PROOF_FILES
    }
    source = (PROOF_ROOT / "AlignmentTheoremV1_1.lean").read_text()
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
        ["lake", "build"],
        cwd=PROOF_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    audit = subprocess.run(
        ["lake", "env", "lean", "AxiomAudit.lean"],
        cwd=PROOF_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    lean_version = (version.stdout + version.stderr).strip()
    axiom_output = audit.stdout + audit.stderr
    reports = _parse_axiom_report(axiom_output)
    passed = (
        build.returncode == 0
        and audit.returncode == 0
        and reports == EXPECTED_AXIOMS
        and not placeholders
        and lean_version.startswith(EXPECTED_LEAN_VERSION_PREFIX)
    )
    return {
        "schema": "alignment-theorem-v1-1-lean-build-v1",
        "checker_sha256": _sha256(Path(__file__).read_bytes()),
        "lean_version": lean_version,
        "source_files_sha256": files,
        "source_bundle_sha256": _bundle_sha256(files),
        "placeholders": placeholders,
        "build_returncode": build.returncode,
        "axiom_audit_returncode": audit.returncode,
        "axiom_reports": reports,
        "expected_axiom_reports": EXPECTED_AXIOMS,
        "passed": passed,
        "error": "" if passed else build.stdout + build.stderr + axiom_output,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    if args.json:
        print(rendered, end="")
    else:
        print(f"Lean: {report['lean_version']}")
        print("PASS" if report["passed"] else "FAIL")
        if not report["passed"]:
            print(report["error"])
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
