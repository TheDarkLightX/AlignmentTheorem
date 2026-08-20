from __future__ import annotations

import itertools
import unittest
from pathlib import Path

from verification.generate_tau_v1_1_packet import OBLIGATIONS, rows

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "tau" / "v1_1"


class TauV1_1TruthTableTests(unittest.TestCase):
    def test_truth_table_is_complete_and_fail_closed(self) -> None:
        # Arrange
        columns = {
            name: (PACKET / "inputs" / f"{name}.in").read_text().split()
            for name in OBLIGATIONS
        }
        expected = (
            PACKET / "expected" / "reference_eligible.out"
        ).read_text().split()

        # Act
        observed = [
            "1" if all(columns[name][row] == "1" for name in OBLIGATIONS) else "0"
            for row in range(len(expected))
        ]

        # Assert
        self.assertEqual({len(values) for values in columns.values()}, {16})
        self.assertEqual(observed, expected)
        self.assertEqual(expected.count("1"), 1)
        rendered_rows = list(zip(*(columns[name] for name in OBLIGATIONS), strict=True))
        self.assertEqual(len(set(rendered_rows)), 16)
        self.assertEqual(
            rendered_rows,
            [tuple("1" if value else "0" for value in row) for row in rows()],
        )

    def test_each_fact_has_a_named_single_mutation_killer(self) -> None:
        # Arrange
        columns = {
            name: (PACKET / "inputs" / f"{name}.in").read_text().split()
            for name in OBLIGATIONS
        }

        # Act / Assert: row zero accepts; each subsequent row kills one fact.
        self.assertTrue(all(values[0] == "1" for values in columns.values()))
        for row, target in enumerate(OBLIGATIONS, start=1):
            false_fields = {
                name for name, values in columns.items() if values[row] == "0"
            }
            self.assertEqual(false_fields, {target})

    def test_tau_spec_mentions_each_fact_and_no_unconditional_reward(self) -> None:
        # Arrange
        spec = (PACKET / "hyperdeflation_gate_v1_1.tau").read_text()

        # Act / Assert
        for name in OBLIGATIONS:
            self.assertIn(f"{name}[t]", spec)
        self.assertIn("reference_eligible[t] =", spec)
        self.assertNotIn("\neligible:sbf", spec)
        self.assertNotIn("is_ethical_echo", spec)
        self.assertIn("does not authenticate", spec)
        self.assertIn("value-moving authority", spec)

    def test_generator_order_contains_every_boolean_row(self) -> None:
        # Arrange / Act
        generated = rows()

        # Assert
        self.assertEqual(len(generated), 16)
        self.assertEqual(set(generated), set(itertools.product((False, True), repeat=4)))

if __name__ == "__main__":
    unittest.main()
