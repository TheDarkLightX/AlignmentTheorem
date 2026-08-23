import Std.Tactic

/-!
# Intelligence-to-abundance bridge

The theorem boundary remains `B < M*K`.  Capability growth is not silently
identified with `M` or `K`: the positive theorem requires explicit bounds on
both deviation and protected reward, while the negative theorems show that an
arbitrary intelligence trajectory cannot overcome a bounded reward.

Boolean facts in the DAC gate are premises supplied by a host/oracle layer.
These proofs do not authenticate capability, prices, rents, identities,
externalities, debt, receipts, or Tau/Tau Net execution.
-/

namespace IntelligenceFlywheel

/-- Strict policy-relative alignment margin from Alignment Theorem V1.1. -/
def Aligned (M K B : Nat) : Prop := B < M * K

/-- A supplied geometric crossing witness is sufficient for alignment. -/
theorem alignment_of_geometric_bounds
    (M K B : Nat → Nat) (B0 b R0 r n : Nat)
    (hDeviation : B n ≤ B0 * b ^ n)
    (hReward : R0 * r ^ n ≤ M n * K n)
    (hCrossing : B0 * b ^ n < R0 * r ^ n) :
    Aligned (M n) (K n) (B n) := by
  unfold Aligned
  omega

/-- If purchasing power doubles and `K ≥ 1`, epoch `B` beats fixed deviation B. -/
theorem fixed_deviation_doubling_witness (B K : Nat) (hK : 1 ≤ K) :
    Aligned (2 ^ B) K B := by
  have hPow : B < 2 ^ B := Nat.lt_pow_self (by decide)
  have hMul : 2 ^ B ≤ (2 ^ B) * K := by
    simpa using Nat.mul_le_mul_left (2 ^ B) hK
  exact Nat.lt_of_lt_of_le hPow hMul

/-- Capability growth alone is logically insufficient: M=K=1, B=2 fails. -/
theorem intelligence_growth_alone_insufficient (I : Nat → Nat) :
    ∀ t : Nat, ¬ Aligned 1 1 2 := by
  intro t
  simp [Aligned]

/-- Any reward cap below a deviation floor rules alignment out pointwise. -/
theorem bounded_reward_blocks_alignment
    (M K B : Nat → Nat) (multiplierCap benefitCap : Nat)
    (hM : ∀ t, M t ≤ multiplierCap)
    (hK : ∀ t, K t ≤ benefitCap)
    (hB : ∀ t, multiplierCap * benefitCap ≤ B t) :
    ∀ t, ¬ Aligned (M t) (K t) (B t) := by
  intro t hAligned
  have hProduct : M t * K t ≤ multiplierCap * benefitCap :=
    Nat.mul_le_mul (hM t) (hK t)
  have hNot : M t * K t ≤ B t := Nat.le_trans hProduct (hB t)
  exact (Nat.not_lt_of_ge hNot) hAligned

/-- Strictness matters: equality at the V1.1 boundary is not alignment. -/
theorem equality_is_not_strict_alignment (M K : Nat) :
    ¬ Aligned M K (M * K) := by
  simp [Aligned]

/-- Claims consumed by the research DAC treasury policy. -/
structure DacGateFacts where
  policyRootOk : Bool
  capabilityReceiptAuthenticated : Bool
  productivityBridgeVerified : Bool
  essentialBasketGainVerified : Bool
  benefitFloorFunded : Bool
  concentrationCapOk : Bool
  gridExternalityBudgetOk : Bool
  debtGuardrailOk : Bool
  strictAlignmentMargin : Bool
  deriving DecidableEq, Repr

/-- The complete nine-fact conjunction executed by the packet. -/
def dacTreasuryAdmits (f : DacGateFacts) : Bool :=
  f.policyRootOk &&
    (f.capabilityReceiptAuthenticated &&
      (f.productivityBridgeVerified &&
        (f.essentialBasketGainVerified &&
          (f.benefitFloorFunded &&
            (f.concentrationCapOk &&
              (f.gridExternalityBudgetOk &&
                (f.debtGuardrailOk && f.strictAlignmentMargin)))))))

theorem dac_admission_implies_every_fact (f : DacGateFacts)
    (h : dacTreasuryAdmits f = true) :
    f.policyRootOk = true ∧
    f.capabilityReceiptAuthenticated = true ∧
    f.productivityBridgeVerified = true ∧
    f.essentialBasketGainVerified = true ∧
    f.benefitFloorFunded = true ∧
    f.concentrationCapOk = true ∧
    f.gridExternalityBudgetOk = true ∧
    f.debtGuardrailOk = true ∧
    f.strictAlignmentMargin = true := by
  simpa [dacTreasuryAdmits, Bool.and_eq_true] using h

/-- Sender scoping: other accounts are not constrained by this treasury rule. -/
def senderScopedAllows (isTreasury : Bool) (f : DacGateFacts) : Bool :=
  if isTreasury then dacTreasuryAdmits f else true

theorem non_treasury_sender_is_unaffected (f : DacGateFacts) :
    senderScopedAllows false f = true := by
  simp [senderScopedAllows]

theorem treasury_admission_implies_gate (f : DacGateFacts)
    (h : senderScopedAllows true f = true) :
    dacTreasuryAdmits f = true := by
  simpa [senderScopedAllows] using h

end IntelligenceFlywheel
