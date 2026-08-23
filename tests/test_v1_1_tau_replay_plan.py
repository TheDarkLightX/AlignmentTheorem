from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from verification.generate_tau_v1_1_packet import rows
from verification.run_tau_v1_1 import (
    EXPECTED_TAU_BINARY_SHA256,
    EXPECTED_TAU_PARSER_COMMIT,
    EXPECTED_TAU_SOURCE_COMMIT,
    EXPECTED_TAU_VERSION,
    OUTPUT_NAME,
    SPEC_NAME,
    TAU_PACKET,
    _tree_sha256,
)

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "verification" / "pending" / "tau_v1_1_fd137e8_replay_plan.json"
CHECKER = ROOT / "verification" / "run_tau_v1_1.py"
GENERATOR = ROOT / "verification" / "generate_tau_v1_1_packet.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V11TauReplayPlanTests(unittest.TestCase):
    def test_pending_plan_binds_current_semantic_packet_and_all_expected_pins(self) -> None:
        plan = json.loads(PLAN.read_text())
        expected = (TAU_PACKET / "expected" / OUTPUT_NAME).read_text().split()

        self.assertEqual(plan["status"], "PENDING_EXACT_REVIEWED_BINARY")
        self.assertFalse(plan["execution_evidence"])
        self.assertEqual(plan["expected_tau_source_commit"], EXPECTED_TAU_SOURCE_COMMIT)
        self.assertEqual(plan["expected_tau_parser_commit"], EXPECTED_TAU_PARSER_COMMIT)
        self.assertEqual(plan["expected_tau_version"], EXPECTED_TAU_VERSION)
        self.assertEqual(plan["expected_tau_binary_sha256"], EXPECTED_TAU_BINARY_SHA256)
        self.assertEqual(plan["tau_packet_sha256"], _tree_sha256(TAU_PACKET))
        self.assertEqual(plan["tau_spec_sha256"], _sha256(TAU_PACKET / SPEC_NAME))
        self.assertEqual(
            plan["expected_output_sha256"],
            _sha256(TAU_PACKET / "expected" / OUTPUT_NAME),
        )
        self.assertEqual(plan["checker_sha256"], _sha256(CHECKER))
        self.assertEqual(plan["generator_sha256"], _sha256(GENERATOR))
        self.assertEqual(plan["semantic_packet_rows"], len(rows()))
        self.assertEqual(plan["semantic_packet_rows"], len(expected))
        self.assertEqual(
            plan["accepted_rows"],
            [index for index, value in enumerate(expected) if value == "1"],
        )


if __name__ == "__main__":
    unittest.main()
