#!/usr/bin/env python3
"""Generate complete deterministic truth tables for both research Tau gates."""

from __future__ import annotations

import itertools
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TAU_ROOT = REPO_ROOT / "tau" / "compute_dividend"
GATES = {
    "dividend": {
        "spec": "dividend_gate.tau",
        "obligations": (
            "policy_root_ok",
            "rent_receipt_authenticated",
            "grid_costs_reserved",
            "dividend_reserve_funded",
            "recipient_eligible",
            "nonce_fresh",
            "concentration_cap_ok",
            "agent_compute_funded",
        ),
    },
    "wealth": {
        "spec": "wealth_action_gate.tau",
        "obligations": (
            "policy_root_ok",
            "household_consent_fresh",
            "proposal_evidence_authenticated",
            "custody_authorized",
            "no_leverage_or_short",
            "concentration_limit_ok",
            "tail_loss_limit_ok",
            "fee_turnover_limit_ok",
        ),
    },
}


def rows(obligation_count: int) -> list[tuple[bool, ...]]:
    all_true = (True,) * obligation_count
    mutations = [
        tuple(index != false_index for index in range(obligation_count))
        for false_index in range(obligation_count)
    ]
    prefix = [all_true, *mutations]
    prefix_set = set(prefix)
    tail = [
        candidate
        for candidate in itertools.product((False, True), repeat=obligation_count)
        if candidate not in prefix_set
    ]
    return [*prefix, *tail]


def generated_payloads(gate: str) -> dict[str, bytes]:
    config = GATES[gate]
    obligations = config["obligations"]
    table = rows(len(obligations))
    payloads = {
        f"inputs/{name}.in": "".join(
            "1\n" if row[column] else "0\n" for row in table
        ).encode("ascii")
        for column, name in enumerate(obligations)
    }
    payloads["expected/allow.out"] = "".join(
        "1\n" if all(row) else "0\n" for row in table
    ).encode("ascii")
    return payloads


def main() -> int:
    for gate in GATES:
        packet = TAU_ROOT / gate
        for relative, payload in generated_payloads(gate).items():
            path = packet / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
