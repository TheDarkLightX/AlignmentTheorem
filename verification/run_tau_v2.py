#!/usr/bin/env python3
"""Run and grade the Version 2 policy on an exact Tau binary."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TAU_PACKET = REPO_ROOT / "tau" / "v2"
EXPECTED_TAU_VERSION = "Tau Language Framework version 0.7.0-alpha (fd137e8)"
EXPECTED_TAU_BINARY_SHA256 = (
    "c49267404e07a1f540c941b618e786710f70001eecbd05bb7c6d8eec0c5645fa"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_sha256(root: Path) -> str:
    """Hash relative names, lengths, and bytes for the complete Tau packet."""

    digest = hashlib.sha256()
    candidates = []
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


def _normalized_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def run(tau_binary: Path) -> dict[str, object]:
    tau_binary = tau_binary.resolve(strict=True)
    if not tau_binary.is_file():
        raise ValueError("Tau binary path is not a file")

    with tempfile.TemporaryDirectory(prefix="alignment-v2-tau-") as temp_dir:
        run_dir = Path(temp_dir)
        shutil.copytree(TAU_PACKET / "inputs", run_dir / "inputs")
        (run_dir / "outputs").mkdir()
        spec = run_dir / "alignment_policy_gate_v2.tau"
        shutil.copy2(TAU_PACKET / spec.name, spec)

        version = subprocess.run(
            [str(tau_binary), "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        execution = subprocess.run(
            [str(tau_binary), "-X"],
            cwd=run_dir,
            check=False,
            capture_output=True,
            text=True,
            input=spec.read_text(),
            timeout=60,
        )
        actual_path = run_dir / "outputs" / "allow.out"
        actual = _normalized_lines(actual_path) if actual_path.exists() else []
        expected = _normalized_lines(TAU_PACKET / "expected" / "allow.out")
        tau_version = (version.stdout + version.stderr).strip()
        tau_binary_sha256 = _sha256(tau_binary)
        passed = (
            execution.returncode == 0
            and actual == expected
            and tau_version == EXPECTED_TAU_VERSION
            and tau_binary_sha256 == EXPECTED_TAU_BINARY_SHA256
        )

        return {
            "schema": "alignment-theorem-v2-tau-run-v1",
            "checker_sha256": _sha256(Path(__file__)),
            "generator_sha256": _sha256(
                REPO_ROOT / "verification" / "generate_tau_v2_packet.py"
            ),
            "tau_version": tau_version,
            "tau_binary_sha256": tau_binary_sha256,
            "tau_spec_sha256": _sha256(TAU_PACKET / spec.name),
            "tau_packet_sha256": _tree_sha256(TAU_PACKET),
            "returncode": execution.returncode,
            "actual": actual,
            "expected": expected,
            "passed": passed,
            "error": "" if passed else execution.stdout + execution.stderr,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau-bin", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = run(args.tau_bin)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    if args.json:
        print(rendered, end="")
    else:
        print(f"Tau: {report['tau_version']}")
        actual = report["actual"]
        expected = report["expected"]
        print(f"Rows: {len(actual)} actual / {len(expected)} expected")
        print(f"Accepted rows: {[index for index, value in enumerate(actual) if value == '1']}")
        print("PASS" if report["passed"] else "FAIL")
        if not report["passed"]:
            print(report["error"])
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
