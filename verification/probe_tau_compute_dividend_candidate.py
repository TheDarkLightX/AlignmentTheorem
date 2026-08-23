#!/usr/bin/env python3
"""Execute all research packets on a non-promotable Tau build candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

from verification.generate_tau_compute_dividend_packets import GATES, TAU_ROOT
from verification.run_tau_compute_dividend import (
    EXPECTED_TAU_BINARY_SHA256,
    EXPECTED_TAU_PARSER_COMMIT,
    EXPECTED_TAU_SOURCE_COMMIT,
    EXPECTED_TAU_VERSION,
    _tree_sha256,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKETS = {
    "v1_1": {
        "root": REPO_ROOT / "tau" / "v1_1",
        "spec": "hyperdeflation_gate_v1_1.tau",
        "output": "reference_eligible.out",
    },
    **{
        gate: {
            "root": TAU_ROOT / gate,
            "spec": config["spec"],
            "output": "allow.out",
        }
        for gate, config in GATES.items()
    },
}
MAX_DIAGNOSTIC_BYTES = 8_192


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(source: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip()


def _command_text(argv: list[str], *, cwd: Path | None = None) -> dict[str, object]:
    result = subprocess.run(
        argv,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "argv": argv,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def run(tau_binary: Path, tau_source: Path) -> dict[str, object]:
    tau_binary = tau_binary.resolve(strict=True)
    tau_source = tau_source.resolve(strict=True)
    source_commit = _git(tau_source, "rev-parse", "HEAD")
    parser_commit = _git(tau_source / "external" / "parser", "rev-parse", "HEAD")
    source_status = _git(tau_source, "status", "--porcelain=v1")
    submodules = _git(tau_source, "submodule", "status", "--recursive").splitlines()

    with tempfile.TemporaryDirectory(prefix="tau-candidate-probe-") as temp:
        temp_root = Path(temp)
        # Execute the candidate in its build tree so its non-hermetic build
        # RPATH can resolve locally built cvc5.  This is deliberately weaker
        # than the reviewed-binary runners, which snapshot a self-contained
        # executable before promotion-oriented replay.
        binary = tau_binary
        binary_hash = _sha256(binary)
        version = subprocess.run(
            [str(binary), "--version"],
            check=False,
            capture_output=True,
            timeout=30,
        )
        version_text = (version.stdout + version.stderr).decode(
            "utf-8", errors="backslashreplace"
        ).strip()

        packet_reports = {}
        for name, config in PACKETS.items():
            packet = temp_root / name
            shutil.copytree(config["root"], packet)
            (packet / "outputs").mkdir()
            expected_path = packet / "expected" / config["output"]
            expected = expected_path.read_bytes()
            spec = packet / config["spec"]
            try:
                execution = subprocess.run(
                    [str(binary), "-X"],
                    cwd=packet,
                    input=spec.read_bytes(),
                    capture_output=True,
                    timeout=120,
                )
                execution_returncode: int | None = execution.returncode
                diagnostic = (execution.stdout + execution.stderr)[
                    :MAX_DIAGNOSTIC_BYTES
                ].decode("utf-8", errors="backslashreplace")
            except (OSError, subprocess.TimeoutExpired) as error:
                execution_returncode = None
                diagnostic = f"execution error: {type(error).__name__}"
            actual_path = packet / "outputs" / config["output"]
            actual = (
                actual_path.read_bytes()
                if actual_path.is_file() and not actual_path.is_symlink()
                else None
            )
            semantic_match = execution_returncode == 0 and actual == expected
            packet_reports[name] = {
                "packet_sha256": _tree_sha256(config["root"]),
                "spec_sha256": _sha256(config["root"] / config["spec"]),
                "expected_output_sha256": hashlib.sha256(expected).hexdigest(),
                "actual_output_sha256": (
                    hashlib.sha256(actual).hexdigest() if actual is not None else ""
                ),
                "expected_rows": len(expected.splitlines()),
                "actual_rows": len(actual.splitlines()) if actual is not None else 0,
                "actual_accepted_rows": (
                    [
                        index
                        for index, value in enumerate(actual.splitlines())
                        if value == b"1"
                    ]
                    if actual is not None
                    else []
                ),
                "execution_returncode": execution_returncode,
                "semantic_match": semantic_match,
                "diagnostic": "" if semantic_match else diagnostic,
            }

    submodule_pins_clean = (
        len(submodules) == 1
        and len(submodules[0].split()) >= 2
        and submodules[0].split()[0] == EXPECTED_TAU_PARSER_COMMIT
        and submodules[0].split()[1] == "external/parser"
    )
    source_pins_match = (
        source_commit == EXPECTED_TAU_SOURCE_COMMIT
        and parser_commit == EXPECTED_TAU_PARSER_COMMIT
        and source_status == ""
        and submodule_pins_clean
    )
    return {
        "schema": "alignment-theorem-tau-candidate-probe-v1",
        "candidate_probe_complete": True,
        "promotion_eligible": False,
        "replay_on_reviewed_binary": binary_hash == EXPECTED_TAU_BINARY_SHA256,
        "authority_status": "CANDIDATE_ONLY_NO_PUBLICATION_INVESTMENT_OR_VALUE_AUTHORITY",
        "source_to_binary_status": "DECLARED_LOCAL_BUILD_RELATION_NOT_INDEPENDENTLY_ATTESTED",
        "execution_environment_status": "HOST_KERNEL_LIBRARIES_AND_SANDBOX_NOT_HERMETICALLY_ATTESTED",
        "checker_sha256": _sha256(Path(__file__)),
        "expected_tau_source_commit": EXPECTED_TAU_SOURCE_COMMIT,
        "actual_tau_source_commit": source_commit,
        "expected_tau_parser_commit": EXPECTED_TAU_PARSER_COMMIT,
        "actual_tau_parser_commit": parser_commit,
        "source_status_porcelain": source_status.splitlines(),
        "submodules": submodules,
        "submodule_pins_clean": submodule_pins_clean,
        "source_pins_match": source_pins_match,
        "expected_tau_binary_sha256": EXPECTED_TAU_BINARY_SHA256,
        "candidate_tau_binary_sha256": binary_hash,
        "binary_execution_location": "SOURCE_BUILD_TREE_IN_PLACE",
        "reviewed_binary_match": binary_hash == EXPECTED_TAU_BINARY_SHA256,
        "expected_tau_version": EXPECTED_TAU_VERSION,
        "candidate_tau_version": version_text,
        "version_returncode": version.returncode,
        "version_match": version.returncode == 0 and version_text == EXPECTED_TAU_VERSION,
        "packets": packet_reports,
        "all_packet_semantics_match": all(
            report["semantic_match"] for report in packet_reports.values()
        ),
        "declared_build": {
            "tau_command": "TAU_BUILD_JOBS=1 ./dev release -DTAU_SHARED_PREFIX=<workspace> -DTAU_BUILD_JOBS=1",
            "boost": "Boost 1.86.0 commit 65c1319bb92fe7a9a4abd588eff5818d9c2bccf9 via Tau dep-boost helper",
            "cvc5": "cvc5-1.3.1 commit ea1b484fa54bfe56c0f8b3ac90a6e3e2f46441e7 manually configured outside Tau checkout after helper path-order failure",
            "m4": "GNU m4 1.4.19 built from archive SHA-256 63aede5c6d33b6d9b13511cd0be2cac046f2e70fd0a07aa9573a04a82783af96",
        },
        "environment_observations": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "compiler": _command_text(["c++", "--version"]),
            "cmake": _command_text(["cmake", "--version"]),
            "glibc": _command_text(["ldd", "--version"]),
        },
        "nonclaims": [
            "There is no passing/receipt field because this is a non-promotable candidate probe.",
            "Matching source pins do not attest which source produced the candidate executable.",
            "A differing candidate hash cannot replace the reviewed binary pin without review.",
            "Packet output does not authenticate host facts or create Tau Net authority.",
            "In-place candidate execution depends on unpinned build-tree libraries and is weaker than the reviewed-binary snapshot runners.",
        ],
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
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    if args.json:
        print(rendered, end="")
    else:
        print(f"Candidate: {report['candidate_tau_binary_sha256']}")
        print(f"Packet semantics match: {report['all_packet_semantics_match']}")
        print("Promotion eligible: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
