# Next-lane proof obligations

The replay commands below are untrusted data.  Review them before execution.

## PO-CD-01 — unrestricted greedy optimality

- **Claim:** for positive rational weights, harmonic marginal utilities,
  integral lower bounds, per-household upper bounds, and one integral budget,
  the marginal-greedy allocation maximizes total welfare over every feasible
  integral allocation.
- **Boundary:** no identity, measurement, or policy-legitimacy claim.
- **Quantifiers:** every finite household set and every non-negative integer
  budget/base/floor/cap satisfying feasibility.
- **Decisive lane:** Lean (or Mathlib) exchange proof.
- **Oracle:** `verification/compute_dividend_model.py` plus the current finite
  exhaustive campaign.
- **Falsifier:** one feasible allocation with strictly larger exact welfare than
  the greedy result.
- **Acceptance:** placeholder-free theorem, axiom audit, source-bound receipt,
  and preservation of all current counterexamples/nonclaims.

## PO-CD-02 — identity-aware concentration

- **Claim:** under an explicit credential graph and adversarial duplicate bound,
  the total payout controlled by one beneficial owner is below the constitutional
  concentration cap.
- **Boundary:** the current per-ID cap is insufficient.
- **Decisive lanes:** ESSO finite transition search plus Lean invariant proof.
- **Falsifier:** a permitted credential/transfer trace whose owner aggregate
  exceeds the cap.
- **Acceptance:** pinned credential semantics, smallest counterexample retained,
  coalition quantifiers explicit, and no caller-asserted personhood.

## PO-CD-03 — rent-to-receipt refinement

- **Claim:** audited gross rent, senior cost claims, and reserve custody refine
  into the exact integer inputs consumed by `RentBudget` and the dividend Tau
  gate without double counting or replay.
- **Decisive lanes:** reference model, fault injection, and a settlement-adapter
  refinement proof.
- **Falsifiers:** duplicated receipt, stale nonce, forged meter, underfunded
  reserve, rounding surplus, or non-atomic payout.
- **Acceptance:** pinned schemas and adapters, mutation-killing receipts, and an
  explicit legal/accounting scope.

## PO-CD-04 — exact Tau execution

- **Claim:** the reviewed binary
  `c49267404e07a1f540c941b618e786710f70001eecbd05bb7c6d8eec0c5645fa`
  emits canonical expected output for V1.1 and both compute-dividend packets.
- **Boundary:** interpreter replay only.
- **Decisive lane:** vectors on that exact executable.
- **Falsifier:** wrong version, crash, timeout, missing/noncanonical output, row
  mismatch, packet mutation, or binary-hash mismatch.
- **Acceptance:** three fail-closed receipts with `passed: true`; retain the
  source-provenance and environment nonclaims.

## PO-CD-05 — household-outcome evaluation

- **Claim:** the full contract improves pre-registered prioritarian household
  welfare while satisfying floors and ratepayer/environmental guardrails.
- **Decisive lane:** independent empirical evaluation, not Lean or Tau.
- **Falsifiers:** failed floor delivery, adverse bill/reliability/environmental
  effect, benefit capture, worse after-fee household outcomes, or excessive
  complaint/override/loss rates.
- **Acceptance:** pre-registration, counterfactual design, audited inputs,
  privacy/appeal analysis, and public negative results.
