import Std.Tactic

/-!
# Alignment Theorem Version 2

This file proves a finite, policy-relative result.  It does not define objective
ethics, prove that authenticated evidence describes the physical world, or prove
that an LLM's internal goals are aligned.

The trusted semantic boundary is explicit:

1. authenticated facts populate `Obligations`;
2. `admits` is the Tau-equivalent fail-closed policy gate;
3. settlement is reserve bounded; and
4. a strict finite utility margin makes policy compliance the only
   epsilon-optimal choice in the two-class model.
-/

namespace AlignmentTheoremV2

/-- Facts that must all be established before an action may be published. -/
structure Obligations where
  policyRootMatches : Bool
  evidenceAuthenticated : Bool
  actionKnown : Bool
  actionPolicyCompliant : Bool
  nonceFresh : Bool
  taskUnclaimed : Bool
  rewardFunded : Bool
  deriving DecidableEq, Repr

/-- The same conjunction executed by `tau/v2/alignment_policy_gate_v2.tau`. -/
def admits (o : Obligations) : Bool :=
  o.policyRootMatches &&
    (o.evidenceAuthenticated &&
      (o.actionKnown &&
        (o.actionPolicyCompliant &&
          (o.nonceFresh &&
            (o.taskUnclaimed && o.rewardFunded)))))

theorem admits_implies_every_obligation (o : Obligations)
    (h : admits o = true) :
    o.policyRootMatches = true ∧
    o.evidenceAuthenticated = true ∧
    o.actionKnown = true ∧
    o.actionPolicyCompliant = true ∧
    o.nonceFresh = true ∧
    o.taskUnclaimed = true ∧
    o.rewardFunded = true := by
  simpa [admits, Bool.and_eq_true] using h

/-- An arbitrary proposal engine cannot publish a policy-violating action. -/
theorem committed_action_is_policy_compliant (o : Obligations)
    (hCommit : admits o = true) : o.actionPolicyCompliant = true := by
  exact (admits_implies_every_obligation o hCommit).2.2.2.1

/-- Finite settlement output for one reward claim. -/
structure Settlement where
  accepted : Bool
  payout : Nat
  reservePost : Nat
  deriving DecidableEq, Repr

/-- Reject is a no-op; accept pays only when the committed reserve covers it. -/
def settle (o : Obligations) (reward reserve : Nat) : Settlement :=
  if admits o = true ∧ reward ≤ reserve then
    { accepted := true, payout := reward, reservePost := reserve - reward }
  else
    { accepted := false, payout := 0, reservePost := reserve }

theorem rejected_settlement_is_noop (o : Obligations) (reward reserve : Nat)
    (hReject : (settle o reward reserve).accepted = false) :
    (settle o reward reserve).payout = 0 ∧
    (settle o reward reserve).reservePost = reserve := by
  by_cases hGate : admits o = true ∧ reward ≤ reserve
  · simp [settle, hGate] at hReject
  · simp [settle, hGate]

theorem accepted_settlement_conserves_reserve
    (o : Obligations) (reward reserve : Nat)
    (hAccept : (settle o reward reserve).accepted = true) :
    (settle o reward reserve).reservePost +
      (settle o reward reserve).payout = reserve := by
  by_cases hGate : admits o = true ∧ reward ≤ reserve
  · simp [settle, hGate, Nat.sub_add_cancel hGate.2]
  · simp [settle, hGate] at hAccept

theorem accepted_payout_is_funded
    (o : Obligations) (reward reserve : Nat)
    (hAccept : (settle o reward reserve).accepted = true) :
    (settle o reward reserve).payout ≤ reserve := by
  by_cases hGate : admits o = true ∧ reward ≤ reserve
  · simp [settle, hGate]
  · simp [settle, hGate] at hAccept

/-- Utility of the selected action class in the restricted two-class model. -/
def chosenUtility (choiceCompliant : Bool)
    (compliantUtility noncompliantUtility : Nat) : Nat :=
  if choiceCompliant then compliantUtility else noncompliantUtility

/--
If the compliant action beats the noncompliant upper bound by more than the
optimizer error, every epsilon-optimal choice is compliant.
-/
theorem epsilon_optimal_choice_is_compliant
    (compliantUtility noncompliantUtility epsilon : Nat)
    (choiceCompliant : Bool)
    (hGap : noncompliantUtility + epsilon < compliantUtility)
    (hOptimal : compliantUtility ≤
      chosenUtility choiceCompliant compliantUtility noncompliantUtility + epsilon) :
    choiceCompliant = true := by
  cases choiceCompliant <;> simp_all [chosenUtility]
  omega

/--
The finite Alignment Theorem.

`expectedSlash` is an already-conservative expected enforcement amount.  The
noncompliant utility bound may include private off-network gain.  The theorem
therefore avoids infinite scarcity and applies at a finite reserve-backed
incentive margin.
-/
theorem finite_alignment_theorem
    (baseProfit compliantReward noncompliantReward expectedSlash : Nat)
    (maxPrivateDeviationGain maxExtraComplianceCost epsilon : Nat)
    (noncompliantUtility : Nat)
    (choiceCompliant : Bool)
    (hDeviationBound :
      noncompliantUtility + expectedSlash ≤
        baseProfit + noncompliantReward +
          maxPrivateDeviationGain + maxExtraComplianceCost)
    (hStrictMechanismMargin :
      noncompliantReward + maxPrivateDeviationGain +
          maxExtraComplianceCost + epsilon <
        compliantReward + expectedSlash)
    (hOptimal : baseProfit + compliantReward ≤
      chosenUtility choiceCompliant
        (baseProfit + compliantReward) noncompliantUtility + epsilon) :
    choiceCompliant = true := by
  apply epsilon_optimal_choice_is_compliant
      (baseProfit + compliantReward) noncompliantUtility epsilon choiceCompliant
  · omega
  · exact hOptimal

/--
Reward-only specialization: punishment is unnecessary when the funded reward
advantage alone clears the complete deviation, compliance-cost, and optimizer
margin.
-/
theorem reward_only_alignment_theorem
    (baseProfit compliantReward noncompliantReward : Nat)
    (maxPrivateDeviationGain maxExtraComplianceCost epsilon : Nat)
    (noncompliantUtility : Nat)
    (choiceCompliant : Bool)
    (hDeviationBound :
      noncompliantUtility ≤
        baseProfit + noncompliantReward +
          maxPrivateDeviationGain + maxExtraComplianceCost)
    (hStrictRewardMargin :
      noncompliantReward + maxPrivateDeviationGain +
          maxExtraComplianceCost + epsilon < compliantReward)
    (hOptimal : baseProfit + compliantReward ≤
      chosenUtility choiceCompliant
        (baseProfit + compliantReward) noncompliantUtility + epsilon) :
    choiceCompliant = true := by
  simpa using finite_alignment_theorem
    baseProfit compliantReward noncompliantReward 0
    maxPrivateDeviationGain maxExtraComplianceCost epsilon
    noncompliantUtility choiceCompliant
    hDeviationBound hStrictRewardMargin hOptimal

/-- A policy revision is safe only relative to a separately retained constitution. -/
def PreservesConstitution {Action : Type}
    (constitution candidate : Action → Bool) : Prop :=
  ∀ action, candidate action = true → constitution action = true

theorem admitted_revision_preserves_constitution {Action : Type}
    (constitution candidate : Action → Bool)
    (hAdmission : PreservesConstitution constitution candidate) :
    ∀ action, candidate action = true → constitution action = true := by
  exact hAdmission

end AlignmentTheoremV2
