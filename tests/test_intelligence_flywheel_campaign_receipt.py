from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "verification" / "receipts" / "intelligence_flywheel_campaign.json"
RUNNER = ROOT / "verification" / "run_intelligence_flywheel_campaign.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IntelligenceFlywheelCampaignReceiptTests(unittest.TestCase):
    def test_campaign_receipt_is_current(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["status"], "SUPPORTED_BOUNDED")
        self.assertEqual(receipt["checker_sha256"], sha256(RUNNER))
        for relative, expected in receipt["bound_files_sha256"].items():
            self.assertEqual(expected, sha256(ROOT / relative))
        self.assertEqual(receipt["bridge_enumeration"]["cases"], 544)
        self.assertEqual(receipt["bridge_enumeration"]["failures"], [])
        self.assertEqual(receipt["maps"]["direct_doubling_full_bridge"]["first_strict_alignment_epoch"], 4)
        self.assertIsNone(receipt["maps"]["direct_doubling_partial_bridge"]["first_strict_alignment_epoch_0_to_32"])
        self.assertIsNone(receipt["maps"]["logistic_saturation"]["first_strict_alignment_epoch_0_to_32"])
        self.assertEqual(receipt["maps"]["dac_reinvestment"]["first_strict_alignment_epoch"], 7)
        self.assertEqual(receipt["tau_semantic_packet"]["rows"], 512)
        self.assertEqual(receipt["tau_semantic_packet"]["accepted_rows"], [0])
        self.assertIn("PENDING", receipt["tau_semantic_packet"]["reviewed_binary_replay"])


if __name__ == "__main__":
    unittest.main()
