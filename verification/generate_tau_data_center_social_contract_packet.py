#!/usr/bin/env python3
"""Generate the complete 1,024-row Tau packet for the ten-fact gate."""

from pathlib import Path

from data_center_social_contract import DATA_CENTER_OBLIGATION_NAMES, tau_truth_rows

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "tau" / "data_center_social_contract"


def main() -> int:
    rows = tau_truth_rows()
    for column, name in enumerate(DATA_CENTER_OBLIGATION_NAMES):
        path = PACKET / "inputs" / f"{name}.in"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join("1\n" if row[column] else "0\n" for row in rows))
    expected = PACKET / "expected" / "allow.out"
    expected.parent.mkdir(parents=True, exist_ok=True)
    expected.write_text("".join("1\n" if all(row) else "0\n" for row in rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
