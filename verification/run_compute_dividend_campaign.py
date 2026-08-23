#!/usr/bin/env python3
"""Run the bounded compute-dividend research campaign and emit a receipt."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

from verification.compute_dividend_model import (
    AllocationPolicy,
    ExternalWealthEvidence,
    Household,
    WealthPlan,
    WealthPolicyLimits,
    allocate_prioritarian,
    choose_wealth_plan,
    evaluate_wealth_plan,
    exhaustive_optimal_welfare,
    progressive_transfer_delta,
)
from verification.generate_tau_compute_dividend_packets import GATES, TAU_ROOT
from verification.run_tau_compute_dividend import _tree_sha256

REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL = REPO_ROOT / "verification" / "compute_dividend_model.py"
MODEL_TEST = REPO_ROOT / "tests" / "test_compute_dividend_model.py"
TAU_TEST = REPO_ROOT / "tests" / "test_tau_compute_dividend.py"
TAU_GENERATOR = REPO_ROOT / "verification" / "generate_tau_compute_dividend_packets.py"
LEAN_RECEIPT = (
    REPO_ROOT
    / "verification"
    / "receipts"
    / "lean_compute_dividend_v4.33.0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def run() -> dict[str, object]:
    ids = ("a", "b", "c")
    allocation_cases = 0
    feasible_cases = 0
    infeasible_cases = 0
    allocation_mismatches: list[dict[str, object]] = []
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
                            allocation_cases += 1
                            feasible_cases += int(result.feasible)
                            infeasible_cases += int(not result.feasible)
                            if result.feasible != (oracle is not None) or (
                                result.feasible and result.welfare_gain != oracle
                            ):
                                allocation_mismatches.append(
                                    {
                                        "households": [
                                            {
                                                "id": row.household_id,
                                                "base": row.base_resources_atoms,
                                                "weight": row.priority_weight,
                                            }
                                            for row in households
                                        ],
                                        "budget": budget,
                                        "floor": floor,
                                        "share": _fraction(share),
                                    }
                                )

    transfer_cases = 0
    transfer_mismatches: list[dict[str, int]] = []
    for poorer in range(32):
        for richer in range(1, 33):
            delta = progressive_transfer_delta(poorer, richer)
            expected_nonnegative = poorer < richer
            expected_strict = poorer + 1 < richer
            observed_nonnegative = delta >= 0
            observed_strict = delta > 0
            transfer_cases += 1
            if (
                observed_nonnegative != expected_nonnegative
                or observed_strict != expected_strict
            ):
                transfer_mismatches.append({"poorer": poorer, "richer": richer})

    evidence = ExternalWealthEvidence(*(True,) * 4)
    limits = WealthPolicyLimits(2_000, 10, 2, 50, 2_000)
    safe = WealthPlan("diversified-index", 10, 0, 0, 500, 5, 100, (0, 2, 4, 6))
    leveraged = replace(
        safe,
        plan_id="leveraged-bet",
        declared_score_atoms=1_000_000,
        leverage_bps=5_000,
    )
    choice = choose_wealth_plan((leveraged, safe), evidence=evidence, limits=limits)
    safe_decision = evaluate_wealth_plan(safe, evidence=evidence, limits=limits)
    unmodeled_loss_atoms = 1_000_000
    unsafe_dominance_killed = choice.plan == safe
    out_of_sample_counterexample = (
        safe_decision.accepted
        and unmodeled_loss_atoms > limits.max_empirical_tail_loss_atoms
    )

    tau_packets = {}
    tau_vectors_ok = True
    for gate, config in GATES.items():
        packet = TAU_ROOT / gate
        expected = (packet / "expected" / "allow.out").read_text().split()
        columns = {
            name: (packet / "inputs" / f"{name}.in").read_text().split()
            for name in config["obligations"]
        }
        observed = [
            "1"
            if all(columns[name][row] == "1" for name in config["obligations"])
            else "0"
            for row in range(len(expected))
        ]
        gate_ok = len(expected) == 256 and observed == expected and expected.count("1") == 1
        tau_vectors_ok = tau_vectors_ok and gate_ok
        tau_packets[gate] = {
            "rows": len(expected),
            "accepted_rows": [index for index, value in enumerate(expected) if value == "1"],
            "packet_sha256": _tree_sha256(packet),
            "semantic_conjunction_match": gate_ok,
        }

    lean_receipt = json.loads(LEAN_RECEIPT.read_text())
    passed = (
        allocation_cases == 10_836
        and not allocation_mismatches
        and transfer_cases == 1_024
        and not transfer_mismatches
        and unsafe_dominance_killed
        and out_of_sample_counterexample
        and tau_vectors_ok
        and lean_receipt["passed"] is True
    )
    return {
        "schema": "alignment-theorem-compute-dividend-campaign-v1",
        "status": "SUPPORTED_BOUNDED" if passed else "FAILED",
        "authority_status": "RESEARCH_REFERENCE_ONLY_NO_FINANCIAL_OR_VALUE_AUTHORITY",
        "randomness": "NONE_EXHAUSTIVE_ENUMERATION_ONLY",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "checker_sha256": _sha256(Path(__file__)),
        "bound_files_sha256": {
            "verification/compute_dividend_model.py": _sha256(MODEL),
            "tests/test_compute_dividend_model.py": _sha256(MODEL_TEST),
            "tests/test_tau_compute_dividend.py": _sha256(TAU_TEST),
            "verification/generate_tau_compute_dividend_packets.py": _sha256(
                TAU_GENERATOR
            ),
            "verification/receipts/lean_compute_dividend_v4.33.0.json": _sha256(
                LEAN_RECEIPT
            ),
        },
        "allocation_campaign": {
            "household_count": [1, 2, 3],
            "base_resources_atoms": [0, 1, 2],
            "priority_weights": [1, 2],
            "earmarked_budget_atoms": [0, 1, 2, 3, 4, 5, 6],
            "universal_floor_atoms": [0, 1],
            "max_earmarked_budget_shares": [
                _fraction(Fraction(1)),
                _fraction(Fraction(1, 2)),
                _fraction(Fraction(2, 3)),
            ],
            "cases": allocation_cases,
            "feasible_cases": feasible_cases,
            "infeasible_cases": infeasible_cases,
            "mismatches": allocation_mismatches,
        },
        "progressive_transfer_campaign": {
            "poorer_post_atoms": [0, 31],
            "richer_post_atoms": [1, 32],
            "cases": transfer_cases,
            "mismatches": transfer_mismatches,
        },
        "wealth_agent_campaign": {
            "unsafe_high_score_plan_rejected": unsafe_dominance_killed,
            "selected_plan": choice.plan.plan_id if choice.plan else None,
            "finite_scenario_envelope_counterexample": {
                "accepted_in_sample": safe_decision.accepted,
                "in_sample_tail_limit_atoms": limits.max_empirical_tail_loss_atoms,
                "unmodeled_loss_atoms": unmodeled_loss_atoms,
                "demonstrates_no_out_of_sample_guarantee": out_of_sample_counterexample,
            },
        },
        "tau_static_packets": tau_packets,
        "tau_interpreter_replay_status": "PENDING_REVIEWED_BINARY_c4926740",
        "lean_receipt_passed": lean_receipt["passed"],
        "nonclaims": [
            "No household identity or Sybil resistance is authenticated.",
            "No data-center rent, grid cost, reserve, or compute receipt is authenticated.",
            "The exhaustive domain is finite and does not establish unrestricted optimizer correctness.",
            "The atom-by-atom allocator rejects earmarked budgets above 10,000 atoms.",
            "Finite scenario loss checks do not bound out-of-sample loss.",
            "No investment return, FIRE date, suitability, fiduciary compliance, or generational wealth is guaranteed.",
            "Static Tau parity is not Tau interpreter execution.",
            "Lean compilation does not attest its host environment or toolchain source-to-binary provenance.",
        ],
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    if args.json:
        print(rendered, end="")
    else:
        print("PASS" if report["passed"] else "FAIL")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
