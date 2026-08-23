from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from verification.run_tau_compute_dividend import EXPECTED_TAU_BINARY_SHA256, _tree_sha256

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "research" / "intelligence_flywheel" / "tau_candidate_probe.json"
CHECKER = ROOT / "verification" / "probe_tau_intelligence_flywheel_candidate.py"
PACKET = ROOT / "tau" / "intelligence_flywheel" / "gate"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TauIntelligenceFlywheelCandidateProbeTests(unittest.TestCase):
    def test_candidate_is_semantically_bound_but_not_promoted(self) -> None:
        report = json.loads(PROBE.read_text())
        self.assertNotIn("passed", report)
        self.assertTrue(report["candidate_probe_complete"])
        self.assertFalse(report["promotion_eligible"])
        self.assertFalse(report["replay_on_reviewed_binary"])
        self.assertFalse(report["reviewed_binary_match"])
        self.assertTrue(report["source_pins_match"])
        self.assertTrue(report["semantic_match"])
        self.assertEqual(report["checker_sha256"], sha256(CHECKER))
        self.assertEqual(report["tau_packet_sha256"], _tree_sha256(PACKET))
        self.assertEqual(report["expected_rows"], 512)
        self.assertEqual(report["actual_rows"], 512)
        self.assertEqual(report["actual_accepted_rows"], [0])
        self.assertEqual(report["execution_returncode"], 0)
        self.assertEqual(report["actual_output_sha256"], report["expected_output_sha256"])
        self.assertEqual(report["expected_tau_binary_sha256"], EXPECTED_TAU_BINARY_SHA256)
        self.assertNotEqual(report["candidate_tau_binary_sha256"], EXPECTED_TAU_BINARY_SHA256)
        self.assertIn("not_independently_attested", report["source_to_binary_status"].lower())
        self.assertIn("not_hermetically_attested", report["execution_environment_status"].lower())


if __name__ == "__main__":
    unittest.main()
