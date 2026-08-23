#!/usr/bin/env python3
"""Replay the V1, V1.1, V2, and flywheel packets on a current Tau source build.

This is a source-pinned local-candidate probe. It deliberately does not promote
the candidate to a reviewed binary or claim a Tau Net deployment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

try:
    from verification.current_tau_baseline import (
        CURRENT_TAU_PARSER_COMMIT,
        CURRENT_TAU_SNAPSHOT_DATE,
        CURRENT_TAU_SOURCE_COMMIT,
        CURRENT_TAU_VERSION,
    )
except ModuleNotFoundError:
    from current_tau_baseline import (
        CURRENT_TAU_PARSER_COMMIT,
        CURRENT_TAU_SNAPSHOT_DATE,
        CURRENT_TAU_SOURCE_COMMIT,
        CURRENT_TAU_VERSION,
    )

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class Packet:
    profile: str
    relative_root: str
    specification: str
    expected_output: str
    actual_output: str


PACKETS = (
    Packet(
        "v1_exclusion",
        "tau/v1",
        "exclusion_gate_v1.tau",
        "expected/v1_eligible.out",
        "outputs/v1_eligible.out",
    ),
    Packet(
        "v1_1_hyperdeflationary",
        "tau/v1_1",
        "hyperdeflation_gate_v1_1.tau",
        "expected/reference_eligible.out",
        "outputs/reference_eligible.out",
    ),
    Packet(
        "v2_finite_policy",
        "tau/v2",
        "alignment_policy_gate_v2.tau",
        "expected/allow.out",
        "outputs/allow.out",
    ),
    Packet(
        "intelligence_flywheel",
        "tau/intelligence_flywheel/gate",
        "intelligence_flywheel_gate.tau",
        "expected/allow.out",
        "outputs/allow.out",
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"packet contains symlink: {path}")
        if path.is_file():
            files.append(path)
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode()
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()


def _replay_packet(tau_binary: Path, packet: Packet) -> dict[str, object]:
    source = REPO_ROOT / packet.relative_root
    with tempfile.TemporaryDirectory(prefix=f"current-tau-{packet.profile}-") as raw:
        run_root = Path(raw) / "packet"
        shutil.copytree(source, run_root)
        (run_root / "outputs").mkdir()
        expected = (run_root / packet.expected_output).read_bytes()
        execution = subprocess.run(
            [str(tau_binary), "-X"],
            cwd=run_root,
            input=(run_root / packet.specification).read_bytes(),
            capture_output=True,
            timeout=180,
        )
        output = run_root / packet.actual_output
        actual = output.read_bytes() if output.is_file() and not output.is_symlink() else None
    semantic_match = execution.returncode == 0 and actual == expected
    return {
        "profile": packet.profile,
        "packet_root": packet.relative_root,
        "packet_sha256": _tree_sha256(source),
        "specification": packet.specification,
        "specification_sha256": _sha256(source / packet.specification),
        "expected_output_sha256": hashlib.sha256(expected).hexdigest(),
        "actual_output_sha256": hashlib.sha256(actual).hexdigest() if actual else "",
        "expected_rows": len(expected.splitlines()),
        "actual_rows": len(actual.splitlines()) if actual else 0,
        "accepted_rows": [
            index for index, value in enumerate(actual.splitlines()) if value == b"1"
        ] if actual else [],
        "execution_returncode": execution.returncode,
        "stdout_sha256": hashlib.sha256(execution.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(execution.stderr).hexdigest(),
        "semantic_match": semantic_match,
        "diagnostic": "" if semantic_match else
            (execution.stdout + execution.stderr)[:8192].decode(errors="backslashreplace"),
    }


def run(*, tau_binary: Path, tau_source: Path, build_command: str) -> dict[str, object]:
    tau_binary = tau_binary.resolve(strict=True)
    tau_source = tau_source.resolve(strict=True)
    source_commit = _git(tau_source, "rev-parse", "HEAD")
    source_status = _git(tau_source, "status", "--porcelain=v1")
    parser_commit = _git(tau_source / "external/parser", "rev-parse", "HEAD")
    submodules = _git(tau_source, "submodule", "status", "--recursive").splitlines()
    version = subprocess.run(
        [str(tau_binary), "--version"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    version_text = (version.stdout + version.stderr).strip()
    packet_results = [_replay_packet(tau_binary, packet) for packet in PACKETS]
    parser_pin_clean = (
        len(submodules) == 1
        and submodules[0].split()[0] == CURRENT_TAU_PARSER_COMMIT
        and submodules[0].split()[1] == "external/parser"
    )
    pins_match = (
        source_commit == CURRENT_TAU_SOURCE_COMMIT
        and parser_commit == CURRENT_TAU_PARSER_COMMIT
        and source_status == ""
        and parser_pin_clean
        and version.returncode == 0
        and version_text == CURRENT_TAU_VERSION
    )
    semantic_match = all(result["semantic_match"] for result in packet_results)
    return {
        "schema": "alignment-theorem-current-tau-multi-profile-probe-v2",
        "snapshot_date": CURRENT_TAU_SNAPSHOT_DATE,
        "status": "SUPPORTED_LOCAL_SOURCE_CANDIDATE" if pins_match and semantic_match else "FAILED",
        "semantic_replay_passed": pins_match and semantic_match,
        "checker_sha256": _sha256(Path(__file__)),
        "expected_tau_source_commit": CURRENT_TAU_SOURCE_COMMIT,
        "actual_tau_source_commit": source_commit,
        "expected_tau_parser_commit": CURRENT_TAU_PARSER_COMMIT,
        "actual_tau_parser_commit": parser_commit,
        "source_status_porcelain": source_status.splitlines(),
        "submodules": submodules,
        "pins_match": pins_match,
        "expected_tau_version": CURRENT_TAU_VERSION,
        "actual_tau_version": version_text,
        "tau_binary_sha256": _sha256(tau_binary),
        "declared_build_command": build_command,
        "packet_results": packet_results,
        "source_to_binary_status": "DECLARED_LOCAL_BUILD_RELATION_NOT_INDEPENDENTLY_ATTESTED",
        "execution_environment_status": "HOST_KERNEL_LIBRARIES_AND_SANDBOX_NOT_HERMETICALLY_ATTESTED",
        "authority_status": "LOCAL_REPLAY_ONLY_NO_TAU_NET_PUBLICATION_SETTLEMENT_OR_VALUE_AUTHORITY",
        "platform_observation": platform.platform(),
        "nonclaims": [
            "The local replay does not prove that public Tau Net nodes run this executable.",
            "The source pin does not independently attest how the executable was built.",
            "Boolean packet inputs are assumed propositions and are not authenticated by Tau.",
            "The packets do not apply settlement effects or establish production readiness.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau-bin", required=True, type=Path)
    parser.add_argument("--tau-source", required=True, type=Path)
    parser.add_argument("--build-command", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run(
        tau_binary=args.tau_bin,
        tau_source=args.tau_source,
        build_command=args.build_command,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    if args.json:
        print(rendered, end="")
    else:
        print(report["status"])
    return 0 if report["semantic_replay_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
