#!/usr/bin/env python3
"""Bind the flywheel predicate to the current Tau Testnet native o5 ABI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from verification.generate_tau_intelligence_flywheel_packet import OBLIGATIONS, TAU_PACKET
    from verification.run_tau_compute_dividend import (
        EXPECTED_TAU_PARSER_COMMIT,
        EXPECTED_TAU_SOURCE_COMMIT,
        _tree_sha256,
    )
except ModuleNotFoundError:
    from generate_tau_intelligence_flywheel_packet import OBLIGATIONS, TAU_PACKET
    from run_tau_compute_dividend import EXPECTED_TAU_PARSER_COMMIT, EXPECTED_TAU_SOURCE_COMMIT, _tree_sha256

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "tau" / "intelligence_flywheel" / "tau_net" / "dac_treasury_o5.tau"
CHILD = Path(__file__).with_name("tau_net_intelligence_flywheel_child.py")
EXPECTED_TAU_TESTNET_COMMIT = "9f9240ded9fd7ff246f4bbd45343c64eef9a1751"
STREAM_MAP = {str(index): name for index, name in zip(range(17, 26), OBLIGATIONS, strict=True)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def run(
    *,
    tau_testnet_root: Path,
    tau_source: Path,
    tau_module: Path,
    library_dirs: list[Path],
) -> dict[str, object]:
    tau_testnet_root = tau_testnet_root.resolve(strict=True)
    tau_source = tau_source.resolve(strict=True)
    tau_module = tau_module.resolve(strict=True)
    resolved_libraries = [path.resolve(strict=True) for path in library_dirs]
    testnet_commit = _git(tau_testnet_root, "rev-parse", "HEAD")
    testnet_status = _git(tau_testnet_root, "status", "--porcelain=v1")
    source_commit = _git(tau_source, "rev-parse", "HEAD")
    parser_commit = _git(tau_source / "external" / "parser", "rev-parse", "HEAD")
    source_status = _git(tau_source, "status", "--porcelain=v1")

    with tempfile.TemporaryDirectory(prefix="tau-net-flywheel-native-") as raw:
        child_output = Path(raw) / "child.json"
        env = os.environ.copy()
        python_entries = [str(tau_module.parent), str(tau_testnet_root)]
        if env.get("PYTHONPATH"):
            python_entries.append(env["PYTHONPATH"])
        env["PYTHONPATH"] = os.pathsep.join(python_entries)
        library_entries = [str(path) for path in resolved_libraries]
        if env.get("LD_LIBRARY_PATH"):
            library_entries.append(env["LD_LIBRARY_PATH"])
        env["LD_LIBRARY_PATH"] = os.pathsep.join(library_entries)
        child = subprocess.run(
            [
                sys.executable,
                str(CHILD),
                "--spec",
                str(SPEC),
                "--output",
                str(child_output),
            ],
            env=env,
            capture_output=True,
            timeout=180,
        )
        child_report = json.loads(child_output.read_text()) if child_output.is_file() else {
            "cases": [],
            "all_cases_match": False,
            "child_error": "CHILD_RECEIPT_MISSING",
        }

    upstream_files = (
        "README.md",
        "tau_native.py",
        "tau_defs.py",
        "consensus/admission.py",
        "consensus/engine.py",
    )
    upstream_hashes = {
        relative: _sha256(tau_testnet_root / relative) for relative in upstream_files
    }
    pins_match = (
        testnet_commit == EXPECTED_TAU_TESTNET_COMMIT
        and testnet_status == ""
        and source_commit == EXPECTED_TAU_SOURCE_COMMIT
        and parser_commit == EXPECTED_TAU_PARSER_COMMIT
        and source_status == ""
    )
    passed = child.returncode == 0 and child_report["all_cases_match"] and pins_match
    return {
        "schema": "alignment-theorem-tau-net-intelligence-flywheel-native-abi-v1",
        "status": "SUPPORTED_BOUNDED_NATIVE_ABI" if passed else "FAILED",
        "passed": passed,
        "checker_sha256": _sha256(Path(__file__)),
        "child_checker_sha256": _sha256(CHILD),
        "tau_spec_sha256": _sha256(SPEC),
        "semantic_cli_packet_sha256": _tree_sha256(TAU_PACKET),
        "semantic_stream_map": STREAM_MAP,
        "semantic_stream_map_sha256": _canonical_hash(STREAM_MAP),
        "expected_tau_testnet_commit": EXPECTED_TAU_TESTNET_COMMIT,
        "actual_tau_testnet_commit": testnet_commit,
        "tau_testnet_status_porcelain": testnet_status.splitlines(),
        "expected_tau_source_commit": EXPECTED_TAU_SOURCE_COMMIT,
        "actual_tau_source_commit": source_commit,
        "expected_tau_parser_commit": EXPECTED_TAU_PARSER_COMMIT,
        "actual_tau_parser_commit": parser_commit,
        "tau_source_status_porcelain": source_status.splitlines(),
        "pins_match": pins_match,
        "tau_native_module_sha256": _sha256(tau_module),
        "tau_native_module_basename": tau_module.name,
        "upstream_files_sha256": upstream_hashes,
        "child_returncode": child.returncode,
        "child_stdout_sha256": hashlib.sha256(child.stdout).hexdigest(),
        "child_stderr_sha256": hashlib.sha256(child.stderr).hexdigest(),
        "cases": child_report["cases"],
        "all_cases_match": child_report["all_cases_match"],
        "child_error": child_report.get("child_error", ""),
        "source_to_binding_status": "DECLARED_LOCAL_BUILD_RELATION_NOT_INDEPENDENTLY_ATTESTED",
        "execution_environment_status": "HOST_KERNEL_DYNAMIC_LIBRARIES_AND_HARDWARE_NOT_HERMETICALLY_ATTESTED",
        "tau_net_authority_status": "DIRECT_NATIVE_ABI_PROBE_NOT_NODE_DEPLOYMENT_OR_CONSENSUS_FINALITY",
        "input_authentication_status": "CUSTOM_I17_TO_I25_VALUES_ARE_SUBMITTER_SUPPLIED_CLAIMS",
        "nonclaims": [
            "Direct TauInterface execution is not an end-to-end node, admission, block-apply, governance, or finality test.",
            "The local source pin does not prove a public Tau Testnet deployment runs these bytes.",
            "The local source pin does not attest how the native module was built.",
            "Consensus enforcement of a Boolean predicate does not authenticate the predicate's economic facts.",
            "Current Tau Testnet is alpha and this receipt is not production-readiness or real-funds evidence.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau-testnet-root", required=True, type=Path)
    parser.add_argument("--tau-source", required=True, type=Path)
    parser.add_argument("--tau-module", required=True, type=Path)
    parser.add_argument("--library-dir", action="append", default=[], type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run(
        tau_testnet_root=args.tau_testnet_root,
        tau_source=args.tau_source,
        tau_module=args.tau_module,
        library_dirs=args.library_dir,
    )
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
