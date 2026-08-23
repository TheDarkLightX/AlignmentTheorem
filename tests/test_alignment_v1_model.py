from __future__ import annotations

import unittest

from verification.alignment_v1_model import (
    EETF_SCALE,
    MAX_ATOMS,
    V1ExclusionPayoff,
    common_upside_cancels,
    direct_reward_coefficient_scaled,
    exclusive_upside_coefficient_scaled,
    is_ethical,
    paper_v1_epoch,
    tier_multiplier,
)


class V1ExclusionModelTests(unittest.TestCase):
    def test_eetf_boundaries_and_tiers_match_the_paper(self) -> None:
        expected = {
            0: (False, 0),
            999: (False, 0),
            1000: (True, 1),
            1499: (True, 1),
            1500: (True, 3),
            1999: (True, 3),
            2000: (True, 5),
            3000: (True, 5),
        }
        for eetf, (ethical, tier) in expected.items():
            with self.subTest(eetf=eetf):
                self.assertEqual(is_ethical(eetf), ethical)
                self.assertEqual(tier_multiplier(eetf), tier)

    def test_exclusion_is_opportunity_cost_and_not_a_debit(self) -> None:
        payoff = V1ExclusionPayoff(
            scarcity_multiplier=7,
            direct_reward_coefficient=11,
            exclusive_scarcity_upside_coefficient=13,
            deviation_gain=100,
        )
        self.assertEqual(payoff.eligible_utility, 168)
        self.assertEqual(payoff.excluded_utility, 100)
        self.assertEqual(payoff.historical_eligible_utility, 77)
        self.assertEqual(payoff.historical_excluded_relative_utility, 9)
        self.assertTrue(payoff.historical_and_normalized_order_agree)
        self.assertTrue(payoff.strict_margin_holds)

    def test_exact_threshold_is_least_strict_integer_multiplier(self) -> None:
        for direct in range(0, 5):
            for upside in range(0, 5):
                if direct + upside == 0:
                    continue
                for gain in range(0, 25):
                    probe = V1ExclusionPayoff(1, direct, upside, gain)
                    threshold = probe.minimum_scarcity_multiplier
                    at_threshold = V1ExclusionPayoff(
                        threshold, direct, upside, gain
                    )
                    self.assertTrue(at_threshold.strict_margin_holds)
                    if threshold > 1:
                        below = V1ExclusionPayoff(
                            threshold - 1, direct, upside, gain
                        )
                        self.assertFalse(below.strict_margin_holds)

    def test_zero_deviation_case_holds_for_every_positive_scarcity(self) -> None:
        for scarcity in range(1, 33):
            payoff = V1ExclusionPayoff(scarcity, 0, 1, 0)
            self.assertTrue(payoff.strict_margin_holds)

    def test_paper_terms_bind_eetf_tier_and_exclusion_upside(self) -> None:
        payoff = paper_v1_epoch(
            balance=2,
            exposure=3,
            scarcity_multiplier=5,
            network_eetf_milli=1300,
            ethical_eetf_milli=EETF_SCALE,
            excluded_eetf_milli=900,
            deviation_gain_scaled=1_000_000,
        )
        self.assertEqual(
            payoff.direct_reward_coefficient,
            direct_reward_coefficient_scaled(2, EETF_SCALE),
        )
        self.assertEqual(
            payoff.exclusive_scarcity_upside_coefficient,
            exclusive_upside_coefficient_scaled(3, 1300, 900),
        )
        self.assertTrue(payoff.historical_and_normalized_order_agree)

    def test_common_scarcity_upside_cannot_create_alignment(self) -> None:
        for common in (0, 1, 1_000_000):
            self.assertTrue(common_upside_cancels(common, 5, 7))
            self.assertTrue(common_upside_cancels(common, 7, 5))
            self.assertTrue(common_upside_cancels(common, 5, 5))

    def test_invalid_types_bounds_and_overflow_fail_closed(self) -> None:
        for bad in (True, -1, MAX_ATOMS + 1, "1"):
            with self.subTest(bad=bad):
                with self.assertRaises((TypeError, ValueError)):
                    V1ExclusionPayoff(bad, 1, 1, 0)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            V1ExclusionPayoff(1, 0, 0, 0)
        with self.assertRaises(ValueError):
            V1ExclusionPayoff(MAX_ATOMS, 1, 1, 0)
        with self.assertRaises(ValueError):
            tier_multiplier(3001)
        with self.assertRaises(ValueError):
            exclusive_upside_coefficient_scaled(1, 1000, 1000)


if __name__ == "__main__":
    unittest.main()
