#!/usr/bin/env python3
"""Run and fail-closed grade the Version 1.1 packet on the pinned Tau binary."""

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
    from verification.generate_tau_v1_1_packet import OBLIGATIONS, rows
except ModuleNotFoundError:  # Direct script execution from verification/.
    from generate_tau_v1_1_packet import OBLIGATIONS, rows

REPO_ROOT = Path(__file__).resolve().parents[1]
TAU_PACKET = REPO_ROOT / "tau" / "v1_1"
SPEC_NAME = "hyperdeflation_gate_v1_1.tau"
OUTPUT_NAME = "reference_eligible.out"

EXPECTED_TAU_SOURCE_COMMIT = "fd137e860b60083b36f9159ec8090cb1a3c3cb5a"
EXPECTED_TAU_PARSER_COMMIT = "5dd036358e194e55a08fd2ec255441bedfe83765"
EXPECTED_TAU_VERSION = "Tau Language Framework version 0.7.0-alpha (fd137e8)"
EXPECTED_TAU_BINARY_SHA256 = (
    "c49267404e07a1f540c941b618e786710f70001eecbd05bb7c6d8eec0c5645fa"
)
AUTHORITY_STATUS = "INTERPRETER_REPLAY_ONLY_NO_PUBLICATION_OR_VALUE_AUTHORITY"
SOURCE_PROVENANCE_STATUS = (
    "DECLARED_SOURCE_PIN_NOT_REBUILT_OR_ATTESTED_BY_THIS_RUNNER"
)
EXECUTION_ENVIRONMENT_STATUS = "HOST_ENVIRONMENT_NOT_HERMETICALLY_PINNED"
MAX_DIAGNOSTIC_BYTES = 8_192


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_sha256(root: Path) -> str:
    """Hash exact relative names, lengths, and bytes for a closed packet tree."""

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


def _generated_payloads() -> dict[str, bytes]:
    table = rows()
    payloads = {
        f"inputs/{obligation}.in": "".join(
            "1\n" if row[column] else "0\n" for row in table
        ).encode("ascii")
        for column, obligation in enumerate(OBLIGATIONS)
    }
    payloads[f"expected/{OUTPUT_NAME}"] = "".join(
        "1\n" if all(row) else "0\n" for row in table
    ).encode("ascii")
    return payloads


def _packet_generation_errors(packet: Path) -> tuple[str, ...]:
    """Check that checked-in vectors are the exact output of the generator."""

    generated = _generated_payloads()
    expected_files = {SPEC_NAME, *generated}
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


def _line_count(payload: bytes) -> int:
    return len(payload.splitlines())


def _display_lines(payload: bytes | None) -> list[str]:
    if payload is None:
        return []
    return payload.decode("utf-8", errors="backslashreplace").splitlines()


def _grade(
    *,
    source_packet_sha256: str,
    copied_packet_sha256: str,
    packet_generation_errors: tuple[str, ...],
    tau_binary_sha256: str,
    version_returncode: int | None,
    tau_version: str,
    execution_returncode: int | None,
    actual_output: bytes | None,
    expected_output: bytes,
) -> tuple[str, ...]:
    """Return the first failed trust layer so downstream failures cannot mask it."""

    preflight_errors = _preflight_errors(
        source_packet_sha256=source_packet_sha256,
        copied_packet_sha256=copied_packet_sha256,
        packet_generation_errors=packet_generation_errors,
        tau_binary_sha256=tau_binary_sha256,
    )
    if preflight_errors:
        return preflight_errors
    if version_returncode != 0:
        return ("TAU_VERSION_COMMAND_FAILED",)
    if tau_version != EXPECTED_TAU_VERSION:
        return ("TAU_VERSION_MISMATCH",)
    if execution_returncode is None:
        return ("TAU_EXECUTION_NO_RESULT",)
    if execution_returncode != 0:
        return ("TAU_EXECUTION_FAILED",)
    if actual_output is None:
        return ("TAU_OUTPUT_MISSING",)
    if _line_count(actual_output) != _line_count(expected_output):
        return ("TAU_OUTPUT_ROW_COUNT_MISMATCH",)
    if actual_output != expected_output:
        return ("TAU_OUTPUT_NONCANONICAL_OR_MISMATCH",)
    return ()


