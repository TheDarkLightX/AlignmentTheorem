from __future__ import annotations

import itertools
import unittest
from dataclasses import replace
from fractions import Fraction

from verification.intelligence_flywheel_model import (
    DacGateFacts,
    PriceBridge,
    aligned,
    bounded_reward_blocks_alignment,
    compute_power_capability,
    dac_reinvestment_capability,
    dac_treasury_admits,
    direct_capability_doubling,
    first_alignment_epoch,
    logistic_capability,
    normalized_basket_price,
    purchasing_power_multiplier,
    simulate,
)


class CapabilityMapTests(unittest.TestCase):
    def test_direct_doubling_is_an_explicit_sequence(self) -> None:
        self.assertEqual(
            [direct_capability_doubling(t) for t in range(7)],
            [Fraction(value) for value in (1, 2, 4, 8, 16, 32, 64)],
        )

    def test_compute_doubling_does_not_imply_capability_doubling(self) -> None:
        half = Fraction(1, 2)
        self.assertEqual(
            [compute_power_capability(t, elasticity=half) for t in (0, 2, 4, 6)],
            [Fraction(value) for value in (1, 2, 4, 8)],
        )
        with self.assertRaisesRegex(ValueError, "exact integral"):
            compute_power_capability(1, elasticity=half)

    def test_logistic_alternative_is_bounded(self) -> None:
        path = [
            logistic_capability(
                t,
                initial=Fraction(1),
                carrying_capacity=Fraction(8),
                decay=Fraction(1, 2),
            )
            for t in range(12)
        ]
        self.assertTrue(all(left < right for left, right in zip(path, path[1:])))
        self.assertTrue(all(value < 8 for value in path))

    def test_dac_growth_depends_on_return_and_reinvestment(self) -> None:
        self.assertEqual(
            dac_reinvestment_capability(
                3,
                initial=Fraction(1),
                reinvestment_share=Fraction(1, 2),
                verified_net_return=Fraction(1, 2),
            ),
            Fraction(125, 64),
        )
        self.assertEqual(
            dac_reinvestment_capability(
                20,
                initial=Fraction(1),
                reinvestment_share=Fraction(0),
                verified_net_return=Fraction(1, 2),
            ),
            1,
        )


class BridgeTests(unittest.TestCase):
    def test_full_bridge_turns_doubling_into_exponential_purchasing_power(self) -> None:
        bridge = PriceBridge(Fraction(1), Fraction(1), 1)
        points = simulate(
            [direct_capability_doubling(t) for t in range(7)],
            bridge=bridge,
            protected_benefits=[Fraction(1)] * 7,
            deviations=[Fraction(8)] * 7,
        )
        self.assertEqual([p.multiplier for p in points], [Fraction(2**t) for t in range(7)])
        self.assertEqual(first_alignment_epoch(points), 4)

    def test_partial_automation_and_pass_through_create_a_price_floor(self) -> None:
        bridge = PriceBridge(Fraction(3, 4), Fraction(4, 5), 1)
        self.assertEqual(bridge.normalized_price_floor, Fraction(2, 5))
        for epoch in range(32):
            price = normalized_basket_price(direct_capability_doubling(epoch), bridge)
            self.assertGreater(price, bridge.normalized_price_floor)
            self.assertLess(purchasing_power_multiplier(price), Fraction(5, 2))

    def test_intelligence_doubling_alone_is_not_alignment(self) -> None:
        bridge = PriceBridge(Fraction(3, 4), Fraction(4, 5), 1)
        points = simulate(
            [direct_capability_doubling(t) for t in range(32)],
            bridge=bridge,
            protected_benefits=[Fraction(1)] * 32,
            deviations=[Fraction(3)] * 32,
        )
        self.assertIsNone(first_alignment_epoch(points))
        self.assertTrue(
            bounded_reward_blocks_alignment(
                multiplier_cap=Fraction(5, 2),
                benefit_cap=Fraction(1),
                deviation_floor=Fraction(3),
            )
        )

    def test_rebound_surcharge_can_reverse_the_core_price_gain(self) -> None:
        bridge = PriceBridge(Fraction(1), Fraction(1), 1)
        points = simulate(
            [direct_capability_doubling(t) for t in range(8)],
            bridge=bridge,
            protected_benefits=[Fraction(1)] * 8,
            deviations=[Fraction(2)] * 8,
            surcharges=[Fraction(2**t - 1, 2**t) for t in range(8)],
        )
        self.assertEqual([p.adjusted_price for p in points], [Fraction(1)] * 8)
        self.assertTrue(all(not p.aligned for p in points))

    def test_strict_boundary_rejects_equality(self) -> None:
        self.assertFalse(
            aligned(multiplier=Fraction(2), protected_benefit=Fraction(3), deviation=Fraction(6))
        )
        self.assertTrue(
            aligned(multiplier=Fraction(2), protected_benefit=Fraction(3), deviation=Fraction(5))
        )


class TauSemanticGateTests(unittest.TestCase):
    def test_complete_nine_bit_gate_accepts_only_all_true(self) -> None:
        names = tuple(DacGateFacts.__dataclass_fields__)
        accepted = []
        for row, values in enumerate(itertools.product((False, True), repeat=len(names))):
            facts = DacGateFacts(**dict(zip(names, values, strict=True)))
            if dac_treasury_admits(facts):
                accepted.append((row, values))
        self.assertEqual(accepted, [(511, (True,) * 9)])

    def test_every_single_fault_fails_closed(self) -> None:
        all_true = DacGateFacts(*(True,) * 9)
        self.assertTrue(dac_treasury_admits(all_true))
        for name in DacGateFacts.__dataclass_fields__:
            with self.subTest(name=name):
                self.assertFalse(dac_treasury_admits(replace(all_true, **{name: False})))


if __name__ == "__main__":
    unittest.main()
