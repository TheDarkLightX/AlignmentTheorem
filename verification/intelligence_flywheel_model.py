"""Exact finite models for the intelligence-to-abundance bridge.

The Alignment Theorem uses the strict policy-relative margin ``B < M * K``.
This module does not treat an intelligence trend as that margin.  It exposes
the missing bridge explicitly:

``capability -> automated unit cost -> passed-through basket price -> M``

where ``K`` is a separately funded/protected household benefit and ``B`` is
the benefit of deviation.  Every numerical operation uses integers or
``fractions.Fraction``.  The model authenticates none of its inputs and makes
no forecast about AGI, prices, investment returns, or Tau Net deployment.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

MAX_EPOCH = 4_096
MAX_EXPONENT = 64


def _fraction(name: str, value: object, *, positive: bool = False) -> Fraction:
    if type(value) is not Fraction:
        raise TypeError(f"{name} must be an exact Fraction")
    if positive and value <= 0:
        raise ValueError(f"{name} must be positive")
    if not positive and value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def _unit_interval(name: str, value: object) -> Fraction:
    result = _fraction(name, value)
    if result > 1:
        raise ValueError(f"{name} must lie in [0, 1]")
    return result


def _epoch(epoch: object) -> int:
    if type(epoch) is not int:
        raise TypeError("epoch must be an exact int")
    if not 0 <= epoch <= MAX_EPOCH:
        raise ValueError(f"epoch must lie in [0, {MAX_EPOCH}]")
    return epoch


@dataclass(frozen=True)
class PriceBridge:
    """A normalized essential-basket bridge.

    ``automatable_share`` is the share of the baseline basket whose unit cost
    responds to capability.  ``pass_through`` is the fraction of that unit-cost
    reduction reaching the household.  Both missing automation and missing
    pass-through create a positive price floor.
    """

    automatable_share: Fraction
    pass_through: Fraction
    cost_elasticity: int = 1

    def __post_init__(self) -> None:
        _unit_interval("automatable_share", self.automatable_share)
        _unit_interval("pass_through", self.pass_through)
        if type(self.cost_elasticity) is not int:
            raise TypeError("cost_elasticity must be an exact int")
        if not 1 <= self.cost_elasticity <= MAX_EXPONENT:
            raise ValueError(
                f"cost_elasticity must lie in [1, {MAX_EXPONENT}]"
            )

    @property
    def normalized_price_floor(self) -> Fraction:
        """Limit floor implied by incomplete automation/transmission."""

        return 1 - self.automatable_share * self.pass_through


def direct_capability_doubling(epoch: int, *, initial: Fraction = Fraction(1)) -> Fraction:
    """The user's Moore-like hypothesis, represented as an assumption."""

    _epoch(epoch)
    _fraction("initial", initial, positive=True)
    return initial * (2**epoch)


def compute_power_capability(
    compute_doublings: int,
    *,
    elasticity: Fraction,
    initial: Fraction = Fraction(1),
) -> Fraction:
    """Exact sampled form of ``I/I0 = (C/C0)^alpha``.

    The function accepts only epochs where ``elasticity * doublings`` is an
    integer.  For example, alpha=1/2 is sampled at even compute doublings.  It
    therefore never silently rounds a fractional power into evidence.
    """

    _epoch(compute_doublings)
    _fraction("elasticity", elasticity)
    _fraction("initial", initial, positive=True)
    exponent = elasticity * compute_doublings
    if exponent.denominator != 1:
        raise ValueError("sample does not have an exact integral binary exponent")
    if exponent.numerator > MAX_EXPONENT:
        raise ValueError("binary exponent exceeds the finite model bound")
    return initial * (2**exponent.numerator)


def logistic_capability(
    epoch: int,
    *,
    initial: Fraction,
    carrying_capacity: Fraction,
    decay: Fraction,
) -> Fraction:
    """Exact bounded alternative to indefinite capability doubling."""

    _epoch(epoch)
    _fraction("initial", initial, positive=True)
    _fraction("carrying_capacity", carrying_capacity, positive=True)
    _unit_interval("decay", decay)
    if initial > carrying_capacity:
        raise ValueError("initial must not exceed carrying_capacity")
    odds = (carrying_capacity - initial) / initial
    return carrying_capacity / (1 + odds * decay**epoch)


def dac_reinvestment_capability(
    epoch: int,
    *,
    initial: Fraction,
    reinvestment_share: Fraction,
    verified_net_return: Fraction,
) -> Fraction:
    """A deliberately conditional DAC reinvestment recurrence.

    ``I[t+1] = I[t] * (1 + s*r)``.  The return is an input, not a prediction;
    negative returns are outside this simple map and require another model.
    """

    _epoch(epoch)
    _fraction("initial", initial, positive=True)
    _unit_interval("reinvestment_share", reinvestment_share)
    _fraction("verified_net_return", verified_net_return)
    return initial * (1 + reinvestment_share * verified_net_return) ** epoch


