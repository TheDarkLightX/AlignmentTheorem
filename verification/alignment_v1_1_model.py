"""Exact finite model for the V1.1 hyperdeflationary alignment theorem.

Version 1's intended mechanism is preserved:

* an ethical action receives a scarcity-amplified reward entitlement;
* a non-ethical action may forfeit a scarcity-amplified entitlement; and
* private deviation gain, compliance cost, and optimizer error oppose that
  mechanism advantage.

The asymptotic theorem belongs in Lean.  This module checks one finite epoch
using unsigned 64-bit inputs and rejects arithmetic that would overflow that
runtime domain.  It does not authenticate EETF evidence, predict asset prices,
or establish that AGI causes hyperdeflation.
"""

from __future__ import annotations

from dataclasses import dataclass

MAX_U64 = (1 << 64) - 1


def _require_u64(name: str, value: object) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an exact int")
    if not 0 <= value <= MAX_U64:
        raise ValueError(f"{name} must lie in [0, {MAX_U64}]")
    return value


def _checked_add(name: str, *values: int) -> int:
    total = sum(values)
    if total > MAX_U64:
        raise ValueError(f"{name} exceeds u64 range")
    return total


def _checked_mul(name: str, left: int, right: int) -> int:
    product = left * right
    if product > MAX_U64:
        raise ValueError(f"{name} exceeds u64 range")
    return product


@dataclass(frozen=True)
class HyperdeflationEnvelope:
    """Finite assumptions for one V1.1 decision epoch.

    Every value uses the same committed real-value accounting scale.
    ``scarcity_multiplier`` is a finite purchasing-power index, rather than a
    claim that literal infinity is representable by the runtime.
    """

    scarcity_multiplier: int
    ethical_reward_coefficient: int
    nonethical_forfeiture_coefficient: int
    max_private_deviation_gain: int
    max_extra_compliance_cost: int
    optimizer_error: int = 0

    def __post_init__(self) -> None:
        for name in (
            "scarcity_multiplier",
            "ethical_reward_coefficient",
            "nonethical_forfeiture_coefficient",
            "max_private_deviation_gain",
            "max_extra_compliance_cost",
            "optimizer_error",
        ):
            _require_u64(name, getattr(self, name))
        # Force all derived arithmetic through the bounded runtime domain.
        _ = (
            self.mechanism_coefficient,
            self.mechanism_advantage,
            self.required_advantage,
        )

    @property
    def mechanism_coefficient(self) -> int:
        """Scarcity exposure favoring the ethical action."""

        return _checked_add(
            "mechanism_coefficient",
            self.ethical_reward_coefficient,
            self.nonethical_forfeiture_coefficient,
        )

    @property
    def mechanism_advantage(self) -> int:
        """Scarcity-amplified ethical advantage at this epoch."""

        return _checked_mul(
            "mechanism_advantage",
            self.scarcity_multiplier,
            self.mechanism_coefficient,
        )

    @property
    def required_advantage(self) -> int:
        """Complete deviation, compliance-cost, and optimizer bound."""

        return _checked_add(
            "required_advantage",
            self.max_private_deviation_gain,
            self.max_extra_compliance_cost,
            self.optimizer_error,
        )

    @property
    def has_strict_hyperdeflation_margin(self) -> bool:
        """Whether scarcity strictly dominates the complete opposing bound."""

        return self.mechanism_advantage > self.required_advantage

    def minimum_scarcity_multiplier(self) -> int:
        """Smallest integer multiplier that creates a strict margin."""

        coefficient = self.mechanism_coefficient
        if coefficient == 0:
            raise ValueError("positive ethical scarcity exposure is required")
        threshold = self.required_advantage // coefficient + 1
        return _require_u64("minimum_scarcity_multiplier", threshold)


@dataclass(frozen=True)
class EthicalAssessment:
    """Authenticated action classification consumed by the finite gate."""

    eetf_authenticated: bool
    action_ethical: bool

    def __post_init__(self) -> None:
        if type(self.eetf_authenticated) is not bool:
            raise TypeError("eetf_authenticated must be an exact bool")
        if type(self.action_ethical) is not bool:
            raise TypeError("action_ethical must be an exact bool")


@dataclass(frozen=True)
class EligibilityDecision:
    eligible: bool
    strict_hyperdeflation_margin: bool
    reward_funded: bool


def evaluate_eligibility(
    assessment: EthicalAssessment,
    envelope: HyperdeflationEnvelope,
    *,
    requested_reward_atoms: int,
    reserve_atoms: int,
) -> EligibilityDecision:
    """Evaluate the Tau-equivalent finite V1.1 conjunction.

    The host derives ``strict_hyperdeflation_margin`` from the exact envelope
    and derives ``reward_funded`` from reserve arithmetic.  Caller-provided
    Boolean substitutes are never accepted by this reference boundary.
    """

    if type(assessment) is not EthicalAssessment:
        raise TypeError("assessment must be an exact EthicalAssessment")
    if type(envelope) is not HyperdeflationEnvelope:
        raise TypeError("envelope must be an exact HyperdeflationEnvelope")
    reward = _require_u64("requested_reward_atoms", requested_reward_atoms)
    reserve = _require_u64("reserve_atoms", reserve_atoms)
    margin = envelope.has_strict_hyperdeflation_margin
    funded = reward <= reserve
    return EligibilityDecision(
        eligible=(
            assessment.eetf_authenticated
            and assessment.action_ethical
            and margin
            and funded
        ),
        strict_hyperdeflation_margin=margin,
        reward_funded=funded,
    )
