import Std.Tactic

/-!
# Alignment Theorem Version 1: EETF-gated scarcity upside

This file reconstructs the operative Version 1 mechanism from the original
academic paper and simulation. Tau aggregates a network EETF signal, an
account or action receives an EETF tier, VCC creates a scarcity multiplier,
and policy-eligible behavior retains access to direct rewards and
scarcity-amplified upside. A non-eligible branch is excluded from that upside.

The paper wrote the foregone upside as a negative "penalty" on the excluded
branch. It is an opportunity cost rather than a tax or balance debit. Adding
the foregone upside to both alternatives yields the equivalent normalized
comparison proved below:

  eligible = base + scarcity * (directReward + exclusiveUpside)
  excluded = base + deviationGain

V1 therefore has a genuine scarcity threshold when deviation gain is positive.
When deviation gain is zero and eligible scarcity exposure is positive, the
eligible branch wins at every positive scarcity multiplier.

The theorem remains conditional on authenticated EETF facts, enforceable
exclusion, funded rewards, an exact optimizer, and a complete deviation-gain
bound. It does not prove objective ethics, market-price appreciation, or those
external premises.
-/

namespace AlignmentTheoremV1

/-! ## Original EETF and tier structure -/

/-- The paper uses thousandths for the interval `[0, 3]` in the executable
finite model. -/
def eetfScale : Nat := 1000

/-- A finite EETF value is inside the paper's declared interval `[0, 3]`. -/
def ValidEETF (eetfMilli : Nat) : Prop := eetfMilli ≤ 3 * eetfScale

/-- The V1 eligibility boundary is EETF at least `1.0`. -/
def IsEthical (eetfMilli : Nat) : Prop := eetfScale ≤ eetfMilli

/-- V1's account/action reward tiers: zero below eligibility, followed by
`1`, `3`, and `5`. -/
def tierMultiplier (eetfMilli : Nat) : Nat :=
  if 2 * eetfScale ≤ eetfMilli then 5
  else if 3 * eetfScale / 2 ≤ eetfMilli then 3
  else if eetfScale ≤ eetfMilli then 1
  else 0

theorem tier_multiplier_of_excluded
    (eetfMilli : Nat) (hExcluded : ¬ IsEthical eetfMilli) :
    tierMultiplier eetfMilli = 0 := by
  simp only [IsEthical, eetfScale] at hExcluded
  have hTwo : ¬ 2000 ≤ eetfMilli := by omega
  have hOneHalf : ¬ 1500 ≤ eetfMilli := by omega
  have hOne : ¬ 1000 ≤ eetfMilli := by omega
  simp [tierMultiplier, eetfScale, hTwo, hOneHalf, hOne]

theorem baseline_is_ethical : IsEthical eetfScale := by
  simp [IsEthical]

theorem baseline_tier_is_one : tierMultiplier eetfScale = 1 := by
  decide

/-!
The next two coefficients put the paper's denominators onto one integer scale.
For an ethical candidate `ethicalEETF`, the direct reward coefficient is
`balance * tier * 100000`. For an excluded alternative `excludedEETF < 1000`,
the foregone scarcity-upside coefficient is
`exposure * (1000 - excludedEETF) * networkEETF`.
-/

def directRewardCoefficientScaled
    (balance ethicalEETF : Nat) : Nat :=
  balance * tierMultiplier ethicalEETF * 100000

def exclusiveUpsideCoefficientScaled
    (exposure networkEETF excludedEETF : Nat) : Nat :=
  if excludedEETF < eetfScale then
    exposure * (eetfScale - excludedEETF) * networkEETF
  else 0

theorem direct_reward_coefficient_positive_at_baseline
    (balance : Nat) (hBalance : 0 < balance) :
    0 < directRewardCoefficientScaled balance eetfScale := by
  simp [directRewardCoefficientScaled, baseline_tier_is_one]
  omega

theorem exclusive_upside_coefficient_positive
    (exposure networkEETF excludedEETF : Nat)
    (hExposure : 0 < exposure)
    (hNetwork : 0 < networkEETF)
    (hExcluded : excludedEETF < eetfScale) :
    0 < exclusiveUpsideCoefficientScaled
      exposure networkEETF excludedEETF := by
  simp [exclusiveUpsideCoefficientScaled, hExcluded]
  have hDeficit : 0 < eetfScale - excludedEETF := by omega
  exact Nat.mul_pos (Nat.mul_pos hExposure hDeficit) hNetwork

