import Std.Tactic

/-!
# Alignment Theorem Version 1.1

This file generalizes Version 1's concrete EETF/VCC exclusion mechanism.
Scarcity has a causal role because it amplifies an eligible reward entitlement
and scarcity upside unavailable to the excluded branch against a bounded or
slower-growing opposing advantage. The foregone upside is opportunity cost,
with no punitive debit.

The theorem is conditional.  It does not prove that Bitcoin purchasing power
diverges, that AGI causes hyperdeflation, that an EETF assessment is honest, or
that private deviation gains satisfy the required growth bound.
-/

namespace AlignmentTheoremV1_1

/-- Scarcity exposure favoring an ethical action. -/
def mechanismCoefficient
    (ethicalRewardCoefficient exclusiveUpsideCoefficient : Nat) : Nat :=
  ethicalRewardCoefficient + exclusiveUpsideCoefficient

/-- Complete opposing bound, including approximate-optimization error. -/
def requiredAdvantage
    (maxPrivateDeviationGain maxExtraComplianceCost optimizerError : Nat) : Nat :=
  maxPrivateDeviationGain + maxExtraComplianceCost + optimizerError

/-- The finite V1.1 condition checked at one decision epoch. -/
def StrictHyperdeflationMargin
    (scarcityMultiplier ethicalRewardCoefficient : Nat)
    (exclusiveUpsideCoefficient maxPrivateDeviationGain : Nat)
    (maxExtraComplianceCost optimizerError : Nat) : Prop :=
  requiredAdvantage maxPrivateDeviationGain maxExtraComplianceCost optimizerError <
    scarcityMultiplier *
      mechanismCoefficient ethicalRewardCoefficient exclusiveUpsideCoefficient

/-- Exact least integer multiplier that strictly clears a fixed bound. -/
def minimumScarcityMultiplier (required coefficient : Nat) : Nat :=
  required / coefficient + 1

theorem minimum_scarcity_multiplier_is_strict
    (required coefficient : Nat) (hCoefficient : 0 < coefficient) :
    required < minimumScarcityMultiplier required coefficient * coefficient := by
  simpa [minimumScarcityMultiplier, Nat.mul_comm] using
    (Nat.lt_mul_div_succ required hCoefficient)

theorem scarcity_below_minimum_is_not_strict
    (scarcityMultiplier required coefficient : Nat)
    (hBelow :
      scarcityMultiplier < minimumScarcityMultiplier required coefficient) :
    ¬ required < scarcityMultiplier * coefficient := by
  have hLeDiv : scarcityMultiplier ≤ required / coefficient := by
    dsimp [minimumScarcityMultiplier] at hBelow
    omega
  have hProduct : scarcityMultiplier * coefficient ≤ required :=
    Nat.mul_le_of_le_div coefficient scarcityMultiplier required hLeDiv
  omega

/-- The threshold is strict at the threshold and no smaller multiplier is. -/
theorem minimum_scarcity_multiplier_is_least
    (required coefficient : Nat) (hCoefficient : 0 < coefficient) :
    required < minimumScarcityMultiplier required coefficient * coefficient ∧
      ∀ scarcityMultiplier,
        scarcityMultiplier < minimumScarcityMultiplier required coefficient →
          ¬ required < scarcityMultiplier * coefficient := by
  constructor
  · exact minimum_scarcity_multiplier_is_strict required coefficient hCoefficient
  · intro scarcityMultiplier hBelow
    exact scarcity_below_minimum_is_not_strict
      scarcityMultiplier required coefficient hBelow

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

/-- Utility selected by the modeled two-action choice. -/
def chosenUtility
    (choiceEthical : Bool) (ethical nonethical : Int) : Int :=
  if choiceEthical then ethical else nonethical

/-- No-debit lower bound for the eligible action's utility. The exclusive
upside is represented as value available on this branch. -/
def ethicalUtilityLower
    (baseline scarcityMultiplier ethicalRewardCoefficient exclusiveUpsideCoefficient
      maxExtraComplianceCost : Int) : Int :=
  baseline + scarcityMultiplier *
      (ethicalRewardCoefficient + exclusiveUpsideCoefficient) - maxExtraComplianceCost

