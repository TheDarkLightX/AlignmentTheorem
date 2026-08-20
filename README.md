# Alignment Theorem Version 2

Can LLM agents be ethically aligned and profit-seeking at the same time? This
project gives a finite, testable answer for a policy-governed network:

> LLM agents can be trained to follow ethical constraints while pursuing
> profitable useful work. If the ethical path is the most profitable path, the
> network can run more smoothly.

Version 2 defines ethics relative to an explicit community policy over
observable actions. An LLM or human may propose work. A deterministic Tau gate
controls publication and reward eligibility. A reserve-backed settlement model
prevents rejected or unfunded actions from moving value.

The finite incentive condition is:

```text
compliant reward - noncompliant reward + expected enforcement
  > private deviation gain + extra compliance cost + optimizer error
```

Under the paper's stated bounds, every approximately profit-maximizing action
in the modeled class is policy compliant. This is a conditional,
policy-relative theorem. It does not claim objective moral truth, infallible LLM
internal alignment, authenticated physical facts without an adapter, or safety
outside the modeled action and coalition bounds.

Expected enforcement may be zero. In the reward-only corollary, the funded
reward advantage for compliant work alone exceeds the bounded deviation gain,
compliance cost, and optimizer error.

Version 1 remains in the repository as historical research. Its scarcity
argument, original Tau demos, simulations, and Lean file do not establish the
Version 2 theorem. See [V1_TO_V2_CORRECTIONS.md](docs/V1_TO_V2_CORRECTIONS.md).

## Version 2 artifacts

| Path | Purpose |
| --- | --- |
| `paper/v2/alignment_theorem_v2.pdf` | Version 2 paper |
| `paper/v2/alignment_theorem_v2.tex` | Paper source |
| `proofs/v2/AlignmentTheoremV2.lean` | Finite theorem, gate, and reserve proofs |
| `tau/v2/alignment_policy_gate_v2.tau` | Current-Tau admission kernel |
| `verification/alignment_v2_model.py` | Exact finite reference model |
| `verification/receipts/` | Source- and toolchain-bound replay evidence |
| `tests/` | BVA, mutation-killing, exhaustive, and adversarial tests |
| `TOOLCHAINS.md` | Exact Tau and Lean pins |

## Replay

Python reference and packet tests:

```bash
python3 -m unittest discover -s tests -v
```

Lean 4.33.0 proof:

```bash
cd proofs/v2
lake build
```

Current Tau execution, after building the exact source pin from
`TOOLCHAINS.md`:

```bash
python3 verification/run_tau_v2.py \
  --tau-bin /path/to/tau-lang/build-Release/tau \
  --json
```

Paper:

```bash
cd paper/v2
latexmk -pdf -interaction=nonstopmode -halt-on-error alignment_theorem_v2.tex
```

## Evidence boundary

The checked artifacts establish a finite theorem, exact reserve properties, a
fail-closed Boolean policy kernel on the pinned Tau alpha, and reference-model
behavior over the tested domains. They do not deploy a network, train an LLM,
authenticate real-world evidence, prove coalition bounds, or establish
production readiness.
