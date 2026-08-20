from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from verification.run_tau_v1_1 import (
    AUTHORITY_STATUS,
    EXPECTED_TAU_BINARY_SHA256,
    EXPECTED_TAU_PARSER_COMMIT,
    EXPECTED_TAU_SOURCE_COMMIT,
    EXPECTED_TAU_VERSION,
    OUTPUT_NAME,
    SPEC_NAME,
    TAU_PACKET,
    _grade,
    _packet_generation_errors,
    _report,
    _tree_sha256,
    run,
)

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "verification" / "run_tau_v1_1.py"
EXPECTED_OUTPUT = (TAU_PACKET / "expected" / OUTPUT_NAME).read_bytes()
PACKET_SHA256 = _tree_sha256(TAU_PACKET)


def valid_grade_arguments() -> dict[str, object]:
    return {
        "source_packet_sha256": PACKET_SHA256,
        "copied_packet_sha256": PACKET_SHA256,
        "packet_generation_errors": (),
        "tau_binary_sha256": EXPECTED_TAU_BINARY_SHA256,
        "version_returncode": 0,
        "tau_version": EXPECTED_TAU_VERSION,
        "execution_returncode": 0,
        "actual_output": EXPECTED_OUTPUT,
        "expected_output": EXPECTED_OUTPUT,
    }


class TauV1_1RunnerGradingTests(unittest.TestCase):
    def test_exact_pinned_replay_shape_is_the_only_passing_grade(self) -> None:
        # Arrange
        arguments = valid_grade_arguments()

        # Act
        failures = _grade(**arguments)

        # Assert
        self.assertEqual(failures, ())

    def test_each_pre_execution_trust_layer_has_a_named_mutation_killer(self) -> None:
        # Arrange
        mutations = {
            "packet_copy": (
                {"copied_packet_sha256": "0" * 64},
                "PACKET_COPY_HASH_MISMATCH",
            ),
            "generated_vectors": (
                {"packet_generation_errors": ("GENERATED_VECTOR_MISMATCH:x",)},
                "GENERATED_VECTOR_MISMATCH:x",
            ),
            "binary_identity": (
                {"tau_binary_sha256": "0" * 64},
                "TAU_BINARY_SHA256_MISMATCH",
            ),
            "version_process": (
                {"version_returncode": 1},
                "TAU_VERSION_COMMAND_FAILED",
            ),
            "version_identity": (
                {"tau_version": "Tau Language Framework version unknown"},
                "TAU_VERSION_MISMATCH",
            ),
        }

        # Act / Assert
        for name, (mutation, expected) in mutations.items():
            with self.subTest(mutant=name):
                failures = _grade(**(valid_grade_arguments() | mutation))
                self.assertEqual(failures, (expected,))

    def test_crash_timeout_nonzero_and_missing_output_fail_closed(self) -> None:
        # Arrange
        mutations = {
            "no_result": (
                {"execution_returncode": None},
                "TAU_EXECUTION_NO_RESULT",
            ),
            "segfault": (
                {"execution_returncode": -11},
                "TAU_EXECUTION_FAILED",
            ),
            "nonzero": (
                {"execution_returncode": 2},
                "TAU_EXECUTION_FAILED",
            ),
            "missing_output": (
                {"actual_output": None},
                "TAU_OUTPUT_MISSING",
            ),
        }

        # Act / Assert
        for name, (mutation, expected) in mutations.items():
            with self.subTest(mutant=name):
                failures = _grade(**(valid_grade_arguments() | mutation))
                self.assertEqual(failures, (expected,))

    def test_output_row_count_boundaries_reject_zero_one_fifteen_and_seventeen(self) -> None:
        # Arrange
        rows = EXPECTED_OUTPUT.splitlines(keepends=True)
        boundary_outputs = {
            "zero": b"",
            "one": rows[0],
            "fifteen": b"".join(rows[:15]),
            "seventeen": EXPECTED_OUTPUT + b"0\n",
        }

        # Act / Assert
        for name, actual in boundary_outputs.items():
            with self.subTest(boundary=name):
                failures = _grade(
                    **(valid_grade_arguments() | {"actual_output": actual})
                )
                self.assertEqual(failures, ("TAU_OUTPUT_ROW_COUNT_MISMATCH",))

    def test_reordered_malformed_and_noncanonical_outputs_reject(self) -> None:
        # Arrange
        rows = EXPECTED_OUTPUT.splitlines(keepends=True)
        malformed = bytearray(EXPECTED_OUTPUT)
        malformed[0] = ord("x")
        mutations = {
            "reordered": b"".join(rows[1:] + rows[:1]),
            "malformed": bytes(malformed),
            "crlf": EXPECTED_OUTPUT.replace(b"\n", b"\r\n"),
            "missing_final_newline": EXPECTED_OUTPUT.rstrip(b"\n"),
        }

        # Act / Assert
        for name, actual in mutations.items():
            with self.subTest(mutant=name):
                failures = _grade(
                    **(valid_grade_arguments() | {"actual_output": actual})
                )
                self.assertEqual(
                    failures,
                    ("TAU_OUTPUT_NONCANONICAL_OR_MISMATCH",),
                )

    def test_passing_report_preserves_source_pins_and_authority_nonclaim(self) -> None:
        # Arrange
        arguments = valid_grade_arguments()

        # Act
        report = _report(
            **arguments,
            execution_attempted=True,
            tau_spec_sha256=hashlib.sha256(
                (TAU_PACKET / SPEC_NAME).read_bytes()
            ).hexdigest(),
            diagnostic="ignored on pass",
        )

        # Assert
        self.assertTrue(report["passed"])
        self.assertEqual(report["failure_codes"], [])
        self.assertEqual(report["tau_source_commit"], EXPECTED_TAU_SOURCE_COMMIT)
        self.assertEqual(report["tau_parser_commit"], EXPECTED_TAU_PARSER_COMMIT)
        self.assertEqual(
            report["tau_spec_sha256"],
            hashlib.sha256((TAU_PACKET / SPEC_NAME).read_bytes()).hexdigest(),
        )
        self.assertEqual(report["authority_status"], AUTHORITY_STATUS)
        self.assertEqual(report["error"], "")


