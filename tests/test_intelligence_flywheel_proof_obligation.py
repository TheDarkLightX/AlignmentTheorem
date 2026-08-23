from __future__ import annotations

import json
import unittest
from pathlib import Path

from verification.generate_intelligence_flywheel_obligation import generate

ROOT = Path(__file__).resolve().parents[1]
OBLIGATION = ROOT / "research" / "intelligence_flywheel" / "proof_obligation_if02.json"
MANIFEST = ROOT / "research" / "intelligence_flywheel" / "manifest.json"


class IntelligenceFlywheelProofObligationTests(unittest.TestCase):
    def test_receipt_refinement_is_exact_and_still_open(self) -> None:
        obligation = json.loads(OBLIGATION.read_text())
        revision = json.loads(MANIFEST.read_text())["artifact_revision"]
        self.assertEqual(obligation, generate(revision))
        self.assertEqual(obligation["schema"], "zrm/proof-obligation/v3")
        self.assertEqual(obligation["status"], "under_test")
        self.assertEqual(obligation["claim_class"], "refinement")
        self.assertIsNotNone(obligation["counterexample"])
        lanes = {lane["tool"]: lane for lane in obligation["lanes"]}
        self.assertEqual(lanes["lean"]["status"], "passed")
        self.assertEqual(lanes["esso"]["status"], "planned")
        self.assertEqual(lanes["tau-testnet-node"]["status"], "planned")
        self.assertIn("transaction-supplied", obligation["counterexample"]["statement"])
        self.assertEqual(
            obligation["execution_policy"],
            "replay_argv_is_untrusted_data_never_execute_from_validation",
        )


if __name__ == "__main__":
    unittest.main()
