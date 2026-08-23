from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from verification.current_tau_baseline import (
    CURRENT_TAU_NATIVE_MODULE_SHA256,
    CURRENT_TAU_PARSER_COMMIT,
    CURRENT_TAU_SOURCE_COMMIT,
    CURRENT_TAU_TESTNET_COMMIT,
)
from verification.probe_tau_net_alignment_profiles import FACT_MAP, PROFILE_MAP

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "research" / "current_tau" / "profile_router_native_probe.json"
CHECKER = ROOT / "verification" / "probe_tau_net_alignment_profiles.py"
CHILD = ROOT / "verification" / "tau_net_alignment_profiles_child.py"
SPEC = ROOT / "tau" / "current_tau" / "alignment_profiles_o5.tau"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TauNetAlignmentProfileProbeTests(unittest.TestCase):
    def test_receipt_is_source_bound_and_complete(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["status"], "SUPPORTED_BOUNDED_NATIVE_ABI")
        self.assertTrue(receipt["pins_match"])
        self.assertTrue(receipt["all_cases_match"])
        self.assertEqual(receipt["expected_case_count"], 27)
        self.assertEqual(len(receipt["cases"]), 27)
        self.assertEqual(receipt["checker_sha256"], sha256(CHECKER))
        self.assertEqual(receipt["child_checker_sha256"], sha256(CHILD))
        self.assertEqual(receipt["tau_spec_sha256"], sha256(SPEC))
        self.assertEqual(receipt["profile_map"], PROFILE_MAP)
        self.assertEqual(receipt["fact_map"], FACT_MAP)
        self.assertEqual(receipt["actual_tau_source_commit"], CURRENT_TAU_SOURCE_COMMIT)
        self.assertEqual(receipt["actual_tau_parser_commit"], CURRENT_TAU_PARSER_COMMIT)
        self.assertEqual(receipt["actual_tau_testnet_commit"], CURRENT_TAU_TESTNET_COMMIT)
        self.assertEqual(
            receipt["tau_native_module_sha256"], CURRENT_TAU_NATIVE_MODULE_SHA256
        )

    def test_every_profile_and_single_false_fact_has_expected_verdict(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        by_name = {case["name"]: case for case in receipt["cases"]}
        for profile in ("v1", "v1_1", "v2"):
            self.assertEqual(
                by_name[f"treasury_{profile}_all_true"]["observed"], "allow"
            )
            for stream in range(18, 25):
                self.assertEqual(
                    by_name[f"treasury_{profile}_i{stream}_false"]["observed"],
                    "block",
                )
        self.assertEqual(by_name["treasury_unknown_profile"]["observed"], "block")
        self.assertEqual(
            by_name["treasury_profile_and_facts_absent"]["observed"], "block"
        )
        self.assertEqual(
            by_name["other_sender_unknown_profile_all_false"]["observed"], "allow"
        )

    def test_authority_claims_remain_closed(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        self.assertIn("not_node_deployment", receipt["tau_net_authority_status"].lower())
        self.assertIn(
            "transaction_supplied", receipt["profile_authentication_status"].lower()
        )
        self.assertIn(
            "transaction_supplied", receipt["fact_authentication_status"].lower()
        )
        self.assertIn("no_reserve", receipt["settlement_status"].lower())
        self.assertTrue(
            any(
                "does not itself enforce exclusion" in item
                for item in receipt["nonclaims"]
            )
        )


if __name__ == "__main__":
    unittest.main()
