import Std.Tactic

/-!
# Alignment Theorem Version 1.1

This file repairs Version 1's original hyperdeflationary mechanism.  Scarcity
has a genuine causal role because it amplifies an ethical reward entitlement
and an optional non-ethical forfeiture against a bounded or slower-growing
opposing advantage.

The theorem is conditional.  It does not prove that Bitcoin purchasing power
diverges, that AGI causes hyperdeflation, that an EETF assessment is honest, or
that private deviation gains satisfy the required growth bound.
-/

namespace AlignmentTheoremV1_1

/-- Scarcity exposure favoring an ethical action. -/
def mechanismCoefficient
    (ethicalRewardCoefficient nonethicalForfeitureCoefficient : Nat) : Nat :=
  ethicalRewardCoefficient + nonethicalForfeitureCoefficient

/-- Complete opposing bound, including approximate-optimization error. -/
def requiredAdvantage
    (maxPrivateDeviationGain maxExtraComplianceCost optimizerError : Nat) : Nat :=
  maxPrivateDeviationGain + maxExtraComplianceCost + optimizerError

/-- The finite V1.1 condition checked at one decision epoch. -/
def StrictHyperdeflationMargin
    (scarcityMultiplier ethicalRewardCoefficient : Nat)
    (nonethicalForfeitureCoefficient maxPrivateDeviationGain : Nat)
    (maxExtraComplianceCost optimizerError : Nat) : Prop :=
  requiredAdvantage maxPrivateDeviationGain maxExtraComplianceCost optimizerError <
    scarcityMultiplier *
      mechanismCoefficient ethicalRewardCoefficient nonethicalForfeitureCoefficient

/-- Exact least integer multiplier that strictly clears a fixed bound. -/
def minimumScarcityMultiplier (required coefficient : Nat) : Nat :=
  required / coefficient + 1

theorem minimum_scarcity_multiplier_is_strict
    (required coefficient : Nat) (hCoefficient : 0 < coefficient) :
    required < minimumScarcityMultiplier required coefficient * coefficient := by
  simpa [minimumScarcityMultiplier, Nat.mul_comm] using
    (Nat.lt_mul_div_succ required hCoefficient)

theorem strict_margin_at_or_above_minimum
    (scarcityMultiplier required coefficient : Nat)
    (hCoefficient : 0 < coefficient)
    (hScarcity : minimumScarcityMultiplier required coefficient ≤ scarcityMultiplier) :
    required < scarcityMultiplier * coefficient := by
  have hMinimum := minimum_scarcity_multiplier_is_strict required coefficient hCoefficient
  have hMonotone :
      minimumScarcityMultiplier required coefficient * coefficient ≤
        scarcityMultiplier * coefficient :=
    Nat.mul_le_mul_right coefficient hScarcity
  exact Nat.lt_of_lt_of_le hMinimum hMonotone

/-- A discrete sequence eventually reaches every finite lower bound. -/
def EventuallyAtLeastEveryBound (scarcity : Nat → Nat) : Prop :=
  ∀ bound, ∃ T, ∀ t, T ≤ t → bound ≤ scarcity t

/-- Normalized score after moving all scarcity exposure to the ethical side. -/
def ethicalScore (scarcityMultiplier coefficient : Nat) : Nat :=
  scarcityMultiplier * coefficient

/-- Normalized score containing deviation gain and compliance cost. -/
def nonethicalScore
    (maxPrivateDeviationGain maxExtraComplianceCost : Nat) : Nat :=
  maxPrivateDeviationGain + maxExtraComplianceCost

def chosenScore
    (choiceEthical : Bool) (ethical nonethical : Nat) : Nat :=
  if choiceEthical then ethical else nonethical

theorem strict_margin_forces_epsilon_optimal_choice_ethical
    (ethical nonethical optimizerError : Nat)
    (choiceEthical : Bool)
    (hStrict : nonethical + optimizerError < ethical)
    (hOptimal : ethical ≤
      chosenScore choiceEthical ethical nonethical + optimizerError) :
    choiceEthical = true := by
  cases choiceEthical <;> simp_all [chosenScore]
  omega

