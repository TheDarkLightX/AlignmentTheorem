#!/usr/bin/env python3
"""Capture non-authoritative build metadata for a V1.1 Tau candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

try:
    from verification.run_tau_v1_1 import (
        EXPECTED_TAU_BINARY_SHA256,
        EXPECTED_TAU_PARSER_COMMIT,
        EXPECTED_TAU_SOURCE_COMMIT,
        EXPECTED_TAU_VERSION,
    )
except ModuleNotFoundError:  # Direct script execution from verification/.
    from run_tau_v1_1 import (
        EXPECTED_TAU_BINARY_SHA256,
        EXPECTED_TAU_PARSER_COMMIT,
        EXPECTED_TAU_SOURCE_COMMIT,
        EXPECTED_TAU_VERSION,
    )

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BUILD_COMMAND = "TAU_BUILD_JOBS=1 ./dev release"
EXPECTED_PARSER_PATH = "external/parser"
AUTHORITY_STATUS = "CANDIDATE_METADATA_ONLY_NO_REPLAY_PUBLICATION_OR_VALUE_AUTHORITY"
MAX_TOOL_OUTPUT_CHARS = 4_096
IMMUTABLE_IMAGE_PATTERN = re.compile(r"^[^\s]+@sha256:[0-9a-f]{64}$")

CommandRunner = Callable[
    [tuple[str, ...], Path | None],
    subprocess.CompletedProcess[str],
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: dict[str, object]) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _run_command(
    args: tuple[str, ...],
    cwd: Path | None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )


def _bounded_output(
    completed: subprocess.CompletedProcess[str],
    *,
    preserve_leading: bool,
) -> str:
    combined = completed.stdout + completed.stderr
    normalized = combined.rstrip() if preserve_leading else combined.strip()
    return normalized[:MAX_TOOL_OUTPUT_CHARS]


def _parse_submodules(payload: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for raw_line in payload.splitlines():
        if not raw_line:
            continue
        marker = raw_line[0]
        fields = raw_line[1:].split(maxsplit=2)
        if len(fields) < 2:
            entries.append({"marker": marker, "commit": "", "path": ""})
            continue
        entries.append(
            {
                "marker": marker,
                "commit": fields[0],
                "path": fields[1],
            }
        )
    return entries


def _is_immutable_image_reference(value: str) -> bool:
    return bool(
        IMMUTABLE_IMAGE_PATTERN.fullmatch(value)
        and value.count("@") == 1
        and "://" not in value
        and "?" not in value
        and "#" not in value
    )


def capture(
    *,
    tau_source: Path,
    tau_binary: Path,
    runpod_image: str,
    build_command: str,
    command_runner: CommandRunner = _run_command,
) -> dict[str, object]:
    """Capture stable candidate facts without running Tau or granting authority."""

    tau_source = tau_source.resolve(strict=True)
    tau_binary = tau_binary.resolve(strict=True)
    if not tau_source.is_dir():
        raise ValueError("Tau source path is not a directory")
    if not tau_binary.is_file():
        raise ValueError("Tau binary path is not a file")

    capture_errors: list[str] = []
    command_succeeded: dict[str, bool] = {}

    def collect(
        args: tuple[str, ...],
        cwd: Path | None = None,
        *,
        preserve_leading: bool = False,
    ) -> str:
        label = " ".join(args)
        try:
            completed = command_runner(args, cwd)
        except (OSError, subprocess.TimeoutExpired):
            command_succeeded[label] = False
            capture_errors.append(f"COMMAND_ERROR:{label}")
            return ""
        if completed.returncode != 0:
            command_succeeded[label] = False
            capture_errors.append(f"COMMAND_FAILED:{label}")
            return ""
        command_succeeded[label] = True
        return _bounded_output(completed, preserve_leading=preserve_leading)

    source_head = collect(("git", "rev-parse", "HEAD"), tau_source)
    source_status = collect(
        ("git", "status", "--porcelain=v1", "--untracked-files=all"),
        tau_source,
        preserve_leading=True,
    )
    submodule_output = collect(
        ("git", "submodule", "status", "--recursive"),
        tau_source,
        preserve_leading=True,
    )
    submodules = _parse_submodules(submodule_output)
    parser = next(
        (entry for entry in submodules if entry["path"] == EXPECTED_PARSER_PATH),
        None,
    )

    tool_versions = {
        "cmake": collect(("cmake", "--version")),
        "cxx": collect(("c++", "--version")),
        "ldd": collect(("ldd", "--version")),
    }
    platform = {
        "system": collect(("uname", "-s")),
        "kernel_release": collect(("uname", "-r")),
        "machine": collect(("uname", "-m")),
    }

    source_head_captured = command_succeeded["git rev-parse HEAD"]
    source_status_captured = command_succeeded[
        "git status --porcelain=v1 --untracked-files=all"
    ]
    submodule_status_captured = command_succeeded[
        "git submodule status --recursive"
    ]
    source_worktree_clean = source_status_captured and source_status == ""
    source_pin_matches = (
        source_head_captured and source_head == EXPECTED_TAU_SOURCE_COMMIT
    )
    parser_pin_matches = bool(
        submodule_status_captured
        and parser is not None
        and parser["marker"] == " "
        and parser["commit"] == EXPECTED_TAU_PARSER_COMMIT
    )
    runpod_image_immutable = _is_immutable_image_reference(runpod_image)
    build_command_matches = build_command == EXPECTED_BUILD_COMMAND
    binary_sha256 = _sha256(tau_binary)
    accepted_binary_hash_match = binary_sha256 == EXPECTED_TAU_BINARY_SHA256

    review_findings: list[str] = []
    if source_status_captured and not source_worktree_clean:
        review_findings.append("SOURCE_WORKTREE_DIRTY")
    if source_head_captured and not source_pin_matches:
        review_findings.append("SOURCE_PIN_MISMATCH")
    if submodule_status_captured and not parser_pin_matches:
        review_findings.append("PARSER_PIN_MISMATCH")
    if not runpod_image_immutable:
        review_findings.append("RUNPOD_IMAGE_NOT_IMMUTABLE")
    if not build_command_matches:
        review_findings.append("BUILD_COMMAND_MISMATCH")

    capture_complete = not capture_errors
    candidate_ready_for_pin_review = capture_complete and not review_findings
    report: dict[str, object] = {
        "schema": "alignment-theorem-v1-1-tau-candidate-manifest-v1",
        "checker_sha256": _sha256(Path(__file__)),
        "replay_checker_sha256": _sha256(
            REPO_ROOT / "verification" / "run_tau_v1_1.py"
        ),
        "authority_status": AUTHORITY_STATUS,
        "capture_complete": capture_complete,
        "candidate_ready_for_pin_review": candidate_ready_for_pin_review,
        "promotion_eligible": False,
        "replay_executed": False,
        "source_to_binary_attested": False,
        "execution_environment_hermetic": False,
        "runpod_image_attested": False,
        "build_execution_attested": False,
        "expected_tau_source_commit": EXPECTED_TAU_SOURCE_COMMIT,
        "observed_tau_source_commit": source_head,
        "source_head_captured": source_head_captured,
        "source_pin_matches": source_pin_matches,
        "source_status_captured": source_status_captured,
        "source_worktree_clean": source_worktree_clean,
        "source_status_sha256": hashlib.sha256(source_status.encode()).hexdigest(),
        "expected_tau_parser_commit": EXPECTED_TAU_PARSER_COMMIT,
        "expected_tau_parser_path": EXPECTED_PARSER_PATH,
        "submodule_status_captured": submodule_status_captured,
        "parser_pin_matches": parser_pin_matches,
        "submodules": submodules,
        "expected_tau_version": EXPECTED_TAU_VERSION,
        "expected_tau_binary_sha256": EXPECTED_TAU_BINARY_SHA256,
        "candidate_tau_binary_sha256": binary_sha256,
        "accepted_binary_hash_match": accepted_binary_hash_match,
        "binary_disposition": (
            "ACCEPTED_BINARY_HASH_MATCH"
            if accepted_binary_hash_match
            else "NEW_BINARY_PIN_REVIEW_REQUIRED"
        ),
        "declared_runpod_image": runpod_image if runpod_image_immutable else "",
        "declared_runpod_image_sha256": (
            hashlib.sha256(runpod_image.encode()).hexdigest()
            if runpod_image_immutable
            else ""
        ),
        "declared_runpod_image_immutable": runpod_image_immutable,
        "documented_build_command": EXPECTED_BUILD_COMMAND,
        "declared_build_command_sha256": (
            hashlib.sha256(build_command.encode()).hexdigest()
            if build_command_matches
            else ""
        ),
        "declared_build_command_matches_documented": build_command_matches,
        "tool_versions": tool_versions,
        "platform": platform,
        "capture_errors": capture_errors,
        "review_findings": review_findings,
    }
    report["candidate_manifest_sha256"] = _canonical_sha256(report)
    return report


def _write_json(output: Path, rendered: str) -> None:
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
    parser.add_argument("--tau-source", required=True, type=Path)
    parser.add_argument("--tau-bin", required=True, type=Path)
    parser.add_argument("--runpod-image", required=True)
    parser.add_argument("--build-command", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = capture(
        tau_source=args.tau_source,
        tau_binary=args.tau_bin,
        runpod_image=args.runpod_image,
        build_command=args.build_command,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        _write_json(args.output, rendered)
    if args.json:
        print(rendered, end="")
    else:
        print("CAPTURE COMPLETE" if report["capture_complete"] else "CAPTURE FAILED")
        print(f"Candidate: {report['candidate_manifest_sha256']}")
        print(f"Binary disposition: {report['binary_disposition']}")
        if report["capture_errors"]:
            print("Capture errors: " + ", ".join(report["capture_errors"]))
        if report["review_findings"]:
            print("Review findings: " + ", ".join(report["review_findings"]))
        print("Replay executed: false; promotion eligible: false")
    return 0 if report["capture_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
