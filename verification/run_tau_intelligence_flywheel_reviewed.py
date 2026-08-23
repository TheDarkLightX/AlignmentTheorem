#!/usr/bin/env python3
"""Fail-closed replay of the flywheel packet on the reviewed Tau binary."""

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
    from verification.generate_tau_intelligence_flywheel_packet import (
        OUTPUT_NAME,
        SPEC_NAME,
        TAU_PACKET,
        generated_payloads,
    )
    from verification.run_tau_compute_dividend import (
        EXPECTED_TAU_BINARY_SHA256,
        EXPECTED_TAU_PARSER_COMMIT,
        EXPECTED_TAU_SOURCE_COMMIT,
        EXPECTED_TAU_VERSION,
        _tree_sha256,
    )
except ModuleNotFoundError:
    from generate_tau_intelligence_flywheel_packet import (
        OUTPUT_NAME,
        SPEC_NAME,
        TAU_PACKET,
        generated_payloads,
    )
    from run_tau_compute_dividend import (
        EXPECTED_TAU_BINARY_SHA256,
        EXPECTED_TAU_PARSER_COMMIT,
        EXPECTED_TAU_SOURCE_COMMIT,
        EXPECTED_TAU_VERSION,
        _tree_sha256,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(tau_binary: Path) -> dict[str, object]:
    tau_binary = tau_binary.resolve(strict=True)
    source_files = {
        path.relative_to(TAU_PACKET).as_posix()
        for path in TAU_PACKET.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    generated = generated_payloads()
    generation_ok = source_files == {SPEC_NAME, *generated} and all(
        (TAU_PACKET / relative).read_bytes() == payload
        for relative, payload in generated.items()
    )
    with tempfile.TemporaryDirectory(prefix="flywheel-reviewed-tau-") as raw:
        root = Path(raw)
        packet = root / "packet"
        shutil.copytree(TAU_PACKET, packet)
        (packet / "outputs").mkdir()
        binary = root / "tau"
        shutil.copyfile(tau_binary, binary)
        os.chmod(binary, 0o500)
        binary_hash = _sha256(binary)
        report: dict[str, object] = {
            "schema": "alignment-theorem-intelligence-flywheel-reviewed-tau-v1",
            "checker_sha256": _sha256(Path(__file__)),
            "expected_tau_source_commit": EXPECTED_TAU_SOURCE_COMMIT,
            "expected_tau_parser_commit": EXPECTED_TAU_PARSER_COMMIT,
            "expected_tau_version": EXPECTED_TAU_VERSION,
            "expected_tau_binary_sha256": EXPECTED_TAU_BINARY_SHA256,
            "tau_binary_sha256": binary_hash,
            "tau_packet_sha256": _tree_sha256(TAU_PACKET),
            "copied_tau_packet_sha256": _tree_sha256(packet),
            "tau_spec_sha256": _sha256(packet / SPEC_NAME),
            "source_to_binary_status": "DECLARED_SOURCE_PIN_NOT_ATTESTED_BY_REPLAY",
            "execution_environment_status": "HOST_ENVIRONMENT_NOT_HERMETICALLY_ATTESTED",
            "authority_status": "RESEARCH_REPLAY_ONLY_NO_TAU_NET_OR_VALUE_AUTHORITY",
            "execution_attempted": False,
        }
        failures = []
        if not generation_ok:
            failures.append("GENERATED_PACKET_MISMATCH")
        if report["tau_packet_sha256"] != report["copied_tau_packet_sha256"]:
            failures.append("PACKET_COPY_HASH_MISMATCH")
        if binary_hash != EXPECTED_TAU_BINARY_SHA256:
            failures.append("TAU_BINARY_SHA256_MISMATCH")
        if failures:
            report.update(passed=False, failure_codes=failures, error="preflight rejected execution")
            return report
        version = subprocess.run([str(binary), "--version"], capture_output=True, timeout=15)
        version_text = (version.stdout + version.stderr).decode(errors="backslashreplace").strip()
        report.update(tau_version=version_text, version_returncode=version.returncode)
        if version.returncode != 0 or version_text != EXPECTED_TAU_VERSION:
            report.update(passed=False, failure_codes=["TAU_VERSION_MISMATCH"], error=version_text)
            return report
        report["execution_attempted"] = True
        execution = subprocess.run(
            [str(binary), "-X"],
            cwd=packet,
            input=(packet / SPEC_NAME).read_bytes(),
            capture_output=True,
            timeout=120,
        )
        expected = (packet / "expected" / OUTPUT_NAME).read_bytes()
        output = packet / "outputs" / OUTPUT_NAME
        actual = output.read_bytes() if output.is_file() and not output.is_symlink() else None
        semantic_match = execution.returncode == 0 and actual == expected
        report.update(
            execution_returncode=execution.returncode,
            expected_output_sha256=hashlib.sha256(expected).hexdigest(),
            actual_output_sha256=hashlib.sha256(actual).hexdigest() if actual else "",
            expected_rows=len(expected.splitlines()),
            actual_rows=len(actual.splitlines()) if actual else 0,
            semantic_match=semantic_match,
            passed=semantic_match,
            failure_codes=[] if semantic_match else ["TAU_OUTPUT_OR_EXECUTION_MISMATCH"],
            error="" if semantic_match else (execution.stdout + execution.stderr)[:8192].decode(errors="backslashreplace"),
        )
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau-bin", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run(args.tau_bin)
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
