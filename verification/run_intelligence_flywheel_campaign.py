#!/usr/bin/env python3
"""Run the exact finite intelligence-flywheel campaign and emit a receipt."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
from fractions import Fraction
from pathlib import Path

try:
    from verification.generate_tau_intelligence_flywheel_packet import OBLIGATIONS, TAU_PACKET, rows
    from verification.intelligence_flywheel_model import (
        PriceBridge,
        compute_power_capability,
        dac_reinvestment_capability,
        direct_capability_doubling,
        first_alignment_epoch,
        logistic_capability,
        normalized_basket_price,
        simulate,
    )
    from verification.run_tau_compute_dividend import _tree_sha256
except ModuleNotFoundError:
    from generate_tau_intelligence_flywheel_packet import OBLIGATIONS, TAU_PACKET, rows
    from intelligence_flywheel_model import (
        PriceBridge,
        compute_power_capability,
        dac_reinvestment_capability,
        direct_capability_doubling,
        first_alignment_epoch,
        logistic_capability,
        normalized_basket_price,
        simulate,
    )
    from run_tau_compute_dividend import _tree_sha256

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "verification" / "intelligence_flywheel_model.py"
MODEL_TEST = ROOT / "tests" / "test_intelligence_flywheel_model.py"
LEAN_RECEIPT = ROOT / "verification" / "receipts" / "lean_intelligence_flywheel_v4.33.0.json"
TAU_CANDIDATE = ROOT / "research" / "intelligence_flywheel" / "tau_candidate_probe.json"
TAU_NET_NATIVE = ROOT / "research" / "intelligence_flywheel" / "tau_net_native_probe.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def run() -> dict[str, object]:
    full = PriceBridge(Fraction(1), Fraction(1), 1)
    full_points = simulate(
        [direct_capability_doubling(t) for t in range(9)],
        bridge=full,
        protected_benefits=[Fraction(1)] * 9,
        deviations=[Fraction(8)] * 9,
    )
    partial = PriceBridge(Fraction(3, 4), Fraction(4, 5), 1)
    partial_points = simulate(
        [direct_capability_doubling(t) for t in range(33)],
        bridge=partial,
        protected_benefits=[Fraction(1)] * 33,
        deviations=[Fraction(3)] * 33,
    )
    logistic_points = simulate(
        [
            logistic_capability(
                t,
                initial=Fraction(1),
                carrying_capacity=Fraction(8),
                decay=Fraction(1, 2),
            )
            for t in range(33)
        ],
        bridge=full,
        protected_benefits=[Fraction(1)] * 33,
        deviations=[Fraction(9)] * 33,
    )
    dac_points = simulate(
        [
            dac_reinvestment_capability(
                t,
                initial=Fraction(1),
                reinvestment_share=Fraction(1, 2),
                verified_net_return=Fraction(1, 2),
            )
            for t in range(17)
        ],
        bridge=full,
        protected_benefits=[Fraction(1)] * 17,
        deviations=[Fraction(4)] * 17,
    )
    rebound_points = simulate(
        [direct_capability_doubling(t) for t in range(17)],
        bridge=full,
        protected_benefits=[Fraction(1)] * 17,
        deviations=[Fraction(2)] * 17,
        surcharges=[Fraction(2**t - 1, 2**t) for t in range(17)],
    )

    bridge_cases = 0
    bridge_failures: list[dict[str, object]] = []
    for share, pass_through, elasticity, epoch in itertools.product(
        (Fraction(0), Fraction(1, 2), Fraction(3, 4), Fraction(1)),
        (Fraction(0), Fraction(1, 2), Fraction(4, 5), Fraction(1)),
        (1, 2),
        range(17),
    ):
        bridge = PriceBridge(share, pass_through, elasticity)
        price = normalized_basket_price(direct_capability_doubling(epoch), bridge)
        bridge_cases += 1
        if price < bridge.normalized_price_floor or (
            share == 1 and pass_through == 1 and price != Fraction(1, 2 ** (elasticity * epoch))
        ):
            bridge_failures.append(
                {
                    "share": _q(share),
                    "pass_through": _q(pass_through),
                    "elasticity": elasticity,
                    "epoch": epoch,
                }
            )

    half_alpha = {
        epoch: compute_power_capability(epoch, elasticity=Fraction(1, 2))
        for epoch in range(0, 9, 2)
    }
    lean = json.loads(LEAN_RECEIPT.read_text())
    candidate = json.loads(TAU_CANDIDATE.read_text())
    native = json.loads(TAU_NET_NATIVE.read_text())
    table = rows()
    passed = (
        first_alignment_epoch(full_points) == 4
        and first_alignment_epoch(partial_points) is None
        and first_alignment_epoch(logistic_points) is None
        and first_alignment_epoch(dac_points) == 7
        and first_alignment_epoch(rebound_points) is None
        and not bridge_failures
        and len(table) == len(set(table)) == 512
        and sum(all(row) for row in table) == 1
        and lean["passed"]
        and candidate["semantic_match"]
        and not candidate["promotion_eligible"]
        and native["passed"]
    )
    return {
        "schema": "alignment-theorem-intelligence-flywheel-campaign-v1",
        "status": "SUPPORTED_BOUNDED" if passed else "FAILED",
        "passed": passed,
        "authority_status": "RESEARCH_REFERENCE_ONLY_NO_MACROECONOMIC_TAU_NET_OR_VALUE_AUTHORITY",
        "randomness": "NONE_EXACT_FINITE_ENUMERATION_ONLY",
        "python_version": platform.python_version(),
        "checker_sha256": _sha256(Path(__file__)),
        "bound_files_sha256": {
            str(path.relative_to(ROOT)): _sha256(path)
            for path in (MODEL, MODEL_TEST, LEAN_RECEIPT, TAU_CANDIDATE, TAU_NET_NATIVE)
        },
        "maps": {
            "direct_doubling_full_bridge": {
                "capability": "2^t",
                "basket_price": "2^-t",
                "deviation": 8,
                "first_strict_alignment_epoch": first_alignment_epoch(full_points),
            },
            "direct_doubling_partial_bridge": {
                "automatable_share": _q(partial.automatable_share),
                "pass_through": _q(partial.pass_through),
                "price_floor": _q(partial.normalized_price_floor),
                "multiplier_upper_bound": _q(1 / partial.normalized_price_floor),
                "deviation": 3,
                "first_strict_alignment_epoch_0_to_32": first_alignment_epoch(partial_points),
            },
            "compute_power_half_elasticity": {
                "assumption": "I/I0=(C/C0)^(1/2)",
                "exact_even_epoch_samples": {str(epoch): _q(value) for epoch, value in half_alpha.items()},
            },
            "logistic_saturation": {
                "carrying_capacity": 8,
                "deviation": 9,
                "first_strict_alignment_epoch_0_to_32": first_alignment_epoch(logistic_points),
            },
            "dac_reinvestment": {
                "recurrence_factor": _q(Fraction(5, 4)),
                "deviation": 4,
                "first_strict_alignment_epoch": first_alignment_epoch(dac_points),
                "nonclaim": "The supplied net return is not forecast or guaranteed.",
            },
            "rebound_surcharge": {
                "adjusted_price_all_epochs": _q(Fraction(1)),
                "first_strict_alignment_epoch_0_to_16": first_alignment_epoch(rebound_points),
            },
        },
        "bridge_enumeration": {
            "cases": bridge_cases,
            "failures": bridge_failures,
        },
        "tau_semantic_packet": {
            "obligations": list(OBLIGATIONS),
            "rows": len(table),
            "accepted_rows": [index for index, row in enumerate(table) if all(row)],
            "packet_sha256": _tree_sha256(TAU_PACKET),
            "candidate_execution_match": candidate["semantic_match"],
            "reviewed_binary_replay": "PENDING_c49267404e07",
            "tau_net_direct_native_abi_match": native["passed"],
        },
        "negative_results": [
            "Capability doubling alone does not determine basket prices, protected benefit, or deviation benefit.",
            "Incomplete automation or pass-through creates a positive price floor and bounded multiplier.",
            "A logistic capability ceiling blocks indefinite hyperdeflation in the full-bridge map.",
            "An equal rebound/externality surcharge can cancel the modeled core price decline.",
            "A DAC reinvestment flywheel depends on a positive supplied net-return premise.",
            "Tau custom inputs are claims, not authenticated economic facts, in the tested alpha ABI.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    if args.json:
        print(rendered, end="")
    else:
        print(report["status"])
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
