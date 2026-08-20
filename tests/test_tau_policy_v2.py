from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from verification.generate_tau_v2_packet import rows as generated_rows
from verification.run_tau_v2 import (
    EXPECTED_TAU_BINARY_SHA256,
    EXPECTED_TAU_VERSION,
    _tree_sha256,
)

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "tau" / "v2"
TAU_CHECKER = ROOT / "verification" / "run_tau_v2.py"
TAU_GENERATOR = ROOT / "verification" / "generate_tau_v2_packet.py"
OBLIGATIONS = (
    "policy_root_ok",
    "evidence_authenticated",
    "action_known",
    "action_policy_compliant",
    "nonce_fresh",
    "task_unclaimed",
    "reward_funded",
)


class TauPolicyTruthTableTests(unittest.TestCase):
    def test_truth_table_is_complete_and_fail_closed(self) -> None:
        # Arrange
        columns = {
            name: (PACKET / "inputs" / f"{name}.in").read_text().split()
            for name in OBLIGATIONS
        }
        expected = (PACKET / "expected" / "allow.out").read_text().split()

        # Act
        observed = [
            "1" if all(columns[name][row] == "1" for name in OBLIGATIONS) else "0"
            for row in range(len(expected))
        ]

        # Assert
        self.assertEqual({len(values) for values in columns.values()}, {len(expected)})
        self.assertEqual(len(expected), 1 << len(OBLIGATIONS))
        self.assertEqual(observed, expected)
        self.assertEqual(expected.count("1"), 1)

        rows = list(zip(*(columns[name] for name in OBLIGATIONS), strict=True))
        self.assertEqual(len(set(rows)), len(expected))
        rendered_generator_rows = [
            tuple("1" if value else "0" for value in row)
            for row in generated_rows()
        ]
        self.assertEqual(rows, rendered_generator_rows)

    def test_each_obligation_has_a_named_mutation_killer(self) -> None:
        # Arrange / Act
        columns = {
            name: (PACKET / "inputs" / f"{name}.in").read_text().split()
            for name in OBLIGATIONS
        }

        # Assert: row zero accepts; each later row kills exactly one obligation.
        self.assertTrue(all(values[0] == "1" for values in columns.values()))
        for row, target in enumerate(OBLIGATIONS, start=1):
            false_fields = {name for name, values in columns.items() if values[row] == "0"}
            self.assertEqual(false_fields, {target})

    def test_tau_spec_mentions_every_obligation_once_in_gate(self) -> None:
        # Arrange
        spec = (PACKET / "alignment_policy_gate_v2.tau").read_text()

        # Act / Assert
        for name in OBLIGATIONS:
            self.assertIn(f"{name}[t]", spec)
        self.assertIn("allow[t] =", spec)

    def test_receipt_binds_complete_packet_and_mutations_change_root(self) -> None:
        # Arrange
        receipt = json.loads(
            (ROOT / "verification" / "receipts" / "tau_v2_fd137e8.json").read_text()
        )
        expected_root = _tree_sha256(PACKET)

        with tempfile.TemporaryDirectory(prefix="alignment-v2-packet-test-") as temp:
            copy = Path(temp) / "v2"
            shutil.copytree(PACKET, copy)

            # Act
            original_copy_root = _tree_sha256(copy)
            input_path = copy / "inputs" / "policy_root_ok.in"
            input_path.write_text(input_path.read_text() + "0\n")
            mutated_root = _tree_sha256(copy)

        # Assert
        self.assertEqual(receipt["tau_packet_sha256"], expected_root)
        self.assertEqual(receipt["tau_binary_sha256"], EXPECTED_TAU_BINARY_SHA256)
        self.assertEqual(receipt["tau_version"], EXPECTED_TAU_VERSION)
        self.assertEqual(
            receipt["checker_sha256"],
            hashlib.sha256(TAU_CHECKER.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            receipt["generator_sha256"],
            hashlib.sha256(TAU_GENERATOR.read_bytes()).hexdigest(),
        )
        self.assertEqual(original_copy_root, expected_root)
        self.assertNotEqual(mutated_root, expected_root)


if __name__ == "__main__":
    unittest.main()
