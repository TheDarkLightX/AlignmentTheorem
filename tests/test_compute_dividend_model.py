from __future__ import annotations

import itertools
import unittest
from dataclasses import replace
from fractions import Fraction

from verification.compute_dividend_model import (
    MAX_ALLOCATION_BUDGET_ATOMS,
    AllocationPolicy,
    DividendObligations,
    DividendRejectCode,
    ExternalWealthEvidence,
    Household,
    RentBudget,
    WealthObligations,
    WealthPlan,
    WealthPolicyLimits,
    WealthRejectCode,
    allocate_prioritarian,
    choose_wealth_plan,
    dividend_admits,
    empirical_tail_loss,
    evaluate_wealth_plan,
    exhaustive_optimal_welfare,
    modeled_loss_preserves_floor,
    progressive_transfer_delta,
    settle_dividend,
    wealth_admits,
)

DIVIDEND_READY = DividendObligations(*(True,) * 8)
WEALTH_EXTERNAL_READY = ExternalWealthEvidence(*(True,) * 4)
WEALTH_LIMITS = WealthPolicyLimits(
    max_issuer_concentration_bps=2_000,
    max_empirical_tail_loss_atoms=10,
    tail_scenario_count=2,
    max_annual_fee_bps=50,
    max_turnover_bps=2_000,
)
SAFE_PLAN = WealthPlan(
    plan_id="diversified-index",
    declared_score_atoms=10,
    leverage_bps=0,
    short_exposure_bps=0,
    issuer_concentration_bps=500,
    annual_fee_bps=5,
    turnover_bps=100,
    scenario_losses_atoms=(0, 2, 4, 6),
)


class RentAndDividendTests(unittest.TestCase):
    def test_funded_rent_budget_conserves_gross_rent(self) -> None:
        budget = RentBudget(100, 25, 15)

        self.assertTrue(budget.senior_claims_funded)
        self.assertEqual(budget.distributable_atoms, 60)
        self.assertEqual(
            budget.incremental_grid_cost_atoms
            + budget.public_reserve_atoms
            + budget.distributable_atoms,
            budget.gross_rent_atoms,
        )

    def test_underfunded_senior_claims_fail_closed(self) -> None:
        budget = RentBudget(10, 8, 3)

        self.assertFalse(budget.senior_claims_funded)
        self.assertEqual(budget.distributable_atoms, 0)

    def test_zero_profit_share_cannot_fund_a_positive_floor(self) -> None:
        # Countermodel to a universal post-AGI rent claim: if a profit-only
        # payment yields zero gross rent, even one positive floor is infeasible.
        budget = RentBudget(0, 0, 0)
        result = allocate_prioritarian(
            (Household("a", 0),),
            earmarked_budget_atoms=budget.distributable_atoms,
            policy=AllocationPolicy(1, Fraction(1)),
        )

        self.assertFalse(result.feasible)
        self.assertEqual(result.failure_code, "FLOOR_EXCEEDS_SHARE_CAP")

    def test_dividend_acceptance_conserves_distributable_reserve(self) -> None:
        decision = settle_dividend(
            DIVIDEND_READY,
            requested_atoms=40,
            distributable_reserve_atoms=60,
        )

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.code, DividendRejectCode.ACCEPTED)
        self.assertEqual(decision.reserve_post_atoms + decision.payout_atoms, 60)

    def test_each_dividend_obligation_rejects_as_noop(self) -> None:
        expected_codes = (
            DividendRejectCode.POLICY_ROOT_MISMATCH,
            DividendRejectCode.RENT_RECEIPT_UNAUTHENTICATED,
            DividendRejectCode.GRID_COSTS_NOT_RESERVED,
            DividendRejectCode.DIVIDEND_RESERVE_UNFUNDED,
            DividendRejectCode.RECIPIENT_INELIGIBLE,
            DividendRejectCode.STALE_NONCE,
            DividendRejectCode.CONCENTRATION_CAP_VIOLATION,
            DividendRejectCode.AGENT_COMPUTE_UNFUNDED,
        )
        for field, expected_code in zip(
            DIVIDEND_READY.__dataclass_fields__, expected_codes, strict=True
        ):
            with self.subTest(field=field):
                obligations = replace(DIVIDEND_READY, **{field: False})
                decision = settle_dividend(
                    obligations,
                    requested_atoms=1,
                    distributable_reserve_atoms=10,
                )
                self.assertFalse(decision.accepted)
                self.assertEqual(decision.code, expected_code)
                self.assertEqual(decision.payout_atoms, 0)
                self.assertEqual(decision.reserve_post_atoms, 10)

    def test_caller_funded_fact_cannot_override_exact_reserve(self) -> None:
        decision = settle_dividend(
            DIVIDEND_READY,
            requested_atoms=11,
            distributable_reserve_atoms=10,
        )

        self.assertFalse(decision.accepted)
        self.assertEqual(
            decision.code, DividendRejectCode.INSUFFICIENT_DISTRIBUTABLE_RESERVE
        )
        self.assertEqual(decision.reserve_post_atoms, 10)

    def test_complete_dividend_boolean_surface_is_conjunction(self) -> None:
        for bits in itertools.product((False, True), repeat=8):
            with self.subTest(bits=bits):
                self.assertEqual(dividend_admits(DividendObligations(*bits)), all(bits))

    def test_truthy_values_cannot_forge_dividend_facts(self) -> None:
        with self.assertRaises(TypeError):
            DividendObligations(1, True, True, True, True, True, True, True)


