from __future__ import annotations

import itertools
import unittest
from dataclasses import replace
from fractions import Fraction

from verification.alignment_v2_model import (
    MAX_CANDIDATES,
    MAX_U64,
    CandidateAction,
    IncentiveEnvelope,
    PolicyEvidence,
    RejectCode,
    choose_most_profitable_admissible_action,
    evaluate_policy_gate,
)

COMPLIANT = PolicyEvidence(
    policy_root_matches=True,
    evidence_authenticated=True,
    action_known=True,
    action_policy_compliant=True,
    nonce_fresh=True,
    task_unclaimed=True,
)


class PolicyGateTests(unittest.TestCase):
    def test_accepts_funded_authenticated_compliant_action(self) -> None:
        # Arrange
        reserve = 100

        # Act
        decision = evaluate_policy_gate(
            COMPLIANT,
            requested_reward_atoms=40,
            reserve_atoms=reserve,
        )

        # Assert
        self.assertTrue(decision.accepted)
        self.assertEqual(decision.code, RejectCode.ACCEPTED)
        self.assertEqual(decision.payout_atoms, 40)
        self.assertEqual(decision.reserve_post_atoms, 60)

    def test_each_failed_obligation_rejects_without_effect(self) -> None:
        # Arrange
        mutations = {
            "policy_root_matches": RejectCode.POLICY_ROOT_MISMATCH,
            "evidence_authenticated": RejectCode.EVIDENCE_UNAUTHENTICATED,
            "action_known": RejectCode.UNKNOWN_ACTION,
            "action_policy_compliant": RejectCode.POLICY_VIOLATION,
            "nonce_fresh": RejectCode.STALE_NONCE,
            "task_unclaimed": RejectCode.TASK_ALREADY_CLAIMED,
        }

        for field, expected_code in mutations.items():
            with self.subTest(field=field):
                evidence = replace(COMPLIANT, **{field: False})

                # Act
                decision = evaluate_policy_gate(
                    evidence,
                    requested_reward_atoms=1,
                    reserve_atoms=10,
                )

                # Assert
                self.assertFalse(decision.accepted)
                self.assertEqual(decision.code, expected_code)
                self.assertEqual(decision.payout_atoms, 0)
                self.assertEqual(decision.reserve_post_atoms, 10)

    def test_reward_reserve_boundary_values(self) -> None:
        cases = (
            (0, 0, True, 0),
            (1, 0, False, 0),
            (1, 1, True, 0),
            (MAX_U64 - 1, MAX_U64, True, 1),
            (MAX_U64, MAX_U64, True, 0),
        )
        for reward, reserve, accepted, post in cases:
            with self.subTest(reward=reward, reserve=reserve):
                # Act
                decision = evaluate_policy_gate(
                    COMPLIANT,
                    requested_reward_atoms=reward,
                    reserve_atoms=reserve,
                )

                # Assert
                self.assertEqual(decision.accepted, accepted)
                self.assertEqual(decision.reserve_post_atoms, post)

    def test_rejects_bool_and_out_of_range_amounts(self) -> None:
        for value in (True, -1, MAX_U64 + 1):
            with self.subTest(value=value), self.assertRaises((TypeError, ValueError)):
                evaluate_policy_gate(
                    COMPLIANT,
                    requested_reward_atoms=value,
                    reserve_atoms=10,
                )

    def test_rejects_non_boolean_evidence_fields(self) -> None:
        # Arrange / Act / Assert: truthy integers cannot forge host facts.
        for value in (1, "true", object()):
            with self.subTest(value=value), self.assertRaises(TypeError):
                PolicyEvidence(
                    policy_root_matches=value,
                    evidence_authenticated=True,
                    action_known=True,
                    action_policy_compliant=True,
                    nonce_fresh=True,
                    task_unclaimed=True,
                )

    def test_gate_rejects_mapping_shaped_evidence(self) -> None:
        # Arrange
        forged = {
            "policy_root_matches": True,
            "evidence_authenticated": True,
            "action_known": True,
            "action_policy_compliant": True,
            "nonce_fresh": True,
            "task_unclaimed": True,
        }

        # Act / Assert
        with self.assertRaises(TypeError):
            evaluate_policy_gate(
                forged,
                requested_reward_atoms=1,
                reserve_atoms=1,
            )

    def test_complete_boolean_surface_matches_tau_conjunction(self) -> None:
        for bits in itertools.product((False, True), repeat=7):
            with self.subTest(bits=bits):
                # Arrange: the seventh Tau fact is derived by exact reserve math.
                evidence = PolicyEvidence(*bits[:6])
                reward = 0 if bits[6] else 1

                # Act
                decision = evaluate_policy_gate(
                    evidence,
                    requested_reward_atoms=reward,
                    reserve_atoms=0,
                )

                # Assert
                self.assertEqual(decision.accepted, all(bits))


