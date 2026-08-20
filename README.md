# Alignment Theorem

Can LLM agents be ethically aligned and profit-seeking at the same time? This
project develops two compatible answers for a policy-governed network:

> LLM agents can be trained to follow ethical constraints while pursuing
> profitable useful work. If the ethical path is the most profitable path, the
> network can run more smoothly.

Version 1.1 repairs the original scarcity-driven idea. Version 2 defines the
finite publication and settlement boundary.

## Version 1.1: hyperdeflationary alignment

At epoch `t`, let `M(t)` be a finite purchasing-power multiplier, let
`K(t)` be the ethical reward exposure plus non-ethical forfeiture exposure, and
let `B(t)` be the complete deviation-gain, compliance-cost, and optimizer-error
bound. The repaired Version 1 condition is:

```text
M(t) * K(t) > B(t)
```

For fixed positive `K` and finite `B`, the exact integer threshold is
`floor(B / K) + 1`. If hyperdeflation eventually exceeds every finite bound,
then it eventually crosses this threshold. The relative-growth theorem also
allows `B(t)` to grow when `B(t) / K(t) < M(t)` eventually.

Version 1.1 preserves V1's economic mechanism. It treats hyperdeflation as a
declared scenario, EETF authentication as an external adapter obligation, and
every runtime epoch as finite. It does not prove that Bitcoin purchasing power
diverges or that AGI necessarily causes hyperdeflation.

Read the [Version 1.1 paper](docs/v1-1-hyperdeflationary-alignment.html) or
[download the PDF](docs/Alignment_Theorem_V1_1_Hyperdeflationary.pdf).

## Version 2: finite policy boundary

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

Original Version 1 remains in the repository as historical research. Its old
Lean file does not establish the repaired scarcity threshold. Version 1.1
supplies that separate theorem. See
[V1_TO_V2_CORRECTIONS.md](docs/V1_TO_V2_CORRECTIONS.md) for the reasons Version
2 changed the publication model.

## Version 1.1 artifacts

| Path | Purpose |
| --- | --- |
| `docs/v1-1-hyperdeflationary-alignment.html` | Human-readable Version 1.1 paper |
| `docs/Alignment_Theorem_V1_1_Hyperdeflationary.pdf` | Rendered seven-page paper |
| `proofs/v1_1/AlignmentTheoremV1_1.lean` | Finite, asymptotic, and relative-growth theorems |
| `verification/alignment_v1_1_model.py` | Exact bounded-integer reference model |
| `tau/v1_1/` | Exhaustive 16-row finite semantic gate packet |
| `verification/run_tau_v1_1.py` | Fail-closed exact-binary Tau replay runner |
| `verification/receipts/v1_1_assurance.json` | Source-bound claim and nonclaim receipt |

## Version 2 artifacts

| Path | Purpose |
| --- | --- |
| `paper/v2/alignment_theorem_v2.pdf` | Version 2 paper |
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

Version 1.1 Lean proof and receipt:

```bash
cd proofs/v1_1
lake build
cd ../..
python3 verification/run_lean_v1_1.py --json
python3 -m verification.run_v1_1_assurance --json
```

Current Tau execution, after obtaining the exact reviewed binary identity from
`TOOLCHAINS.md`:

```bash
python3 verification/run_tau_v1_1.py \
  --tau-bin /path/to/tau-lang/build-Release/tau \
  --output verification/receipts/tau_v1_1_fd137e8.json \
  --json

python3 verification/run_tau_v2.py \
  --tau-bin /path/to/tau-lang/build-Release/tau \
  --json
```

The Version 1.1 Tau packet has exhaustive semantic parity tests over four
assumed propositions. It does not authenticate them or create authority.
Its runner checks the exact binary hash and version before execution, requires
byte-exact canonical output, and writes a receipt only after a passing replay.
That pinned-binary replay remains pending and is not claimed.


## Evidence boundary

The checked artifacts establish restricted finite and asymptotic theorems,
exact reserve properties, a fail-closed Version 2 Boolean policy kernel on the
pinned Tau alpha, and non-authoritative reference-model behavior over the
tested domains. They do
not deploy a network, train an LLM, authenticate real-world evidence, prove
coalition bounds, forecast asset prices, or establish production readiness.
