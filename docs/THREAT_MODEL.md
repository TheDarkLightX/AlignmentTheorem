# Alignment Theorem Threat Model (Tau Net)

## Version 1.1 Hyperdeflationary Boundary

- **Relative-growth failure**: increasing purchasing power helps only while the
  complete deviation, compliance-cost, and optimizer-error bound remains below
  the scarcity-amplified eligible reward and exclusive-upside exposure. Common scaling
  or faster deviation growth defeats the theorem.
- **Zero exposure**: if eligible reward plus exclusive-upside exposure is
  zero, no scarcity threshold exists. The exact model rejects threshold
  construction in this case.
- **Forged classification**: EETF is authenticated action evidence. An actor or
  LLM cannot supply its own authoritative ethical classification.
- **Unfunded reward**: the finite gate requires a funded reward fact. Production
  settlement still needs reserve custody, replay protection, and an atomic
  value-moving implementation.
- **Exclusion bypass**: an excluded actor who can still claim the same reward or
  scarcity-sensitive entitlement makes the exclusive-upside coefficient zero.
  Shared token appreciation cancels from the choice comparison.
- **Forecast uncertainty**: Bitcoin-style issuance scarcity and AGI abundance
  do not establish the required purchasing-power path. The multiplier and its
  opposing bound remain explicit scenario inputs.

## Aggregation Layer ($\mathcal{A}$)
- **Sybil/credential spam**: require stake-weighted or credentialed submissions; plan to prove that adversarial weight $\leq \lambda$ cannot move $E(t)$ more than $\delta$. Future work: formalize aggregator contract, run zk-attested identities.
- **Collusion / preference utilitarian abuse**: implement median/trimmed-mean fallback when stake concentration exceeds policy bounds; for utilitarian aggregation, enforce normalization constraints and publish proofs (or audits) of any weight scaling so no coalition can inflate its utilities.

## Pointwise Revision Safety
- Tau testnet replays rule edits per formula. We still need Lean guards ensuring certain predicates are immutable (e.g., constitutional invariants, extralogical policy gates).
- Add pre-commit hooks verifying that new rules cannot call unsafe extralogical functions without developer approval.

## Extralogical Primitives
- **Commit-reveal**: require hashing algorithm parity between Tau rule and runtime; add tests verifying reveal window closure.
- **Oracles/MEV**: use `libraries/mev_oracle_safety_v1.tau` monitors; future work includes formalizing freshness checks in Lean and linking them to Tau daemon metrics (see `tau-testnet` repo).

## Economic Stressors
- Extend `analysis/simulations/run_alignment_simulations.py` with tail-risk (shock drops in $E(t)$, partial reversions). Use tau-testnet traces to seed real scarcity trajectories.

## Roadmap
1. Implement stake-based throttling contract for $\mathcal{A}$.
2. Write Lean lemmas marking specific predicate families as immutable under pointwise revision.
3. Add regression tests for commit-reveal and MEV monitors.
4. Publish extended simulation plots + empirical tau-testnet data (see `docs/SIMULATION_RESULTS.md`).

## Compute-Dividend and Household-Agent Boundary

- **Cost shifting disguised as rent:** gross public rent is not distributable
  until authenticated incremental grid/interconnection costs and the public
  reserve are funded. The model does not measure those costs.
- **Post-AGI rent collapse:** a profit share alone cannot guarantee a positive
  floor when accounting profit can be zero. Any minimum capacity/land/permit
  payment and reserve must be explicit, enforceable, and stress-tested.
- **Speculative or stranded load:** contract and escrow adapters must retain
  cost recovery even if the promised large load is delayed or never arrives.
- **Sybil capture:** the current per-identifier share cap is not a beneficial-
  owner cap. Personhood, duplicate detection, household composition, appeals,
  and privacy remain external proof obligations.
- **Political weights:** arbitrary priority weights can reverse poor-first
  allocation even under concave utility. Equal civic weights are the default;
  any alternative requires separately governed justification and tests.
- **Forced concentration:** when all per-household caps bind, the reference
  allocator leaves the balance unspent rather than relaxing a cap.
- **Model-risk laundering:** a plan that passes a finite scenario tail-loss
  limit can still suffer arbitrarily larger unmodeled loss. No return, FIRE,
  suitability, or capital-preservation guarantee follows. The Lean
  protected-floor result is conditional on a true loss bound and does not turn
  this empirical statistic into one.
- **Autonomy/custody:** household consent, custody authorization, market data,
  and proposal evidence are host facts. Tau only evaluates their conjunction;
  it does not establish or execute them.
- **Environmental omission:** water, emissions, land, and reliability limits
  are required pilot guardrails but are not authenticated or quantified by the
  current research packet.
- **Marketing overclaim:** “personal Warren Buffett” is product shorthand only.
  The checked object is a constrained selector with a no-op baseline.