/-- Upper bound for the excluded action's utility. Exclusion withholds the
protected upside and applies no balance debit. -/
def nonethicalUtilityUpper
    (baseline maxPrivateDeviationGain : Int) : Int :=
  baseline + maxPrivateDeviationGain

/--
The utility-bound bridge stated in the V1.1 paper.  The strict economic margin,
the ethical lower bound, and the non-ethical upper bound force every
epsilon-optimal modeled choice to be ethical.
-/
theorem paper_utility_bounds_force_epsilon_optimal_choice_ethical
    (baseline scarcityMultiplier ethicalRewardCoefficient : Int)
    (exclusiveUpsideCoefficient maxPrivateDeviationGain : Int)
    (maxExtraComplianceCost optimizerError : Int)
    (ethicalUtility nonethicalUtility : Int)
    (choiceEthical : Bool)
    (hEthicalLower :
      ethicalUtilityLower baseline scarcityMultiplier
          ethicalRewardCoefficient exclusiveUpsideCoefficient
          maxExtraComplianceCost ≤ ethicalUtility)
    (hNonethicalUpper :
      nonethicalUtility ≤ nonethicalUtilityUpper baseline maxPrivateDeviationGain)
    (hMargin :
      maxPrivateDeviationGain + maxExtraComplianceCost + optimizerError <
        scarcityMultiplier *
          (ethicalRewardCoefficient + exclusiveUpsideCoefficient))
    (_hOptimizerError : 0 ≤ optimizerError)
    (hOptimal :
      ethicalUtility ≤
        chosenUtility choiceEthical ethicalUtility nonethicalUtility +
          optimizerError) :
    choiceEthical = true := by
  cases choiceEthical with
  | false =>
      simp [chosenUtility] at hOptimal
      simp [ethicalUtilityLower] at hEthicalLower
      simp [nonethicalUtilityUpper] at hNonethicalUpper
      omega
  | true => rfl

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
    (exclusiveUpsideCoefficient maxPrivateDeviationGain : Nat)
    (maxExtraComplianceCost optimizerError : Nat)
    (choiceEthical : Bool)
    (hMargin : StrictHyperdeflationMargin scarcityMultiplier
      ethicalRewardCoefficient exclusiveUpsideCoefficient
      maxPrivateDeviationGain maxExtraComplianceCost optimizerError)
    (hOptimal :
      ethicalScore scarcityMultiplier
          (mechanismCoefficient ethicalRewardCoefficient
            exclusiveUpsideCoefficient) ≤
        chosenScore choiceEthical
            (ethicalScore scarcityMultiplier
              (mechanismCoefficient ethicalRewardCoefficient
                exclusiveUpsideCoefficient))
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
    (ethicalRewardCoefficient exclusiveUpsideCoefficient : Nat)
    (maxPrivateDeviationGain maxExtraComplianceCost optimizerError : Nat)
    (hCoefficient :
      0 < mechanismCoefficient ethicalRewardCoefficient
        exclusiveUpsideCoefficient)
    (hHyperdeflation : EventuallyAtLeastEveryBound scarcity) :
    ∃ T, ∀ t, T ≤ t → ∀ choiceEthical : Bool,
      (ethicalScore (scarcity t)
          (mechanismCoefficient ethicalRewardCoefficient
            exclusiveUpsideCoefficient) ≤
        chosenScore choiceEthical
            (ethicalScore (scarcity t)
              (mechanismCoefficient ethicalRewardCoefficient
                exclusiveUpsideCoefficient))
            (nonethicalScore maxPrivateDeviationGain maxExtraComplianceCost) +
          optimizerError) →
      choiceEthical = true := by
  let required := requiredAdvantage maxPrivateDeviationGain
    maxExtraComplianceCost optimizerError
  let coefficient := mechanismCoefficient ethicalRewardCoefficient
    exclusiveUpsideCoefficient
  let threshold := minimumScarcityMultiplier required coefficient
  obtain ⟨T, hT⟩ := hHyperdeflation threshold
  refine ⟨T, ?_⟩
  intro t ht choiceEthical hOptimal
  apply finite_hyperdeflationary_alignment
      (scarcity t) ethicalRewardCoefficient exclusiveUpsideCoefficient
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
