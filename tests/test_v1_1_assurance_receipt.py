from __future__ import annotations

import json
import unittest

from verification.run_v1_1_assurance import (
    BOUND_FILES,
    REPO_ROOT,
    _bundle_sha256,
    _sha256,
)

RECEIPT = REPO_ROOT / "verification" / "receipts" / "v1_1_assurance.json"
CHECKER = REPO_ROOT / "verification" / "run_v1_1_assurance.py"


class V1_1AssuranceReceiptTests(unittest.TestCase):
    def test_receipt_binds_every_declared_artifact_and_explicit_nonclaims(self) -> None:
        # Arrange
        receipt = json.loads(RECEIPT.read_text())
        current_hashes = {
            relative: _sha256((REPO_ROOT / relative).read_bytes())
            for relative in BOUND_FILES
        }

        # Act
        current_bundle = _bundle_sha256(current_hashes)

        # Assert
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["bound_files_sha256"], current_hashes)
        self.assertEqual(receipt["source_bundle_sha256"], current_bundle)
        self.assertEqual(receipt["checker_sha256"], _sha256(CHECKER.read_bytes()))
        self.assertEqual(receipt["python_test_returncode"], 0)
        self.assertTrue(receipt["lean_passed"])
        self.assertEqual(receipt["tau_semantic_packet_rows"], 16)
        self.assertEqual(
            receipt["tau_interpreter_replay_status"],
            "PENDING_EXACT_SOURCE_PIN",
        )
        self.assertEqual(
            receipt["authority_status"],
            "REFERENCE_ONLY_NO_PUBLICATION_OR_VALUE_AUTHORITY",
        )

    def test_one_bound_hash_mutation_changes_the_bundle(self) -> None:
        # Arrange
        current_hashes = {
            relative: _sha256((REPO_ROOT / relative).read_bytes())
            for relative in BOUND_FILES
        }
        target = BOUND_FILES[0]
        mutated = current_hashes | {target: "0" * 64}

        # Act / Assert
        self.assertNotEqual(
            _bundle_sha256(current_hashes),
            _bundle_sha256(mutated),
        )


if __name__ == "__main__":
    unittest.main()
