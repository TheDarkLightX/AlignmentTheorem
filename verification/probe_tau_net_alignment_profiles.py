#!/usr/bin/env python3
"""Bind the V1/V1.1/V2 profile router to the current Tau Testnet o5 ABI."""

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
    from verification.current_tau_baseline import (
        CURRENT_TAU_NATIVE_MODULE_SHA256,
        CURRENT_TAU_PARSER_COMMIT,
        CURRENT_TAU_SOURCE_COMMIT,
        CURRENT_TAU_TESTNET_COMMIT,
    )
except ModuleNotFoundError:
    from current_tau_baseline import (
        CURRENT_TAU_NATIVE_MODULE_SHA256,
        CURRENT_TAU_PARSER_COMMIT,
        CURRENT_TAU_SOURCE_COMMIT,
        CURRENT_TAU_TESTNET_COMMIT,
    )

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "tau" / "current_tau" / "alignment_profiles_o5.tau"
CHILD = Path(__file__).with_name("tau_net_alignment_profiles_child.py")
PROFILE_MAP = {
    "1": "v1_eetf_vcc_exclusion",
    "2": "v1_1_hyperdeflationary_margin",
    "3": "v2_finite_policy_settlement",
}
FACT_MAP = {
    "18": {
        "v1": "policy_root",
        "v1_1": "policy_root",
        "v2": "policy_root",
    },
    "19": {
        "v1": "network_eetf_authenticated",
        "v1_1": "eetf_evidence_authenticated",
        "v2": "evidence_authenticated",
    },
    "20": {
        "v1": "candidate_eetf_authenticated",
        "v1_1": "action_eligible",
        "v2": "action_known",
    },
    "21": {
        "v1": "scarcity_snapshot_authenticated",
        "v1_1": "scarcity_snapshot_authenticated",
        "v2": "action_policy_compliant",
    },
    "22": {
        "v1": "reward_funded",
        "v1_1": "eligible_exposure_funded",
        "v2": "nonce_fresh",
    },
    "23": {
        "v1": "exclusive_upside_enforceable",
        "v1_1": "exclusive_upside_enforceable_or_zero_coefficient",
        "v2": "task_unclaimed",
    },
    "24": {
        "v1": "strict_v1_margin",
        "v1_1": "strict_v1_1_margin",
        "v2": "reward_funded_and_finite_v2_margin",
    },
}


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
    module_sha256 = _sha256(tau_module)

    with tempfile.TemporaryDirectory(prefix="tau-net-alignment-profiles-") as raw:
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
        child_report = (
            json.loads(child_output.read_text())
            if child_output.is_file()
            else {
                "cases": [],
                "all_cases_match": False,
                "child_error": "CHILD_RECEIPT_MISSING",
            }
        )

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
        testnet_commit == CURRENT_TAU_TESTNET_COMMIT
        and testnet_status == ""
        and source_commit == CURRENT_TAU_SOURCE_COMMIT
        and parser_commit == CURRENT_TAU_PARSER_COMMIT
        and source_status == ""
        and module_sha256 == CURRENT_TAU_NATIVE_MODULE_SHA256
    )
    passed = child.returncode == 0 and child_report["all_cases_match"] and pins_match
    return {
        "schema": "alignment-theorem-tau-net-profile-router-native-abi-v1",
        "status": "SUPPORTED_BOUNDED_NATIVE_ABI" if passed else "FAILED",
        "passed": passed,
        "checker_sha256": _sha256(Path(__file__)),
        "child_checker_sha256": _sha256(CHILD),
        "tau_spec_sha256": _sha256(SPEC),
        "profile_map": PROFILE_MAP,
        "profile_map_sha256": _canonical_hash(PROFILE_MAP),
        "fact_map": FACT_MAP,
        "fact_map_sha256": _canonical_hash(FACT_MAP),
        "expected_case_count": 27,
        "expected_tau_testnet_commit": CURRENT_TAU_TESTNET_COMMIT,
        "actual_tau_testnet_commit": testnet_commit,
        "tau_testnet_status_porcelain": testnet_status.splitlines(),
        "expected_tau_source_commit": CURRENT_TAU_SOURCE_COMMIT,
        "actual_tau_source_commit": source_commit,
        "expected_tau_parser_commit": CURRENT_TAU_PARSER_COMMIT,
        "actual_tau_parser_commit": parser_commit,
        "tau_source_status_porcelain": source_status.splitlines(),
        "expected_tau_native_module_sha256": CURRENT_TAU_NATIVE_MODULE_SHA256,
        "tau_native_module_sha256": module_sha256,
        "tau_native_module_basename": tau_module.name,
        "pins_match": pins_match,
        "upstream_files_sha256": upstream_hashes,
        "child_returncode": child.returncode,
        "child_stdout_sha256": hashlib.sha256(child.stdout).hexdigest(),
        "child_stderr_sha256": hashlib.sha256(child.stderr).hexdigest(),
        "cases": child_report["cases"],
        "all_cases_match": child_report["all_cases_match"],
        "child_error": child_report.get("child_error", ""),
        "source_to_binding_status": (
            "DECLARED_LOCAL_BUILD_RELATION_NOT_INDEPENDENTLY_ATTESTED"
        ),
        "execution_environment_status": (
            "HOST_KERNEL_DYNAMIC_LIBRARIES_AND_HARDWARE_NOT_HERMETICALLY_ATTESTED"
        ),
        "tau_net_authority_status": (
            "DIRECT_NATIVE_ABI_PROBE_NOT_NODE_DEPLOYMENT_OR_CONSENSUS_FINALITY"
        ),
        "profile_authentication_status": (
            "CUSTOM_I17_PROFILE_IS_A_TRANSACTION_SUPPLIED_CLAIM"
        ),
        "fact_authentication_status": (
            "CUSTOM_I18_TO_I24_VALUES_ARE_TRANSACTION_SUPPLIED_CLAIMS"
        ),
        "settlement_status": "NO_RESERVE_NONCE_NULLIFIER_OR_ATOMIC_EFFECT_MOUNT",
        "nonclaims": [
            "Direct TauInterface execution is not an end-to-end node, admission, block-apply, governance, or finality test.",
            "The local source pin does not prove that public Tau Testnet nodes run these bytes.",
            "The local source pin does not independently attest how the native module was built.",
            "The transaction-supplied profile selector is not an authenticated protocol choice.",
            "The transaction-supplied fact values do not authenticate EETF, scarcity, exclusion, margins, evidence, reserves, or settlement.",
            "The V1 exclusive-upside fact does not itself enforce exclusion or move value.",
            "Current Tau Testnet is alpha; this receipt is not production-readiness or real-funds evidence.",
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