def normalized_basket_price(capability: Fraction, bridge: PriceBridge) -> Fraction:
    """Price of a baseline-one basket under the declared causal bridge."""

    _fraction("capability", capability, positive=True)
    if type(bridge) is not PriceBridge:
        raise TypeError("bridge must be an exact PriceBridge")
    automated_unit_cost = 1 / capability**bridge.cost_elasticity
    household_automated_price = (
        (1 - bridge.pass_through) + bridge.pass_through * automated_unit_cost
    )
    return (
        (1 - bridge.automatable_share)
        + bridge.automatable_share * household_automated_price
    )


def externality_adjusted_price(
    core_price: Fraction, *, unpriced_surcharge: Fraction
) -> Fraction:
    """Add a grid/resource/rebound surcharge rather than hiding it."""

    _fraction("core_price", core_price, positive=True)
    _fraction("unpriced_surcharge", unpriced_surcharge)
    return core_price + unpriced_surcharge


def purchasing_power_multiplier(price: Fraction) -> Fraction:
    """Baseline-one real purchasing power, ``M = 1/P``."""

    _fraction("price", price, positive=True)
    return 1 / price


def aligned(*, multiplier: Fraction, protected_benefit: Fraction, deviation: Fraction) -> bool:
    """The strict V1.1 semantic boundary: ``B < M*K``."""

    _fraction("multiplier", multiplier)
    _fraction("protected_benefit", protected_benefit)
    _fraction("deviation", deviation)
    return deviation < multiplier * protected_benefit


@dataclass(frozen=True)
class FlywheelPoint:
    epoch: int
    capability: Fraction
    core_price: Fraction
    adjusted_price: Fraction
    multiplier: Fraction
    protected_benefit: Fraction
    deviation: Fraction
    strict_margin: Fraction
    aligned: bool


def simulate(
    capabilities: Sequence[Fraction],
    *,
    bridge: PriceBridge,
    protected_benefits: Sequence[Fraction],
    deviations: Sequence[Fraction],
    surcharges: Sequence[Fraction] | None = None,
) -> tuple[FlywheelPoint, ...]:
    """Evaluate a finite, fully supplied trajectory with no interpolation."""

    count = len(capabilities)
    if count == 0 or len(protected_benefits) != count or len(deviations) != count:
        raise ValueError("capability, benefit, and deviation sequences must align")
    if surcharges is None:
        surcharges = (Fraction(0),) * count
    if len(surcharges) != count:
        raise ValueError("surcharge sequence must align")
    points = []
    for epoch, (capability, benefit, deviation, surcharge) in enumerate(
        zip(capabilities, protected_benefits, deviations, surcharges, strict=True)
    ):
        _epoch(epoch)
        _fraction("protected_benefit", benefit)
        _fraction("deviation", deviation)
        core = normalized_basket_price(capability, bridge)
        adjusted = externality_adjusted_price(core, unpriced_surcharge=surcharge)
        multiplier = purchasing_power_multiplier(adjusted)
        margin = multiplier * benefit - deviation
        points.append(
            FlywheelPoint(
                epoch=epoch,
                capability=capability,
                core_price=core,
                adjusted_price=adjusted,
                multiplier=multiplier,
                protected_benefit=benefit,
                deviation=deviation,
                strict_margin=margin,
                aligned=margin > 0,
            )
        )
    return tuple(points)


def first_alignment_epoch(points: Iterable[FlywheelPoint]) -> int | None:
    for point in points:
        if point.aligned:
            return point.epoch
    return None


@dataclass(frozen=True)
class DacGateFacts:
    """Claims the Tau policy consumes; truth must come from outside Tau."""

    policy_root_ok: bool
    capability_receipt_authenticated: bool
    productivity_bridge_verified: bool
    essential_basket_gain_verified: bool
    benefit_floor_funded: bool
    concentration_cap_ok: bool
    grid_externality_budget_ok: bool
    debt_guardrail_ok: bool
    strict_alignment_margin: bool

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be an exact bool")


def dac_treasury_admits(facts: DacGateFacts) -> bool:
    if type(facts) is not DacGateFacts:
        raise TypeError("facts must be an exact DacGateFacts")
    return all(getattr(facts, name) for name in facts.__dataclass_fields__)


def bounded_reward_blocks_alignment(
    *, multiplier_cap: Fraction, benefit_cap: Fraction, deviation_floor: Fraction
) -> bool:
    """Return the checked sufficient condition for non-alignment."""

    _fraction("multiplier_cap", multiplier_cap)
    _fraction("benefit_cap", benefit_cap)
    _fraction("deviation_floor", deviation_floor)
    return multiplier_cap * benefit_cap <= deviation_floor
