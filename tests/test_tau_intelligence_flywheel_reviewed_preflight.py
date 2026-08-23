from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from verification.run_tau_compute_dividend import EXPECTED_TAU_BINARY_SHA256, _tree_sha256

ROOT = Path(__file__).resolve().parents[1]
PENDING = ROOT / "verification" / "pending" / "tau_intelligence_flywheel_fd137e8_preflight.json"
RUNNER = ROOT / "verification" / "run_tau_intelligence_flywheel_reviewed.py"
PACKET = ROOT / "tau" / "intelligence_flywheel" / "gate"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TauIntelligenceFlywheelReviewedPreflightTests(unittest.TestCase):
    def test_candidate_is_rejected_before_reviewed_execution(self) -> None:
        receipt = json.loads(PENDING.read_text())
        self.assertFalse(receipt["passed"])
        self.assertFalse(receipt["execution_attempted"])
        self.assertEqual(receipt["failure_codes"], ["TAU_BINARY_SHA256_MISMATCH"])
        self.assertEqual(receipt["checker_sha256"], sha256(RUNNER))
        self.assertEqual(receipt["expected_tau_binary_sha256"], EXPECTED_TAU_BINARY_SHA256)
        self.assertNotEqual(receipt["tau_binary_sha256"], EXPECTED_TAU_BINARY_SHA256)
        self.assertEqual(receipt["tau_packet_sha256"], _tree_sha256(PACKET))
        self.assertEqual(receipt["copied_tau_packet_sha256"], _tree_sha256(PACKET))
        self.assertIn("not_attested", receipt["source_to_binary_status"].lower())
        self.assertIn("not_hermetically_attested", receipt["execution_environment_status"].lower())


if __name__ == "__main__":
    unittest.main()
