"""Exact finite model for a utilitarian-populist data-center social contract.

The model is deliberately narrow and fail-closed. It separates:

* senior project costs that must be reserved before any benefit is advertised;
* household-specific project losses and direct benefits;
* a universal household cash floor plus targeted no-harm top-ups;
* a separately funded universal compute entitlement; and
* a Tau-style Boolean constitutional gate over authenticated host facts.

All accounting uses non-negative integer atoms. This module does not estimate
real losses, authenticate evidence, establish causation, price compute, resolve
personhood, or move value. Those are external obligations.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Callable, Iterable, Sequence

MAX_U64 = (1 << 64) - 1
BASIS_POINTS = 10_000


def _u64(name: str, value: object) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an exact int")
    if not 0 <= value <= MAX_U64:
        raise ValueError(f"{name} must lie in [0, {MAX_U64}]")
    return value


@dataclass(frozen=True)
class HouseholdImpact:
    """Authenticated one-epoch household impact, expressed in common atoms."""

    household_id: str
    baseline_resources_atoms: int
    project_loss_atoms: int
    direct_project_benefit_atoms: int

    def __post_init__(self) -> None:
        if type(self.household_id) is not str or not self.household_id:
            raise TypeError("household_id must be a nonempty string")
        _u64("baseline_resources_atoms", self.baseline_resources_atoms)
        _u64("project_loss_atoms", self.project_loss_atoms)
        _u64("direct_project_benefit_atoms", self.direct_project_benefit_atoms)

    @property
    def uncompensated_deficit_atoms(self) -> int:
        """Minimum cash-equivalent transfer needed merely to avoid modeled harm."""

        return max(self.project_loss_atoms - self.direct_project_benefit_atoms, 0)

    def minimal_transfer_atoms(self, universal_floor_atoms: int) -> int:
        """Pointwise least transfer satisfying the floor and modeled no-harm."""

        _u64("universal_floor_atoms", universal_floor_atoms)
        return max(universal_floor_atoms, self.uncompensated_deficit_atoms)

    def post_project_resources_atoms(self, transfer_atoms: int) -> int:
        """Resources after modeled direct benefits, transfer, and project loss."""

        _u64("transfer_atoms", transfer_atoms)
        gross = (
            self.baseline_resources_atoms
            + self.direct_project_benefit_atoms
            + transfer_atoms
        )
        return max(gross - self.project_loss_atoms, 0)

    def no_worse_off(self, transfer_atoms: int) -> bool:
        _u64("transfer_atoms", transfer_atoms)
        return (
            self.direct_project_benefit_atoms + transfer_atoms
            >= self.project_loss_atoms
        )


@dataclass(frozen=True)
class SeniorProjectCosts:
    """Authenticated claims senior to household cash and compute benefits."""

    incremental_grid_atoms: int
    reliability_and_curtailment_atoms: int
    water_emissions_land_atoms: int
    decommissioning_and_remediation_atoms: int
    administration_and_security_atoms: int = 0

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            _u64(name, getattr(self, name))

    @property
    def total_atoms(self) -> int:
        return sum(getattr(self, name) for name in self.__dataclass_fields__)


@dataclass(frozen=True)
class ProjectRentBudget:
    """One epoch of project rent and separate cash/compute benefit budgets."""

    gross_public_rent_atoms: int
    senior_costs: SeniorProjectCosts
    compute_entitlement_atoms: int

    def __post_init__(self) -> None:
        _u64("gross_public_rent_atoms", self.gross_public_rent_atoms)
        _u64("compute_entitlement_atoms", self.compute_entitlement_atoms)
        if type(self.senior_costs) is not SeniorProjectCosts:
            raise TypeError("senior_costs must be an exact SeniorProjectCosts")

    @property
    def senior_claims_funded(self) -> bool:
        return self.senior_costs.total_atoms <= self.gross_public_rent_atoms

    @property
    def distributable_cash_atoms(self) -> int:
        if not self.senior_claims_funded:
            return 0
        return self.gross_public_rent_atoms - self.senior_costs.total_atoms


def _ordered_impacts(
    impacts: Iterable[HouseholdImpact],
) -> tuple[HouseholdImpact, ...]:
    rows = tuple(impacts)
    if not rows:
        raise ValueError("at least one household is required")
    if any(type(row) is not HouseholdImpact for row in rows):
        raise TypeError("every impact must be an exact HouseholdImpact")
    ids = [row.household_id for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("household_id values must be unique")
    return tuple(sorted(rows, key=lambda row: row.household_id))


def minimal_hybrid_transfers(
    impacts: Iterable[HouseholdImpact], *, universal_floor_atoms: int
) -> tuple[int, ...]:
    """Universal base plus the least household-specific no-harm top-ups."""

    _u64("universal_floor_atoms", universal_floor_atoms)
    ordered = _ordered_impacts(impacts)
    return tuple(
        row.minimal_transfer_atoms(universal_floor_atoms) for row in ordered
    )


def minimal_hybrid_requirement_atoms(
    impacts: Iterable[HouseholdImpact], *, universal_floor_atoms: int
) -> int:
    return sum(
        minimal_hybrid_transfers(
            impacts, universal_floor_atoms=universal_floor_atoms
        )
    )


def universal_base_plus_topups_identity_atoms(
    impacts: Iterable[HouseholdImpact], *, universal_floor_atoms: int
) -> tuple[int, int]:
    """Return both sides of H = n*m + sum(max(d_i-m, 0))."""

    _u64("universal_floor_atoms", universal_floor_atoms)
    ordered = _ordered_impacts(impacts)
    left = minimal_hybrid_requirement_atoms(
        ordered, universal_floor_atoms=universal_floor_atoms
    )
    right = len(ordered) * universal_floor_atoms + sum(
        max(row.uncompensated_deficit_atoms - universal_floor_atoms, 0)
        for row in ordered
    )
    return left, right


def minimal_uniform_requirement_atoms(
    impacts: Iterable[HouseholdImpact], *, universal_floor_atoms: int
) -> int:
    """Least budget for one identical payment that satisfies every household."""

    _u64("universal_floor_atoms", universal_floor_atoms)
    ordered = _ordered_impacts(impacts)
    per_household = max(
        universal_floor_atoms,
        max(row.uncompensated_deficit_atoms for row in ordered),
    )
    return len(ordered) * per_household


def transfers_satisfy_floor_and_no_harm(
    impacts: Iterable[HouseholdImpact],
    transfers_atoms: Sequence[int],
    *,
    universal_floor_atoms: int,
) -> bool:
    _u64("universal_floor_atoms", universal_floor_atoms)
    ordered = _ordered_impacts(impacts)
    if len(transfers_atoms) != len(ordered):
        return False
    for transfer in transfers_atoms:
        _u64("transfer_atoms", transfer)
    return all(
        transfer >= universal_floor_atoms and row.no_worse_off(transfer)
        for row, transfer in zip(ordered, transfers_atoms, strict=True)
    )


def project_cash_contract_feasible(
    impacts: Iterable[HouseholdImpact],
    *,
    distributable_cash_atoms: int,
    universal_floor_atoms: int,
) -> bool:
    _u64("distributable_cash_atoms", distributable_cash_atoms)
    return distributable_cash_atoms >= minimal_hybrid_requirement_atoms(
        impacts, universal_floor_atoms=universal_floor_atoms
    )


def joint_cash_compute_contract_feasible(
    impacts: Iterable[HouseholdImpact],
    *,
    distributable_cash_atoms: int,
    universal_cash_floor_atoms: int,
    available_compute_atoms: int,
    universal_compute_floor_atoms: int,
) -> bool:
    """Safe separable threshold when cash and compute are not interchangeable."""

    _u64("available_compute_atoms", available_compute_atoms)
    _u64("universal_compute_floor_atoms", universal_compute_floor_atoms)
    ordered = _ordered_impacts(impacts)
    cash_ok = project_cash_contract_feasible(
        ordered,
        distributable_cash_atoms=distributable_cash_atoms,
        universal_floor_atoms=universal_cash_floor_atoms,
    )
    compute_ok = available_compute_atoms >= (
        len(ordered) * universal_compute_floor_atoms
    )
    return cash_ok and compute_ok


def harmonic_utility(resources_atoms: int) -> Fraction:
    """Exact monotone, concave utility used only for bounded welfare checks."""

    _u64("resources_atoms", resources_atoms)
    return sum(
        (Fraction(1, k) for k in range(1, resources_atoms + 1)),
        start=Fraction(0),
    )


def separable_welfare(
    impacts: Iterable[HouseholdImpact],
    transfers_atoms: Sequence[int] | None,
    *,
    utility: Callable[[int], Fraction] = harmonic_utility,
) -> Fraction:
    ordered = _ordered_impacts(impacts)
    if transfers_atoms is None:
        return sum(
            (utility(row.baseline_resources_atoms) for row in ordered),
            start=Fraction(0),
        )
    if len(transfers_atoms) != len(ordered):
        raise ValueError("transfer count must equal household count")
    return sum(
        (
            utility(row.post_project_resources_atoms(transfer))
            for row, transfer in zip(ordered, transfers_atoms, strict=True)
        ),
        start=Fraction(0),
    )


DATA_CENTER_OBLIGATION_NAMES = (
    "policy_root_ok",
    "project_identity_authenticated",
    "local_consent_authenticated",
    "incremental_energy_costs_reserved",
    "reliability_curtailment_plan_ok",
    "water_emissions_land_limits_ok",
    "decommissioning_bond_funded",
    "no_harm_compensation_funded",
    "universal_dividend_compute_floor_funded",
    "public_audit_receipt_current",
)


@dataclass(frozen=True)
class DataCenterObligations:
    policy_root_ok: bool
    project_identity_authenticated: bool
    local_consent_authenticated: bool
    incremental_energy_costs_reserved: bool
    reliability_curtailment_plan_ok: bool
    water_emissions_land_limits_ok: bool
    decommissioning_bond_funded: bool
    no_harm_compensation_funded: bool
    universal_dividend_compute_floor_funded: bool
    public_audit_receipt_current: bool

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be an exact bool")

    def as_tuple(self) -> tuple[bool, ...]:
        return tuple(getattr(self, name) for name in self.__dataclass_fields__)


def data_center_admits(obligations: DataCenterObligations) -> bool:
    if type(obligations) is not DataCenterObligations:
        raise TypeError("obligations must be exact DataCenterObligations")
    return all(obligations.as_tuple())


class ProjectPhase(str, Enum):
    PROPOSED = "PROPOSED"
    REJECTED = "REJECTED"
    ADMITTED = "ADMITTED"
    OPERATING = "OPERATING"
    CURTAILED = "CURTAILED"
    SETTLEMENT_DUE = "SETTLEMENT_DUE"
    SETTLED = "SETTLED"
    DEFAULTED = "DEFAULTED"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class ProjectState:
    phase: ProjectPhase
    obligations_mask: int
    distributable_reserve_atoms: int
    required_transfer_atoms: int
    payout_atoms: int = 0
    reserve_post_atoms: int | None = None

    def __post_init__(self) -> None:
        if type(self.phase) is not ProjectPhase:
            raise TypeError("phase must be an exact ProjectPhase")
        _u64("obligations_mask", self.obligations_mask)
        if self.obligations_mask >= (1 << len(DATA_CENTER_OBLIGATION_NAMES)):
            raise ValueError("obligations_mask exceeds the ten-fact domain")
        _u64("distributable_reserve_atoms", self.distributable_reserve_atoms)
        _u64("required_transfer_atoms", self.required_transfer_atoms)
        _u64("payout_atoms", self.payout_atoms)
        if self.reserve_post_atoms is not None:
            _u64("reserve_post_atoms", self.reserve_post_atoms)

    @property
    def all_obligations_true(self) -> bool:
        return self.obligations_mask == (1 << len(DATA_CENTER_OBLIGATION_NAMES)) - 1


FULL_OBLIGATION_MASK = (1 << len(DATA_CENTER_OBLIGATION_NAMES)) - 1


def admit_project(state: ProjectState) -> ProjectState:
    if state.phase is not ProjectPhase.PROPOSED:
        raise ValueError("admission is defined only from PROPOSED")
    admitted = (
        state.all_obligations_true
        and state.distributable_reserve_atoms >= state.required_transfer_atoms
    )
    return ProjectState(
        phase=ProjectPhase.ADMITTED if admitted else ProjectPhase.REJECTED,
        obligations_mask=state.obligations_mask,
        distributable_reserve_atoms=state.distributable_reserve_atoms,
        required_transfer_atoms=state.required_transfer_atoms,
    )


def start_operating(state: ProjectState) -> ProjectState:
    if state.phase is not ProjectPhase.ADMITTED:
        raise ValueError("operation can start only from ADMITTED")
    return ProjectState(
        phase=ProjectPhase.OPERATING,
        obligations_mask=state.obligations_mask,
        distributable_reserve_atoms=state.distributable_reserve_atoms,
        required_transfer_atoms=state.required_transfer_atoms,
    )


def fail_obligation(state: ProjectState, obligation_index: int) -> ProjectState:
    if state.phase not in {ProjectPhase.ADMITTED, ProjectPhase.OPERATING}:
        raise ValueError("obligation failure applies only to admitted/operating states")
    if not 0 <= obligation_index < len(DATA_CENTER_OBLIGATION_NAMES):
        raise ValueError("invalid obligation_index")
    failed_mask = state.obligations_mask & ~(1 << obligation_index)
    return ProjectState(
        phase=ProjectPhase.CURTAILED,
        obligations_mask=failed_mask,
        distributable_reserve_atoms=state.distributable_reserve_atoms,
        required_transfer_atoms=state.required_transfer_atoms,
    )


def close_epoch(state: ProjectState) -> ProjectState:
    if state.phase is not ProjectPhase.OPERATING:
        raise ValueError("epoch can close only from OPERATING")
    if not state.all_obligations_true:
        return ProjectState(
            phase=ProjectPhase.CURTAILED,
            obligations_mask=state.obligations_mask,
            distributable_reserve_atoms=state.distributable_reserve_atoms,
            required_transfer_atoms=state.required_transfer_atoms,
        )
    return ProjectState(
        phase=ProjectPhase.SETTLEMENT_DUE,
        obligations_mask=state.obligations_mask,
        distributable_reserve_atoms=state.distributable_reserve_atoms,
        required_transfer_atoms=state.required_transfer_atoms,
    )


def settle_epoch(state: ProjectState) -> ProjectState:
    if state.phase is not ProjectPhase.SETTLEMENT_DUE:
        raise ValueError("settlement applies only to SETTLEMENT_DUE")
    if (
        not state.all_obligations_true
        or state.required_transfer_atoms > state.distributable_reserve_atoms
    ):
        return ProjectState(
            phase=ProjectPhase.DEFAULTED,
            obligations_mask=state.obligations_mask,
            distributable_reserve_atoms=state.distributable_reserve_atoms,
            required_transfer_atoms=state.required_transfer_atoms,
            payout_atoms=0,
            reserve_post_atoms=state.distributable_reserve_atoms,
        )
    return ProjectState(
        phase=ProjectPhase.SETTLED,
        obligations_mask=state.obligations_mask,
        distributable_reserve_atoms=state.distributable_reserve_atoms,
        required_transfer_atoms=state.required_transfer_atoms,
        payout_atoms=state.required_transfer_atoms,
        reserve_post_atoms=(
            state.distributable_reserve_atoms - state.required_transfer_atoms
        ),
    )


@dataclass(frozen=True)
class PriceFactors:
    """One-period multiplicative price decomposition.

    `effective_productivity_factor` compresses intelligence improvement, the
    automation share, diffusion, and pass-through. Raw intelligence doubling
    does not determine this factor.
    """

    effective_productivity_factor: Fraction
    scarce_resource_cost_factor: Fraction
    markup_and_rent_factor: Fraction

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            value = getattr(self, name)
            if type(value) is not Fraction or value <= 0:
                raise ValueError(f"{name} must be a positive Fraction")

    @property
    def price_ratio(self) -> Fraction:
        return (
            self.scarce_resource_cost_factor
            * self.markup_and_rent_factor
            / self.effective_productivity_factor
        )

    @property
    def is_deflationary(self) -> bool:
        return self.price_ratio < 1


def cumulative_price_ratio(periods: Iterable[PriceFactors]) -> Fraction:
    ratio = Fraction(1)
    for period in periods:
        if type(period) is not PriceFactors:
            raise TypeError("every period must be an exact PriceFactors")
        ratio *= period.price_ratio
    return ratio


def tau_truth_rows() -> list[tuple[bool, ...]]:
    """Canonical all-true row, ten single-fault rows, then the remaining rows."""

    n = len(DATA_CENTER_OBLIGATION_NAMES)
    all_true = (True,) * n
    single_faults = [
        tuple(index != false_index for index in range(n))
        for false_index in range(n)
    ]
    prefix = [all_true, *single_faults]
    prefix_set = set(prefix)
    tail = [
        row
        for row in itertools.product((False, True), repeat=n)
        if row not in prefix_set
    ]
    return [*prefix, *tail]
