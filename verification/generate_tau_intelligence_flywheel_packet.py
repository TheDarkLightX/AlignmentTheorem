#!/usr/bin/env python3
"""Generate the complete deterministic nine-bit Tau packet."""

from __future__ import annotations

import itertools
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TAU_PACKET = REPO_ROOT / "tau" / "intelligence_flywheel" / "gate"
SPEC_NAME = "intelligence_flywheel_gate.tau"
OUTPUT_NAME = "allow.out"
OBLIGATIONS = (
    "policy_root_ok",
    "capability_receipt_authenticated",
    "productivity_bridge_verified",
    "essential_basket_gain_verified",
    "benefit_floor_funded",
    "concentration_cap_ok",
    "grid_externality_budget_ok",
    "debt_guardrail_ok",
    "strict_alignment_margin",
)


def rows() -> list[tuple[bool, ...]]:
    all_true = (True,) * len(OBLIGATIONS)
    single_faults = [
        tuple(index != false_index for index in range(len(OBLIGATIONS)))
        for false_index in range(len(OBLIGATIONS))
    ]
    prefix = [all_true, *single_faults]
    seen = set(prefix)
    tail = [
        row
        for row in itertools.product((False, True), repeat=len(OBLIGATIONS))
        if row not in seen
    ]
    return [*prefix, *tail]


def generated_payloads() -> dict[str, bytes]:
    table = rows()
    payloads = {
        f"inputs/{name}.in": "".join(
            "1\n" if row[column] else "0\n" for row in table
        ).encode("ascii")
        for column, name in enumerate(OBLIGATIONS)
    }
    payloads[f"expected/{OUTPUT_NAME}"] = "".join(
        "1\n" if all(row) else "0\n" for row in table
    ).encode("ascii")
    return payloads


def main() -> int:
    for relative, payload in generated_payloads().items():
        path = TAU_PACKET / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
