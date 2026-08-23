import Std.Tactic

/-!
# Compute Dividend and Household Wealth-Agent Kernel

This file proves finite accounting, floor-feasibility, transfer, and policy-gate
claims.  Boolean obligations are assumed host-derived.  The proofs do not
authenticate rent, meters, people, consent, market data, custody, or Tau source
provenance, and they do not guarantee investment returns.
-/

namespace ComputeDividend

/-- Facts required before one dividend-and-compute entitlement is admitted. -/
structure DividendObligations where
  policyRootOk : Bool
  rentReceiptAuthenticated : Bool
  gridCostsReserved : Bool
  dividendReserveFunded : Bool
  recipientEligible : Bool
  nonceFresh : Bool
  concentrationCapOk : Bool
  agentComputeFunded : Bool
  deriving DecidableEq, Repr

/-- The conjunction executed by `tau/compute_dividend/dividend`. -/
def dividendAdmits (o : DividendObligations) : Bool :=
  o.policyRootOk &&
    (o.rentReceiptAuthenticated &&
      (o.gridCostsReserved &&
        (o.dividendReserveFunded &&
          (o.recipientEligible &&
            (o.nonceFresh &&
              (o.concentrationCapOk && o.agentComputeFunded))))))

theorem dividend_admission_implies_every_obligation (o : DividendObligations)
    (h : dividendAdmits o = true) :
    o.policyRootOk = true ∧
    o.rentReceiptAuthenticated = true ∧
    o.gridCostsReserved = true ∧
    o.dividendReserveFunded = true ∧
    o.recipientEligible = true ∧
    o.nonceFresh = true ∧
    o.concentrationCapOk = true ∧
    o.agentComputeFunded = true := by
  simpa [dividendAdmits, Bool.and_eq_true] using h

/-- Gross rent remaining after senior grid and public-reserve claims. -/
def distributableRent (grossRent gridCost publicReserve : Nat) : Nat :=
  grossRent - (gridCost + publicReserve)

theorem funded_rent_conserves_gross
    (grossRent gridCost publicReserve : Nat)
    (hFunded : gridCost + publicReserve ≤ grossRent) :
    gridCost + publicReserve +
      distributableRent grossRent gridCost publicReserve = grossRent := by
  simp [distributableRent, Nat.add_sub_of_le hFunded]

/-- Gross rent above senior claims and `n * floor` funds the universal floor. -/
theorem gross_rent_threshold_supports_universal_floor
    (grossRent gridCost publicReserve householdCount floor : Nat)
    (hThreshold :
      gridCost + publicReserve + householdCount * floor ≤ grossRent) :
    householdCount * floor ≤
      distributableRent grossRent gridCost publicReserve := by
  simp [distributableRent]
  omega

/-- Finite settlement result for a dividend claim. -/
structure DividendSettlement where
  accepted : Bool
  payout : Nat
  reservePost : Nat
  deriving DecidableEq, Repr

/-- Rejection is a no-op; acceptance requires both gate and exact reserve. -/
def settleDividend (o : DividendObligations) (request reserve : Nat) :
    DividendSettlement :=
  if dividendAdmits o = true ∧ request ≤ reserve then
    { accepted := true, payout := request, reservePost := reserve - request }
  else
    { accepted := false, payout := 0, reservePost := reserve }

theorem rejected_dividend_is_noop
    (o : DividendObligations) (request reserve : Nat)
    (hReject : (settleDividend o request reserve).accepted = false) :
    (settleDividend o request reserve).payout = 0 ∧
    (settleDividend o request reserve).reservePost = reserve := by
  by_cases hGate : dividendAdmits o = true ∧ request ≤ reserve
  · simp [settleDividend, hGate] at hReject
  · simp [settleDividend, hGate]

theorem accepted_dividend_conserves_reserve
    (o : DividendObligations) (request reserve : Nat)
    (hAccept : (settleDividend o request reserve).accepted = true) :
    (settleDividend o request reserve).reservePost +
      (settleDividend o request reserve).payout = reserve := by
  by_cases hGate : dividendAdmits o = true ∧ request ≤ reserve
  · simp [settleDividend, hGate, Nat.sub_add_cancel hGate.2]
  · simp [settleDividend, hGate] at hAccept

/-- Every member receives at least `floor`. -/
def HasUniversalFloor (floor : Nat) (allocation : List Nat) : Prop :=
  ∀ amount ∈ allocation, floor ≤ amount

theorem universal_floor_cost_lower_bound
    (floor : Nat) (allocation : List Nat)
    (hFloor : HasUniversalFloor floor allocation) :
    allocation.length * floor ≤ allocation.sum := by
  induction allocation with
  | nil => simp
  | cons amount rest ih =>
      have hAmount : floor ≤ amount := hFloor amount (by simp)
      have hRest : HasUniversalFloor floor rest := by
        intro candidate hMember
        exact hFloor candidate (by simp [hMember])
      have hInductive := ih hRest
      simp only [List.length_cons, List.sum_cons, Nat.succ_mul]
      omega

