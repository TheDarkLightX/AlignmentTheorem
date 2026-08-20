"""Generate claim-scoped, source-bound assurance evidence for Version 1.1."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    from verification.run_lean_v1_1 import run as run_lean
except ModuleNotFoundError:  # Direct script execution from verification/.
    from run_lean_v1_1 import run as run_lean

REPO_ROOT = Path(__file__).resolve().parents[1]
BOUND_FILES = (
    "README.md",
    "TOOLCHAINS.md",
    "docs/Alignment_Theorem_Academic.pdf",
    "docs/Alignment_Theorem_V1_1_Hyperdeflationary.pdf",
    "docs/SIMULATION_RESULTS.md",
    "docs/THREAT_MODEL.md",
    "docs/V1_TO_V2_CORRECTIONS.md",
    "docs/VERIFICATION_SUMMARY.md",
    "docs/alignment-theorem-v1-archive-notice.html",
    "docs/alignment-theorem-deep-dive.html",
    "docs/index.html",
    "docs/v1-1-hyperdeflationary-alignment.html",
    "proofs/v1_1/AlignmentTheoremV1_1.lean",
    "proofs/v1_1/AxiomAudit.lean",
    "proofs/v1_1/lake-manifest.json",
    "proofs/v1_1/lakefile.lean",
    "proofs/v1_1/lean-toolchain",
    "tau/v1_1/expected/reference_eligible.out",
    "tau/v1_1/hyperdeflation_gate_v1_1.tau",
    "tau/v1_1/inputs/action_ethical.in",
    "tau/v1_1/inputs/eetf_authenticated.in",
    "tau/v1_1/inputs/reward_funded.in",
    "tau/v1_1/inputs/strict_hyperdeflation_margin.in",
    "tests/test_alignment_v1_1_model.py",
    "tests/test_lean_v1_1_receipt.py",
    "tests/test_tau_v1_1.py",
    "tests/test_v1_1_assurance_receipt.py",
    "tests/test_v1_1_publication.py",
    "verification/alignment_v1_1_model.py",
    "verification/generate_tau_v1_1_packet.py",
    "verification/receipts/lean_v1_1_v4.33.0.json",
    "verification/run_lean_v1_1.py",
)
TEST_MODULES = (
    "tests.test_alignment_v1_1_model",
    "tests.test_tau_v1_1",
    "tests.test_lean_v1_1_receipt",
    "tests.test_v1_1_publication",
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


def run() -> dict[str, object]:
    bound_hashes = {
        relative: _sha256((REPO_ROOT / relative).read_bytes())
        for relative in BOUND_FILES
    }
    tests = subprocess.run(
        [sys.executable, "-m", "unittest", *TEST_MODULES],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    lean = run_lean()
    passed = tests.returncode == 0 and lean["passed"] is True
    return {
        "schema": "alignment-theorem-v1-1-assurance-v1",
        "checker_sha256": _sha256(Path(__file__).read_bytes()),
        "bound_files_sha256": bound_hashes,
        "source_bundle_sha256": _bundle_sha256(bound_hashes),
        "python_version": sys.version.split()[0],
        "python_test_modules": list(TEST_MODULES),
        "python_test_returncode": tests.returncode,
        "lean_source_bundle_sha256": lean["source_bundle_sha256"],
        "lean_passed": lean["passed"],
        "tau_semantic_packet_rows": 16,
        "tau_interpreter_replay_status": "PENDING_EXACT_SOURCE_PIN",
        "authority_status": "REFERENCE_ONLY_NO_PUBLICATION_OR_VALUE_AUTHORITY",
        "passed": passed,
        "error": "" if passed else tests.stdout + tests.stderr + str(lean["error"]),
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
        print("PASS" if report["passed"] else "FAIL")
        if not report["passed"]:
            print(report["error"])
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