class IncentiveTheoremTests(unittest.TestCase):
    def test_strict_margin_is_required_at_equality_boundary(self) -> None:
        # Arrange
        envelope = IncentiveEnvelope(
            compliant_reward_atoms=10,
            noncompliant_reward_atoms=0,
            slash_atoms=10,
            detection_probability=Fraction(1, 2),
            max_private_deviation_gain_atoms=12,
            max_extra_compliance_cost_atoms=2,
            optimizer_error_atoms=1,
        )

        # Act / Assert: mechanism gap = required gap = 15.
        self.assertEqual(envelope.mechanism_gap, 15)
        self.assertEqual(envelope.required_gap, 15)
        self.assertFalse(envelope.has_strict_alignment_margin)

        # One additional reward atom creates a strict margin.
        stronger = replace(envelope, compliant_reward_atoms=11)
        self.assertTrue(stronger.has_strict_alignment_margin)

    def test_zero_detection_can_leave_profitable_deviation(self) -> None:
        # Arrange
        envelope = IncentiveEnvelope(
            compliant_reward_atoms=5,
            noncompliant_reward_atoms=0,
            slash_atoms=MAX_U64,
            detection_probability=Fraction(0, 1),
            max_private_deviation_gain_atoms=6,
            max_extra_compliance_cost_atoms=0,
        )

        # Act / Assert
        self.assertFalse(envelope.has_strict_alignment_margin)

    def test_rejects_fraction_subclass_at_probability_boundary(self) -> None:
        # Arrange
        class HostileFraction(Fraction):
            pass

        # Act / Assert
        with self.assertRaises(TypeError):
            IncentiveEnvelope(
                compliant_reward_atoms=1,
                noncompliant_reward_atoms=0,
                slash_atoms=0,
                detection_probability=HostileFraction(0, 1),
                max_private_deviation_gain_atoms=0,
                max_extra_compliance_cost_atoms=0,
            )

    def test_reward_only_margin_can_align_without_punishment(self) -> None:
        # Arrange: reward advantage 11 exceeds gain 7 + cost 2 + error 1.
        envelope = IncentiveEnvelope(
            compliant_reward_atoms=11,
            noncompliant_reward_atoms=0,
            slash_atoms=0,
            detection_probability=Fraction(0, 1),
            max_private_deviation_gain_atoms=7,
            max_extra_compliance_cost_atoms=2,
            optimizer_error_atoms=1,
        )

        # Act / Assert
        self.assertTrue(envelope.has_strict_alignment_margin)

    def test_exhaustive_small_domain_matches_independent_utility_oracle(self) -> None:
        values = range(3)
        probabilities = (Fraction(0), Fraction(1, 2), Fraction(1))
        for reward_c, reward_n, slash, gain, cost, error, probability in itertools.product(
            values,
            values,
            values,
            values,
            values,
            values,
            probabilities,
        ):
            envelope = IncentiveEnvelope(
                compliant_reward_atoms=reward_c,
                noncompliant_reward_atoms=reward_n,
                slash_atoms=slash,
                detection_probability=probability,
                max_private_deviation_gain_atoms=gain,
                max_extra_compliance_cost_atoms=cost,
                optimizer_error_atoms=error,
            )

            # Independent oracle: normalize compliant private utility to zero.
            compliant_lower_bound = Fraction(reward_c - cost)
            deviation_upper_bound = Fraction(gain + reward_n) - probability * slash
            oracle = compliant_lower_bound > deviation_upper_bound + error

            self.assertEqual(envelope.has_strict_alignment_margin, oracle)


