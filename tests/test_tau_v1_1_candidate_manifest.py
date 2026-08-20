from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from verification.capture_tau_v1_1_candidate import (
    EXPECTED_BUILD_COMMAND,
    EXPECTED_TAU_PARSER_COMMIT,
    EXPECTED_TAU_SOURCE_COMMIT,
    capture,
)

IMMUTABLE_IMAGE = "docker.io/example/tau@sha256:" + "a" * 64
ROOT = Path(__file__).resolve().parents[1]


def command_result(
    args: tuple[str, ...],
    stdout: str,
    *,
    returncode: int = 0,
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args, returncode, stdout, "")


def successful_runner(
    args: tuple[str, ...],
    cwd: Path | None,
) -> subprocess.CompletedProcess[str]:
    del cwd
    outputs = {
        ("git", "rev-parse", "HEAD"): EXPECTED_TAU_SOURCE_COMMIT + "\n",
        ("git", "status", "--porcelain=v1", "--untracked-files=all"): "",
        ("git", "submodule", "status", "--recursive"): (
            f" {EXPECTED_TAU_PARSER_COMMIT} external/parser (pinned)\n"
        ),
        ("cmake", "--version"): "cmake version 3.30.0\n",
        ("c++", "--version"): "Example C++ 14.2.0\n",
        ("ldd", "--version"): "ldd 2.40\n",
        ("uname", "-s"): "Linux\n",
        ("uname", "-r"): "6.8.0\n",
        ("uname", "-m"): "x86_64\n",
    }
    return command_result(args, outputs[args])


