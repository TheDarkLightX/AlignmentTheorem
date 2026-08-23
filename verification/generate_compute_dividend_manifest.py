#!/usr/bin/env python3
"""Generate a revision-bound digest manifest after the evidence commit exists."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from verification.run_tau_compute_dividend import (
    EXPECTED_TAU_BINARY_SHA256,
    EXPECTED_TAU_PARSER_COMMIT,
    EXPECTED_TAU_SOURCE_COMMIT,
    EXPECTED_TAU_VERSION,
    _tree_sha256,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_REVISION = "b44540b69231a8dbadaaf86cb507220465c06ca0"
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
FILES = (
    "README.md",
    "TOOLCHAINS.md",
    "docs/THREAT_MODEL.md",
    "proofs/compute_dividend/ComputeDividend.lean",
    "proofs/compute_dividend/AxiomAudit.lean",
    "proofs/compute_dividend/lakefile.lean",
    "proofs/compute_dividend/lake-manifest.json",
    "proofs/compute_dividend/lean-toolchain",
    "research/compute_dividend/README.md",
    "research/compute_dividend/CLAIM_BOUNDARY.md",
    "research/compute_dividend/TAU_REPLAY.md",
    "research/compute_dividend/PROOF_OBLIGATIONS.md",
    "research/compute_dividend/source_ledger.json",
    "research/compute_dividend/hypothesis_ledger.json",
    "research/compute_dividend/experiment_ledger.json",
    "research/compute_dividend/graph_ledger.json",
    "research/compute_dividend/context_bundle.json",
    "research/compute_dividend/research_kernel_status.json",
    "research/compute_dividend/handoff_blocker.json",
    "research/compute_dividend/tau_source_candidate_probe.json",
    "verification/compat/lean_proc_self_compat.c",
    "verification/compute_dividend_model.py",
    "verification/generate_tau_compute_dividend_packets.py",
    "verification/run_tau_compute_dividend.py",
    "verification/probe_tau_compute_dividend_candidate.py",
    "verification/run_lean_compute_dividend.py",
    "verification/run_compute_dividend_campaign.py",
    "verification/generate_compute_dividend_manifest.py",
    "verification/generate_compute_dividend_obligation.py",
    "verification/pending/tau_v1_1_fd137e8_replay_plan.json",
    "verification/receipts/lean_compute_dividend_v4.33.0.json",
    "verification/receipts/compute_dividend_campaign.json",
    "tests/test_compute_dividend_model.py",
    "tests/test_tau_compute_dividend.py",
    "tests/test_lean_compute_dividend_receipt.py",
    "tests/test_compute_dividend_campaign_receipt.py",
    "tests/test_compute_dividend_research_packet.py",
    "tests/test_v1_1_tau_replay_plan.py",
    "tests/test_tau_compute_dividend_candidate_probe.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(artifact_revision: str) -> dict[str, object]:
    if SHA1.fullmatch(artifact_revision) is None:
        raise ValueError("artifact_revision must be lowercase 40-hex")
    files = {}
    for relative in FILES:
        path = REPO_ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"manifest input is not a regular file: {relative}")
        files[relative] = _sha256(path)
    return {
        "schema": "alignment-theorem-compute-dividend-manifest-v1",
        "base_revision": BASE_REVISION,
        "artifact_revision": artifact_revision,
        "files_sha256": files,
        "tau_packet_roots_sha256": {
            "v1_1": _tree_sha256(REPO_ROOT / "tau" / "v1_1"),
            "compute_dividend_dividend": _tree_sha256(
                REPO_ROOT / "tau" / "compute_dividend" / "dividend"
            ),
            "compute_dividend_wealth": _tree_sha256(
                REPO_ROOT / "tau" / "compute_dividend" / "wealth"
            ),
        },
        "expected_tau": {
            "source_commit": EXPECTED_TAU_SOURCE_COMMIT,
            "parser_commit": EXPECTED_TAU_PARSER_COMMIT,
            "version": EXPECTED_TAU_VERSION,
            "reviewed_linux_binary_sha256": EXPECTED_TAU_BINARY_SHA256,
        },
        "claim_status": "SUPPORTED_BOUNDED_WITH_OPEN_EMPIRICAL_AND_TAU_REPLAY_GATES",
        "authority_status": "RESEARCH_REFERENCE_ONLY_NO_FINANCIAL_OR_VALUE_AUTHORITY",
        "execution_policy": "commands_are_untrusted_data_do_not_execute_without_separate_approval",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = generate(args.artifact_revision)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
