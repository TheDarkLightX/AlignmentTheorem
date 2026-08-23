#!/usr/bin/env python3
"""Execute the flywheel packet on a source-pinned, non-promotable Tau candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    from verification.generate_tau_intelligence_flywheel_packet import OUTPUT_NAME, SPEC_NAME, TAU_PACKET
    from verification.run_tau_compute_dividend import (
        EXPECTED_TAU_BINARY_SHA256,
        EXPECTED_TAU_PARSER_COMMIT,
        EXPECTED_TAU_SOURCE_COMMIT,
        EXPECTED_TAU_VERSION,
        _tree_sha256,
    )
except ModuleNotFoundError:
    from generate_tau_intelligence_flywheel_packet import OUTPUT_NAME, SPEC_NAME, TAU_PACKET
    from run_tau_compute_dividend import (
        EXPECTED_TAU_BINARY_SHA256,
        EXPECTED_TAU_PARSER_COMMIT,
        EXPECTED_TAU_SOURCE_COMMIT,
        EXPECTED_TAU_VERSION,
        _tree_sha256,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()


def run(tau_binary: Path, tau_source: Path) -> dict[str, object]:
    tau_binary = tau_binary.resolve(strict=True)
    tau_source = tau_source.resolve(strict=True)
    source_commit = _git(tau_source, "rev-parse", "HEAD")
    parser_commit = _git(tau_source / "external" / "parser", "rev-parse", "HEAD")
    source_status = _git(tau_source, "status", "--porcelain=v1")
    submodules = _git(tau_source, "submodule", "status", "--recursive").splitlines()
    binary_hash = _sha256(tau_binary)
    version = subprocess.run([str(tau_binary), "--version"], capture_output=True, timeout=30)
    version_text = (version.stdout + version.stderr).decode(errors="backslashreplace").strip()
    with tempfile.TemporaryDirectory(prefix="flywheel-candidate-") as raw:
        packet = Path(raw) / "packet"
        shutil.copytree(TAU_PACKET, packet)
        (packet / "outputs").mkdir()
        execution = subprocess.run(
            [str(tau_binary), "-X"],
            cwd=packet,
            input=(packet / SPEC_NAME).read_bytes(),
            capture_output=True,
            timeout=180,
        )
        expected = (packet / "expected" / OUTPUT_NAME).read_bytes()
        output = packet / "outputs" / OUTPUT_NAME
        actual = output.read_bytes() if output.is_file() and not output.is_symlink() else None
    submodule_pins_clean = (
        len(submodules) == 1
        and submodules[0].split()[0] == EXPECTED_TAU_PARSER_COMMIT
        and submodules[0].split()[1] == "external/parser"
    )
    source_pins_match = (
        source_commit == EXPECTED_TAU_SOURCE_COMMIT
        and parser_commit == EXPECTED_TAU_PARSER_COMMIT
        and source_status == ""
        and submodule_pins_clean
    )
    semantic_match = execution.returncode == 0 and actual == expected
    return {
        "schema": "alignment-theorem-intelligence-flywheel-tau-candidate-v1",
        "candidate_probe_complete": True,
        "promotion_eligible": False,
        "replay_on_reviewed_binary": binary_hash == EXPECTED_TAU_BINARY_SHA256,
        "checker_sha256": _sha256(Path(__file__)),
        "expected_tau_source_commit": EXPECTED_TAU_SOURCE_COMMIT,
        "actual_tau_source_commit": source_commit,
        "expected_tau_parser_commit": EXPECTED_TAU_PARSER_COMMIT,
        "actual_tau_parser_commit": parser_commit,
        "source_status_porcelain": source_status.splitlines(),
        "submodules": submodules,
        "source_pins_match": source_pins_match,
        "expected_tau_binary_sha256": EXPECTED_TAU_BINARY_SHA256,
        "candidate_tau_binary_sha256": binary_hash,
        "reviewed_binary_match": binary_hash == EXPECTED_TAU_BINARY_SHA256,
        "expected_tau_version": EXPECTED_TAU_VERSION,
        "candidate_tau_version": version_text,
        "version_match": version.returncode == 0 and version_text == EXPECTED_TAU_VERSION,
        "tau_packet_sha256": _tree_sha256(TAU_PACKET),
        "tau_spec_sha256": _sha256(TAU_PACKET / SPEC_NAME),
        "expected_output_sha256": hashlib.sha256(expected).hexdigest(),
        "actual_output_sha256": hashlib.sha256(actual).hexdigest() if actual else "",
        "expected_rows": len(expected.splitlines()),
        "actual_rows": len(actual.splitlines()) if actual else 0,
        "actual_accepted_rows": [
            index for index, value in enumerate(actual.splitlines()) if value == b"1"
        ] if actual else [],
        "execution_returncode": execution.returncode,
        "semantic_match": semantic_match,
        "source_to_binary_status": "DECLARED_LOCAL_BUILD_RELATION_NOT_INDEPENDENTLY_ATTESTED",
        "execution_environment_status": "HOST_KERNEL_LIBRARIES_AND_SANDBOX_NOT_HERMETICALLY_ATTESTED",
        "authority_status": "CANDIDATE_ONLY_NO_TAU_NET_PUBLICATION_INVESTMENT_OR_VALUE_AUTHORITY",
        "platform_observation": platform.platform(),
        "nonclaims": [
            "No passing or promotion field is issued for this candidate identity.",
            "Matching source pins do not attest which source produced the executable.",
            "Candidate output cannot replace the reviewed-binary replay.",
            "The packet does not authenticate its economic or governance inputs.",
        ],
        "diagnostic": "" if semantic_match else (execution.stdout + execution.stderr)[:8192].decode(errors="backslashreplace"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau-bin", required=True, type=Path)
    parser.add_argument("--tau-source", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run(args.tau_bin, args.tau_source)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    if args.json:
        print(rendered, end="")
    else:
        print(f"Candidate semantic match: {report['semantic_match']}")
        print("Promotion eligible: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
