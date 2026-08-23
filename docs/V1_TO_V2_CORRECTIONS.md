# Alignment Theorem V1, V1.1, and V2

The three versions serve different cases. Version 1 is the concrete EETF/VCC
mechanism in which eligibility controls direct rewards and access to
scarcity-amplified upside. Version 1.1 supplies an abstract relative-growth
theorem. Version 2 supplies a finite policy, publication, and settlement
boundary. Version numbers do not define a quality ordering.

This document distinguishes demonstrated defects from modeling limitations and
deliberate scope changes. A version is changed only where a counterexample,
checker failure, or claim/evidence mismatch establishes a defect.

## Profile selection

| Version | Use it when | Operative condition |
| --- | --- | --- |
| V1 | Tau-authenticated EETF eligibility can control direct rewards and a genuinely exclusive VCC scarcity entitlement. | `G(t) < M(t) * [R(t) + L(t)]`, where `L` is upside unavailable to the excluded branch. |
| V1.1 | The V1 comparison needs arbitrary costs, optimizer error, or time-varying relative-growth bounds. | `B(t) < M(t) * K(t)` with `K(t) > 0`. |
| V2 | The protocol needs a finite policy-relative admission and reserve-backed settlement contract. | `R_c - R_n + enforcement > G + C + epsilon`. |

V2 can wrap either V1 or V1.1 as the outer publication and settlement
boundary.

## Findings and disposition

| V1 finding | Classification | Disposition |
| --- | --- | --- |
| The paper and simulation contain a direct ethical reward, an EETF-scaled lost-upside term, VCC scarcity, and a bounded misaligned gain `g_max`. | Valid V1 mechanism. | Retained. In normalized form, the eligible value is `M(R+L)` and the excluded value is `G`. The standalone Lean proof shows the original negative-opportunity-cost placement has the same ordering. |
| The paper called foregone upside a “penalty.” In its utility comparison this denotes value missed through exclusion, although the word can be misread as a tax or balance debit. | Interpretation and implementation boundary; no algebraic correction. | V1 keeps the same ordering and represents `L` as an entitlement accessible only to the eligible branch. Exclusion moves no value from the excluded actor. Settlement code must never implement this term as confiscation. |
| The printed indifference formula used a positive tier below the EETF eligibility threshold and omitted the bounded deviation gain used by the simulation. Its common scarcity factor therefore canceled. | Mathematical defect in the threshold derivation. | The corrected concrete V1 condition is `G < M(R+L)`. For integer values with `R+L>0`, the least multiplier is `floor(G/(R+L))+1`. When `G=0`, every positive multiplier suffices. |
| Scarcity upside was sometimes described as if every token holder received it equally. | Missing exclusivity premise. | Upside common to both branches cancels. V1 requires an eligibility-controlled reward, claim, capability, or access right whose value scales with scarcity and which the excluded branch cannot obtain. |
| “Ethical” was an account EETF threshold and the modeled agent could choose its EETF directly. | Modeling limitation. | Retained only as a declared V1 abstraction. V2 classifies observable actions under a versioned policy and authenticated evidence. |
| Real-valued supply approached zero under assumed infinite divisibility. | External premise and runtime mismatch. | V1/V1.1 may use it as a scenario. Runtime settlement uses bounded integer atoms, explicit scale, reserve conservation, and reject-without-effect behavior. |
| The paper used a time-varying rate `r(t)` while its Lean file proved a constant-rate geometric path. | Proof/statement mismatch. | The current V1 theorem consumes an explicit finite scarcity value or an abstract unbounded-scarcity premise. A variable-rate supply theorem is required before claiming that a particular VCC schedule establishes that premise. |
| EETF was described as an ethics oracle. | Claim-scope defect. | EETF is treated as a community-selected policy output. No version proves objective moral truth. |
| Preference aggregation lacked a complete identity, weighting, missing-data, manipulation, and revision model. | Incomplete external module. | Any theorem using aggregation must state the participant domain, identity assumptions, rule, adversarial weight bound, and update constitution. |
| The Tau reward demo read `is_ethical` while issuing the reward unconditionally. | Executable defect. | The legacy demo remains historical. The current V1 packet requires authenticated EETF, scarcity, reward funding, enforceable exclusion, and the strict margin; it accepts only the all-true row. V1.1 and V2 retain separate gates. |
| Tau declarations and “current” verification claims drifted from the public interpreter. | Evidence defect. | A source-pinned `9b191af...` local candidate replayed V1, V1.1, V2, and flywheel packets byte-for-byte. Earlier exact receipts remain historical snapshots. |
| The V1 Lean source lacked a project/toolchain lock, does not build against the available modern toolchain, and describes the lost-upside limit as quadratic although its formula is linear in scarcity. | Replay and proof defect. | `proofs/v1/` is a standalone Lean 4.33.0 project for the reconstructed exclusion theorem, exact threshold, EETF tiers, normalization, and unbounded-scarcity implication. The historical source remains unchanged for provenance. |
| Simulations were described as proving convergence. | Evidence-category defect. | Tests, bounded campaigns, Tau traces, and Lean theorems are labeled separately. Simulations remain exploratory evidence. |
| The paper generalized from its payoff model to all rational agents and objective ethics. | Claim-scope defect. | V1 covers exact maximizers over its declared eligible and excluded alternatives. V1.1 and V2 state their own finite or epsilon-optimal scopes. |

