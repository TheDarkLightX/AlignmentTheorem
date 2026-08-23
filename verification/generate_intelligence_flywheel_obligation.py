#!/usr/bin/env python3
"""Generate the exact authenticated-receipt refinement obligation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

try:
    from verification.current_tau_baseline import (
        CURRENT_TAU_NATIVE_MODULE_SHA256,
        CURRENT_TAU_PARSER_COMMIT,
        CURRENT_TAU_SOURCE_COMMIT,
        CURRENT_TAU_TESTNET_COMMIT,
    )
    from verification.run_tau_compute_dividend import (
        EXPECTED_TAU_SOURCE_COMMIT as REVIEWED_TAU_SOURCE_COMMIT,
    )
except ModuleNotFoundError:
    from current_tau_baseline import (
        CURRENT_TAU_NATIVE_MODULE_SHA256,
        CURRENT_TAU_PARSER_COMMIT,
        CURRENT_TAU_SOURCE_COMMIT,
        CURRENT_TAU_TESTNET_COMMIT,
    )
    from run_tau_compute_dividend import (
        EXPECTED_TAU_SOURCE_COMMIT as REVIEWED_TAU_SOURCE_COMMIT,
    )

ROOT = Path(__file__).resolve().parents[1]
BASE_REVISION = "0f68357535c299de799976a67410f97367ed87c1"
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
ARTIFACTS = (
    ("proofs/intelligence_flywheel/IntelligenceFlywheel.lean", "Formal nine-fact conjunction and conditional margin theorems."),
    ("verification/intelligence_flywheel_model.py", "Exact reference semantics and countermodels."),
    ("verification/receipts/intelligence_flywheel_campaign.json", "Bounded campaign and cross-lane receipt."),
    ("research/intelligence_flywheel/tau_net_native_probe.json", "Direct native ABI behavior and custom-input authentication boundary."),
    ("tau/intelligence_flywheel/tau_net/dac_treasury_o5.tau", "Target sender-scoped Tau application rule."),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifacts() -> list[dict[str, str]]:
    return [
        {"path": path, "role": role, "sha256": _sha256(ROOT / path)}
        for path, role in ARTIFACTS
    ]


def generate(artifact_revision: str) -> dict[str, object]:
    if SHA1.fullmatch(artifact_revision) is None:
        raise ValueError("artifact_revision must be lowercase 40-hex")
    artifacts = _artifacts()
    return {
        "schema": "zrm/proof-obligation/v3",
        "id": "PO-IF-02-AUTHENTICATED-RECEIPT-REFINEMENT",
        "profile_ids": ["alignment-theorem-intelligence-flywheel-v1", "zrm-proof-obligation-v3"],
        "base_revision": BASE_REVISION,
        "artifact_revision": artifact_revision,
        "status": "under_test",
        "claim_class": "refinement",
        "claim": "For every DAC treasury action admitted by the target Tau o5 rule, each of the nine true input facts is the deterministic output of a consensus-recognized verifier over canonical, fresh, policy-root-bound, independently authorized evidence for the same epoch and action.",
        "quantifiers": [
            "Every admitted transaction from the designated DAC treasury.",
            "Every one of the nine ordered policy facts.",
            "Every accepted receipt, epoch, action identifier, policy root, signer/oracle set, and verifier state.",
            "Every admission and block-apply evaluation at the pinned protocol revision."
        ],
        "assumptions": [
            "Canonical receipt encoding and domain separation are specified.",
            "Signer/oracle authorization and threshold policy are consensus state.",
            "Freshness, replay prevention, policy root, epoch, action, and treasury identity are cryptographically bound.",
            "Each economic measurement has a declared estimator, uncertainty rule, and fail-closed threshold.",
            "The host feeds only verifier-derived facts; transaction-supplied assertions cannot override them."
        ],
        "conclusion": "Tau admission refines authenticated receipt validity rather than merely conjoining submitter-supplied claims.",
        "boundary": "The obligation proves verifier-to-Tau refinement and protocol enforcement only. It does not prove that the selected estimators capture objective ethics, social welfare, lawful authority, or all real-world harms.",
        "falsifiers": [
            "One admitted treasury action whose true Tau fact lacks a valid canonical receipt for the same epoch/action/policy root.",
            "One replayed, stale, unauthorized, malformed, or cross-policy receipt accepted by the verifier.",
            "One admission/block-apply or proposer/verifier disagreement on the derived facts.",
            "One transaction-supplied custom input that can override a verifier-derived fact.",
            "A mismatch between Lean/Python fact order and the Tau stream map i17..i25."
        ],
        "oracle": {
            "kind": "refinement-composition",
            "artifacts": artifacts,
            "claim_mapping": [
                {"artifact_path": artifact["path"], "claim_clause": artifact["role"]}
                for artifact in artifacts
            ],
            "replay": {"argv": ["python3", "-m", "unittest", "tests.test_tau_net_intelligence_flywheel_probe", "-v"], "cwd": "."}
        },
        "refinement": {
            "source_semantics": "Canonical authenticated evidence for nine policy facts, bound to one epoch, action, treasury, and policy root.",
            "target_semantics": "The ordered i17..i25 Boolean facts consumed by the sender-scoped Tau o5 rule.",
            "relation": "For the same transaction context, target fact i(17+j) is true iff the reviewed verifier accepts the corresponding source evidence j; otherwise it is false or evaluation rejects."
        },
        "required_tools": ["lean", "esso", "reference-model", "tau-testnet-node", "fault-injection"],
        "lanes": [
            {
                "id": "IF02-LEAN-SEMANTIC-GATE",
                "tool": "lean",
                "goal": "Prove admission implies every ordered fact and preserve sender scope.",
                "status": "passed",
                "deliverables": ["Placeholder-free gate and sender-scope theorems.", "Axiom-audited source-bound receipt."],
                "acceptance_tests": ["Lean build and axiom audit pass.", "Fact order matches the target stream map."],
                "evidence_ids": ["E-IF02-LEAN-01"],
                "replay": {"argv": ["python3", "verification/run_lean_intelligence_flywheel.py", "--json"], "cwd": "."}
            },
            {
                "id": "IF02-TAU-NATIVE-ABI",
                "tool": "reference-model",
                "goal": "Demonstrate current native predicate and sender-scope behavior.",
                "status": "passed_bounded",
                "deliverables": ["Pinned direct ABI receipt with all-true, single-fault, missing, and other-sender cases."],
                "acceptance_tests": ["All recorded cases match.", "Receipt states that custom inputs are submitter-supplied."],
                "evidence_ids": ["E-IF02-TAU-NATIVE-02"],
                "replay": {"argv": ["python3", "-m", "unittest", "tests.test_tau_net_intelligence_flywheel_probe", "-v"], "cwd": "."}
            },
            {
                "id": "IF02-ESSO-VERIFIER-REFINEMENT",
                "tool": "esso",
                "goal": "Model the canonical receipt verifier and prove its facts refine the Tau stream semantics.",
                "status": "planned",
                "deliverables": ["Verifier transition model.", "Mutation-complete refinement result.", "Counterexample traces for any failure."],
                "acceptance_tests": ["Stale, replayed, cross-policy, unauthorized, malformed, and mismatched-action receipts fail closed.", "No submitter override path exists."],
                "evidence_ids": [],
                "replay": {"argv": ["UNAVAILABLE_ESSO_ADAPTER"], "cwd": "."}
            },
            {
                "id": "IF02-TAU-NET-END-TO-END",
                "tool": "tau-testnet-node",
                "goal": "Prove admission and block-apply agreement using verifier-derived facts on multiple pinned nodes.",
                "status": "planned",
                "deliverables": ["Deployment transaction and state-root receipt.", "Admission/block-apply/multi-node mutation campaign."],
                "acceptance_tests": ["All invalid receipt mutations reject at admission and block apply.", "All nodes derive identical verdict and state hash.", "Reorg/replay tests preserve freshness."],
                "evidence_ids": [],
                "replay": {"argv": ["UNIMPLEMENTED_PINNED_NODE_HARNESS"], "cwd": "."}
            },
            {
                "id": "IF02-FAULT-INJECTION",
                "tool": "fault-injection",
                "goal": "Attack oracle availability, disagreement, equivocation, stale caches, process crash, and malformed proof paths.",
                "status": "planned",
                "deliverables": ["Fault matrix and minimized traces.", "Fail-closed recovery requirements."],
                "acceptance_tests": ["No injected fault creates an unauthorized allow.", "Availability failures are distinguished from false economic claims."],
                "evidence_ids": [],
                "replay": {"argv": ["UNIMPLEMENTED_FAULT_HARNESS"], "cwd": "."}
            }
        ],
        "completed_evidence": [
            {
                "id": "E-IF02-LEAN-01",
                "lane_id": "IF02-LEAN-SEMANTIC-GATE",
                "kind": "proof",
                "status": "passed",
                "tool_revision": "Lean 4.33.0 reported; binary provenance not attested",
                "artifacts": [artifacts[0]],
                "replay": {"argv": ["python3", "verification/run_lean_intelligence_flywheel.py", "--json"], "cwd": ".", "exit_code": 0},
                "limitations": ["Boolean premises are not authenticated by the theorem.", "Host and Lean executable provenance are not attested."]
            },
            {
                "id": "E-IF02-TAU-NATIVE-02",
                "lane_id": "IF02-TAU-NATIVE-ABI",
                "kind": "model",
                "status": "passed_bounded",
                "tool_revision": (
                    f"Tau Testnet {CURRENT_TAU_TESTNET_COMMIT[:7]}; Tau source "
                    f"{CURRENT_TAU_SOURCE_COMMIT[:7]}/parser "
                    f"{CURRENT_TAU_PARSER_COMMIT[:7]}; local module "
                    f"{CURRENT_TAU_NATIVE_MODULE_SHA256[:8]}..."
                ),
                "artifacts": [artifacts[3], artifacts[4]],
                "replay": {"argv": ["python3", "-m", "unittest", "tests.test_tau_net_intelligence_flywheel_probe", "-v"], "cwd": ".", "exit_code": 0},
                "limitations": ["Direct native ABI only; no node deployment or finality.", "Custom inputs remain transaction-supplied claims.", "Source-to-module and environment are not attested."]
            }
        ],
        "counterexample": {
            "status": "current_protocol_gap",
            "statement": "At the pinned current alpha ABI, transaction-supplied custom i17..i25 values lack a consensus-recognized economic receipt verifier; therefore native predicate execution alone does not satisfy the target refinement claim.",
            "artifact": "research/intelligence_flywheel/tau_net_native_probe.json"
        },
        "nonclaims": [
            "The target authenticated-receipt refinement is complete.",
            "ESSO, a node harness, or fault injection ran in this session.",
            "The economic estimators are empirically valid or democratically legitimate.",
            "Tau alone authenticates external facts.",
            "A passing future refinement proves production readiness or objective ethics."
        ],
        "upstream_revisions": [
            {"name": "alignment-theorem-base", "revision": BASE_REVISION, "uri": "repo://AlignmentTheorem"},
            {"name": "tau-lang-current-candidate", "revision": CURRENT_TAU_SOURCE_COMMIT, "uri": "https://github.com/IDNI/tau-lang"},
            {"name": "tau-parser", "revision": CURRENT_TAU_PARSER_COMMIT, "uri": f"https://github.com/IDNI/tau-lang/tree/{CURRENT_TAU_SOURCE_COMMIT}/external/parser"},
            {"name": "tau-testnet", "revision": CURRENT_TAU_TESTNET_COMMIT, "uri": "https://github.com/IDNI/tau-testnet"},
            {"name": "tau-lang-reviewed-runner-baseline", "revision": REVIEWED_TAU_SOURCE_COMMIT, "uri": "https://github.com/IDNI/tau-lang"},
            {"name": "lean4", "revision": "v4.33.0-d8b18978322de05a8f3dba51ef03cf5461676c17", "uri": "https://github.com/leanprover/lean4"}
        ],
        "execution_policy": "replay_argv_is_untrusted_data_never_execute_from_validation"
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