/-! ## Exclusion utility model -/

/-- Total scarcity exposure reserved for an eligible branch. -/
def eligibilityCoefficient
    (directReward exclusiveScarcityUpside : Nat) : Nat :=
  directReward + exclusiveScarcityUpside

/-- Utility of the eligible branch after normalizing foregone upside as a
positive benefit available only under eligibility. -/
def eligibleUtility
    (base : Int) (scarcityMultiplier directReward
      exclusiveScarcityUpside : Nat) : Int :=
  base + Int.ofNat
    (scarcityMultiplier *
      eligibilityCoefficient directReward exclusiveScarcityUpside)

/-- Utility of the excluded branch. No penalty, tax, burn, or balance debit is
applied; the branch receives its bounded deviation gain and lacks the exclusive
scarcity upside. -/
def excludedUtility (base : Int) (deviationGain : Nat) : Int :=
  base + Int.ofNat deviationGain

/-- The historical paper/simulation placement of opportunity cost. This is a
relative-utility normalization, not a settlement transition. -/
def historicalEligibleUtility
    (base : Int) (scarcityMultiplier directReward : Nat) : Int :=
  base + Int.ofNat (scarcityMultiplier * directReward)

def historicalExcludedUtility
    (base : Int) (scarcityMultiplier exclusiveScarcityUpside
      deviationGain : Nat) : Int :=
  base + Int.ofNat deviationGain -
    Int.ofNat (scarcityMultiplier * exclusiveScarcityUpside)

/-- Moving the foregone scarcity upside from the excluded branch to the
eligible branch preserves the strict choice ordering. -/
theorem exclusion_opportunity_cost_normalization
    (base : Int) (scarcityMultiplier directReward
      exclusiveScarcityUpside deviationGain : Nat) :
    historicalExcludedUtility base scarcityMultiplier
        exclusiveScarcityUpside deviationGain <
      historicalEligibleUtility base scarcityMultiplier directReward ↔
    excludedUtility base deviationGain <
      eligibleUtility base scarcityMultiplier directReward
        exclusiveScarcityUpside := by
  simp [historicalExcludedUtility, historicalEligibleUtility,
    excludedUtility, eligibleUtility, eligibilityCoefficient, Int.mul_add]
  omega

/-- V1's exact finite margin. -/
def StrictExclusionMargin
    (scarcityMultiplier directReward exclusiveScarcityUpside
      deviationGain : Nat) : Prop :=
  deviationGain <
    scarcityMultiplier *
      eligibilityCoefficient directReward exclusiveScarcityUpside

theorem strict_exclusion_margin_orders_utilities
    (base : Int) (scarcityMultiplier directReward
      exclusiveScarcityUpside deviationGain : Nat)
    (hMargin : StrictExclusionMargin scarcityMultiplier directReward
      exclusiveScarcityUpside deviationGain) :
    excludedUtility base deviationGain <
      eligibleUtility base scarcityMultiplier directReward
        exclusiveScarcityUpside := by
  simp [StrictExclusionMargin, excludedUtility, eligibleUtility] at *
  omega

/-- Utility selected by V1's declared two-branch exact optimizer. -/
def chosenUtility
    (choiceEligible : Bool) (eligible excluded : Int) : Int :=
  if choiceEligible then eligible else excluded

theorem strict_order_forces_exact_maximizer_eligible
    (eligible excluded : Int) (choiceEligible : Bool)
    (hStrict : excluded < eligible)
    (hOptimal : eligible ≤
      chosenUtility choiceEligible eligible excluded) :
    choiceEligible = true := by
  cases choiceEligible with
  | false =>
      simp [chosenUtility] at hOptimal
      omega
  | true => rfl