class PrioritarianAllocationTests(unittest.TestCase):
    def test_floor_priority_and_share_cap_bind(self) -> None:
        households = (
            Household("poor", 0),
            Household("middle", 4),
            Household("rich", 9),
        )
        policy = AllocationPolicy(1, Fraction(1, 2))

        result = allocate_prioritarian(
            households, earmarked_budget_atoms=6, policy=policy
        )

        self.assertTrue(result.feasible)
        self.assertEqual(result.by_household(), {"middle": 2, "poor": 3, "rich": 1})
        self.assertEqual(result.spent_atoms, 6)
        self.assertEqual(result.unspent_atoms, 0)
        self.assertEqual(result.per_household_cap_atoms, 3)
        self.assertTrue(all(amount >= 1 for amount in result.by_household().values()))
        self.assertTrue(all(amount <= 3 for amount in result.by_household().values()))

    def test_floor_feasibility_bound_is_exact_for_uniform_floor(self) -> None:
        households = tuple(Household(f"h{index}", index) for index in range(3))

        underfunded = allocate_prioritarian(
            households,
            earmarked_budget_atoms=5,
            policy=AllocationPolicy(2, Fraction(1)),
        )
        funded = allocate_prioritarian(
            households,
            earmarked_budget_atoms=6,
            policy=AllocationPolicy(2, Fraction(1)),
        )

        self.assertFalse(underfunded.feasible)
        self.assertEqual(underfunded.failure_code, "UNIVERSAL_FLOOR_UNFUNDED")
        self.assertTrue(funded.feasible)
        self.assertEqual(funded.by_household(), {"h0": 2, "h1": 2, "h2": 2})

    def test_share_cap_can_make_floor_infeasible(self) -> None:
        result = allocate_prioritarian(
            (Household("a", 0), Household("b", 0)),
            earmarked_budget_atoms=10,
            policy=AllocationPolicy(3, Fraction(1, 4)),
        )

        self.assertFalse(result.feasible)
        self.assertEqual(result.failure_code, "FLOOR_EXCEEDS_SHARE_CAP")

    def test_cap_can_leave_budget_unspent_without_breaking_constraints(self) -> None:
        result = allocate_prioritarian(
            (Household("a", 0), Household("b", 0)),
            earmarked_budget_atoms=10,
            policy=AllocationPolicy(0, Fraction(1, 4)),
        )

        self.assertTrue(result.feasible)
        self.assertEqual(result.by_household(), {"a": 2, "b": 2})
        self.assertEqual(result.unspent_atoms, 6)

    def test_tie_break_is_identifier_stable_not_input_order(self) -> None:
        policy = AllocationPolicy(0, Fraction(1))
        forward = allocate_prioritarian(
            (Household("a", 0), Household("b", 0)),
            earmarked_budget_atoms=1,
            policy=policy,
        )
        reverse = allocate_prioritarian(
            (Household("b", 0), Household("a", 0)),
            earmarked_budget_atoms=1,
            policy=policy,
        )

        self.assertEqual(forward.by_household(), {"a": 1, "b": 0})
        self.assertEqual(reverse.by_household(), forward.by_household())

    def test_reference_allocator_rejects_unbounded_work_request(self) -> None:
        with self.assertRaises(ValueError):
            allocate_prioritarian(
                (Household("a", 0),),
                earmarked_budget_atoms=MAX_ALLOCATION_BUDGET_ATOMS + 1,
                policy=AllocationPolicy(0, Fraction(1)),
            )

    def test_progressive_transfer_is_strict_only_beyond_adjacent_levels(self) -> None:
        self.assertGreater(progressive_transfer_delta(2, 5), 0)
        self.assertEqual(progressive_transfer_delta(2, 3), 0)
        self.assertLess(progressive_transfer_delta(5, 2), 0)

    def test_priority_weights_can_override_wealth_priority(self) -> None:
        # Negative result: concavity alone is not enough if political weights
        # are allowed to encode extreme privilege.
        result = allocate_prioritarian(
            (Household("poor", 0, 1), Household("rich", 100, 1_000)),
            earmarked_budget_atoms=1,
            policy=AllocationPolicy(0, Fraction(1)),
        )

        self.assertEqual(result.by_household(), {"poor": 0, "rich": 1})

    def test_greedy_optimizer_matches_independent_exhaustive_oracle(self) -> None:
        ids = ("a", "b", "c")
        checked = 0
        for count in range(1, 4):
            for bases in itertools.product(range(3), repeat=count):
                for weights in itertools.product((1, 2), repeat=count):
                    households = tuple(
                        Household(ids[index], bases[index], weights[index])
                        for index in range(count)
                    )
                    for budget in range(7):
                        for floor in (0, 1):
                            for share in (Fraction(1), Fraction(1, 2), Fraction(2, 3)):
                                policy = AllocationPolicy(floor, share)
                                result = allocate_prioritarian(
                                    households,
                                    earmarked_budget_atoms=budget,
                                    policy=policy,
                                )
                                oracle = exhaustive_optimal_welfare(
                                    households,
                                    earmarked_budget_atoms=budget,
                                    policy=policy,
                                )
                                self.assertEqual(result.feasible, oracle is not None)
                                if result.feasible:
                                    self.assertEqual(result.welfare_gain, oracle)
                                checked += 1
        self.assertEqual(checked, 10_836)


