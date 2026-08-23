from __future__ import annotations

import unittest

from verification.generate_tau_intelligence_flywheel_packet import (
    OBLIGATIONS,
    OUTPUT_NAME,
    TAU_PACKET,
    generated_payloads,
    rows,
)


class TauIntelligenceFlywheelPacketTests(unittest.TestCase):
    def test_truth_table_is_complete_unique_and_fail_closed(self) -> None:
        table = rows()
        self.assertEqual(len(table), 512)
        self.assertEqual(len(set(table)), 512)
        self.assertEqual(table[0], (True,) * 9)
        for index in range(9):
            self.assertEqual(sum(not bit for bit in table[index + 1]), 1)
        expected = (TAU_PACKET / "expected" / OUTPUT_NAME).read_text().splitlines()
        self.assertEqual(expected.count("1"), 1)
        self.assertEqual([index for index, value in enumerate(expected) if value == "1"], [0])

    def test_checked_in_vectors_equal_generator_bytes(self) -> None:
        for relative, payload in generated_payloads().items():
            with self.subTest(path=relative):
                self.assertEqual((TAU_PACKET / relative).read_bytes(), payload)

    def test_spec_names_every_obligation_and_discloses_boundary(self) -> None:
        source = (TAU_PACKET / "intelligence_flywheel_gate.tau").read_text()
        for name in OBLIGATIONS:
            self.assertIn(name, source)
        self.assertIn("does not authenticate", source.lower())


if __name__ == "__main__":
    unittest.main()