class VerifierConditionedAgentTests(unittest.TestCase):
    def test_untrusted_profit_seeker_cannot_select_rejected_action(self) -> None:
        # Arrange: the policy-violating proposal has much greater private profit.
        ethical_work = CandidateAction(
            action_id="ethical-work",
            evidence=COMPLIANT,
            private_profit_atoms=10,
            requested_reward_atoms=5,
        )
        forbidden_work = CandidateAction(
            action_id="forbidden-work",
            evidence=replace(COMPLIANT, action_policy_compliant=False),
            private_profit_atoms=10_000,
            requested_reward_atoms=0,
        )

        # Act
        choice = choose_most_profitable_admissible_action(
            [forbidden_work, ethical_work],
            reserve_atoms=100,
        )

        # Assert
        self.assertIsNotNone(choice.action)
        self.assertEqual(choice.action.action_id, "ethical-work")
        self.assertEqual(choice.total_profit_atoms, 15)

    def test_no_admissible_action_returns_safe_noop(self) -> None:
        # Arrange
        rejected = CandidateAction(
            action_id="stale",
            evidence=replace(COMPLIANT, nonce_fresh=False),
            private_profit_atoms=100,
            requested_reward_atoms=0,
        )

        # Act
        choice = choose_most_profitable_admissible_action(
            [rejected],
            reserve_atoms=0,
        )

        # Assert
        self.assertIsNone(choice.action)
        self.assertIsNone(choice.decision)
        self.assertEqual(choice.total_profit_atoms, 0)

    def test_tie_breaking_is_deterministic(self) -> None:
        # Arrange
        actions = [
            CandidateAction("zeta", COMPLIANT, 5, 5),
            CandidateAction("alpha", COMPLIANT, 8, 2),
        ]

        # Act
        forward = choose_most_profitable_admissible_action(actions, reserve_atoms=10)
        reverse = choose_most_profitable_admissible_action(
            reversed(actions), reserve_atoms=10
        )

        # Assert
        self.assertEqual(forward.action.action_id, "alpha")
        self.assertEqual(reverse.action.action_id, "alpha")

    def test_rejects_ambiguous_duplicate_action_ids(self) -> None:
        # Arrange
        duplicate_ids = [
            CandidateAction("same", COMPLIANT, 1, 0),
            CandidateAction("same", COMPLIANT, 2, 0),
        ]

        # Act / Assert
        with self.assertRaisesRegex(ValueError, "duplicate action_id"):
            choose_most_profitable_admissible_action(duplicate_ids, reserve_atoms=0)

    def test_rejects_noncanonical_action_ids(self) -> None:
        for action_id in ("", "Uppercase", "space id", "éthique", "a" * 65):
            with self.subTest(action_id=action_id), self.assertRaises(TypeError):
                CandidateAction(action_id, COMPLIANT, 0, 0)

    def test_candidate_count_is_bounded(self) -> None:
        # Arrange: a generator verifies that the function cannot silently
        # materialize or scan an attacker-controlled unbounded stream.
        candidates = (
            CandidateAction(f"a{index}", COMPLIANT, 0, 0)
            for index in range(MAX_CANDIDATES + 1)
        )

        # Act / Assert
        with self.assertRaisesRegex(ValueError, "candidate count exceeds"):
            choose_most_profitable_admissible_action(candidates, reserve_atoms=0)

    def test_rejects_mapping_shaped_candidate(self) -> None:
        # Arrange
        forged = {"action_id": "forged"}

        # Act / Assert
        with self.assertRaises(TypeError):
            choose_most_profitable_admissible_action([forged], reserve_atoms=0)


if __name__ == "__main__":
    unittest.main()