class WealthAgentTests(unittest.TestCase):
    def test_exact_one_period_loss_budget_preserves_declared_floor(self) -> None:
        self.assertTrue(
            modeled_loss_preserves_floor(
                wealth_atoms=100, protected_floor_atoms=70, modeled_loss_atoms=30
            )
        )
        self.assertFalse(
            modeled_loss_preserves_floor(
                wealth_atoms=100, protected_floor_atoms=70, modeled_loss_atoms=31
            )
        )

    def test_tail_loss_is_exact_average_of_worst_declared_scenarios(self) -> None:
        self.assertEqual(empirical_tail_loss((1, 8, 3, 10), 2), 9)
        self.assertEqual(empirical_tail_loss((1, 8, 3), 2), Fraction(11, 2))

    def test_high_score_unsafe_plan_cannot_displace_admitted_plan(self) -> None:
        unsafe = replace(
            SAFE_PLAN,
            plan_id="leveraged-bet",
            declared_score_atoms=1_000_000,
            leverage_bps=5_000,
        )

        choice = choose_wealth_plan(
            (unsafe, SAFE_PLAN),
            evidence=WEALTH_EXTERNAL_READY,
            limits=WEALTH_LIMITS,
        )

        self.assertEqual(choice.plan, SAFE_PLAN)
        self.assertFalse(choice.safe_noop)

    def test_each_wealth_constraint_has_a_rejection(self) -> None:
        cases = (
            (
                replace(WEALTH_EXTERNAL_READY, policy_root_ok=False),
                SAFE_PLAN,
                WealthRejectCode.POLICY_ROOT_MISMATCH,
            ),
            (
                replace(WEALTH_EXTERNAL_READY, household_consent_fresh=False),
                SAFE_PLAN,
                WealthRejectCode.CONSENT_STALE,
            ),
            (
                replace(
                    WEALTH_EXTERNAL_READY, proposal_evidence_authenticated=False
                ),
                SAFE_PLAN,
                WealthRejectCode.PROPOSAL_EVIDENCE_UNAUTHENTICATED,
            ),
            (
                replace(WEALTH_EXTERNAL_READY, custody_authorized=False),
                SAFE_PLAN,
                WealthRejectCode.CUSTODY_UNAUTHORIZED,
            ),
            (
                WEALTH_EXTERNAL_READY,
                replace(SAFE_PLAN, leverage_bps=1),
                WealthRejectCode.LEVERAGE_OR_SHORT_EXPOSURE,
            ),
            (
                WEALTH_EXTERNAL_READY,
                replace(SAFE_PLAN, issuer_concentration_bps=2_001),
                WealthRejectCode.CONCENTRATION_LIMIT_EXCEEDED,
            ),
            (
                WEALTH_EXTERNAL_READY,
                replace(SAFE_PLAN, scenario_losses_atoms=(1,)),
                WealthRejectCode.TAIL_SCENARIO_SET_INSUFFICIENT,
            ),
            (
                WEALTH_EXTERNAL_READY,
                replace(SAFE_PLAN, scenario_losses_atoms=(20, 30)),
                WealthRejectCode.EMPIRICAL_TAIL_LOSS_EXCEEDED,
            ),
            (
                WEALTH_EXTERNAL_READY,
                replace(SAFE_PLAN, annual_fee_bps=51),
                WealthRejectCode.FEE_OR_TURNOVER_LIMIT_EXCEEDED,
            ),
        )
        for evidence, plan, expected in cases:
            with self.subTest(expected=expected):
                decision = evaluate_wealth_plan(
                    plan, evidence=evidence, limits=WEALTH_LIMITS
                )
                self.assertFalse(decision.accepted)
                self.assertEqual(decision.code, expected)

    def test_nonpositive_admitted_plan_yields_safe_noop(self) -> None:
        choice = choose_wealth_plan(
            (replace(SAFE_PLAN, declared_score_atoms=0),),
            evidence=WEALTH_EXTERNAL_READY,
            limits=WEALTH_LIMITS,
        )

        self.assertTrue(choice.safe_noop)
        self.assertIsNone(choice.plan)

    def test_complete_wealth_boolean_surface_is_conjunction(self) -> None:
        for bits in itertools.product((False, True), repeat=8):
            with self.subTest(bits=bits):
                self.assertEqual(wealth_admits(WealthObligations(*bits)), all(bits))

    def test_scenario_admission_does_not_bound_unmodeled_loss(self) -> None:
        # Negative result: the plan passes its finite scenario envelope while a
        # separately posited out-of-sample loss can be arbitrarily larger.
        decision = evaluate_wealth_plan(
            SAFE_PLAN, evidence=WEALTH_EXTERNAL_READY, limits=WEALTH_LIMITS
        )
        unmodeled_realized_loss = 1_000_000

        self.assertTrue(decision.accepted)
        self.assertGreater(unmodeled_realized_loss, WEALTH_LIMITS.max_empirical_tail_loss_atoms)


if __name__ == "__main__":
    unittest.main()
