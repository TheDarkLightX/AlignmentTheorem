"""Finite reference model for Alignment Theorem Version 2.

The model separates three claims that Version 1 combined:

* a policy gate decides whether an observable action is admissible;
* reserve accounting decides whether an admitted reward is funded; and
* a finite incentive inequality says when compliance is more profitable than
  a bounded deviation.

All monetary quantities are non-negative integer atoms.  Detection
probabilities use ``fractions.Fraction``.  This module is a reference model and
does not authenticate signatures or publish network state.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction

MAX_U64 = (1 << 64) - 1
MAX_CANDIDATES = 1_024
ACTION_ID = re.compile(r"[a-z][a-z0-9._-]{0,63}\Z")


class RejectCode(str, Enum):
    """Canonical, deterministic policy-gate outcomes."""

    ACCEPTED = "ACCEPTED"
    POLICY_ROOT_MISMATCH = "POLICY_ROOT_MISMATCH"
    EVIDENCE_UNAUTHENTICATED = "EVIDENCE_UNAUTHENTICATED"
    UNKNOWN_ACTION = "UNKNOWN_ACTION"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    STALE_NONCE = "STALE_NONCE"
    TASK_ALREADY_CLAIMED = "TASK_ALREADY_CLAIMED"
    INSUFFICIENT_REWARD_RESERVE = "INSUFFICIENT_REWARD_RESERVE"


@dataclass(frozen=True)
class PolicyEvidence:
    """Host-authenticated facts consumed by the Tau policy kernel.

    A production adapter must derive these fields from authenticated state and
    receipts.  Caller assertions are not evidence.
    """

    policy_root_matches: bool
    evidence_authenticated: bool
    action_known: bool
    action_policy_compliant: bool
    nonce_fresh: bool
    task_unclaimed: bool

    def __post_init__(self) -> None:
        for name in (
            "policy_root_matches",
            "evidence_authenticated",
            "action_known",
            "action_policy_compliant",
            "nonce_fresh",
            "task_unclaimed",
        ):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be an exact bool")


@dataclass(frozen=True)
class GateDecision:
    accepted: bool
    code: RejectCode
    payout_atoms: int
    reserve_pre_atoms: int
    reserve_post_atoms: int


@dataclass(frozen=True)
class IncentiveEnvelope:
    """Finite assumptions for policy-relative incentive compatibility.

    ``max_private_deviation_gain_atoms`` bounds the benefit an agent can obtain
    from a noncompliant action outside the mechanism.  The theorem is only as
    credible as this bound and the evidence supporting it.
    """

    compliant_reward_atoms: int
    noncompliant_reward_atoms: int
    slash_atoms: int
    detection_probability: Fraction
    max_private_deviation_gain_atoms: int
    max_extra_compliance_cost_atoms: int
    optimizer_error_atoms: int = 0

    def __post_init__(self) -> None:
        for name in (
            "compliant_reward_atoms",
            "noncompliant_reward_atoms",
            "slash_atoms",
            "max_private_deviation_gain_atoms",
            "max_extra_compliance_cost_atoms",
            "optimizer_error_atoms",
        ):
            _require_u64(name, getattr(self, name))
        if type(self.detection_probability) is not Fraction:
            raise TypeError("detection_probability must be an exact Fraction")
        if not 0 <= self.detection_probability <= 1:
            raise ValueError("detection_probability must lie in [0, 1]")

    @property
    def mechanism_gap(self) -> Fraction:
        """Transfer advantage of compliance over noncompliance."""

        return Fraction(
            self.compliant_reward_atoms - self.noncompliant_reward_atoms
        ) + self.detection_probability * self.slash_atoms

    @property
    def required_gap(self) -> int:
        """Worst-case deviation advantage plus bounded optimizer error."""

        return (
            self.max_private_deviation_gain_atoms
            + self.max_extra_compliance_cost_atoms
            + self.optimizer_error_atoms
        )

    @property
    def has_strict_alignment_margin(self) -> bool:
        """Whether every epsilon-optimal response must be compliant."""

        return self.mechanism_gap > self.required_gap


@dataclass(frozen=True)
class CandidateAction:
    """One action proposed by a human, deterministic program, or LLM agent."""

    action_id: str
    evidence: PolicyEvidence
    private_profit_atoms: int
    requested_reward_atoms: int

    def __post_init__(self) -> None:
        if type(self.action_id) is not str or ACTION_ID.fullmatch(self.action_id) is None:
            raise TypeError("action_id must be a canonical lowercase ASCII identifier")
        if type(self.evidence) is not PolicyEvidence:
            raise TypeError("evidence must be an exact PolicyEvidence")
        _require_u64("private_profit_atoms", self.private_profit_atoms)
        _require_u64("requested_reward_atoms", self.requested_reward_atoms)


@dataclass(frozen=True)
class ShieldedChoice:
    action: CandidateAction | None
    decision: GateDecision | None
    total_profit_atoms: int


def _require_u64(name: str, value: object) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an exact int")
    if not 0 <= value <= MAX_U64:
        raise ValueError(f"{name} must lie in [0, {MAX_U64}]")
    return value


def evaluate_policy_gate(
    evidence: PolicyEvidence,
    *,
    requested_reward_atoms: int,
    reserve_atoms: int,
) -> GateDecision:
    """Evaluate the canonical fail-closed policy and reserve gate.

    Rejection is a no-op: payout is zero and the reserve is unchanged.
    """

    if type(evidence) is not PolicyEvidence:
        raise TypeError("evidence must be an exact PolicyEvidence")
    _require_u64("requested_reward_atoms", requested_reward_atoms)
    _require_u64("reserve_atoms", reserve_atoms)

    if not evidence.policy_root_matches:
        code = RejectCode.POLICY_ROOT_MISMATCH
    elif not evidence.evidence_authenticated:
        code = RejectCode.EVIDENCE_UNAUTHENTICATED
    elif not evidence.action_known:
        code = RejectCode.UNKNOWN_ACTION
    elif not evidence.action_policy_compliant:
        code = RejectCode.POLICY_VIOLATION
    elif not evidence.nonce_fresh:
        code = RejectCode.STALE_NONCE
    elif not evidence.task_unclaimed:
        code = RejectCode.TASK_ALREADY_CLAIMED
    elif requested_reward_atoms > reserve_atoms:
        code = RejectCode.INSUFFICIENT_REWARD_RESERVE
    else:
        return GateDecision(
            accepted=True,
            code=RejectCode.ACCEPTED,
            payout_atoms=requested_reward_atoms,
            reserve_pre_atoms=reserve_atoms,
            reserve_post_atoms=reserve_atoms - requested_reward_atoms,
        )

    return GateDecision(
        accepted=False,
        code=code,
        payout_atoms=0,
        reserve_pre_atoms=reserve_atoms,
        reserve_post_atoms=reserve_atoms,
    )


def choose_most_profitable_admissible_action(
    candidates: Iterable[CandidateAction],
    *,
    reserve_atoms: int,
) -> ShieldedChoice:
    """Choose profit after policy admission, with deterministic tie-breaking.

    This models a network where an LLM agent may propose arbitrary actions but
    only policy-admitted actions can be selected for publication.  It is not a
    model of LLM training or cognition.
    """

    _require_u64("reserve_atoms", reserve_atoms)
    admitted: list[tuple[int, str, CandidateAction, GateDecision]] = []
    seen_ids: set[str] = set()
    for index, action in enumerate(candidates):
        if index >= MAX_CANDIDATES:
            raise ValueError(f"candidate count exceeds {MAX_CANDIDATES}")
        if type(action) is not CandidateAction:
            raise TypeError("every candidate must be an exact CandidateAction")
        if action.action_id in seen_ids:
            raise ValueError(f"duplicate action_id: {action.action_id}")
        seen_ids.add(action.action_id)
        decision = evaluate_policy_gate(
            action.evidence,
            requested_reward_atoms=action.requested_reward_atoms,
            reserve_atoms=reserve_atoms,
        )
        if decision.accepted:
            total = action.private_profit_atoms + decision.payout_atoms
            if total > MAX_U64:
                raise ValueError("total profit exceeds u64 range")
            admitted.append((total, action.action_id, action, decision))

    if not admitted:
        return ShieldedChoice(action=None, decision=None, total_profit_atoms=0)

    # Highest profit wins.  Lexicographically smallest action ID breaks ties.
    admitted.sort(key=lambda row: (-row[0], row[1]))
    total, _, action, decision = admitted[0]
    return ShieldedChoice(
        action=action,
        decision=decision,
        total_profit_atoms=total,
    )
