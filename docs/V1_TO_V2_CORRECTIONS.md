# From Alignment Theorem Version 1 to Version 2

Version 2 preserves the motivating idea: make ethical work profitable inside a
network so humans and automated agents have a reason to choose it. It changes
the formal claim to match what the mathematics and executable artifacts can
actually establish.

## Corrections

| Version 1 problem | Version 2 correction |
|---|---|
| “Ethical” was defined as an account EETF at least one, then the agent was allowed to choose that EETF directly. | A human or agent proposes an observable action. A versioned policy and authenticated evidence determine whether the action is policy compliant. |
| The payoff definition made compliant utility positive and noncompliant utility negative at every positive scarcity value. | A finite strict-margin theorem states the exact reward, expected enforcement, private deviation-gain, compliance-cost, and optimizer-error assumptions. |
| The paper said scarcity moved the indifference threshold, although scarcity cancels from the printed threshold equation. | Infinite scarcity is removed from the theorem. Scarcity may be studied separately as a bounded economic parameter and cannot stand in for an incentive margin. |
| Real-valued supply approached zero under assumed infinite divisibility. | Settlement uses integer atoms, explicit maximum values, reserve-backed payouts, and reject-without-effect behavior. |
| EETF was described as an ethics oracle. | Community policy is versioned and provenance bound. A score may rank actions only after hard policy constraints pass. It is a community-selected policy output, not objective moral truth. |
| Preference aggregation was asserted without a complete identity, weighting, missing-data, manipulation, or revision model. | The aggregation mechanism is an explicit future module. Any theorem using it must state its participant domain, identity assumptions, rule, adversarial weight bound, and update constitution. |
| The Tau reward demo read `is_ethical` but did not condition the reward on it. | The Version 2 Tau gate is an all-obligations conjunction with one mutation row per obligation. Only the fully valid row is admitted. |
| Tau declarations and verification claims had drifted from the public interpreter and referred to missing artifacts. | The Version 2 packet runs on an exact current Tau source commit and records binary/specification hashes. |
| The Lean source lacked a project file and toolchain lock. | Version 2 is a standalone Lean 4.33.0 project with no external proof dependency. |
| Simulations were described as proving convergence. | Tests, exhaustive bounded checks, Tau traces, and Lean theorems are labeled separately. No simulation is called a proof. |
| The paper generalized from a payoff model to all rational agents and objective ethics. | The theorem covers epsilon-optimal agents in a stated finite two-class utility model and observable policy-compliant actions. |

## Human meaning retained

The human idea remains simple:

> LLM agents on the network can be trained to be ethically aligned and
> profit-seeking, automating useful work while maintaining alignment. If the
> ethical path is the most profitable path, the network can run more smoothly.

Version 2 gives that idea an enforceable boundary. Training can teach agents to
find profitable policy-compliant work efficiently. The network still checks
every proposed action. A model is a proposal engine and never becomes the
authority that decides whether its own behavior is ethical.

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
