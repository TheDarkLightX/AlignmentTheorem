from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from verification.generate_tau_compute_dividend_packets import GATES, TAU_ROOT
from verification.run_tau_compute_dividend import (
    EXPECTED_TAU_BINARY_SHA256,
    EXPECTED_TAU_PARSER_COMMIT,
    EXPECTED_TAU_SOURCE_COMMIT,
    EXPECTED_TAU_VERSION,
    _tree_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "research" / "compute_dividend" / "tau_source_candidate_probe.json"
CHECKER = ROOT / "verification" / "probe_tau_compute_dividend_candidate.py"
V1_PACKET = ROOT / "tau" / "v1_1"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TauSourceCandidateProbeTests(unittest.TestCase):
    def test_candidate_native_execution_is_bound_but_not_promotable(self) -> None:
        report = json.loads(PROBE.read_text())

        self.assertNotIn("passed", report)
        self.assertTrue(report["candidate_probe_complete"])
        self.assertFalse(report["promotion_eligible"])
        self.assertFalse(report["replay_on_reviewed_binary"])
        self.assertFalse(report["reviewed_binary_match"])
        self.assertEqual(report["binary_execution_location"], "SOURCE_BUILD_TREE_IN_PLACE")
        self.assertEqual(report["checker_sha256"], _sha256(CHECKER))

        self.assertEqual(report["actual_tau_source_commit"], EXPECTED_TAU_SOURCE_COMMIT)
        self.assertEqual(report["actual_tau_parser_commit"], EXPECTED_TAU_PARSER_COMMIT)
        self.assertTrue(report["source_pins_match"])
        self.assertTrue(report["submodule_pins_clean"])
        self.assertEqual(report["source_status_porcelain"], [])

        candidate_hash = report["candidate_tau_binary_sha256"]
        self.assertRegex(candidate_hash, SHA256)
        self.assertEqual(report["expected_tau_binary_sha256"], EXPECTED_TAU_BINARY_SHA256)
        self.assertNotEqual(candidate_hash, EXPECTED_TAU_BINARY_SHA256)
        self.assertEqual(report["expected_tau_version"], EXPECTED_TAU_VERSION)
        self.assertEqual(
            report["candidate_tau_version"],
            "Tau Language Framework version 0.7.0-alpha (fd137e86)",
        )
        self.assertFalse(report["version_match"])

        packet_roots = {
            "v1_1": _tree_sha256(V1_PACKET),
            **{
                gate: _tree_sha256(TAU_ROOT / gate)
                for gate in GATES
            },
        }
        expected_rows = {"v1_1": 16, "dividend": 256, "wealth": 256}
        self.assertTrue(report["all_packet_semantics_match"])
        for name, packet in report["packets"].items():
            with self.subTest(packet=name):
                self.assertEqual(packet["packet_sha256"], packet_roots[name])
                self.assertEqual(packet["expected_rows"], expected_rows[name])
                self.assertEqual(packet["actual_rows"], expected_rows[name])
                self.assertEqual(packet["actual_accepted_rows"], [0])
                self.assertEqual(packet["execution_returncode"], 0)
                self.assertEqual(
                    packet["actual_output_sha256"],
                    packet["expected_output_sha256"],
                )
                self.assertTrue(packet["semantic_match"])

        source_boundary = report["source_to_binary_status"].lower().replace("_", " ")
        environment_boundary = report["execution_environment_status"].lower().replace(
            "_", " "
        )
        self.assertIn("not independently attested", source_boundary)
        self.assertIn("not hermetically attested", environment_boundary)


if __name__ == "__main__":
    unittest.main()
