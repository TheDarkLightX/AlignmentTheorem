import ComputeDividend

/-!
# Data-Center Social Contract Extension

This file strengthens a universal compute-dividend floor into a modeled
household no-harm condition. The formal kernel assumes that losses, direct
benefits, reserves, people, and policy facts are already authenticated. It
proves arithmetic and Boolean consequences only.
-/

namespace ComputeDividend

/-- One household's authenticated project loss and direct project benefit. -/
structure HouseholdImpactAtoms where
  loss : Nat
  directBenefit : Nat
  deriving DecidableEq, Repr

/-- Project loss left after modeled direct project benefits. -/
def uncompensatedDeficit (loss directBenefit : Nat) : Nat :=
  loss - directBenefit

/-- Least candidate transfer: universal base or household no-harm top-up. -/
def minimalNoHarmFloorTransfer
    (floor loss directBenefit : Nat) : Nat :=
  if floor ≤ uncompensatedDeficit loss directBenefit then
    uncompensatedDeficit loss directBenefit
  else
    floor

theorem minimal_no_harm_transfer_meets_floor
    (floor loss directBenefit : Nat) :
    floor ≤ minimalNoHarmFloorTransfer floor loss directBenefit := by
  by_cases h : floor ≤ uncompensatedDeficit loss directBenefit
  · simpa [minimalNoHarmFloorTransfer, h] using h
  · simp [minimalNoHarmFloorTransfer, h]

theorem loss_le_direct_benefit_plus_deficit
    (loss directBenefit : Nat) :
    loss ≤ directBenefit + uncompensatedDeficit loss directBenefit := by
  unfold uncompensatedDeficit
  omega

theorem deficit_le_minimal_no_harm_transfer
    (floor loss directBenefit : Nat) :
    uncompensatedDeficit loss directBenefit ≤
      minimalNoHarmFloorTransfer floor loss directBenefit := by
  by_cases h : floor ≤ uncompensatedDeficit loss directBenefit
  · simp [minimalNoHarmFloorTransfer, h]
  · have hDeficit : uncompensatedDeficit loss directBenefit ≤ floor := by
      omega
    simpa [minimalNoHarmFloorTransfer, h] using hDeficit

theorem minimal_no_harm_transfer_prevents_modeled_harm
    (floor loss directBenefit : Nat) :
    loss ≤ directBenefit +
      minimalNoHarmFloorTransfer floor loss directBenefit := by
  have hLoss := loss_le_direct_benefit_plus_deficit loss directBenefit
  have hTransfer :=
    deficit_le_minimal_no_harm_transfer floor loss directBenefit
  omega

/-- Any transfer satisfying both constraints is at least the proposed one. -/
theorem minimal_no_harm_transfer_is_pointwise_least
    (floor loss directBenefit transfer : Nat)
    (hFloor : floor ≤ transfer)
    (hNoHarm : loss ≤ directBenefit + transfer) :
    minimalNoHarmFloorTransfer floor loss directBenefit ≤ transfer := by
  by_cases h : floor ≤ uncompensatedDeficit loss directBenefit
  · simp [minimalNoHarmFloorTransfer, h]
    unfold uncompensatedDeficit
    omega
  · simpa [minimalNoHarmFloorTransfer, h] using hFloor

/-- Universal base plus household-specific top-up identity. -/
theorem minimal_no_harm_transfer_base_plus_topup
    (floor loss directBenefit : Nat) :
    minimalNoHarmFloorTransfer floor loss directBenefit =
      floor + (uncompensatedDeficit loss directBenefit - floor) := by
  by_cases h : floor ≤ uncompensatedDeficit loss directBenefit
  · simp [minimalNoHarmFloorTransfer, h, Nat.add_sub_of_le h]
  · have hDeficit : uncompensatedDeficit loss directBenefit ≤ floor := by
      omega
    simp [minimalNoHarmFloorTransfer, h, Nat.sub_eq_zero_of_le hDeficit]

/-- Pointwise minimal transfers for a finite household list. -/
def requiredNoHarmTransfers
    (floor : Nat) : List HouseholdImpactAtoms → List Nat
  | [] => []
  | impact :: impacts =>
      minimalNoHarmFloorTransfer floor impact.loss impact.directBenefit ::
        requiredNoHarmTransfers floor impacts