def _preflight_errors(
    *,
    source_packet_sha256: str,
    copied_packet_sha256: str,
    packet_generation_errors: tuple[str, ...],
    tau_binary_sha256: str,
) -> tuple[str, ...]:
    """Reject mutable packet copies or unreviewed binaries before execution."""

    if source_packet_sha256 != copied_packet_sha256:
        return ("PACKET_COPY_HASH_MISMATCH",)
    if packet_generation_errors:
        return packet_generation_errors
    if tau_binary_sha256 != EXPECTED_TAU_BINARY_SHA256:
        return ("TAU_BINARY_SHA256_MISMATCH",)
    return ()


def _diagnostic(*payloads: bytes) -> str:
    combined = b"".join(payloads)[:MAX_DIAGNOSTIC_BYTES]
    return combined.decode("utf-8", errors="backslashreplace")


def _report(
    *,
    source_packet_sha256: str,
    copied_packet_sha256: str,
    packet_generation_errors: tuple[str, ...],
    tau_binary_sha256: str,
    version_returncode: int | None,
    tau_version: str,
    execution_returncode: int | None,
    execution_attempted: bool,
    actual_output: bytes | None,
    expected_output: bytes,
    tau_spec_sha256: str,
    diagnostic: str,
) -> dict[str, object]:
    failure_codes = _grade(
        source_packet_sha256=source_packet_sha256,
        copied_packet_sha256=copied_packet_sha256,
        packet_generation_errors=packet_generation_errors,
        tau_binary_sha256=tau_binary_sha256,
        version_returncode=version_returncode,
        tau_version=tau_version,
        execution_returncode=execution_returncode,
        actual_output=actual_output,
        expected_output=expected_output,
    )
    passed = not failure_codes
    return {
        "schema": "alignment-theorem-v1-1-tau-run-v2",
        "checker_sha256": _sha256(Path(__file__)),
        "generator_sha256": _sha256(
            REPO_ROOT / "verification" / "generate_tau_v1_1_packet.py"
        ),
        "expected_tau_source_commit": EXPECTED_TAU_SOURCE_COMMIT,
        "expected_tau_parser_commit": EXPECTED_TAU_PARSER_COMMIT,
        "source_provenance_status": SOURCE_PROVENANCE_STATUS,
        "execution_environment_status": EXECUTION_ENVIRONMENT_STATUS,
        "tau_version": tau_version,
        "tau_binary_sha256": tau_binary_sha256,
        "tau_spec_sha256": tau_spec_sha256,
        "tau_packet_sha256": source_packet_sha256,
        "copied_tau_packet_sha256": copied_packet_sha256,
        "version_returncode": version_returncode,
        "execution_returncode": execution_returncode,
        "execution_attempted": execution_attempted,
        "actual_output_sha256": (
            hashlib.sha256(actual_output).hexdigest()
            if actual_output is not None
            else ""
        ),
        "expected_output_sha256": hashlib.sha256(expected_output).hexdigest(),
        "actual": _display_lines(actual_output),
        "expected": _display_lines(expected_output),
        "failure_codes": list(failure_codes),
        "authority_status": AUTHORITY_STATUS,
        "passed": passed,
        "error": "" if passed else diagnostic,
    }


