#!/usr/bin/env python3
"""Fail-closed replay of a compute-dividend packet on the reviewed Tau binary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    from verification.generate_tau_compute_dividend_packets import (
        GATES,
        TAU_ROOT,
        generated_payloads,
    )
except ModuleNotFoundError:
    from generate_tau_compute_dividend_packets import GATES, TAU_ROOT, generated_payloads

EXPECTED_TAU_SOURCE_COMMIT = "fd137e860b60083b36f9159ec8090cb1a3c3cb5a"
EXPECTED_TAU_PARSER_COMMIT = "5dd036358e194e55a08fd2ec255441bedfe83765"
EXPECTED_TAU_VERSION = "Tau Language Framework version 0.7.0-alpha (fd137e8)"
EXPECTED_TAU_BINARY_SHA256 = (
    "c49267404e07a1f540c941b618e786710f70001eecbd05bb7c6d8eec0c5645fa"
)
AUTHORITY_STATUS = "RESEARCH_REPLAY_ONLY_NO_PUBLICATION_INVESTMENT_OR_VALUE_AUTHORITY"
SOURCE_PROVENANCE_STATUS = "DECLARED_SOURCE_PIN_NOT_ATTESTED_BY_THIS_REPLAY"
EXECUTION_ENVIRONMENT_STATUS = "HOST_ENVIRONMENT_NOT_HERMETICALLY_PINNED"
MAX_DIAGNOSTIC_BYTES = 8_192


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    candidates: list[Path] = []
    for candidate in root.rglob("*"):
        if candidate.is_symlink():
            raise ValueError(f"Tau packet contains symlink: {candidate}")
        if candidate.is_file():
            candidates.append(candidate)
    for path in sorted(candidates, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _packet_errors(gate: str, packet: Path) -> tuple[str, ...]:
    config = GATES[gate]
    generated = generated_payloads(gate)
    expected_files = {config["spec"], *generated}
    actual_files = {
        path.relative_to(packet).as_posix()
        for path in packet.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    errors: list[str] = []
    if actual_files != expected_files:
        errors.append("PACKET_FILE_SET_MISMATCH")
    for relative, expected in generated.items():
        path = packet / relative
        if not path.is_file() or path.is_symlink() or path.read_bytes() != expected:
            errors.append(f"GENERATED_VECTOR_MISMATCH:{relative}")
    return tuple(errors)


def _base_report(gate: str, packet: Path, binary_hash: str) -> dict[str, object]:
    config = GATES[gate]
    return {
        "schema": "alignment-theorem-compute-dividend-tau-run-v1",
        "gate": gate,
        "checker_sha256": _sha256(Path(__file__)),
        "generator_sha256": _sha256(
            Path(__file__).with_name("generate_tau_compute_dividend_packets.py")
        ),
        "expected_tau_source_commit": EXPECTED_TAU_SOURCE_COMMIT,
        "expected_tau_parser_commit": EXPECTED_TAU_PARSER_COMMIT,
        "expected_tau_version": EXPECTED_TAU_VERSION,
        "expected_tau_binary_sha256": EXPECTED_TAU_BINARY_SHA256,
        "source_provenance_status": SOURCE_PROVENANCE_STATUS,
        "execution_environment_status": EXECUTION_ENVIRONMENT_STATUS,
        "authority_status": AUTHORITY_STATUS,
        "tau_binary_sha256": binary_hash,
        "tau_spec_sha256": _sha256(packet / config["spec"]),
        "tau_packet_sha256": _tree_sha256(packet),
    }


def run(tau_binary: Path, gate: str) -> dict[str, object]:
    if gate not in GATES:
        raise ValueError(f"unknown gate: {gate}")
    tau_binary = tau_binary.resolve(strict=True)
    if not tau_binary.is_file():
        raise ValueError("Tau binary path is not a file")
    source_packet = TAU_ROOT / gate
    source_root = _tree_sha256(source_packet)

    with tempfile.TemporaryDirectory(prefix=f"compute-dividend-{gate}-tau-") as temp:
        run_root = Path(temp)
        packet = run_root / "packet"
        shutil.copytree(source_packet, packet)
        (packet / "outputs").mkdir()
        binary = run_root / "tau"
        shutil.copyfile(tau_binary, binary)
        os.chmod(binary, 0o500)
        binary_hash = _sha256(binary)
        report = _base_report(gate, source_packet, binary_hash)
        report["copied_tau_packet_sha256"] = _tree_sha256(packet)
        report["tau_version"] = ""
        report["version_returncode"] = None
        report["execution_attempted"] = False
        report["execution_returncode"] = None
        report["actual"] = []
        expected = (packet / "expected" / "allow.out").read_bytes()
        report["expected"] = expected.decode("ascii").splitlines()

        failures: list[str] = []
        if source_root != report["copied_tau_packet_sha256"]:
            failures.append("PACKET_COPY_HASH_MISMATCH")
        failures.extend(_packet_errors(gate, source_packet))
        if binary_hash != EXPECTED_TAU_BINARY_SHA256:
            failures.append("TAU_BINARY_SHA256_MISMATCH")
        if failures:
            report["failure_codes"] = failures
            report["passed"] = False
            report["error"] = "preflight rejected execution: " + ", ".join(failures)
            return report

        try:
            version = subprocess.run(
                [str(binary), "--version"], capture_output=True, timeout=15
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            report["failure_codes"] = ["TAU_VERSION_COMMAND_FAILED"]
            report["passed"] = False
            report["error"] = f"version command error: {type(error).__name__}"
            return report
        tau_version = (version.stdout + version.stderr).decode(
            "utf-8", errors="backslashreplace"
        ).strip()
        report["tau_version"] = tau_version
        report["version_returncode"] = version.returncode
        if version.returncode != 0 or tau_version != EXPECTED_TAU_VERSION:
            report["failure_codes"] = ["TAU_VERSION_MISMATCH"]
            report["passed"] = False
            report["error"] = tau_version[:MAX_DIAGNOSTIC_BYTES]
            return report

        spec = packet / GATES[gate]["spec"]
        report["execution_attempted"] = True
        try:
            execution = subprocess.run(
                [str(binary), "-X"],
                cwd=packet,
                capture_output=True,
                input=spec.read_bytes(),
                timeout=90,
            )
            report["execution_returncode"] = execution.returncode
            diagnostic = (execution.stdout + execution.stderr)[
                :MAX_DIAGNOSTIC_BYTES
            ].decode("utf-8", errors="backslashreplace")
        except (OSError, subprocess.TimeoutExpired) as error:
            report["failure_codes"] = ["TAU_EXECUTION_NO_RESULT"]
            report["passed"] = False
            report["error"] = f"execution error: {type(error).__name__}"
            return report

        output = packet / "outputs" / "allow.out"
        actual = output.read_bytes() if output.is_file() and not output.is_symlink() else None
        report["actual"] = actual.decode("ascii").splitlines() if actual else []
        if execution.returncode != 0:
            failures = ["TAU_EXECUTION_FAILED"]
        elif actual is None:
            failures = ["TAU_OUTPUT_MISSING"]
        elif len(actual.splitlines()) != len(expected.splitlines()):
            failures = ["TAU_OUTPUT_ROW_COUNT_MISMATCH"]
        elif actual != expected:
            failures = ["TAU_OUTPUT_NONCANONICAL_OR_MISMATCH"]
        else:
            failures = []
        report["failure_codes"] = failures
        report["passed"] = not failures
        report["error"] = "" if not failures else diagnostic
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau-bin", required=True, type=Path)
    parser.add_argument("--gate", choices=sorted(GATES), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run(args.tau_bin, args.gate)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    if args.json:
        print(rendered, end="")
    else:
        print("PASS" if report["passed"] else "FAIL")
        print(", ".join(report["failure_codes"]))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
