from __future__ import annotations

import json
import unittest
from pathlib import Path

from verification.generate_intelligence_flywheel_obligation import generate
from verification.current_tau_baseline import CURRENT_TAU_SOURCE_COMMIT

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
        upstream = {item["name"]: item["revision"] for item in obligation["upstream_revisions"]}
        self.assertEqual(upstream["tau-lang-current-candidate"], CURRENT_TAU_SOURCE_COMMIT)
        self.assertIn("tau-lang-reviewed-runner-baseline", upstream)
        self.assertEqual(
            obligation["execution_policy"],
            "replay_argv_is_untrusted_data_never_execute_from_validation",
        )


if __name__ == "__main__":
    unittest.main()
