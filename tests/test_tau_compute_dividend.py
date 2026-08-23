from __future__ import annotations

import hashlib
import itertools
import shutil
import tempfile
import unittest
from pathlib import Path

from verification.generate_tau_compute_dividend_packets import (
    GATES,
    TAU_ROOT,
    generated_payloads,
    rows,
)
from verification.run_tau_compute_dividend import (
    EXPECTED_TAU_BINARY_SHA256,
    _packet_errors,
    _tree_sha256,
    run,
)

ROOT = Path(__file__).resolve().parents[1]


class ComputeDividendTauPacketTests(unittest.TestCase):
    def test_both_truth_tables_are_complete_unique_conjunctions(self) -> None:
        for gate, config in GATES.items():
            with self.subTest(gate=gate):
                packet = TAU_ROOT / gate
                obligations = config["obligations"]
                columns = {
                    name: (packet / "inputs" / f"{name}.in").read_text().split()
                    for name in obligations
                }
                expected = (packet / "expected" / "allow.out").read_text().split()
                observed = [
                    "1"
                    if all(columns[name][row] == "1" for name in obligations)
                    else "0"
                    for row in range(len(expected))
                ]
                rendered_rows = list(zip(*(columns[name] for name in obligations), strict=True))

                self.assertEqual({len(values) for values in columns.values()}, {256})
                self.assertEqual(len(expected), 256)
                self.assertEqual(expected, observed)
                self.assertEqual(expected.count("1"), 1)
                self.assertEqual(len(set(rendered_rows)), 256)
                self.assertEqual(
                    rendered_rows,
                    [
                        tuple("1" if bit else "0" for bit in row)
                        for row in rows(len(obligations))
                    ],
                )

    def test_each_obligation_has_a_single_false_mutation_killer(self) -> None:
        for gate, config in GATES.items():
            packet = TAU_ROOT / gate
            obligations = config["obligations"]
            columns = {
                name: (packet / "inputs" / f"{name}.in").read_text().split()
                for name in obligations
            }
            self.assertTrue(all(values[0] == "1" for values in columns.values()))
            for row, target in enumerate(obligations, start=1):
                with self.subTest(gate=gate, target=target):
                    false_fields = {
                        name for name, values in columns.items() if values[row] == "0"
                    }
                    self.assertEqual(false_fields, {target})

    def test_specs_name_every_obligation_and_output(self) -> None:
        for gate, config in GATES.items():
            spec = (TAU_ROOT / gate / config["spec"]).read_text()
            with self.subTest(gate=gate):
                for obligation in config["obligations"]:
                    self.assertIn(f"{obligation}[t]", spec)
                self.assertIn("allow[t] =", spec)

    def test_checked_in_vectors_are_exact_generator_output(self) -> None:
        for gate in GATES:
            with self.subTest(gate=gate):
                packet = TAU_ROOT / gate
                self.assertEqual(_packet_errors(gate, packet), ())
                for relative, payload in generated_payloads(gate).items():
                    self.assertEqual((packet / relative).read_bytes(), payload)

    def test_packet_root_changes_on_vector_mutation(self) -> None:
        for gate in GATES:
            with self.subTest(gate=gate), tempfile.TemporaryDirectory() as temp:
                source = TAU_ROOT / gate
                copy = Path(temp) / gate
                shutil.copytree(source, copy)
                original = _tree_sha256(copy)
                target = next((copy / "inputs").glob("*.in"))
                target.write_text(target.read_text() + "0\n")
                self.assertNotEqual(_tree_sha256(copy), original)

    def test_unreviewed_binary_is_rejected_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp) / "tau"
            fake.write_bytes(b"#!/bin/sh\ntouch should-not-run\n")
            fake.chmod(0o700)
            self.assertNotEqual(
                hashlib.sha256(fake.read_bytes()).hexdigest(), EXPECTED_TAU_BINARY_SHA256
            )

            report = run(fake, "dividend")

            self.assertFalse(report["passed"])
            self.assertFalse(report["execution_attempted"])
            self.assertEqual(report["failure_codes"], ["TAU_BINARY_SHA256_MISMATCH"])


if __name__ == "__main__":
    unittest.main()
