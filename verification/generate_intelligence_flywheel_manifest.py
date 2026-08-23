#!/usr/bin/env python3
"""Generate the revision-bound intelligence-flywheel manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

try:
    from verification.current_tau_baseline import (
        CURRENT_TAU_BINARY_SHA256,
        CURRENT_TAU_NATIVE_MODULE_SHA256,
        CURRENT_TAU_PARSER_COMMIT,
        CURRENT_TAU_SOURCE_COMMIT,
        CURRENT_TAU_TESTNET_COMMIT,
        CURRENT_TAU_VERSION,
    )
    from verification.run_tau_compute_dividend import (
        EXPECTED_TAU_BINARY_SHA256,
        EXPECTED_TAU_PARSER_COMMIT,
        EXPECTED_TAU_SOURCE_COMMIT,
        EXPECTED_TAU_VERSION,
        _tree_sha256,
    )
except ModuleNotFoundError:
    from current_tau_baseline import (
        CURRENT_TAU_BINARY_SHA256,
        CURRENT_TAU_NATIVE_MODULE_SHA256,
        CURRENT_TAU_PARSER_COMMIT,
        CURRENT_TAU_SOURCE_COMMIT,
        CURRENT_TAU_TESTNET_COMMIT,
        CURRENT_TAU_VERSION,
    )
    from run_tau_compute_dividend import (
        EXPECTED_TAU_BINARY_SHA256,
        EXPECTED_TAU_PARSER_COMMIT,
        EXPECTED_TAU_SOURCE_COMMIT,
        EXPECTED_TAU_VERSION,
        _tree_sha256,
    )

ROOT = Path(__file__).resolve().parents[1]
BASE_REVISION = "44c14df0a9b3f74d7cceb7f122176c84374faf1e"
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
FILES = (
    "README.md",
    "TOOLCHAINS.md",
    "docs/index.html",
    "docs/alignment-theorem-deep-dive.html",
    "docs/intelligence-hyperdeflation-flywheel.html",
    "proofs/intelligence_flywheel/IntelligenceFlywheel.lean",
    "proofs/intelligence_flywheel/AxiomAudit.lean",
    "proofs/intelligence_flywheel/lakefile.lean",
    "proofs/intelligence_flywheel/lake-manifest.json",
    "proofs/intelligence_flywheel/lean-toolchain",
    "research/intelligence_flywheel/README.md",
    "research/intelligence_flywheel/MATHEMATICAL_MODEL.md",
    "research/intelligence_flywheel/TAU_NET_REPLAY.md",
    "research/intelligence_flywheel/CLAIM_BOUNDARY.md",
    "research/intelligence_flywheel/PROOF_OBLIGATIONS.md",
    "research/intelligence_flywheel/source_ledger.json",
    "research/intelligence_flywheel/hypothesis_ledger.json",
    "research/intelligence_flywheel/experiment_ledger.json",
    "research/intelligence_flywheel/graph_ledger.json",
    "research/intelligence_flywheel/context_bundle.json",
    "research/intelligence_flywheel/research_kernel_status.json",
    "research/intelligence_flywheel/handoff_blocker.json",
    "research/intelligence_flywheel/tau_candidate_probe.json",
    "research/intelligence_flywheel/tau_net_native_probe.json",
    "research/current_tau/current_tau_packet_probe.json",
    "verification/current_tau_baseline.py",
    "verification/intelligence_flywheel_model.py",
    "verification/generate_tau_intelligence_flywheel_packet.py",
    "verification/run_lean_intelligence_flywheel.py",
    "verification/run_tau_intelligence_flywheel_reviewed.py",
    "verification/probe_tau_intelligence_flywheel_candidate.py",
    "verification/tau_net_intelligence_flywheel_child.py",
    "verification/probe_tau_net_intelligence_flywheel.py",
    "verification/run_intelligence_flywheel_campaign.py",
    "verification/generate_intelligence_flywheel_manifest.py",
    "verification/generate_intelligence_flywheel_obligation.py",
    "verification/receipts/lean_intelligence_flywheel_v4.33.0.json",
    "verification/receipts/intelligence_flywheel_campaign.json",
    "verification/pending/tau_intelligence_flywheel_fd137e8_preflight.json",
    "tests/test_intelligence_flywheel_model.py",
    "tests/test_lean_intelligence_flywheel_receipt.py",
    "tests/test_tau_intelligence_flywheel.py",
    "tests/test_tau_intelligence_flywheel_candidate_probe.py",
    "tests/test_tau_intelligence_flywheel_reviewed_preflight.py",
    "tests/test_tau_net_intelligence_flywheel_probe.py",
    "tests/test_intelligence_flywheel_campaign_receipt.py",
    "tests/test_intelligence_flywheel_research_packet.py",
    "tests/test_intelligence_flywheel_manifest.py",
    "tests/test_intelligence_flywheel_proof_obligation.py"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(artifact_revision: str) -> dict[str, object]:
    if SHA1.fullmatch(artifact_revision) is None:
        raise ValueError("artifact_revision must be lowercase 40-hex")
    files = {}
    for relative in FILES:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"manifest input is not a regular file: {relative}")
        files[relative] = _sha256(path)
    return {
        "schema": "alignment-theorem-intelligence-flywheel-manifest-v1",
        "base_revision": BASE_REVISION,
        "artifact_revision": artifact_revision,
        "files_sha256": files,
        "tau_packet_roots_sha256": {
            "semantic_gate": _tree_sha256(ROOT / "tau" / "intelligence_flywheel" / "gate"),
            "tau_net_rule": _tree_sha256(ROOT / "tau" / "intelligence_flywheel" / "tau_net"),
        },
        "expected_tau": {
            "source_commit": EXPECTED_TAU_SOURCE_COMMIT,
            "parser_commit": EXPECTED_TAU_PARSER_COMMIT,
            "version": EXPECTED_TAU_VERSION,
            "reviewed_linux_binary_sha256": EXPECTED_TAU_BINARY_SHA256,
            "reviewed_replay_status": "PENDING",
        },
        "current_tau_candidate": {
            "source_commit": CURRENT_TAU_SOURCE_COMMIT,
            "parser_commit": CURRENT_TAU_PARSER_COMMIT,
            "version": CURRENT_TAU_VERSION,
            "local_binary_sha256": CURRENT_TAU_BINARY_SHA256,
            "semantic_replay_status": "SUPPORTED_LOCAL_SOURCE_CANDIDATE",
            "source_to_binary_status": "DECLARED_NOT_INDEPENDENTLY_ATTESTED",
        },
        "observed_tau_net": {
            "source_commit": CURRENT_TAU_TESTNET_COMMIT,
            "tau_source_commit": CURRENT_TAU_SOURCE_COMMIT,
            "native_module_sha256": CURRENT_TAU_NATIVE_MODULE_SHA256,
            "evidence_scope": "DIRECT_NATIVE_ABI_ONLY",
        },
        "claim_status": "SUPPORTED_BOUNDED_WITH_OPEN_CAUSAL_ORACLE_NODE_AND_REVIEWED_REPLAY_GATES",
        "authority_status": "RESEARCH_REFERENCE_ONLY_NO_MACROECONOMIC_TAU_NET_OR_VALUE_AUTHORITY",
        "execution_policy": "commands_are_untrusted_data_do_not_execute_without_separate_approval",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-revision", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(generate(args.artifact_revision), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
