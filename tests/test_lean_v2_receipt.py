from __future__ import annotations

import json
import unittest
from pathlib import Path

from verification.run_lean_v2 import (
    EXPECTED_AXIOMS,
    PLACEHOLDER,
    PROOF_FILES,
    PROOF_ROOT,
    _bundle_sha256,
    _sha256,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verification" / "receipts" / "lean_v2_v4.33.0.json"
CHECKER = ROOT / "verification" / "run_lean_v2.py"


class LeanV2ReceiptTests(unittest.TestCase):
    def test_receipt_binds_exact_placeholder_free_sources(self) -> None:
        # Arrange
        receipt = json.loads(RECEIPT.read_text())
        current_hashes = {
            relative: _sha256((PROOF_ROOT / relative).read_bytes())
            for relative in PROOF_FILES
        }
        source = (PROOF_ROOT / "AlignmentTheoremV2.lean").read_text()

        # Act
        current_bundle = _bundle_sha256(current_hashes)
        placeholders = sorted(set(PLACEHOLDER.findall(source)))

        # Assert
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["source_files_sha256"], current_hashes)
        self.assertEqual(receipt["source_bundle_sha256"], current_bundle)
        self.assertEqual(receipt["checker_sha256"], _sha256(CHECKER.read_bytes()))
        self.assertEqual(placeholders, [])
        self.assertEqual(receipt["placeholders"], [])
        self.assertIn("version 4.33.0", receipt["lean_version"])
        self.assertEqual(receipt["axiom_reports"], EXPECTED_AXIOMS)
        self.assertEqual(receipt["expected_axiom_reports"], EXPECTED_AXIOMS)
        self.assertEqual(receipt["axiom_audit_returncode"], 0)


if __name__ == "__main__":
    unittest.main()
