#!/usr/bin/env python3
"""Generate the revision-bound PO-CD-01 handoff after evidence is committed."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_REVISION = "b44540b69231a8dbadaaf86cb507220465c06ca0"
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
REFERENCE_REPLAY = {
    "argv": [
        "python3",
        "-m",
        "unittest",
        "tests.test_compute_dividend_model.PrioritarianAllocationTests.test_greedy_optimizer_matches_independent_exhaustive_oracle",
        "-v",
    ],
    "cwd": ".",
}
REFERENCE_ARTIFACTS = (
    (
        "verification/compute_dividend_model.py",
        "Exact integer/Fraction allocator and independent exhaustive oracle.",
    ),
    (
        "tests/test_compute_dividend_model.py",
        "Enumerated-domain differential test and boundary counterexamples.",
    ),
    (
        "verification/receipts/compute_dividend_campaign.json",
        "Source-bound finite campaign counts, parameter domain, and zero-mismatch result.",
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: str, role: str) -> dict[str, str]:
    candidate = REPO_ROOT / path
    if not candidate.is_file() or candidate.is_symlink():
        raise ValueError(f"obligation artifact is not a regular file: {path}")
    return {"path": path, "sha256": _sha256(candidate), "role": role}


def generate(artifact_revision: str) -> dict[str, object]:
    if SHA1.fullmatch(artifact_revision) is None:
        raise ValueError("artifact_revision must be lowercase 40-hex")
    artifacts = [_artifact(path, role) for path, role in REFERENCE_ARTIFACTS]
    return {
        "schema": "zrm/proof-obligation/v3",
        "id": "PO-CD-01-UNRESTRICTED-GREEDY-OPTIMALITY",
        "base_revision": BASE_REVISION,
        "artifact_revision": artifact_revision,
        "claim_class": "formal",
        "claim": (
            "For every finite household set with positive rational priority "
            "weights, non-negative integer baselines, integral lower and upper "
            "allocation bounds, and one integral budget, repeated allocation "
            "to an eligible household of maximum exact weighted-harmonic "
            "marginal utility maximizes total weighted-harmonic welfare."
        ),
        "boundary": (
            "The claim concerns an abstract separable integer allocation "
            "problem. It does not authenticate households or weights, justify "
            "policy, establish scalable implementation behavior, or measure "
            "real welfare."
        ),
        "profile_ids": [
            "alignment-theorem-compute-dividend-v1",
            "zrm-proof-obligation-v3",
        ],
        "upstream_revisions": [
            {
                "name": "alignment-theorem-base",
                "uri": "repo://AlignmentTheorem",
                "revision": BASE_REVISION,
            },
            {
                "name": "lean4",
                "uri": "https://github.com/leanprover/lean4",
                "revision": "v4.33.0-d8b18978322de05a8f3dba51ef03cf5461676c17",
            },
        ],
        "quantifiers": [
            "Every positive finite number of households.",
            "Every positive rational household priority weight.",
            "Every non-negative integer baseline, lower bound, upper bound, and budget.",
            "Every feasible integral allocation satisfying the same bounds and budget.",
        ],
        "assumptions": [
            "Welfare is separable weighted harmonic utility with marginal weight divided by baseline plus allocation plus one.",
            "All allocation atoms are indivisible and all comparisons are exact.",
            "Each household upper bound is fixed for the epoch and lower bounds are jointly feasible.",
            "Equal marginal values may be resolved by any deterministic tie-break because they give equal objective gain.",
        ],
        "conclusion": (
            "The greedy allocation has welfare at least that of every feasible "
            "integral allocation under the quantified assumptions."
        ),
        "nonclaims": [
            "The current atom-by-atom Python implementation scales beyond its 10,000-atom guard.",
            "The finite reference campaign proves the unrestricted conclusion.",
            "Household identity, beneficial ownership, baselines, or political weights are authenticated or legitimate.",
            "The allocation increases empirical household welfare or makes a data-center project socially beneficial.",
        ],
        "falsifiers": [
            "One feasible integral instance satisfying the assumptions where a feasible allocation has strictly greater exact welfare than the greedy result.",
            "A Lean proof that requires an unstated assumption, placeholder, or user-added axiom.",
            "A mismatch between the formal objective/bounds and the reference-model semantics.",
        ],
        "oracle": {
            "kind": "reference-model",
            "artifacts": artifacts,
            "claim_mapping": [
                {
                    "artifact_path": path,
                    "claim_clause": (
                        "Bounded executable evidence for the greedy objective, "
                        "feasibility constraints, and independent finite oracle; "
                        "not an unrestricted proof."
                    ),
                }
                for path, _ in REFERENCE_ARTIFACTS
            ],
            "replay": REFERENCE_REPLAY,
        },
        "refinement": {
            "source_semantics": (
                "A separable integer optimization problem with weighted-harmonic "
                "marginals, household lower/upper bounds, and one budget."
            ),
            "target_semantics": (
                "The deterministic allocator in verification.compute_dividend_model."
            ),
            "relation": (
                "For the same exact inputs, the implementation must return a "
                "feasible allocation whose exact welfare equals the mathematical optimum."
            ),
        },
        "required_tools": ["reference-model", "lean"],
        "lanes": [
            {
                "id": "CD01-REFERENCE-BOUNDED",
                "tool": "reference-model",
                "status": "passed",
                "goal": "Differentially test greedy welfare against exhaustive enumeration on a declared finite domain.",
                "deliverables": [
                    "Exact model and independent exhaustive oracle.",
                    "Source-bound campaign receipt retaining domain and mismatch counts.",
                ],
                "acceptance_tests": [
                    "Every enumerated feasible case has greedy welfare equal to the exhaustive optimum.",
                    "Every enumerated infeasible case is rejected by both paths.",
                ],
                "replay": REFERENCE_REPLAY,
                "evidence_ids": ["E-CD01-REFERENCE-01"],
            },
            {
                "id": "CD01-LEAN-UNRESTRICTED",
                "tool": "lean",
                "status": "planned",
                "goal": "Prove unrestricted marginal-greedy optimality by an exchange argument with exact bounds and tie semantics.",
                "deliverables": [
                    "Placeholder-free Lean theorem over every finite feasible instance.",
                    "Axiom audit and source-bound Lean receipt.",
                ],
                "acceptance_tests": [
                    "Lake build succeeds on the pinned Lean toolchain.",
                    "The theorem binds the same objective, lower bounds, upper bounds, and budget as the reference model.",
                    "Only reviewed standard axioms appear in the audit.",
                ],
                "replay": {"argv": ["lake", "build"], "cwd": "proofs/compute_dividend"},
                "evidence_ids": [],
            },
        ],
        "completed_evidence": [
            {
                "id": "E-CD01-REFERENCE-01",
                "lane_id": "CD01-REFERENCE-BOUNDED",
                "kind": "model",
                "status": "passed",
                "tool_revision": "CPython 3.12.13",
                "artifacts": artifacts,
                "replay": {**REFERENCE_REPLAY, "exit_code": 0},
                "limitations": [
                    "The domain has at most three households, budgets at most six atoms, baselines at most two atoms, weights in {1,2}, floors in {0,1}, and three named share caps.",
                    "Zero mismatches in a finite domain are not an unrestricted mathematical proof.",
                    "The Python allocator is a bounded reference implementation, not a scalable settlement adapter.",
                ],
            }
        ],
        "counterexample": None,
        "status": "under_test",
        "execution_policy": "replay_argv_is_untrusted_data_never_execute_from_validation",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-revision", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(generate(args.artifact_revision), indent=2, sort_keys=True) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