/-- A uniform floor is feasible exactly when its aggregate cost fits. -/
theorem universal_floor_feasible_iff
    (householdCount floor budget : Nat) :
    (∃ allocation : List Nat,
      allocation.length = householdCount ∧
      HasUniversalFloor floor allocation ∧
      allocation.sum ≤ budget) ↔
    householdCount * floor ≤ budget := by
  constructor
  · rintro ⟨allocation, hLength, hFloor, hBudget⟩
    have hCost := universal_floor_cost_lower_bound floor allocation hFloor
    rw [hLength] at hCost
    omega
  · intro hFunded
    refine ⟨List.replicate householdCount floor, ?_, ?_, ?_⟩
    · simp
    · intro amount hMember
      simp only [List.mem_replicate] at hMember
      rcases hMember with ⟨_, rfl⟩
      exact Nat.le_refl amount
    · simpa using hFunded

/-- Exact integer form of `amount / budget ≤ numerator / denominator`. -/
def WithinEarmarkedShareCap
    (numerator denominator budget amount : Nat) : Prop :=
  denominator * amount ≤ numerator * budget

def AllocationRespectsShareCap
    (numerator denominator budget : Nat) (allocation : List Nat) : Prop :=
  ∀ amount ∈ allocation,
    WithinEarmarkedShareCap numerator denominator budget amount

theorem allocation_member_respects_share_cap
    (numerator denominator budget amount : Nat) (allocation : List Nat)
    (hCaps : AllocationRespectsShareCap numerator denominator budget allocation)
    (hMember : amount ∈ allocation) :
    WithinEarmarkedShareCap numerator denominator budget amount := by
  exact hCaps amount hMember

/-- Discrete diminishing marginal welfare, stated without subtraction. -/
def DiscreteConcave (utility : Nat → Nat) : Prop :=
  ∀ poorer richer, poorer < richer →
    utility poorer + utility (richer + 1) ≤
      utility (poorer + 1) + utility richer

/-- A one-atom transfer from richer to poorer weakly improves concave welfare. -/
theorem progressive_transfer_weakly_improves
    (utility : Nat → Nat) (hConcave : DiscreteConcave utility)
    (poorer richer : Nat) (hGap : poorer < richer) :
    utility poorer + utility (richer + 1) ≤
      utility (poorer + 1) + utility richer := by
  exact hConcave poorer richer hGap

/-- A true one-period loss bound preserves a separately declared wealth floor. -/
theorem bounded_loss_preserves_protected_floor
    (wealth protectedFloor modeledLoss : Nat)
    (hFloor : protectedFloor ≤ wealth)
    (hLoss : modeledLoss ≤ wealth - protectedFloor) :
    protectedFloor ≤ wealth - modeledLoss := by
  omega

/-- Facts required before the household agent may commit an action. -/
structure WealthObligations where
  policyRootOk : Bool
  householdConsentFresh : Bool
  proposalEvidenceAuthenticated : Bool
  custodyAuthorized : Bool
  noLeverageOrShort : Bool
  concentrationLimitOk : Bool
  tailLossLimitOk : Bool
  feeTurnoverLimitOk : Bool
  deriving DecidableEq, Repr

/-- The conjunction executed by `tau/compute_dividend/wealth`. -/
def wealthAdmits (o : WealthObligations) : Bool :=
  o.policyRootOk &&
    (o.householdConsentFresh &&
      (o.proposalEvidenceAuthenticated &&
        (o.custodyAuthorized &&
          (o.noLeverageOrShort &&
            (o.concentrationLimitOk &&
              (o.tailLossLimitOk && o.feeTurnoverLimitOk))))))

theorem wealth_admission_implies_every_obligation (o : WealthObligations)
    (h : wealthAdmits o = true) :
    o.policyRootOk = true ∧
    o.householdConsentFresh = true ∧
    o.proposalEvidenceAuthenticated = true ∧
    o.custodyAuthorized = true ∧
    o.noLeverageOrShort = true ∧
    o.concentrationLimitOk = true ∧
    o.tailLossLimitOk = true ∧
    o.feeTurnoverLimitOk = true := by
  simpa [wealthAdmits, Bool.and_eq_true] using h

theorem committed_wealth_action_has_modeled_limits (o : WealthObligations)
    (hCommit : wealthAdmits o = true) :
    o.noLeverageOrShort = true ∧
    o.concentrationLimitOk = true ∧
    o.tailLossLimitOk = true ∧
    o.feeTurnoverLimitOk = true := by
  have hAll := wealth_admission_implies_every_obligation o hCommit
  exact hAll.2.2.2.2

end ComputeDividend
