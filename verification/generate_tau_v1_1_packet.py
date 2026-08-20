"""Generate the exhaustive deterministic truth table for the V1.1 Tau gate."""

from __future__ import annotations

import itertools
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET = REPO_ROOT / "tau" / "v1_1"
OBLIGATIONS = (
    "eetf_authenticated",
    "action_ethical",
    "strict_hyperdeflation_margin",
    "reward_funded",
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
    (PACKET / "expected" / "reference_eligible.out").write_text(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
