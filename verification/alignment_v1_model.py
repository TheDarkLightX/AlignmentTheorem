"""Exact bounded reference model for Alignment Theorem Version 1.

V1 combines an EETF reward tier with scarcity upside that is accessible only
to policy-eligible behavior. Exclusion is an opportunity cost: this model does
not debit, burn, fine, or tax the excluded branch.

The original simulation placed foregone upside as a negative term on the
excluded branch. Adding that amount to both alternatives yields the equivalent
normalization used here:

    eligible = scarcity * (direct_reward + exclusive_scarcity_upside)
    excluded = deviation_gain

All quantities use finite integers. Market value, evidence authenticity,
reward funding, and enforceability of exclusion remain external premises.
"""

from __future__ import annotations

from dataclasses import dataclass


MAX_ATOMS = (1 << 63) - 1
EETF_SCALE = 1_000
MAX_EETF_MILLI = 3 * EETF_SCALE
PAPER_REWARD_COMMON_SCALE = 100_000


def _integer(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _bounded_nat(name: str, value: object) -> int:
    integer = _integer(name, value)
    if not 0 <= integer <= MAX_ATOMS:
        raise ValueError(f"{name} must be in [0, MAX_ATOMS]")
    return integer


def _positive_atom(name: str, value: object) -> int:
    integer = _bounded_nat(name, value)
    if integer == 0:
        raise ValueError(f"{name} must be positive")
    return integer


def _checked_product(name: str, *values: int) -> int:
    result = 1
    for value in values:
        if value != 0 and result > MAX_ATOMS // value:
            raise ValueError(f"{name} exceeds the declared finite domain")
        result *= value
    return result


def valid_eetf(eetf_milli: object) -> int:
    value = _bounded_nat("eetf_milli", eetf_milli)
    if value > MAX_EETF_MILLI:
        raise ValueError("eetf_milli must represent a value in [0, 3]")
    return value


def is_ethical(eetf_milli: object) -> bool:
    return valid_eetf(eetf_milli) >= EETF_SCALE


def tier_multiplier(eetf_milli: object) -> int:
    value = valid_eetf(eetf_milli)
    if value >= 2 * EETF_SCALE:
        return 5
    if value >= 3 * EETF_SCALE // 2:
        return 3
    if value >= EETF_SCALE:
        return 1
    return 0


def direct_reward_coefficient_scaled(balance: object, ethical_eetf_milli: object) -> int:
    balance_atoms = _positive_atom("balance", balance)
    eetf = valid_eetf(ethical_eetf_milli)
    if not is_ethical(eetf):
        raise ValueError("direct reward requires an eligible EETF tier")
    return _checked_product(
        "direct reward coefficient",
        balance_atoms,
        tier_multiplier(eetf),
        PAPER_REWARD_COMMON_SCALE,
    )


def exclusive_upside_coefficient_scaled(
    exposure: object, network_eetf_milli: object, excluded_eetf_milli: object
) -> int:
    exposure_atoms = _positive_atom("exposure", exposure)
    network_eetf = valid_eetf(network_eetf_milli)
    if network_eetf == 0:
        raise ValueError("network_eetf_milli must be positive")
    excluded_eetf = valid_eetf(excluded_eetf_milli)
    if is_ethical(excluded_eetf):
        raise ValueError("exclusive upside comparison requires an excluded EETF")
    deficit = EETF_SCALE - excluded_eetf
    return _checked_product(
        "exclusive scarcity upside coefficient",
        exposure_atoms,
        deficit,
        network_eetf,
    )


@dataclass(frozen=True, slots=True)
class V1ExclusionPayoff:
    """One exact V1 eligible-versus-excluded decision epoch."""

    scarcity_multiplier: int
    direct_reward_coefficient: int
    exclusive_scarcity_upside_coefficient: int
    deviation_gain: int

    def __post_init__(self) -> None:
        scarcity = _positive_atom("scarcity_multiplier", self.scarcity_multiplier)
        reward = _bounded_nat(
            "direct_reward_coefficient", self.direct_reward_coefficient
        )
        upside = _bounded_nat(
            "exclusive_scarcity_upside_coefficient",
            self.exclusive_scarcity_upside_coefficient,
        )
        _bounded_nat("deviation_gain", self.deviation_gain)
        coefficient = reward + upside
        if coefficient == 0:
            raise ValueError("at least one eligible scarcity exposure must be positive")
        if coefficient > MAX_ATOMS:
            raise ValueError("eligibility coefficient exceeds the declared finite domain")
        _checked_product("eligible utility", scarcity, coefficient)

    @property
    def eligibility_coefficient(self) -> int:
        return (
            self.direct_reward_coefficient
            + self.exclusive_scarcity_upside_coefficient
        )

    @property
    def eligible_utility(self) -> int:
        return self.scarcity_multiplier * self.eligibility_coefficient

    @property
    def excluded_utility(self) -> int:
        return self.deviation_gain

    @property
    def historical_eligible_utility(self) -> int:
        return self.scarcity_multiplier * self.direct_reward_coefficient

    @property
    def historical_excluded_relative_utility(self) -> int:
        return self.deviation_gain - (
            self.scarcity_multiplier
            * self.exclusive_scarcity_upside_coefficient
        )

    @property
    def strict_margin_holds(self) -> bool:
        return self.excluded_utility < self.eligible_utility

    @property
    def historical_and_normalized_order_agree(self) -> bool:
        historical = (
            self.historical_excluded_relative_utility
            < self.historical_eligible_utility
        )
        normalized = self.excluded_utility < self.eligible_utility
        return historical == normalized

    @property
    def minimum_scarcity_multiplier(self) -> int:
        return self.deviation_gain // self.eligibility_coefficient + 1


def paper_v1_epoch(
    *,
    balance: object,
    exposure: object,
    scarcity_multiplier: object,
    network_eetf_milli: object,
    ethical_eetf_milli: object,
    excluded_eetf_milli: object,
    deviation_gain_scaled: object,
) -> V1ExclusionPayoff:
    """Construct the exact common-scale V1 comparison from paper terms."""

    return V1ExclusionPayoff(
        scarcity_multiplier=_positive_atom(
            "scarcity_multiplier", scarcity_multiplier
        ),
        direct_reward_coefficient=direct_reward_coefficient_scaled(
            balance, ethical_eetf_milli
        ),
        exclusive_scarcity_upside_coefficient=(
            exclusive_upside_coefficient_scaled(
                exposure, network_eetf_milli, excluded_eetf_milli
            )
        ),
        deviation_gain=_bounded_nat("deviation_gain_scaled", deviation_gain_scaled),
    )


def common_upside_cancels(common_upside: object, eligible: object, excluded: object) -> bool:
    """Check that upside shared by both alternatives cannot change ordering."""

    common = _bounded_nat("common_upside", common_upside)
    eligible_value = _bounded_nat("eligible", eligible)
    excluded_value = _bounded_nat("excluded", excluded)
    if common + max(eligible_value, excluded_value) > MAX_ATOMS:
        raise ValueError("common-upside comparison exceeds the finite domain")
    return ((common + excluded_value) < (common + eligible_value)) == (
        excluded_value < eligible_value
    )
