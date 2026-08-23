"""Exact finite model for a data-center dividend and household wealth agent.

This module deliberately separates three boundaries:

* authenticated rent receipts determine a finite distributable reserve;
* a discrete concave allocator distributes that reserve subject to a universal
  floor and an earmarked-budget share cap; and
* an untrusted proposal engine may rank investment plans, but a fail-closed
  policy filter decides which plans are selectable.

All accounting is integer-valued and all ratios use ``fractions.Fraction``.
The model does not authenticate people, meters, rent receipts, market data, or
custody state.  It also does not predict or guarantee investment returns.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Iterable, Sequence

MAX_U64 = (1 << 64) - 1
MAX_HOUSEHOLDS = 64
MAX_PLANS = 1_024
MAX_ALLOCATION_BUDGET_ATOMS = 10_000
MAX_SCENARIOS = 10_000
MAX_ORACLE_STATES = 1_000_000
BASIS_POINTS = 10_000
CANONICAL_ID = re.compile(r"[a-z][a-z0-9._-]{0,63}\Z")


def _require_u64(name: str, value: object) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an exact int")
    if not 0 <= value <= MAX_U64:
        raise ValueError(f"{name} must lie in [0, {MAX_U64}]")
    return value


def _require_bps(name: str, value: object) -> int:
    _require_u64(name, value)
    if value > BASIS_POINTS:
        raise ValueError(f"{name} must lie in [0, {BASIS_POINTS}]")
    return value


def _require_bool(name: str, value: object) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{name} must be an exact bool")
    return value


def _require_id(name: str, value: object) -> str:
    if type(value) is not str or CANONICAL_ID.fullmatch(value) is None:
        raise TypeError(f"{name} must be a canonical lowercase ASCII identifier")
    return value


@dataclass(frozen=True)
class RentBudget:
    """One epoch of gross rent and senior claims on that rent."""

    gross_rent_atoms: int
    incremental_grid_cost_atoms: int
    public_reserve_atoms: int

    def __post_init__(self) -> None:
        _require_u64("gross_rent_atoms", self.gross_rent_atoms)
        _require_u64("incremental_grid_cost_atoms", self.incremental_grid_cost_atoms)
        _require_u64("public_reserve_atoms", self.public_reserve_atoms)

    @property
    def senior_claims_funded(self) -> bool:
        return (
            self.incremental_grid_cost_atoms + self.public_reserve_atoms
            <= self.gross_rent_atoms
        )

    @property
    def distributable_atoms(self) -> int:
        """Fail closed when authenticated senior claims exceed gross rent."""

        if not self.senior_claims_funded:
            return 0
        return self.gross_rent_atoms - (
            self.incremental_grid_cost_atoms + self.public_reserve_atoms
        )


@dataclass(frozen=True)
class DividendObligations:
    """Host-derived facts consumed by the Tau dividend gate."""

    policy_root_ok: bool
    rent_receipt_authenticated: bool
    grid_costs_reserved: bool
    dividend_reserve_funded: bool
    recipient_eligible: bool
    nonce_fresh: bool
    concentration_cap_ok: bool
    agent_compute_funded: bool

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            _require_bool(name, getattr(self, name))


def dividend_admits(obligations: DividendObligations) -> bool:
    if type(obligations) is not DividendObligations:
        raise TypeError("obligations must be an exact DividendObligations")
    return all(getattr(obligations, name) for name in obligations.__dataclass_fields__)


class DividendRejectCode(str, Enum):
    ACCEPTED = "ACCEPTED"
    POLICY_ROOT_MISMATCH = "POLICY_ROOT_MISMATCH"
    RENT_RECEIPT_UNAUTHENTICATED = "RENT_RECEIPT_UNAUTHENTICATED"
    GRID_COSTS_NOT_RESERVED = "GRID_COSTS_NOT_RESERVED"
    DIVIDEND_RESERVE_UNFUNDED = "DIVIDEND_RESERVE_UNFUNDED"
    RECIPIENT_INELIGIBLE = "RECIPIENT_INELIGIBLE"
    STALE_NONCE = "STALE_NONCE"
    CONCENTRATION_CAP_VIOLATION = "CONCENTRATION_CAP_VIOLATION"
    AGENT_COMPUTE_UNFUNDED = "AGENT_COMPUTE_UNFUNDED"
    INSUFFICIENT_DISTRIBUTABLE_RESERVE = "INSUFFICIENT_DISTRIBUTABLE_RESERVE"


@dataclass(frozen=True)
class DividendDecision:
    accepted: bool
    code: DividendRejectCode
    payout_atoms: int
    reserve_pre_atoms: int
    reserve_post_atoms: int


def settle_dividend(
    obligations: DividendObligations,
    *,
    requested_atoms: int,
    distributable_reserve_atoms: int,
) -> DividendDecision:
    """Apply the semantic gate and exact reserve check; rejection is a no-op."""

    if type(obligations) is not DividendObligations:
        raise TypeError("obligations must be an exact DividendObligations")
    _require_u64("requested_atoms", requested_atoms)
    _require_u64("distributable_reserve_atoms", distributable_reserve_atoms)

    checks = (
        (obligations.policy_root_ok, DividendRejectCode.POLICY_ROOT_MISMATCH),
        (
            obligations.rent_receipt_authenticated,
            DividendRejectCode.RENT_RECEIPT_UNAUTHENTICATED,
        ),
        (
            obligations.grid_costs_reserved,
            DividendRejectCode.GRID_COSTS_NOT_RESERVED,
        ),
        (
            obligations.dividend_reserve_funded,
            DividendRejectCode.DIVIDEND_RESERVE_UNFUNDED,
        ),
        (obligations.recipient_eligible, DividendRejectCode.RECIPIENT_INELIGIBLE),
        (obligations.nonce_fresh, DividendRejectCode.STALE_NONCE),
        (
            obligations.concentration_cap_ok,
            DividendRejectCode.CONCENTRATION_CAP_VIOLATION,
        ),
        (
            obligations.agent_compute_funded,
            DividendRejectCode.AGENT_COMPUTE_UNFUNDED,
        ),
    )
    for passed, code in checks:
        if not passed:
            return DividendDecision(
                accepted=False,
                code=code,
                payout_atoms=0,
                reserve_pre_atoms=distributable_reserve_atoms,
                reserve_post_atoms=distributable_reserve_atoms,
            )

    if requested_atoms > distributable_reserve_atoms:
        return DividendDecision(
            accepted=False,
            code=DividendRejectCode.INSUFFICIENT_DISTRIBUTABLE_RESERVE,
            payout_atoms=0,
            reserve_pre_atoms=distributable_reserve_atoms,
            reserve_post_atoms=distributable_reserve_atoms,
        )
    return DividendDecision(
        accepted=True,
        code=DividendRejectCode.ACCEPTED,
        payout_atoms=requested_atoms,
        reserve_pre_atoms=distributable_reserve_atoms,
        reserve_post_atoms=distributable_reserve_atoms - requested_atoms,
    )


@dataclass(frozen=True)
class Household:
    household_id: str
    base_resources_atoms: int
    priority_weight: int = 1

    def __post_init__(self) -> None:
        _require_id("household_id", self.household_id)
        _require_u64("base_resources_atoms", self.base_resources_atoms)
        _require_u64("priority_weight", self.priority_weight)
        if self.priority_weight == 0:
            raise ValueError("priority_weight must be positive")


@dataclass(frozen=True)
class AllocationPolicy:
    """A universal floor plus a cap relative to the earmarked epoch budget."""

    universal_floor_atoms: int
    max_earmarked_budget_share: Fraction

    def __post_init__(self) -> None:
        _require_u64("universal_floor_atoms", self.universal_floor_atoms)
        if type(self.max_earmarked_budget_share) is not Fraction:
            raise TypeError("max_earmarked_budget_share must be an exact Fraction")
        if not 0 < self.max_earmarked_budget_share <= 1:
            raise ValueError("max_earmarked_budget_share must lie in (0, 1]")

    def per_household_cap_atoms(self, earmarked_budget_atoms: int) -> int:
        _require_u64("earmarked_budget_atoms", earmarked_budget_atoms)
        share = self.max_earmarked_budget_share
        return (share.numerator * earmarked_budget_atoms) // share.denominator


@dataclass(frozen=True)
class HouseholdAllocation:
    household_id: str
    allocation_atoms: int


@dataclass(frozen=True)
class AllocationResult:
    feasible: bool
    failure_code: str
    allocations: tuple[HouseholdAllocation, ...]
    earmarked_budget_atoms: int
    spent_atoms: int
    unspent_atoms: int
    per_household_cap_atoms: int
    welfare_gain: Fraction

    def by_household(self) -> dict[str, int]:
        return {row.household_id: row.allocation_atoms for row in self.allocations}


def _marginal_gain(household: Household, allocated_atoms: int) -> Fraction:
    """Exact discrete derivative of weighted harmonic (log-like) utility."""

    return Fraction(
        household.priority_weight,
        household.base_resources_atoms + allocated_atoms + 1,
    )


def _welfare_gain(household: Household, allocated_atoms: int) -> Fraction:
    return sum(
        (
            Fraction(household.priority_weight, household.base_resources_atoms + unit)
            for unit in range(1, allocated_atoms + 1)
        ),
        start=Fraction(0),
    )


def _prepare_households(households: Iterable[Household]) -> tuple[Household, ...]:
    ordered: list[Household] = []
    seen: set[str] = set()
    for index, household in enumerate(households):
        if index >= MAX_HOUSEHOLDS:
            raise ValueError(f"household count exceeds {MAX_HOUSEHOLDS}")
        if type(household) is not Household:
            raise TypeError("every household must be an exact Household")
        if household.household_id in seen:
            raise ValueError(f"duplicate household_id: {household.household_id}")
        seen.add(household.household_id)
        ordered.append(household)
    if not ordered:
        raise ValueError("at least one household is required")
    return tuple(sorted(ordered, key=lambda row: row.household_id))


def allocate_prioritarian(
    households: Iterable[Household],
    *,
    earmarked_budget_atoms: int,
    policy: AllocationPolicy,
) -> AllocationResult:
    """Greedy exact optimizer for separable discrete concave welfare.

    Each household first receives the universal floor.  Remaining atoms go to
    the highest exact marginal weighted-harmonic gain.  Lexicographic household
    ID breaks equal-marginal ties.  The cap is a share of the original earmarked
    budget, not a claim about total household wealth or Sybil resistance.
    """

    ordered = _prepare_households(households)
    _require_u64("earmarked_budget_atoms", earmarked_budget_atoms)
    if earmarked_budget_atoms > MAX_ALLOCATION_BUDGET_ATOMS:
        raise ValueError(
            f"earmarked_budget_atoms exceeds {MAX_ALLOCATION_BUDGET_ATOMS}"
        )
    if type(policy) is not AllocationPolicy:
        raise TypeError("policy must be an exact AllocationPolicy")

    cap = policy.per_household_cap_atoms(earmarked_budget_atoms)
    floor = policy.universal_floor_atoms
    floor_cost = len(ordered) * floor
    if floor > cap:
        return AllocationResult(
            feasible=False,
            failure_code="FLOOR_EXCEEDS_SHARE_CAP",
            allocations=(),
            earmarked_budget_atoms=earmarked_budget_atoms,
            spent_atoms=0,
            unspent_atoms=earmarked_budget_atoms,
            per_household_cap_atoms=cap,
            welfare_gain=Fraction(0),
        )
    if floor_cost > earmarked_budget_atoms:
        return AllocationResult(
            feasible=False,
            failure_code="UNIVERSAL_FLOOR_UNFUNDED",
            allocations=(),
            earmarked_budget_atoms=earmarked_budget_atoms,
            spent_atoms=0,
            unspent_atoms=earmarked_budget_atoms,
            per_household_cap_atoms=cap,
            welfare_gain=Fraction(0),
        )

    allocation = [floor for _ in ordered]
    remaining = earmarked_budget_atoms - floor_cost
    while remaining:
        eligible = [index for index, amount in enumerate(allocation) if amount < cap]
        if not eligible:
            break
        winner = min(
            eligible,
            key=lambda index: (
                -_marginal_gain(ordered[index], allocation[index]),
                ordered[index].household_id,
            ),
        )
        allocation[winner] += 1
        remaining -= 1

    spent = sum(allocation)
    welfare = sum(
        (
            _welfare_gain(household, amount)
            for household, amount in zip(ordered, allocation, strict=True)
        ),
        start=Fraction(0),
    )
    return AllocationResult(
        feasible=True,
        failure_code="",
        allocations=tuple(
            HouseholdAllocation(household.household_id, amount)
            for household, amount in zip(ordered, allocation, strict=True)
        ),
        earmarked_budget_atoms=earmarked_budget_atoms,
        spent_atoms=spent,
        unspent_atoms=earmarked_budget_atoms - spent,
        per_household_cap_atoms=cap,
        welfare_gain=welfare,
    )


def exhaustive_optimal_welfare(
    households: Sequence[Household],
    *,
    earmarked_budget_atoms: int,
    policy: AllocationPolicy,
) -> Fraction | None:
    """Independent bounded oracle used only for finite research campaigns."""

    ordered = _prepare_households(households)
    _require_u64("earmarked_budget_atoms", earmarked_budget_atoms)
    if earmarked_budget_atoms > MAX_ALLOCATION_BUDGET_ATOMS:
        raise ValueError(
            f"earmarked_budget_atoms exceeds {MAX_ALLOCATION_BUDGET_ATOMS}"
        )
    if type(policy) is not AllocationPolicy:
        raise TypeError("policy must be an exact AllocationPolicy")
    floor = policy.universal_floor_atoms
    cap = policy.per_household_cap_atoms(earmarked_budget_atoms)
    if floor > cap or len(ordered) * floor > earmarked_budget_atoms:
        return None
    width = cap - floor + 1
    if width ** len(ordered) > MAX_ORACLE_STATES:
        raise ValueError("exhaustive oracle domain exceeds MAX_ORACLE_STATES")

    best: Fraction | None = None
    for candidate in itertools.product(range(floor, cap + 1), repeat=len(ordered)):
        if sum(candidate) > earmarked_budget_atoms:
            continue
        welfare = sum(
            (
                _welfare_gain(household, amount)
                for household, amount in zip(ordered, candidate, strict=True)
            ),
            start=Fraction(0),
        )
        if best is None or welfare > best:
            best = welfare
    return best


def progressive_transfer_delta(poorer_post: int, richer_post: int) -> Fraction:
    """Welfare change from moving one atom from richer to poorer.

    Equal-priority harmonic utility is assumed.  A non-negative value is a
    discrete Pigou-Dalton improvement; it is strictly positive when the initial
    post-resource gap exceeds one atom.
    """

    _require_u64("poorer_post", poorer_post)
    _require_u64("richer_post", richer_post)
    if richer_post == 0:
        raise ValueError("richer_post must be positive for a transfer")
    return Fraction(1, poorer_post + 1) - Fraction(1, richer_post)


def modeled_loss_preserves_floor(
    *, wealth_atoms: int, protected_floor_atoms: int, modeled_loss_atoms: int
) -> bool:
    """One-period arithmetic guard, not a claim that the loss bound is true."""

    _require_u64("wealth_atoms", wealth_atoms)
    _require_u64("protected_floor_atoms", protected_floor_atoms)
    _require_u64("modeled_loss_atoms", modeled_loss_atoms)
    return (
        protected_floor_atoms <= wealth_atoms
        and modeled_loss_atoms <= wealth_atoms - protected_floor_atoms
    )


@dataclass(frozen=True)
class ExternalWealthEvidence:
    policy_root_ok: bool
    household_consent_fresh: bool
    proposal_evidence_authenticated: bool
    custody_authorized: bool

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            _require_bool(name, getattr(self, name))


@dataclass(frozen=True)
class WealthPolicyLimits:
    max_issuer_concentration_bps: int
    max_empirical_tail_loss_atoms: int
    tail_scenario_count: int
    max_annual_fee_bps: int
    max_turnover_bps: int

    def __post_init__(self) -> None:
        _require_bps(
            "max_issuer_concentration_bps", self.max_issuer_concentration_bps
        )
        _require_u64(
            "max_empirical_tail_loss_atoms", self.max_empirical_tail_loss_atoms
        )
        _require_u64("tail_scenario_count", self.tail_scenario_count)
        if self.tail_scenario_count == 0:
            raise ValueError("tail_scenario_count must be positive")
        _require_bps("max_annual_fee_bps", self.max_annual_fee_bps)
        _require_bps("max_turnover_bps", self.max_turnover_bps)


@dataclass(frozen=True)
class WealthPlan:
    plan_id: str
    declared_score_atoms: int
    leverage_bps: int
    short_exposure_bps: int
    issuer_concentration_bps: int
    annual_fee_bps: int
    turnover_bps: int
    scenario_losses_atoms: tuple[int, ...]

    def __post_init__(self) -> None:
        _require_id("plan_id", self.plan_id)
        if type(self.declared_score_atoms) is not int:
            raise TypeError("declared_score_atoms must be an exact int")
        if not -MAX_U64 <= self.declared_score_atoms <= MAX_U64:
            raise ValueError("declared_score_atoms is outside the signed model range")
        _require_bps("leverage_bps", self.leverage_bps)
        _require_bps("short_exposure_bps", self.short_exposure_bps)
        _require_bps("issuer_concentration_bps", self.issuer_concentration_bps)
        _require_bps("annual_fee_bps", self.annual_fee_bps)
        _require_bps("turnover_bps", self.turnover_bps)
        if type(self.scenario_losses_atoms) is not tuple:
            raise TypeError("scenario_losses_atoms must be an exact tuple")
        if len(self.scenario_losses_atoms) > MAX_SCENARIOS:
            raise ValueError(f"scenario count exceeds {MAX_SCENARIOS}")
        for loss in self.scenario_losses_atoms:
            _require_u64("scenario loss", loss)


def empirical_tail_loss(losses: tuple[int, ...], tail_scenario_count: int) -> Fraction:
    if type(losses) is not tuple:
        raise TypeError("losses must be an exact tuple")
    _require_u64("tail_scenario_count", tail_scenario_count)
    if tail_scenario_count == 0:
        raise ValueError("tail_scenario_count must be positive")
    for loss in losses:
        _require_u64("scenario loss", loss)
    if len(losses) < tail_scenario_count:
        raise ValueError("not enough scenarios for the declared tail count")
    worst = sorted(losses, reverse=True)[:tail_scenario_count]
    return Fraction(sum(worst), tail_scenario_count)


@dataclass(frozen=True)
class WealthObligations:
    policy_root_ok: bool
    household_consent_fresh: bool
    proposal_evidence_authenticated: bool
    custody_authorized: bool
    no_leverage_or_short: bool
    concentration_limit_ok: bool
    tail_loss_limit_ok: bool
    fee_turnover_limit_ok: bool

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            _require_bool(name, getattr(self, name))


def wealth_admits(obligations: WealthObligations) -> bool:
    if type(obligations) is not WealthObligations:
        raise TypeError("obligations must be an exact WealthObligations")
    return all(getattr(obligations, name) for name in obligations.__dataclass_fields__)


class WealthRejectCode(str, Enum):
    ACCEPTED = "ACCEPTED"
    POLICY_ROOT_MISMATCH = "POLICY_ROOT_MISMATCH"
    CONSENT_STALE = "CONSENT_STALE"
    PROPOSAL_EVIDENCE_UNAUTHENTICATED = "PROPOSAL_EVIDENCE_UNAUTHENTICATED"
    CUSTODY_UNAUTHORIZED = "CUSTODY_UNAUTHORIZED"
    LEVERAGE_OR_SHORT_EXPOSURE = "LEVERAGE_OR_SHORT_EXPOSURE"
    CONCENTRATION_LIMIT_EXCEEDED = "CONCENTRATION_LIMIT_EXCEEDED"
    TAIL_SCENARIO_SET_INSUFFICIENT = "TAIL_SCENARIO_SET_INSUFFICIENT"
    EMPIRICAL_TAIL_LOSS_EXCEEDED = "EMPIRICAL_TAIL_LOSS_EXCEEDED"
    FEE_OR_TURNOVER_LIMIT_EXCEEDED = "FEE_OR_TURNOVER_LIMIT_EXCEEDED"


@dataclass(frozen=True)
class WealthPlanDecision:
    accepted: bool
    code: WealthRejectCode
    obligations: WealthObligations
    empirical_tail_loss_atoms: Fraction | None


def evaluate_wealth_plan(
    plan: WealthPlan,
    *,
    evidence: ExternalWealthEvidence,
    limits: WealthPolicyLimits,
) -> WealthPlanDecision:
    if type(plan) is not WealthPlan:
        raise TypeError("plan must be an exact WealthPlan")
    if type(evidence) is not ExternalWealthEvidence:
        raise TypeError("evidence must be an exact ExternalWealthEvidence")
    if type(limits) is not WealthPolicyLimits:
        raise TypeError("limits must be an exact WealthPolicyLimits")

    enough_scenarios = len(plan.scenario_losses_atoms) >= limits.tail_scenario_count
    tail_loss = (
        empirical_tail_loss(plan.scenario_losses_atoms, limits.tail_scenario_count)
        if enough_scenarios
        else None
    )
    obligations = WealthObligations(
        policy_root_ok=evidence.policy_root_ok,
        household_consent_fresh=evidence.household_consent_fresh,
        proposal_evidence_authenticated=evidence.proposal_evidence_authenticated,
        custody_authorized=evidence.custody_authorized,
        no_leverage_or_short=plan.leverage_bps == 0 and plan.short_exposure_bps == 0,
        concentration_limit_ok=(
            plan.issuer_concentration_bps <= limits.max_issuer_concentration_bps
        ),
        tail_loss_limit_ok=(
            tail_loss is not None
            and tail_loss <= limits.max_empirical_tail_loss_atoms
        ),
        fee_turnover_limit_ok=(
            plan.annual_fee_bps <= limits.max_annual_fee_bps
            and plan.turnover_bps <= limits.max_turnover_bps
        ),
    )

    if not evidence.policy_root_ok:
        code = WealthRejectCode.POLICY_ROOT_MISMATCH
    elif not evidence.household_consent_fresh:
        code = WealthRejectCode.CONSENT_STALE
    elif not evidence.proposal_evidence_authenticated:
        code = WealthRejectCode.PROPOSAL_EVIDENCE_UNAUTHENTICATED
    elif not evidence.custody_authorized:
        code = WealthRejectCode.CUSTODY_UNAUTHORIZED
    elif not obligations.no_leverage_or_short:
        code = WealthRejectCode.LEVERAGE_OR_SHORT_EXPOSURE
    elif not obligations.concentration_limit_ok:
        code = WealthRejectCode.CONCENTRATION_LIMIT_EXCEEDED
    elif not enough_scenarios:
        code = WealthRejectCode.TAIL_SCENARIO_SET_INSUFFICIENT
    elif not obligations.tail_loss_limit_ok:
        code = WealthRejectCode.EMPIRICAL_TAIL_LOSS_EXCEEDED
    elif not obligations.fee_turnover_limit_ok:
        code = WealthRejectCode.FEE_OR_TURNOVER_LIMIT_EXCEEDED
    else:
        code = WealthRejectCode.ACCEPTED
    return WealthPlanDecision(
        accepted=code is WealthRejectCode.ACCEPTED,
        code=code,
        obligations=obligations,
        empirical_tail_loss_atoms=tail_loss,
    )


@dataclass(frozen=True)
class WealthChoice:
    plan: WealthPlan | None
    decision: WealthPlanDecision | None
    safe_noop: bool


def choose_wealth_plan(
    plans: Iterable[WealthPlan],
    *,
    evidence: ExternalWealthEvidence,
    limits: WealthPolicyLimits,
    noop_score_atoms: int = 0,
) -> WealthChoice:
    """Choose the highest declared score only among admitted plans.

    The score is an external model input, not a verified return forecast.  A
    plan must beat the no-op score; otherwise the selector returns a no-op.
    """

    if type(noop_score_atoms) is not int:
        raise TypeError("noop_score_atoms must be an exact int")
    admitted: list[tuple[int, str, WealthPlan, WealthPlanDecision]] = []
    seen: set[str] = set()
    for index, plan in enumerate(plans):
        if index >= MAX_PLANS:
            raise ValueError(f"plan count exceeds {MAX_PLANS}")
        if type(plan) is not WealthPlan:
            raise TypeError("every plan must be an exact WealthPlan")
        if plan.plan_id in seen:
            raise ValueError(f"duplicate plan_id: {plan.plan_id}")
        seen.add(plan.plan_id)
        decision = evaluate_wealth_plan(plan, evidence=evidence, limits=limits)
        if decision.accepted and plan.declared_score_atoms > noop_score_atoms:
            admitted.append((plan.declared_score_atoms, plan.plan_id, plan, decision))
    if not admitted:
        return WealthChoice(plan=None, decision=None, safe_noop=True)
    admitted.sort(key=lambda row: (-row[0], row[1]))
    _, _, plan, decision = admitted[0]
    return WealthChoice(plan=plan, decision=decision, safe_noop=False)
