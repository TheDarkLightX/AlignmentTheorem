#!/usr/bin/env python3
"""Fresh-process Tau native-ABI probe for the three-profile router."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

TREASURY = "#x" + "a" * 96
OTHER_SENDER = "#x" + "b" * 96
PROFILE_STREAM = 17
FACT_STREAMS = tuple(range(18, 25))
PROFILES = (1, 2, 3)
PROFILE_LABELS = {1: "v1", 2: "v1_1", 3: "v2"}


def _blocked(rendered: str) -> bool:
    return "0" in rendered.split()


def run(spec: Path) -> dict[str, object]:
    from tau_native import TauInterface

    interface = TauInterface(str(spec))
    cases: list[dict[str, object]] = []

    def evaluate(name: str, sender: str, values: dict[int, str], expected: str) -> None:
        inputs = {12: [sender], **{index: [value] for index, value in values.items()}}
        rendered = interface.communicate(
            target_output_stream_index=5,
            input_stream_values=inputs,
        )
        observed = "block" if _blocked(rendered) else "allow"
        cases.append(
            {
                "name": name,
                "sender": "treasury" if sender == TREASURY else "other",
                "provided_streams": sorted(values),
                "expected": expected,
                "observed": observed,
                "raw_tokens": rendered.split(),
                "matched": observed == expected,
            }
        )

    for profile in PROFILES:
        label = PROFILE_LABELS[profile]
        all_true = {
            PROFILE_STREAM: f"#x{profile:04x}",
            **{stream: "#x0001" for stream in FACT_STREAMS},
        }
        evaluate(f"treasury_{label}_all_true", TREASURY, all_true, "allow")
        for stream in FACT_STREAMS:
            mutation = dict(all_true)
            mutation[stream] = "#x0000"
            evaluate(
                f"treasury_{label}_i{stream}_false",
                TREASURY,
                mutation,
                "block",
            )

    evaluate(
        "treasury_unknown_profile",
        TREASURY,
        {PROFILE_STREAM: "#x0004", **{stream: "#x0001" for stream in FACT_STREAMS}},
        "block",
    )
    evaluate(
        "other_sender_unknown_profile_all_false",
        OTHER_SENDER,
        {PROFILE_STREAM: "#x0004", **{stream: "#x0000" for stream in FACT_STREAMS}},
        "allow",
    )
    evaluate("treasury_profile_and_facts_absent", TREASURY, {}, "block")
    return {
        "child_schema": "alignment-theorem-tau-net-profile-router-child-v1",
        "cases": cases,
        "all_cases_match": all(case["matched"] for case in cases),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = run(args.spec.resolve(strict=True))
        result["child_error"] = ""
        code = 0 if result["all_cases_match"] else 1
    except BaseException as error:
        result = {
            "child_schema": "alignment-theorem-tau-net-profile-router-child-v1",
            "cases": [],
            "all_cases_match": False,
            "child_error": f"{type(error).__name__}: {error}",
        }
        code = 2
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    os._exit(code)


if __name__ == "__main__":
    main()