/-- Operative finite V1 theorem for the EETF/VCC exclusion mechanism. -/
theorem v1_exclusion_alignment
    (base : Int) (scarcityMultiplier directReward
      exclusiveScarcityUpside deviationGain : Nat)
    (choiceEligible : Bool)
    (hMargin : StrictExclusionMargin scarcityMultiplier directReward
      exclusiveScarcityUpside deviationGain)
    (hOptimal :
      eligibleUtility base scarcityMultiplier directReward
          exclusiveScarcityUpside ≤
        chosenUtility choiceEligible
          (eligibleUtility base scarcityMultiplier directReward
            exclusiveScarcityUpside)
          (excludedUtility base deviationGain)) :
    choiceEligible = true := by
  apply strict_order_forces_exact_maximizer_eligible
  · exact strict_exclusion_margin_orders_utilities base scarcityMultiplier
      directReward exclusiveScarcityUpside deviationGain hMargin
  · exact hOptimal

/-! ## Scarcity threshold and asymptotic V1 result -/

def minimumScarcityMultiplier
    (deviationGain coefficient : Nat) : Nat :=
  deviationGain / coefficient + 1

theorem minimum_scarcity_multiplier_is_strict
    (deviationGain coefficient : Nat) (hCoefficient : 0 < coefficient) :
    deviationGain <
      minimumScarcityMultiplier deviationGain coefficient * coefficient := by
  simpa [minimumScarcityMultiplier, Nat.mul_comm] using
    (Nat.lt_mul_div_succ deviationGain hCoefficient)

theorem scarcity_below_minimum_is_not_strict
    (scarcityMultiplier deviationGain coefficient : Nat)
    (hBelow :
      scarcityMultiplier <
        minimumScarcityMultiplier deviationGain coefficient) :
    ¬ deviationGain < scarcityMultiplier * coefficient := by
  have hLeDiv : scarcityMultiplier ≤ deviationGain / coefficient := by
    dsimp [minimumScarcityMultiplier] at hBelow
    omega
  have hProduct : scarcityMultiplier * coefficient ≤ deviationGain :=
    Nat.mul_le_of_le_div coefficient scarcityMultiplier deviationGain hLeDiv
  omega

theorem zero_deviation_needs_only_positive_scarcity_and_exposure
    (scarcityMultiplier directReward exclusiveScarcityUpside : Nat)
    (hScarcity : 0 < scarcityMultiplier)
    (hExposure :
      0 < eligibilityCoefficient directReward exclusiveScarcityUpside) :
    StrictExclusionMargin scarcityMultiplier directReward
      exclusiveScarcityUpside 0 := by
  simp only [StrictExclusionMargin]
  exact Nat.mul_pos hScarcity hExposure

/-- An unbounded scarcity path eventually reaches every finite lower bound. -/
def EventuallyAtLeastEveryBound (scarcity : Nat → Nat) : Prop :=
  ∀ bound, ∃ T, ∀ t, T ≤ t → bound ≤ scarcity t

theorem unbounded_scarcity_eventually_establishes_v1_margin
    (scarcity : Nat → Nat)
    (directReward exclusiveScarcityUpside deviationGain : Nat)
    (hExposure :
      0 < eligibilityCoefficient directReward exclusiveScarcityUpside)
    (hUnbounded : EventuallyAtLeastEveryBound scarcity) :
    ∃ T, ∀ t, T ≤ t →
      StrictExclusionMargin (scarcity t) directReward
        exclusiveScarcityUpside deviationGain := by
  let coefficient :=
    eligibilityCoefficient directReward exclusiveScarcityUpside
  let threshold := minimumScarcityMultiplier deviationGain coefficient
  obtain ⟨T, hT⟩ := hUnbounded threshold
  refine ⟨T, ?_⟩
  intro t ht
  have hMinimum :=
    minimum_scarcity_multiplier_is_strict deviationGain coefficient hExposure
  have hMonotone :
      threshold * coefficient ≤ scarcity t * coefficient :=
    Nat.mul_le_mul_right coefficient (hT t ht)
  exact Nat.lt_of_lt_of_le hMinimum hMonotone

/-- Scarcity or token appreciation shared equally by both alternatives cancels
from the decision. Exclusion must bind the relevant upside to eligibility. -/
theorem common_scarcity_upside_cancels
    (common eligible excluded : Int) :
    common + excluded < common + eligible ↔ excluded < eligible := by
  omega

end AlignmentTheoremV1
