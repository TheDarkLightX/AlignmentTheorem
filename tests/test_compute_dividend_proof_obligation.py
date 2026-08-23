from __future__ import annotations

import json
import unittest
from pathlib import Path

from verification.generate_compute_dividend_obligation import generate


ROOT = Path(__file__).resolve().parents[1]
OBLIGATION = (
    ROOT / "research" / "compute_dividend" / "proof_obligation_cd01.json"
)
MANIFEST = ROOT / "research" / "compute_dividend" / "manifest.json"


class ComputeDividendProofObligationTests(unittest.TestCase):
    def test_unrestricted_claim_is_under_test_not_promoted(self) -> None:
        obligation = json.loads(OBLIGATION.read_text())
        manifest = json.loads(MANIFEST.read_text())
        revision = manifest["artifact_revision"]

        self.assertEqual(obligation, generate(revision))
        self.assertEqual(obligation["schema"], "zrm/proof-obligation/v3")
        self.assertEqual(obligation["artifact_revision"], revision)
        self.assertEqual(obligation["status"], "under_test")
        self.assertIsNone(obligation["counterexample"])
        self.assertEqual(
            set(obligation["required_tools"]), {"reference-model", "lean"}
        )

        lanes = {lane["tool"]: lane for lane in obligation["lanes"]}
        self.assertEqual(lanes["reference-model"]["status"], "passed")
        self.assertTrue(lanes["reference-model"]["evidence_ids"])
        self.assertEqual(lanes["lean"]["status"], "planned")
        self.assertEqual(lanes["lean"]["evidence_ids"], [])
        self.assertIn(
            "not an unrestricted mathematical proof",
            " ".join(obligation["completed_evidence"][0]["limitations"]).lower(),
        )
        self.assertEqual(
            obligation["execution_policy"],
            "replay_argv_is_untrusted_data_never_execute_from_validation",
        )


if __name__ == "__main__":
    unittest.main()
