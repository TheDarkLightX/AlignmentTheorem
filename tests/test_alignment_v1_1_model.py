from __future__ import annotations

import itertools
import unittest
from dataclasses import replace

from verification.alignment_v1_1_model import (
    MAX_U64,
    EligibilityFacts,
    HyperdeflationEnvelope,
    evaluate_reference_eligibility,
)


class HyperdeflationMarginTests(unittest.TestCase):
    def test_minimum_multiplier_is_strict_boundary(self) -> None:
        # Arrange: coefficient = 3 and complete opposing bound = 10.
        envelope = HyperdeflationEnvelope(
            scarcity_multiplier=1,
            ethical_reward_coefficient=2,
            exclusive_upside_coefficient=1,
            max_private_deviation_gain=7,
            max_extra_compliance_cost=2,
            optimizer_error=1,
        )

        # Act
        threshold = envelope.minimum_scarcity_multiplier()
        below = replace(envelope, scarcity_multiplier=threshold - 1)
        at = replace(envelope, scarcity_multiplier=threshold)

        # Assert: equality at 3 * 3 = 9 does not clear the bound of 10.
        self.assertEqual(threshold, 4)
        self.assertFalse(below.has_strict_hyperdeflation_margin)
        self.assertTrue(at.has_strict_hyperdeflation_margin)

    def test_zero_ethical_exposure_has_no_scarcity_threshold(self) -> None:
        # Arrange
        envelope = HyperdeflationEnvelope(
            scarcity_multiplier=MAX_U64,
            ethical_reward_coefficient=0,
            exclusive_upside_coefficient=0,
            max_private_deviation_gain=0,
            max_extra_compliance_cost=0,
        )

        # Act / Assert
        self.assertFalse(envelope.has_strict_hyperdeflation_margin)
        with self.assertRaisesRegex(ValueError, "positive eligible scarcity exposure"):
            envelope.minimum_scarcity_multiplier()

    def test_common_scaling_does_not_create_alignment(self) -> None:
        # Arrange / Act / Assert: deviation opportunity grows at the same rate
        # and coefficient, so scarcity never creates a strict advantage.
        for scarcity in range(1, 50):
            with self.subTest(scarcity=scarcity):
                envelope = HyperdeflationEnvelope(
                    scarcity_multiplier=scarcity,
                    ethical_reward_coefficient=2,
                    exclusive_upside_coefficient=0,
                    max_private_deviation_gain=2 * scarcity,
                    max_extra_compliance_cost=0,
                )
                self.assertFalse(envelope.has_strict_hyperdeflation_margin)

    def test_faster_deviation_growth_defeats_hyperdeflation(self) -> None:
        # Arrange / Act / Assert: a quadratic deviation opportunity dominates
        # a linear scarcity-amplified ethical entitlement.
        for scarcity in range(2, 50):
            with self.subTest(scarcity=scarcity):
                envelope = HyperdeflationEnvelope(
                    scarcity_multiplier=scarcity,
                    ethical_reward_coefficient=1,
                    exclusive_upside_coefficient=0,
                    max_private_deviation_gain=scarcity * scarcity,
                    max_extra_compliance_cost=0,
                )
                self.assertFalse(envelope.has_strict_hyperdeflation_margin)

    def test_margin_is_monotone_for_a_fixed_envelope(self) -> None:
        # Arrange
        base = HyperdeflationEnvelope(
            scarcity_multiplier=1,
            ethical_reward_coefficient=3,
            exclusive_upside_coefficient=2,
            max_private_deviation_gain=20,
            max_extra_compliance_cost=4,
            optimizer_error=1,
        )
        threshold = base.minimum_scarcity_multiplier()

        # Act / Assert
        outcomes = [
            replace(base, scarcity_multiplier=value).has_strict_hyperdeflation_margin
            for value in range(1, threshold + 10)
        ]
        first_true = outcomes.index(True)
        self.assertEqual(first_true + 1, threshold)
        self.assertTrue(all(outcomes[first_true:]))

    def test_exhaustive_small_domain_matches_raw_utility_oracle(self) -> None:
        # Arrange / Act: exhaustive finite pressure over 3,125 configurations.
        for scarcity, reward, exclusive_upside, gain, cost in itertools.product(
            range(5), repeat=5
        ):
            with self.subTest(
                scarcity=scarcity,
                reward=reward,
                exclusive_upside=exclusive_upside,
                gain=gain,
                cost=cost,
            ):
                envelope = HyperdeflationEnvelope(
                    scarcity_multiplier=scarcity,
                    ethical_reward_coefficient=reward,
                    exclusive_upside_coefficient=exclusive_upside,
                    max_private_deviation_gain=gain,
                    max_extra_compliance_cost=cost,
                    optimizer_error=1,
                )
                ethical_utility = scarcity * (reward + exclusive_upside) - cost
                nonethical_utility = gain

                # Assert: direct utility comparison is an independent oracle.
                self.assertEqual(
                    envelope.has_strict_hyperdeflation_margin,
                    ethical_utility > nonethical_utility + 1,
                )
                self.assertEqual(envelope.eligible_utility_lower, ethical_utility)
                self.assertEqual(envelope.excluded_utility_upper, nonethical_utility)

    def test_exclusion_never_debits_the_excluded_branch(self) -> None:
        for scarcity in (1, 2, 10, 1_000):
            with self.subTest(scarcity=scarcity):
                envelope = HyperdeflationEnvelope(
                    scarcity_multiplier=scarcity,
                    ethical_reward_coefficient=2,
                    exclusive_upside_coefficient=3,
                    max_private_deviation_gain=7,
                    max_extra_compliance_cost=1,
                )
                self.assertEqual(envelope.excluded_utility_upper, 7)

    def test_rejects_bool_out_of_range_and_derived_overflow(self) -> None:
        valid = {
            "scarcity_multiplier": 1,
            "ethical_reward_coefficient": 1,
            "exclusive_upside_coefficient": 0,
            "max_private_deviation_gain": 0,
            "max_extra_compliance_cost": 0,
        }
        for field in valid:
            with self.subTest(field=field), self.assertRaises(TypeError):
                HyperdeflationEnvelope(**(valid | {field: True}))

        with self.assertRaises(ValueError):
            HyperdeflationEnvelope(**(valid | {"scarcity_multiplier": MAX_U64 + 1}))
        with self.assertRaisesRegex(ValueError, "mechanism_advantage"):
            HyperdeflationEnvelope(
                **(
                    valid
                    | {
                        "scarcity_multiplier": MAX_U64,
                        "ethical_reward_coefficient": 2,
                    }
                )
            )


class HyperdeflationEligibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.envelope = HyperdeflationEnvelope(
            scarcity_multiplier=10,
            ethical_reward_coefficient=1,
            exclusive_upside_coefficient=1,
            max_private_deviation_gain=5,
            max_extra_compliance_cost=1,
        )

    def test_accepts_authenticated_ethical_funded_strict_margin(self) -> None:
        # Arrange
        facts = EligibilityFacts(
            eetf_authenticated=True,
            action_ethical=True,
        )

        # Act
        decision = evaluate_reference_eligibility(
            facts,
            self.envelope,
            requested_reward_atoms=5,
            reserve_atoms=5,
        )

        # Assert
        self.assertTrue(decision.reference_eligible)
        self.assertFalse(decision.authority_granted)
        with self.assertRaises(TypeError):
            type(decision)(True, True, True, authority_granted=True)
        self.assertTrue(decision.strict_hyperdeflation_margin)
        self.assertTrue(decision.reward_funded)

    def test_complete_tau_boolean_surface_is_fail_closed(self) -> None:
        # Arrange / Act / Assert
        for authenticated, ethical, margin, funded in itertools.product(
            (False, True), repeat=4
        ):
            with self.subTest(
                authenticated=authenticated,
                ethical=ethical,
                margin=margin,
                funded=funded,
            ):
                facts = EligibilityFacts(authenticated, ethical)
                envelope = replace(
                    self.envelope,
                    scarcity_multiplier=10 if margin else 1,
                )
                reward, reserve = (1, 1) if funded else (1, 0)
                decision = evaluate_reference_eligibility(
                    facts,
                    envelope,
                    requested_reward_atoms=reward,
                    reserve_atoms=reserve,
                )
                self.assertEqual(
                    decision.reference_eligible,
                    authenticated and ethical and margin and funded,
                )
                self.assertFalse(decision.authority_granted)

    def test_rejects_mapping_shaped_assessment_and_envelope(self) -> None:
        facts = EligibilityFacts(True, True)
        with self.assertRaises(TypeError):
            evaluate_reference_eligibility(
                {"eetf_authenticated": True, "action_ethical": True},
                self.envelope,
                requested_reward_atoms=1,
                reserve_atoms=1,
            )
        with self.assertRaises(TypeError):
            evaluate_reference_eligibility(
                facts,
                {"scarcity_multiplier": 10},
                requested_reward_atoms=1,
                reserve_atoms=1,
            )

    def test_assessment_requires_exact_booleans(self) -> None:
        for value in (1, "true", object()):
            with self.subTest(value=value), self.assertRaises(TypeError):
                EligibilityFacts(value, True)

    def test_claimed_facts_can_never_create_authority(self) -> None:
        # Arrange: reproduce the peer review's all-true claimed-fact example.
        envelope = HyperdeflationEnvelope(10, 1, 1, 5, 1)
        facts = EligibilityFacts(True, True)

        # Act
        decision = evaluate_reference_eligibility(
            facts,
            envelope,
            requested_reward_atoms=1,
            reserve_atoms=1,
        )

        # Assert: the arithmetic hypothesis passes while authority stays absent.
        self.assertTrue(decision.reference_eligible)
        self.assertFalse(decision.authority_granted)


if __name__ == "__main__":
    unittest.main()