class TauV1_1RunnerBoundaryTests(unittest.TestCase):
    def test_packet_vectors_match_generator_and_closed_file_set(self) -> None:
        # Arrange / Act
        errors = _packet_generation_errors(TAU_PACKET)

        # Assert
        self.assertEqual(errors, ())

    def test_vector_mutation_and_extra_file_are_observable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="alignment-v1-1-packet-") as temp:
            copy = Path(temp) / "v1_1"
            shutil.copytree(TAU_PACKET, copy)
            original_hash = _tree_sha256(copy)

            # Act: infect one generated vector and add one undeclared file.
            target = copy / "inputs" / "reward_funded.in"
            target.write_bytes(target.read_bytes() + b"0\n")
            (copy / "undeclared.in").write_text("1\n")
            errors = _packet_generation_errors(copy)
            mutated_hash = _tree_sha256(copy)

        # Assert
        self.assertEqual(original_hash, PACKET_SHA256)
        self.assertNotEqual(mutated_hash, PACKET_SHA256)
        self.assertIn("PACKET_FILE_SET_MISMATCH", errors)
        self.assertIn(
            "GENERATED_VECTOR_MISMATCH:inputs/reward_funded.in",
            errors,
        )

    def test_packet_symlink_is_rejected_before_hashing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="alignment-v1-1-symlink-") as temp:
            packet = Path(temp) / "packet"
            packet.mkdir()
            target = packet / "target"
            target.write_text("1\n")
            (packet / "alias").symlink_to(target)

            # Act / Assert
            with self.assertRaisesRegex(ValueError, "contains symlink"):
                _tree_sha256(packet)

    def test_wrong_binary_is_rejected_without_execution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="alignment-v1-1-fake-tau-") as temp:
            root = Path(temp)
            sentinel = root / "executed"
            fake = root / "tau"
            fake.write_text(
                f"#!{sys.executable}\n"
                "from pathlib import Path\n"
                f"Path({str(sentinel)!r}).write_text('executed')\n"
            )
            os.chmod(fake, 0o700)

            # Act
            report = run(fake)

            # Assert
            self.assertFalse(report["passed"])
            self.assertFalse(report["execution_attempted"])
            self.assertEqual(
                report["failure_codes"],
                ["TAU_BINARY_SHA256_MISMATCH"],
            )
            self.assertFalse(sentinel.exists())

    def test_failed_cli_replay_cannot_write_a_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="alignment-v1-1-cli-") as temp:
            root = Path(temp)
            fake = root / "tau"
            fake.write_text("invalid Tau binary\n")
            os.chmod(fake, 0o700)
            receipt = root / "receipt.json"

            # Act
            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--tau-bin",
                    str(fake),
                    "--output",
                    str(receipt),
                    "--json",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            report = json.loads(completed.stdout)

            # Assert
            self.assertEqual(completed.returncode, 1)
            self.assertFalse(report["passed"])
            self.assertEqual(
                report["failure_codes"],
                ["TAU_BINARY_SHA256_MISMATCH"],
            )
            self.assertFalse(receipt.exists())


if __name__ == "__main__":
    unittest.main()
