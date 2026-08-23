#!/usr/bin/env python3
"""Fresh-process native Tau ABI probe; results are written before hard exit."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

TREASURY = "#x" + "a" * 96
OTHER_SENDER = "#x" + "b" * 96
CUSTOM_STREAMS = tuple(range(17, 26))


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

    all_true = {stream: "#x0001" for stream in CUSTOM_STREAMS}
    evaluate("treasury_all_true", TREASURY, all_true, "allow")
    for stream in CUSTOM_STREAMS:
        mutation = dict(all_true)
        mutation[stream] = "#x0000"
        evaluate(f"treasury_i{stream}_false", TREASURY, mutation, "block")
    evaluate(
        "other_sender_all_false",
        OTHER_SENDER,
        {stream: "#x0000" for stream in CUSTOM_STREAMS},
        "allow",
    )
    # When custom streams are absent, the raw solver can expose more than one
    # possible o5 value.  The current host's policy convention treats any 0 as
    # a block; capture the behavior instead of assuming it.
    evaluate("treasury_custom_inputs_absent", TREASURY, {}, "block")
    return {
        "child_schema": "alignment-theorem-tau-net-native-child-v1",
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
            "child_schema": "alignment-theorem-tau-net-native-child-v1",
            "cases": [],
            "all_cases_match": False,
            "child_error": f"{type(error).__name__}: {error}",
        }
        code = 2
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    # The alpha binding may fault during native/global teardown.  The evidence
    # is complete above, so exit without running destructors, matching the
    # isolation pattern used by upstream native tests.
    os._exit(code)


if __name__ == "__main__":
    main()
