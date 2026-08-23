from __future__ import annotations

import itertools
import unittest
from pathlib import Path

from verification.generate_tau_v1_packet import OBLIGATIONS, rows

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "tau" / "v1"


class TauV1TruthTableTests(unittest.TestCase):
    def test_complete_fail_closed_packet_matches_generator(self) -> None:
        columns = {
            name: (PACKET / "inputs" / f"{name}.in").read_text().split()
            for name in OBLIGATIONS
        }
        expected = (PACKET / "expected" / "v1_eligible.out").read_text().split()
        rendered_rows = list(zip(*(columns[name] for name in OBLIGATIONS), strict=True))
        expected_count = 1 << len(OBLIGATIONS)
        self.assertEqual(len(expected), expected_count)
        self.assertEqual(len(set(rendered_rows)), expected_count)
        self.assertEqual(expected.count("1"), 1)
        self.assertEqual(
            rendered_rows,
            [tuple("1" if value else "0" for value in row) for row in rows()],
        )
        self.assertEqual(
            expected,
            ["1" if all(row) else "0" for row in rows()],
        )

    def test_each_obligation_has_a_single_fault_rejection(self) -> None:
        generated = rows()
        self.assertEqual(
            set(generated),
            set(itertools.product((False, True), repeat=len(OBLIGATIONS))),
        )
        self.assertTrue(all(generated[0]))
        for index, obligation in enumerate(OBLIGATIONS, start=1):
            false_fields = {
                name for name, value in zip(OBLIGATIONS, generated[index], strict=True)
                if not value
            }
            self.assertEqual(false_fields, {obligation})

    def test_spec_names_authority_boundary(self) -> None:
        spec = (PACKET / "exclusion_gate_v1.tau").read_text()
        for obligation in OBLIGATIONS:
            self.assertIn(f"{obligation}[t]", spec)
        self.assertIn("does not authenticate", spec)
        self.assertIn("value-moving authority", spec)
        self.assertIn("no punitive debit", spec)


if __name__ == "__main__":
    unittest.main()
