from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from verification.current_tau_baseline import (
    CURRENT_TAU_PARSER_COMMIT,
    CURRENT_TAU_SOURCE_COMMIT,
    CURRENT_TAU_VERSION,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "research" / "current_tau" / "current_tau_packet_probe.json"
CHECKER = ROOT / "verification" / "probe_current_tau_packets.py"


class CurrentTauSnapshotTests(unittest.TestCase):
    def test_all_version_profiles_replay_on_the_source_pinned_candidate(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        self.assertTrue(receipt["semantic_replay_passed"])
        self.assertEqual(receipt["status"], "SUPPORTED_LOCAL_SOURCE_CANDIDATE")
        self.assertTrue(receipt["pins_match"])
        self.assertEqual(receipt["actual_tau_source_commit"], CURRENT_TAU_SOURCE_COMMIT)
        self.assertEqual(receipt["actual_tau_parser_commit"], CURRENT_TAU_PARSER_COMMIT)
        self.assertEqual(receipt["actual_tau_version"], CURRENT_TAU_VERSION)
        self.assertEqual(
            receipt["checker_sha256"], hashlib.sha256(CHECKER.read_bytes()).hexdigest()
        )
        by_profile = {row["profile"]: row for row in receipt["packet_results"]}
        self.assertEqual(
            set(by_profile),
            {
                "v1_exclusion",
                "v1_1_hyperdeflationary",
                "v2_finite_policy",
                "intelligence_flywheel",
            },
        )
        expected_rows = {
            "v1_exclusion": 128,
            "v1_1_hyperdeflationary": 16,
            "v2_finite_policy": 128,
            "intelligence_flywheel": 512,
        }
        for profile, row_count in expected_rows.items():
            result = by_profile[profile]
            self.assertTrue(result["semantic_match"])
            self.assertEqual(result["expected_rows"], row_count)
            self.assertEqual(result["actual_rows"], row_count)
            self.assertEqual(result["accepted_rows"], [0])
            self.assertEqual(
                result["expected_output_sha256"], result["actual_output_sha256"]
            )

    def test_receipt_keeps_authority_and_authentication_claims_closed(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        self.assertIn("no_tau_net", receipt["authority_status"].lower())
        self.assertIn("not_independently_attested", receipt["source_to_binary_status"].lower())
        self.assertIn("not_hermetically_attested", receipt["execution_environment_status"].lower())
        self.assertTrue(any("not authenticated" in item for item in receipt["nonclaims"]))


if __name__ == "__main__":
    unittest.main()