## Human meaning retained

The human idea remains simple:

> LLM agents on the network can be trained to be ethically aligned and
> profit-seeking, automating useful work while maintaining alignment. If the
> ethical path is the most profitable path, the network can run more smoothly.

Version 2 gives that idea an enforceable boundary. Training can teach agents to
find profitable policy-compliant work efficiently. The network still checks
every proposed action. A model is a proposal engine and never becomes the
authority that decides whether its own behavior is ethical.

## Formal Version 1 claim

At a finite decision epoch, let `M` be the scarcity multiplier, `R` the funded
direct-reward coefficient available only to the eligible branch, `L` the
coefficient of other scarcity upside protected by eligibility, and `G` the
excluded branch's bounded deviation gain. Normalize the common baseline away:

```text
U_eligible = M * (R + L)
U_excluded = G
```

The historical placement
`U_eligible = M*R`, `U_excluded = G - M*L` has the same ordering because adding
`M*L` to both alternatives cannot change the maximizer. This is the precise
sense in which `M*L` is opportunity cost. It is never a ledger debit.

If `G < M*(R+L)`, every exact maximizer over the declared alternatives selects
the eligible branch. If an unbounded scarcity sequence is assumed and `R+L`
is a fixed positive coefficient while `G` is fixed and finite, the strict
margin eventually holds. If excluded actors can obtain `L`, if `L` is common
market appreciation, or if `G` grows as fast or faster, that conclusion does
not follow.

## Formal Version 2 claim

For a policy-compliant action, let `R_c` be its funded reward. For a
noncompliant action, let `R_n` be any reward it can still receive, `pL` the
conservatively estimated expected enforcement amount, `G` the maximum private
deviation gain, `C` the maximum extra cost of compliance, and `epsilon` the
agent's optimizer error. Version 2 assumes:

```text
R_c - R_n + pL > G + C + epsilon.
```

Under that strict finite margin, every epsilon-optimal choice in the restricted
model is policy compliant. If the inequality is equal rather than strict, the
conclusion does not follow. If `G` is unbounded, the theorem does not apply.

For actions the network can block directly, a stronger operational rule holds:

```text
Committed(action)
  -> authenticated evidence
  -> active policy accepts action
  -> reward is funded
  -> nonce and task nullifier are fresh.
```

## Nonclaims

Version 2 does not prove:

- objective moral truth;
- that community consensus is morally correct;
- honesty of unauthenticated sensors, oracles, or host flags;
- internal alignment or consciousness of an LLM;
- absence of reward hacking outside the modeled interface;
- incentive compatibility when private deviation gains exceed the stated bound;
- production deployment on Tau Net; or
- a universal theorem for every agent, society, governance rule, or future.