class TauV1_1CandidateManifestTests(unittest.TestCase):
    def test_complete_capture_remains_non_authoritative_and_path_free(self) -> None:
        with tempfile.TemporaryDirectory(prefix="tau-candidate-") as temp:
            root = Path(temp)
            source = root / "tau-lang"
            source.mkdir()
            binary = root / "tau"
            binary.write_bytes(b"candidate binary")

            # Act
            report = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image=IMMUTABLE_IMAGE,
                build_command=EXPECTED_BUILD_COMMAND,
                command_runner=successful_runner,
            )
            rendered = json.dumps(report, sort_keys=True)

            # Assert
            self.assertTrue(report["capture_complete"])
            self.assertTrue(report["candidate_ready_for_pin_review"])
            self.assertFalse(report["accepted_binary_hash_match"])
            self.assertFalse(report["promotion_eligible"])
            self.assertFalse(report["replay_executed"])
            self.assertFalse(report["runpod_image_attested"])
            self.assertFalse(report["build_execution_attested"])
            self.assertEqual(report["declared_runpod_image"], IMMUTABLE_IMAGE)
            self.assertEqual(
                report["declared_build_command_sha256"],
                hashlib.sha256(EXPECTED_BUILD_COMMAND.encode()).hexdigest(),
            )
            self.assertNotIn("runpod_image", report)
            self.assertNotIn("observed_build_command", report)
            self.assertNotIn("declared_build_command", report)
            self.assertNotIn("passed", report)
            self.assertEqual(
                report["checker_sha256"],
                hashlib.sha256(
                    (ROOT / "verification" / "capture_tau_v1_1_candidate.py").read_bytes()
                ).hexdigest(),
            )
            self.assertEqual(
                report["replay_checker_sha256"],
                hashlib.sha256(
                    (ROOT / "verification" / "run_tau_v1_1.py").read_bytes()
                ).hexdigest(),
            )
            self.assertNotIn(str(root), rendered)
            self.assertEqual(report["capture_errors"], [])
            self.assertEqual(report["review_findings"], [])

    def test_dirty_or_mismatched_parser_blocks_pin_review(self) -> None:
        def dirty_runner(
            args: tuple[str, ...],
            cwd: Path | None,
        ) -> subprocess.CompletedProcess[str]:
            if args == ("git", "status", "--porcelain=v1", "--untracked-files=all"):
                return command_result(args, " M src/main.cpp\n")
            if args == ("git", "submodule", "status", "--recursive"):
                return command_result(
                    args,
                    f"+{EXPECTED_TAU_PARSER_COMMIT} external/parser (modified)\n",
                )
            return successful_runner(args, cwd)

        with tempfile.TemporaryDirectory(prefix="tau-dirty-") as temp:
            root = Path(temp)
            source = root / "tau-lang"
            source.mkdir()
            binary = root / "tau"
            binary.write_bytes(b"candidate binary")

            # Act
            report = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image=IMMUTABLE_IMAGE,
                build_command=EXPECTED_BUILD_COMMAND,
                command_runner=dirty_runner,
            )

            # Assert
            self.assertTrue(report["capture_complete"])
            self.assertFalse(report["source_worktree_clean"])
            self.assertFalse(report["parser_pin_matches"])
            self.assertFalse(report["candidate_ready_for_pin_review"])
            self.assertIn("SOURCE_WORKTREE_DIRTY", report["review_findings"])
            self.assertIn("PARSER_PIN_MISMATCH", report["review_findings"])

    def test_mutable_image_and_changed_build_command_are_visible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="tau-image-") as temp:
            root = Path(temp)
            source = root / "tau-lang"
            source.mkdir()
            binary = root / "tau"
            binary.write_bytes(b"candidate binary")

            # Act
            report = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image="docker.io/example/tau:latest",
                build_command="./dev release",
                command_runner=successful_runner,
            )

            # Assert
            self.assertTrue(report["capture_complete"])
            self.assertFalse(report["declared_runpod_image_immutable"])
            self.assertFalse(report["declared_build_command_matches_documented"])
            self.assertEqual(report["declared_build_command_sha256"], "")
            self.assertFalse(report["candidate_ready_for_pin_review"])
            self.assertIn("RUNPOD_IMAGE_NOT_IMMUTABLE", report["review_findings"])
            self.assertIn("BUILD_COMMAND_MISMATCH", report["review_findings"])

    def test_image_reference_cannot_embed_url_credentials(self) -> None:
        with tempfile.TemporaryDirectory(prefix="tau-image-secret-") as temp:
            root = Path(temp)
            source = root / "tau-lang"
            source.mkdir()
            binary = root / "tau"
            binary.write_bytes(b"candidate binary")

            # Act
            report = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image=(
                    "https://user:secret@example.invalid/tau@sha256:" + "a" * 64
                ),
                build_command=EXPECTED_BUILD_COMMAND,
                command_runner=successful_runner,
            )

            # Assert
            self.assertFalse(report["declared_runpod_image_immutable"])
            self.assertEqual(report["declared_runpod_image"], "")
            self.assertEqual(report["declared_runpod_image_sha256"], "")
            self.assertNotIn("secret", json.dumps(report, sort_keys=True))
            self.assertFalse(report["candidate_ready_for_pin_review"])
            self.assertIn("RUNPOD_IMAGE_NOT_IMMUTABLE", report["review_findings"])

    def test_source_head_mismatch_is_a_review_finding(self) -> None:
        def mismatched_runner(
            args: tuple[str, ...],
            cwd: Path | None,
        ) -> subprocess.CompletedProcess[str]:
            if args == ("git", "rev-parse", "HEAD"):
                return command_result(args, "0" * 40 + "\n")
            return successful_runner(args, cwd)

        with tempfile.TemporaryDirectory(prefix="tau-source-") as temp:
            root = Path(temp)
            source = root / "tau-lang"
            source.mkdir()
            binary = root / "tau"
            binary.write_bytes(b"candidate binary")

            # Act
            report = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image=IMMUTABLE_IMAGE,
                build_command=EXPECTED_BUILD_COMMAND,
                command_runner=mismatched_runner,
            )

            # Assert
            self.assertFalse(report["source_pin_matches"])
            self.assertFalse(report["candidate_ready_for_pin_review"])
            self.assertIn("SOURCE_PIN_MISMATCH", report["review_findings"])

    def test_command_failure_is_capture_failure_without_promotion(self) -> None:
        def failed_runner(
            args: tuple[str, ...],
            cwd: Path | None,
        ) -> subprocess.CompletedProcess[str]:
            if args == ("cmake", "--version"):
                return command_result(args, "", returncode=127)
            return successful_runner(args, cwd)

        with tempfile.TemporaryDirectory(prefix="tau-command-") as temp:
            root = Path(temp)
            source = root / "tau-lang"
            source.mkdir()
            binary = root / "tau"
            binary.write_bytes(b"candidate binary")

            # Act
            report = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image=IMMUTABLE_IMAGE,
                build_command=EXPECTED_BUILD_COMMAND,
                command_runner=failed_runner,
            )

            # Assert
            self.assertFalse(report["capture_complete"])
            self.assertFalse(report["candidate_ready_for_pin_review"])
            self.assertFalse(report["promotion_eligible"])
            self.assertIn("COMMAND_FAILED:cmake --version", report["capture_errors"])

    def test_failed_status_capture_cannot_appear_as_a_clean_worktree(self) -> None:
        def failed_status_runner(
            args: tuple[str, ...],
            cwd: Path | None,
        ) -> subprocess.CompletedProcess[str]:
            if args == ("git", "status", "--porcelain=v1", "--untracked-files=all"):
                return command_result(args, "", returncode=128)
            return successful_runner(args, cwd)

        with tempfile.TemporaryDirectory(prefix="tau-status-") as temp:
            root = Path(temp)
            source = root / "tau-lang"
            source.mkdir()
            binary = root / "tau"
            binary.write_bytes(b"candidate binary")

            # Act
            report = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image=IMMUTABLE_IMAGE,
                build_command=EXPECTED_BUILD_COMMAND,
                command_runner=failed_status_runner,
            )

            # Assert
            self.assertFalse(report["capture_complete"])
            self.assertFalse(report["source_status_captured"])
            self.assertFalse(report["source_worktree_clean"])
            self.assertNotIn("SOURCE_WORKTREE_DIRTY", report["review_findings"])

    def test_candidate_id_is_deterministic_and_binary_sensitive(self) -> None:
        with tempfile.TemporaryDirectory(prefix="tau-id-") as temp:
            root = Path(temp)
            source = root / "tau-lang"
            source.mkdir()
            binary = root / "tau"
            binary.write_bytes(b"candidate binary A")
            first = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image=IMMUTABLE_IMAGE,
                build_command=EXPECTED_BUILD_COMMAND,
                command_runner=successful_runner,
            )
            repeated = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image=IMMUTABLE_IMAGE,
                build_command=EXPECTED_BUILD_COMMAND,
                command_runner=successful_runner,
            )

            # Act
            binary.write_bytes(b"candidate binary B")
            changed = capture(
                tau_source=source,
                tau_binary=binary,
                runpod_image=IMMUTABLE_IMAGE,
                build_command=EXPECTED_BUILD_COMMAND,
                command_runner=successful_runner,
            )

            # Assert
            self.assertEqual(first["candidate_manifest_sha256"], repeated["candidate_manifest_sha256"])
            self.assertNotEqual(first["candidate_manifest_sha256"], changed["candidate_manifest_sha256"])


if __name__ == "__main__":
    unittest.main()
