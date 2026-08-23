"""Generate the exhaustive deterministic truth table for the V1 Tau gate."""

from __future__ import annotations

import itertools
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET = REPO_ROOT / "tau" / "v1"
OBLIGATIONS = (
    "policy_root_ok",
    "network_eetf_authenticated",
    "candidate_eetf_authenticated",
    "scarcity_snapshot_authenticated",
    "reward_funded",
    "exclusive_upside_enforceable",
    "strict_v1_margin_verified",
)


def rows() -> list[tuple[bool, ...]]:
    all_true = (True,) * len(OBLIGATIONS)
    mutation_rows = [
        tuple(index != false_index for index in range(len(OBLIGATIONS)))
        for false_index in range(len(OBLIGATIONS))
    ]
    prefix = [all_true, *mutation_rows]
    prefix_set = set(prefix)
    tail = [
        row
        for row in itertools.product((False, True), repeat=len(OBLIGATIONS))
        if row not in prefix_set
    ]
    return [*prefix, *tail]


def main() -> int:
    table = rows()
    if len(table) != 1 << len(OBLIGATIONS) or len(set(table)) != len(table):
        raise RuntimeError("truth-table generation is incomplete or duplicated")
    (PACKET / "inputs").mkdir(parents=True, exist_ok=True)
    (PACKET / "expected").mkdir(parents=True, exist_ok=True)
    for column, obligation in enumerate(OBLIGATIONS):
        rendered = "".join("1\n" if row[column] else "0\n" for row in table)
        (PACKET / "inputs" / f"{obligation}.in").write_text(rendered)
    expected = "".join("1\n" if all(row) else "0\n" for row in table)
    (PACKET / "expected" / "v1_eligible.out").write_text(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
