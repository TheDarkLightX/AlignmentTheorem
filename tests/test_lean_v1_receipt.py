from __future__ import annotations

import json
import unittest
from pathlib import Path

from verification.run_lean_v1 import PROOF_FILES, PROOF_ROOT, _bundle_sha256, _sha256

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verification" / "receipts" / "lean_v1_v4.33.0.json"
CHECKER = ROOT / "verification" / "run_lean_v1.py"


class LeanV1ReceiptTests(unittest.TestCase):
    def test_receipt_is_source_bound_and_passed(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        current = {
            relative: _sha256((PROOF_ROOT / relative).read_bytes())
            for relative in PROOF_FILES
        }
        self.assertEqual(receipt["schema"], "alignment-theorem-v1-lean-build-v1")
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["placeholders"], [])
        self.assertEqual(receipt["source_files_sha256"], current)
        self.assertEqual(receipt["source_bundle_sha256"], _bundle_sha256(current))
        self.assertEqual(receipt["checker_sha256"], _sha256(CHECKER.read_bytes()))
        self.assertEqual(receipt["axiom_reports"], receipt["expected_axiom_reports"])


if __name__ == "__main__":
    unittest.main()