/-- Every paired transfer satisfies the universal base and modeled no-harm. -/
def HasFloorAndNoHarm
    (floor : Nat) : List HouseholdImpactAtoms → List Nat → Prop
  | [], [] => True
  | impact :: impacts, transfer :: transfers =>
      floor ≤ transfer ∧
      impact.loss ≤ impact.directBenefit + transfer ∧
      HasFloorAndNoHarm floor impacts transfers
  | _, _ => False

/-- Aggregate least cost of the hybrid universal-base/top-up schedule. -/
def minimalHybridCost
    (floor : Nat) (impacts : List HouseholdImpactAtoms) : Nat :=
  (requiredNoHarmTransfers floor impacts).sum

theorem required_no_harm_transfers_are_admissible
    (floor : Nat) (impacts : List HouseholdImpactAtoms) :
    HasFloorAndNoHarm floor impacts (requiredNoHarmTransfers floor impacts) := by
  induction impacts with
  | nil =>
      simp [requiredNoHarmTransfers, HasFloorAndNoHarm]
  | cons impact rest ih =>
      simp only [requiredNoHarmTransfers, HasFloorAndNoHarm]
      exact ⟨
        minimal_no_harm_transfer_meets_floor
          floor impact.loss impact.directBenefit,
        minimal_no_harm_transfer_prevents_modeled_harm
          floor impact.loss impact.directBenefit,
        ih
      ⟩

/-- Any admissible finite transfer vector costs at least the hybrid schedule. -/
theorem admissible_transfer_cost_lower_bound
    (floor : Nat) (impacts : List HouseholdImpactAtoms)
    (transfers : List Nat)
    (h : HasFloorAndNoHarm floor impacts transfers) :
    minimalHybridCost floor impacts ≤ transfers.sum := by
  induction impacts generalizing transfers with
  | nil =>
      cases transfers with
      | nil => simp [minimalHybridCost, requiredNoHarmTransfers]
      | cons transfer tail => simp [HasFloorAndNoHarm] at h
  | cons impact rest ih =>
      cases transfers with
      | nil => simp [HasFloorAndNoHarm] at h
      | cons transfer tail =>
          simp only [HasFloorAndNoHarm] at h
          have hHead := minimal_no_harm_transfer_is_pointwise_least
            floor impact.loss impact.directBenefit transfer h.1 h.2.1
          have hTail := ih tail h.2.2
          simpa [minimalHybridCost, requiredNoHarmTransfers] using
            Nat.add_le_add hHead hTail

/-- Existence of any admissible schedule within the cash reserve. -/
def HybridCashFeasible
    (floor : Nat) (impacts : List HouseholdImpactAtoms) (budget : Nat) : Prop :=
  ∃ transfers,
    HasFloorAndNoHarm floor impacts transfers ∧ transfers.sum ≤ budget

/-- Exact feasibility threshold for universal base plus no-harm top-ups. -/
theorem hybrid_cash_feasible_iff_minimal_cost_funded
    (floor : Nat) (impacts : List HouseholdImpactAtoms) (budget : Nat) :
    HybridCashFeasible floor impacts budget ↔
      minimalHybridCost floor impacts ≤ budget := by
  constructor
  · rintro ⟨transfers, hAdmissible, hBudget⟩
    have hCost := admissible_transfer_cost_lower_bound
      floor impacts transfers hAdmissible
    exact Nat.le_trans hCost hBudget
  · intro hBudget
    refine ⟨requiredNoHarmTransfers floor impacts, ?_, ?_⟩
    · exact required_no_harm_transfers_are_admissible floor impacts
    · simpa [minimalHybridCost] using hBudget

/-- Gross public rent after senior claims. -/
def distributableProjectRent (grossRent seniorClaims : Nat) : Nat :=
  grossRent - seniorClaims

