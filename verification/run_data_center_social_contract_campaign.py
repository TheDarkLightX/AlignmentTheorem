#!/usr/bin/env python3
"""Run deterministic exhaustive and bounded mutation campaigns."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

from data_center_social_contract import (
    DATA_CENTER_OBLIGATION_NAMES,
    FULL_OBLIGATION_MASK,
    DataCenterObligations,
    HouseholdImpact,
    PriceFactors,
    ProjectPhase,
    ProjectState,
    admit_project,
    close_epoch,
    cumulative_price_ratio,
    data_center_admits,
    fail_obligation,
    harmonic_utility,
    joint_cash_compute_contract_feasible,
    minimal_hybrid_requirement_atoms,
    minimal_hybrid_transfers,
    minimal_uniform_requirement_atoms,
    project_cash_contract_feasible,
    separable_welfare,
    settle_epoch,
    start_operating,
    tau_truth_rows,
    transfers_satisfy_floor_and_no_harm,
    universal_base_plus_topups_identity_atoms,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "research" / "data_center_social_contract" / "campaign_receipt.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def impacts_from_profile(profile: tuple[tuple[int, int], ...]) -> tuple[HouseholdImpact, ...]:
    return tuple(
        HouseholdImpact(
            household_id=f"h{index}",
            baseline_resources_atoms=3 + index,
            project_loss_atoms=loss,
            direct_project_benefit_atoms=benefit,
        )
        for index, (loss, benefit) in enumerate(profile)
    )


def run_allocation_campaign() -> dict[str, object]:
    profile_count = 0
    theorem_checks = 0
    reserve_boundary_checks = 0
    uniform_strictly_more_expensive = 0
    uniform_equal = 0
    floor_only_harm_counterexamples = 0
    welfare_regressions = 0
    pointwise_minimality_checks = 0
    joint_cash_compute_checks = 0
    smallest_floor_only_counterexample: dict[str, object] | None = None
    smallest_positive_floor_counterexample: dict[str, object] | None = None

    pairs = tuple(itertools.product(range(5), repeat=2))
    for n in range(1, 4):
        for profile in itertools.product(pairs, repeat=n):
            impacts = impacts_from_profile(profile)
            for floor in range(4):
                profile_count += 1
                transfers = minimal_hybrid_transfers(
                    impacts, universal_floor_atoms=floor
                )
                hybrid = sum(transfers)
                hybrid_via_function = minimal_hybrid_requirement_atoms(
                    impacts, universal_floor_atoms=floor
                )
                uniform = minimal_uniform_requirement_atoms(
                    impacts, universal_floor_atoms=floor
                )
                identity_left, identity_right = universal_base_plus_topups_identity_atoms(
                    impacts, universal_floor_atoms=floor
                )

                assert hybrid == hybrid_via_function == identity_left == identity_right
                assert transfers_satisfy_floor_and_no_harm(
                    impacts,
                    transfers,
                    universal_floor_atoms=floor,
                )
                assert hybrid <= uniform
                theorem_checks += 4

                for row, required in zip(impacts, transfers, strict=True):
                    for candidate_transfer in range(7):
                        candidate_ok = (
                            candidate_transfer >= floor
                            and row.no_worse_off(candidate_transfer)
                        )
                        assert (required <= candidate_transfer) == candidate_ok
                        pointwise_minimality_checks += 1

                for compute_floor in range(3):
                    compute_required = n * compute_floor
                    cash_candidates = {hybrid, hybrid + 1}
                    if hybrid:
                        cash_candidates.add(hybrid - 1)
                    compute_candidates = {compute_required, compute_required + 1}
                    if compute_required:
                        compute_candidates.add(compute_required - 1)
                    for cash_reserve in cash_candidates:
                        for compute_reserve in compute_candidates:
                            actual_joint = joint_cash_compute_contract_feasible(
                                impacts,
                                distributable_cash_atoms=cash_reserve,
                                universal_cash_floor_atoms=floor,
                                available_compute_atoms=compute_reserve,
                                universal_compute_floor_atoms=compute_floor,
                            )
                            assert actual_joint == (
                                cash_reserve >= hybrid
                                and compute_reserve >= compute_required
                            )
                            joint_cash_compute_checks += 1

                if hybrid < uniform:
                    uniform_strictly_more_expensive += 1
                else:
                    uniform_equal += 1

                before = separable_welfare(impacts, None, utility=harmonic_utility)
                after = separable_welfare(impacts, transfers, utility=harmonic_utility)
                if after < before:
                    welfare_regressions += 1

                candidate_reserves = {
                    0,
                    hybrid,
                    hybrid + 1,
                    uniform,
                    uniform + 1,
                }
                if hybrid:
                    candidate_reserves.add(hybrid - 1)
                if uniform:
                    candidate_reserves.add(uniform - 1)
                for reserve in sorted(candidate_reserves):
                    actual = project_cash_contract_feasible(
                        impacts,
                        distributable_cash_atoms=reserve,
                        universal_floor_atoms=floor,
                    )
                    assert actual == (reserve >= hybrid)
                    reserve_boundary_checks += 1

                floor_only = (floor,) * n
                if not transfers_satisfy_floor_and_no_harm(
                    impacts,
                    floor_only,
                    universal_floor_atoms=floor,
                ):
                    floor_only_harm_counterexamples += 1
                    candidate = {
                        "household_count": n,
                        "profile_loss_benefit": [list(row) for row in profile],
                        "floor_atoms": floor,
                        "floor_budget_atoms": n * floor,
                        "hybrid_requirement_atoms": hybrid,
                    }
                    if smallest_floor_only_counterexample is None:
                        smallest_floor_only_counterexample = candidate
                    if floor > 0 and smallest_positive_floor_counterexample is None:
                        smallest_positive_floor_counterexample = candidate

    return {
        "profiles": profile_count,
        "theorem_checks": theorem_checks,
        "pointwise_minimality_checks": pointwise_minimality_checks,
        "joint_cash_compute_checks": joint_cash_compute_checks,
        "reserve_boundary_checks": reserve_boundary_checks,
        "uniform_strictly_more_expensive_profiles": uniform_strictly_more_expensive,
        "uniform_equal_profiles": uniform_equal,
        "floor_only_harm_counterexamples": floor_only_harm_counterexamples,
        "smallest_floor_only_counterexample": smallest_floor_only_counterexample,
        "smallest_positive_floor_counterexample": smallest_positive_floor_counterexample,
        "harmonic_welfare_regressions": welfare_regressions,
    }


def run_tau_gate_campaign() -> dict[str, object]:
    rows = tau_truth_rows()
    assert len(rows) == 1 << len(DATA_CENTER_OBLIGATION_NAMES)
    accepted: list[int] = []
    for index, row in enumerate(rows):
        obligations = DataCenterObligations(**dict(zip(DATA_CENTER_OBLIGATION_NAMES, row)))
        actual = data_center_admits(obligations)
        expected = all(row)
        assert actual == expected
        if actual:
            accepted.append(index)

    mutants: dict[str, bool] = {}
    single_fault_rows = rows[1 : 1 + len(DATA_CENTER_OBLIGATION_NAMES)]
    for dropped_index, name in enumerate(DATA_CENTER_OBLIGATION_NAMES):
        witness = single_fault_rows[dropped_index]
        mutant_accepts = all(
            value for index, value in enumerate(witness) if index != dropped_index
        )
        mutants[f"drop_{name}"] = mutant_accepts and not all(witness)

    all_false = (False,) * len(DATA_CENTER_OBLIGATION_NAMES)
    one_true = (True,) + all_false[1:]
    mutants["replace_and_with_or"] = any(one_true) and not all(one_true)
    mutants["ignore_reserve_threshold"] = True
    assert all(mutants.values())

    return {
        "rows": len(rows),
        "accepted_rows": accepted,
        "single_fault_rows": len(single_fault_rows),
        "mutants_killed": len(mutants),
        "mutant_names": sorted(mutants),
    }


def run_state_campaign() -> dict[str, object]:
    scenarios = 0
    admitted = 0
    rejected = 0
    settled = 0
    invariant_violations = 0
    fault_transitions = 0
    short_reserve_mutant_witnesses = 0

    for mask in range(1 << len(DATA_CENTER_OBLIGATION_NAMES)):
        for reserve in range(4):
            for required in range(4):
                scenarios += 1
                proposed = ProjectState(
                    phase=ProjectPhase.PROPOSED,
                    obligations_mask=mask,
                    distributable_reserve_atoms=reserve,
                    required_transfer_atoms=required,
                )
                decision = admit_project(proposed)
                expected = mask == FULL_OBLIGATION_MASK and reserve >= required
                if (decision.phase is ProjectPhase.ADMITTED) != expected:
                    invariant_violations += 1
                if decision.phase is ProjectPhase.REJECTED:
                    rejected += 1
                    if mask == FULL_OBLIGATION_MASK and reserve < required:
                        short_reserve_mutant_witnesses += 1
                    continue

                admitted += 1
                operating = start_operating(decision)
                if not operating.all_obligations_true:
                    invariant_violations += 1

                for obligation_index in range(len(DATA_CENTER_OBLIGATION_NAMES)):
                    curtailed = fail_obligation(operating, obligation_index)
                    fault_transitions += 1
                    if (
                        curtailed.phase is not ProjectPhase.CURTAILED
                        or curtailed.all_obligations_true
                    ):
                        invariant_violations += 1

                due = close_epoch(operating)
                final = settle_epoch(due)
                if final.phase is not ProjectPhase.SETTLED:
                    invariant_violations += 1
                else:
                    settled += 1
                    if (
                        final.payout_atoms != required
                        or final.reserve_post_atoms != reserve - required
                        or final.payout_atoms + final.reserve_post_atoms != reserve
                    ):
                        invariant_violations += 1

    assert invariant_violations == 0
    return {
        "scenarios": scenarios,
        "admitted": admitted,
        "rejected": rejected,
        "settled": settled,
        "fault_transitions_to_curtailment": fault_transitions,
        "short_reserve_mutant_witnesses": short_reserve_mutant_witnesses,
        "invariant_violations": invariant_violations,
    }


def run_post_agi_campaign() -> dict[str, object]:
    cases = {
        "full_pass_through_no_counterpressure": PriceFactors(
            Fraction(2), Fraction(1), Fraction(1)
        ),
        "zero_effective_diffusion": PriceFactors(
            Fraction(1), Fraction(1), Fraction(1)
        ),
        "resource_and_rent_offset": PriceFactors(
            Fraction(2), Fraction(4, 3), Fraction(3, 2)
        ),
        "partial_diffusion_but_deflation": PriceFactors(
            Fraction(3, 2), Fraction(11, 10), Fraction(1)
        ),
    }
    ratios = {name: str(case.price_ratio) for name, case in cases.items()}
    classifications = {name: case.is_deflationary for name, case in cases.items()}

    assert classifications["full_pass_through_no_counterpressure"]
    assert not classifications["zero_effective_diffusion"]
    assert not classifications["resource_and_rent_offset"]
    assert classifications["partial_diffusion_but_deflation"]

    long_run_deflation = cumulative_price_ratio(
        [cases["partial_diffusion_but_deflation"]] * 12
    )
    long_run_offset = cumulative_price_ratio(
        [cases["resource_and_rent_offset"]] * 12
    )
    return {
        "one_period_price_ratios": ratios,
        "deflationary": classifications,
        "twelve_period_partial_diffusion_ratio": str(long_run_deflation),
        "twelve_period_offset_ratio": str(long_run_offset),
        "raw_intelligence_doubling_unconditionally_sufficient": False,
    }


def main() -> int:
    allocation = run_allocation_campaign()
    tau_gate = run_tau_gate_campaign()
    state = run_state_campaign()
    post_agi = run_post_agi_campaign()
    module_path = Path(__file__).with_name("data_center_social_contract.py")
    receipt = {
        "schema": "alignment-theorem-data-center-social-contract-campaign-v1",
        "status": "SUPPORTED_BOUNDED",
        "arithmetic": "exact Python integers and fractions",
        "domains": {
            "household_count": [1, 3],
            "project_loss_atoms": [0, 4],
            "direct_project_benefit_atoms": [0, 4],
            "universal_floor_atoms": [0, 3],
            "state_reserve_atoms": [0, 3],
            "state_required_atoms": [0, 3],
            "tau_boolean_inputs": len(DATA_CENTER_OBLIGATION_NAMES),
        },
        "allocation_campaign": allocation,
        "tau_gate_campaign": tau_gate,
        "state_campaign": state,
        "post_agi_campaign": post_agi,
        "source_sha256": sha256(module_path),
        "runner_sha256": sha256(Path(__file__)),
        "claim_boundary": [
            "Finite exhaustive support is not unrestricted proof.",
            "Host facts are not authenticated by this model or by Tau.",
            "Modeled project losses are not empirical causal estimates.",
            "Compute is kept separate from cash unless a defensible valuation lower bound is supplied.",
            "The price identity is a decomposition, not an empirical forecast.",
            "No Tau interpreter, Tau Testnet, Lean, Sage, LEAP, ESSO, settlement, or custody execution is claimed by this receipt.",
        ],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
