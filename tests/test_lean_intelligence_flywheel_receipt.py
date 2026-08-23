from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verification" / "receipts" / "lean_intelligence_flywheel_v4.33.0.json"
RUNNER = ROOT / "verification" / "run_lean_intelligence_flywheel.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LeanIntelligenceFlywheelReceiptTests(unittest.TestCase):
    def test_receipt_is_current_and_bounded(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["checker_sha256"], sha256(RUNNER))
        self.assertEqual(receipt["placeholders"], [])
        self.assertEqual(receipt["build_returncode"], 0)
        self.assertEqual(receipt["axiom_audit_returncode"], 0)
        self.assertIn("not_attested", receipt["source_to_executable_status"].lower())
        self.assertIn("not_hermetically_attested", receipt["execution_environment_status"].lower())
        for relative, expected in receipt["source_files_sha256"].items():
            self.assertEqual(expected, sha256(ROOT / "proofs" / "intelligence_flywheel" / relative))


if __name__ == "__main__":
    unittest.main()