/--
Finite V1.1 theorem: at a strict scarcity margin, every epsilon-optimal choice
in the normalized two-action model is ethical.
-/
theorem finite_hyperdeflationary_alignment
    (scarcityMultiplier ethicalRewardCoefficient : Nat)
    (nonethicalForfeitureCoefficient maxPrivateDeviationGain : Nat)
    (maxExtraComplianceCost optimizerError : Nat)
    (choiceEthical : Bool)
    (hMargin : StrictHyperdeflationMargin scarcityMultiplier
      ethicalRewardCoefficient nonethicalForfeitureCoefficient
      maxPrivateDeviationGain maxExtraComplianceCost optimizerError)
    (hOptimal :
      ethicalScore scarcityMultiplier
          (mechanismCoefficient ethicalRewardCoefficient
            nonethicalForfeitureCoefficient) ≤
        chosenScore choiceEthical
            (ethicalScore scarcityMultiplier
              (mechanismCoefficient ethicalRewardCoefficient
                nonethicalForfeitureCoefficient))
            (nonethicalScore maxPrivateDeviationGain maxExtraComplianceCost) +
          optimizerError) :
    choiceEthical = true := by
  apply strict_margin_forces_epsilon_optimal_choice_ethical
  · simpa [StrictHyperdeflationMargin, requiredAdvantage, ethicalScore,
      nonethicalScore] using hMargin
  · exact hOptimal

/--
Asymptotic V1.1 theorem for fixed coefficients and a fixed opposing bound.
Unbounded hyperdeflation eventually crosses the exact finite threshold.
-/
theorem hyperdeflation_eventually_aligns_bounded_deviations
    (scarcity : Nat → Nat)
    (ethicalRewardCoefficient nonethicalForfeitureCoefficient : Nat)
    (maxPrivateDeviationGain maxExtraComplianceCost optimizerError : Nat)
    (hCoefficient :
      0 < mechanismCoefficient ethicalRewardCoefficient
        nonethicalForfeitureCoefficient)
    (hHyperdeflation : EventuallyAtLeastEveryBound scarcity) :
    ∃ T, ∀ t, T ≤ t → ∀ choiceEthical : Bool,
      (ethicalScore (scarcity t)
          (mechanismCoefficient ethicalRewardCoefficient
            nonethicalForfeitureCoefficient) ≤
        chosenScore choiceEthical
            (ethicalScore (scarcity t)
              (mechanismCoefficient ethicalRewardCoefficient
                nonethicalForfeitureCoefficient))
            (nonethicalScore maxPrivateDeviationGain maxExtraComplianceCost) +
          optimizerError) →
      choiceEthical = true := by
  let required := requiredAdvantage maxPrivateDeviationGain
    maxExtraComplianceCost optimizerError
  let coefficient := mechanismCoefficient ethicalRewardCoefficient
    nonethicalForfeitureCoefficient
  let threshold := minimumScarcityMultiplier required coefficient
  obtain ⟨T, hT⟩ := hHyperdeflation threshold
  refine ⟨T, ?_⟩
  intro t ht choiceEthical hOptimal
  apply finite_hyperdeflationary_alignment
      (scarcity t) ethicalRewardCoefficient nonethicalForfeitureCoefficient
      maxPrivateDeviationGain maxExtraComplianceCost optimizerError
      choiceEthical
  · apply strict_margin_at_or_above_minimum
      (scarcity t) required coefficient hCoefficient
    exact hT t ht
  · exact hOptimal

/--
Relative-growth form for AGI scenarios: the opposing bound may grow, provided
its coefficient-normalized value eventually remains below scarcity.
-/
theorem relative_growth_eventually_has_strict_margin
    (scarcity coefficient required : Nat → Nat)
    (hCoefficient : ∀ t, 0 < coefficient t)
    (hRelativeGrowth :
      ∃ T, ∀ t, T ≤ t → required t / coefficient t < scarcity t) :
    ∃ T, ∀ t, T ≤ t → required t < scarcity t * coefficient t := by
  obtain ⟨T, hT⟩ := hRelativeGrowth
  refine ⟨T, ?_⟩
  intro t ht
  exact Nat.lt_mul_of_div_lt (hT t ht) (hCoefficient t)

end AlignmentTheoremV1_1