def run(tau_binary: Path) -> dict[str, object]:
    """Execute a stable snapshot only after its bytes and packet pass preflight."""

    tau_binary = tau_binary.resolve(strict=True)
    if not tau_binary.is_file():
        raise ValueError("Tau binary path is not a file")

    source_packet_sha256 = _tree_sha256(TAU_PACKET)
    generation_errors = _packet_generation_errors(TAU_PACKET)
    expected_output = (TAU_PACKET / "expected" / OUTPUT_NAME).read_bytes()

    with tempfile.TemporaryDirectory(prefix="alignment-v1-1-tau-") as temp_dir:
        run_root = Path(temp_dir)
        packet = run_root / "packet"
        shutil.copytree(TAU_PACKET, packet)
        copied_packet_sha256 = _tree_sha256(packet)
        tau_spec_sha256 = _sha256(packet / SPEC_NAME)
        (packet / "outputs").mkdir()

        binary_snapshot = run_root / "tau"
        shutil.copyfile(tau_binary, binary_snapshot)
        os.chmod(binary_snapshot, 0o500)
        tau_binary_sha256 = _sha256(binary_snapshot)

        preflight = _preflight_errors(
            source_packet_sha256=source_packet_sha256,
            copied_packet_sha256=copied_packet_sha256,
            packet_generation_errors=generation_errors,
            tau_binary_sha256=tau_binary_sha256,
        )
        if preflight:
            return _report(
                source_packet_sha256=source_packet_sha256,
                copied_packet_sha256=copied_packet_sha256,
                packet_generation_errors=generation_errors,
                tau_binary_sha256=tau_binary_sha256,
                version_returncode=None,
                tau_version="",
                execution_returncode=None,
                execution_attempted=False,
                actual_output=None,
                expected_output=expected_output,
                tau_spec_sha256=tau_spec_sha256,
                diagnostic="preflight rejected execution: " + ", ".join(preflight),
            )

        try:
            version = subprocess.run(
                [str(binary_snapshot), "--version"],
                check=False,
                capture_output=True,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            return _report(
                source_packet_sha256=source_packet_sha256,
                copied_packet_sha256=copied_packet_sha256,
                packet_generation_errors=generation_errors,
                tau_binary_sha256=tau_binary_sha256,
                version_returncode=None,
                tau_version="",
                execution_returncode=None,
                execution_attempted=False,
                actual_output=None,
                expected_output=expected_output,
                tau_spec_sha256=tau_spec_sha256,
                diagnostic=f"version command error: {type(error).__name__}",
            )

        tau_version = (version.stdout + version.stderr).decode(
            "utf-8", errors="backslashreplace"
        ).strip()
        if version.returncode != 0 or tau_version != EXPECTED_TAU_VERSION:
            return _report(
                source_packet_sha256=source_packet_sha256,
                copied_packet_sha256=copied_packet_sha256,
                packet_generation_errors=generation_errors,
                tau_binary_sha256=tau_binary_sha256,
                version_returncode=version.returncode,
                tau_version=tau_version,
                execution_returncode=None,
                execution_attempted=False,
                actual_output=None,
                expected_output=expected_output,
                tau_spec_sha256=tau_spec_sha256,
                diagnostic=_diagnostic(version.stdout, version.stderr),
            )

        spec = packet / SPEC_NAME
        try:
            execution = subprocess.run(
                [str(binary_snapshot), "-X"],
                cwd=packet,
                check=False,
                capture_output=True,
                input=spec.read_bytes(),
                timeout=60,
            )
            execution_returncode: int | None = execution.returncode
            diagnostic = _diagnostic(execution.stdout, execution.stderr)
        except (OSError, subprocess.TimeoutExpired) as error:
            execution_returncode = None
            diagnostic = f"execution error: {type(error).__name__}"

        actual_path = packet / "outputs" / OUTPUT_NAME
        actual_output = (
            actual_path.read_bytes()
            if actual_path.is_file() and not actual_path.is_symlink()
            else None
        )
        return _report(
            source_packet_sha256=source_packet_sha256,
            copied_packet_sha256=copied_packet_sha256,
            packet_generation_errors=generation_errors,
            tau_binary_sha256=tau_binary_sha256,
            version_returncode=version.returncode,
            tau_version=tau_version,
            execution_returncode=execution_returncode,
            execution_attempted=True,
            actual_output=actual_output,
            expected_output=expected_output,
            tau_spec_sha256=tau_spec_sha256,
            diagnostic=diagnostic,
        )


def _write_passed_receipt(output: Path, rendered: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=output.parent,
        prefix=f".{output.name}.",
        delete=False,
    ) as temporary:
        temporary.write(rendered)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau-bin", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = run(args.tau_bin)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None and report["passed"] is True:
        _write_passed_receipt(args.output, rendered)
    if args.json:
        print(rendered, end="")
    else:
        print(f"Tau: {report['tau_version'] or 'not executed'}")
        print(f"Rows: {len(report['actual'])} actual / {len(report['expected'])} expected")
        print("PASS" if report["passed"] else "FAIL")
        if not report["passed"]:
            print(", ".join(report["failure_codes"]))
            if report["error"]:
                print(report["error"])
            if args.output is not None:
                print("No receipt written because replay did not pass.")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
