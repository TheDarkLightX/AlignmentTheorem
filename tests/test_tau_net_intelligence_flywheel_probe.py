from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from verification.generate_tau_intelligence_flywheel_packet import OBLIGATIONS
from verification.run_tau_compute_dividend import EXPECTED_TAU_PARSER_COMMIT, EXPECTED_TAU_SOURCE_COMMIT

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "research" / "intelligence_flywheel" / "tau_net_native_probe.json"
TAU_CANDIDATE = ROOT / "research" / "intelligence_flywheel" / "tau_candidate_probe.json"
CAMPAIGN = ROOT / "verification" / "receipts" / "intelligence_flywheel_campaign.json"
CHECKER = ROOT / "verification" / "probe_tau_net_intelligence_flywheel.py"
CHILD = ROOT / "verification" / "tau_net_intelligence_flywheel_child.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TauNetIntelligenceFlywheelProbeTests(unittest.TestCase):
    def test_native_abi_receipt_is_current_and_bounded(self) -> None:
        receipt = json.loads(RECEIPT.read_text())
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["status"], "SUPPORTED_BOUNDED_NATIVE_ABI")
        self.assertTrue(receipt["pins_match"])
        self.assertTrue(receipt["all_cases_match"])
        self.assertEqual(receipt["checker_sha256"], sha256(CHECKER))
        self.assertEqual(receipt["child_checker_sha256"], sha256(CHILD))
        self.assertEqual(receipt["actual_tau_source_commit"], EXPECTED_TAU_SOURCE_COMMIT)
        self.assertEqual(receipt["actual_tau_parser_commit"], EXPECTED_TAU_PARSER_COMMIT)
        self.assertEqual(
            tuple(receipt["semantic_stream_map"][str(index)] for index in range(17, 26)),
            OBLIGATIONS,
        )
        by_name = {case["name"]: case for case in receipt["cases"]}
        self.assertEqual(by_name["treasury_all_true"]["observed"], "allow")
        self.assertEqual(by_name["other_sender_all_false"]["observed"], "allow")
        self.assertEqual(by_name["treasury_custom_inputs_absent"]["observed"], "block")
        for stream in range(17, 26):
            self.assertEqual(by_name[f"treasury_i{stream}_false"]["observed"], "block")
        self.assertIn("not_node_deployment", receipt["tau_net_authority_status"].lower())
        self.assertIn("submitter_supplied", receipt["input_authentication_status"].lower())
        self.assertIn("not_independently_attested", receipt["source_to_binding_status"].lower())
        self.assertIn("not_hermetically_attested", receipt["execution_environment_status"].lower())

    def test_receipts_bind_one_semantic_packet_and_source_parser_pins(self) -> None:
        native = json.loads(RECEIPT.read_text())
        candidate = json.loads(TAU_CANDIDATE.read_text())
        campaign = json.loads(CAMPAIGN.read_text())
        packet_hash = candidate["tau_packet_sha256"]
        self.assertEqual(native["semantic_cli_packet_sha256"], packet_hash)
        self.assertEqual(campaign["tau_semantic_packet"]["packet_sha256"], packet_hash)
        self.assertEqual(candidate["expected_rows"], campaign["tau_semantic_packet"]["rows"])
        self.assertEqual(candidate["actual_accepted_rows"], campaign["tau_semantic_packet"]["accepted_rows"])
        for receipt in (native, candidate):
            self.assertEqual(receipt["actual_tau_source_commit"], EXPECTED_TAU_SOURCE_COMMIT)
            self.assertEqual(receipt["actual_tau_parser_commit"], EXPECTED_TAU_PARSER_COMMIT)
        self.assertEqual(
            tuple(native["semantic_stream_map"][str(index)] for index in range(17, 26)),
            tuple(campaign["tau_semantic_packet"]["obligations"]),
        )


if __name__ == "__main__":
    unittest.main()