theorem gross_rent_threshold_supports_hybrid_no_harm_cost
    (grossRent seniorClaims floor : Nat)
    (impacts : List HouseholdImpactAtoms)
    (hThreshold :
      seniorClaims + minimalHybridCost floor impacts ≤ grossRent) :
    minimalHybridCost floor impacts ≤
      distributableProjectRent grossRent seniorClaims := by
  simp [distributableProjectRent]
  omega

/-- Modeled post-project resources after benefit, transfer, and loss. -/
def postProjectResources
    (baseline directBenefit transfer loss : Nat) : Nat :=
  baseline + directBenefit + transfer - loss

theorem modeled_no_harm_preserves_household_baseline
    (baseline directBenefit transfer loss : Nat)
    (hNoHarm : loss ≤ directBenefit + transfer) :
    baseline ≤ postProjectResources baseline directBenefit transfer loss := by
  simp [postProjectResources]
  omega

/-- Concavity is unnecessary for this no-harm implication; monotonicity suffices. -/
theorem monotone_utility_weakly_improves_under_modeled_no_harm
    (utility : Nat → Nat)
    (hMonotone : ∀ x y, x ≤ y → utility x ≤ utility y)
    (baseline directBenefit transfer loss : Nat)
    (hNoHarm : loss ≤ directBenefit + transfer) :
    utility baseline ≤
      utility (postProjectResources baseline directBenefit transfer loss) := by
  exact hMonotone baseline
    (postProjectResources baseline directBenefit transfer loss)
    (modeled_no_harm_preserves_household_baseline
      baseline directBenefit transfer loss hNoHarm)

/-- Cash and compute remain separate unless an external conversion floor exists. -/
def JointCashComputeFeasible
    (cashRequired cashAvailable householdCount computeFloor computeAvailable : Nat) :
    Prop :=
  cashRequired ≤ cashAvailable ∧ householdCount * computeFloor ≤ computeAvailable

theorem joint_cash_compute_feasible_iff_separate_thresholds
    (cashRequired cashAvailable householdCount computeFloor computeAvailable : Nat) :
    JointCashComputeFeasible cashRequired cashAvailable householdCount
      computeFloor computeAvailable ↔
    cashRequired ≤ cashAvailable ∧
      householdCount * computeFloor ≤ computeAvailable := by
  rfl

/-- Authenticated facts required before a data-center project is admitted. -/
structure DataCenterObligations where
  policyRootOk : Bool
  projectIdentityAuthenticated : Bool
  localConsentAuthenticated : Bool
  incrementalEnergyCostsReserved : Bool
  reliabilityCurtailmentPlanOk : Bool
  waterEmissionsLandLimitsOk : Bool
  decommissioningBondFunded : Bool
  noHarmCompensationFunded : Bool
  universalDividendComputeFloorFunded : Bool
  publicAuditReceiptCurrent : Bool
  deriving DecidableEq, Repr

/-- Complete fail-closed conjunction mirrored by the Tau research packet. -/
def dataCenterAdmits (o : DataCenterObligations) : Bool :=
  o.policyRootOk &&
    (o.projectIdentityAuthenticated &&
      (o.localConsentAuthenticated &&
        (o.incrementalEnergyCostsReserved &&
          (o.reliabilityCurtailmentPlanOk &&
            (o.waterEmissionsLandLimitsOk &&
              (o.decommissioningBondFunded &&
                (o.noHarmCompensationFunded &&
                  (o.universalDividendComputeFloorFunded &&
                    o.publicAuditReceiptCurrent))))))))

theorem data_center_admission_implies_every_obligation
    (o : DataCenterObligations) (h : dataCenterAdmits o = true) :
    o.policyRootOk = true ∧
    o.projectIdentityAuthenticated = true ∧
    o.localConsentAuthenticated = true ∧
    o.incrementalEnergyCostsReserved = true ∧
    o.reliabilityCurtailmentPlanOk = true ∧
    o.waterEmissionsLandLimitsOk = true ∧
    o.decommissioningBondFunded = true ∧
    o.noHarmCompensationFunded = true ∧
    o.universalDividendComputeFloorFunded = true ∧
    o.publicAuditReceiptCurrent = true := by
  simpa [dataCenterAdmits, Bool.and_eq_true] using h

end ComputeDividend
