# Alignment Theorem

Can LLM agents be ethically aligned and profit-seeking at the same time? This
project develops three compatible theorem profiles for a policy-governed
network:

> LLM agents can be trained to follow ethical constraints while pursuing
> profitable useful work. If the ethical path is the most profitable path, the
> network can run more smoothly.

Version 1 is the concrete EETF/VCC scarcity-upside exclusion mechanism.
Version 1.1 abstracts that mechanism into a conditional relative-growth
theorem. Version 2 defines the finite publication and settlement boundary. A
later version does not replace an earlier profile when their premises and use
cases differ.

## Version 1: EETF-gated scarcity-upside exclusion

Version 1 aggregates ethical models into a network EETF, assigns account or
action EETF tiers, and uses VCC scarcity to amplify value available only to the
eligible branch. Exclusion is opportunity cost. It does not impose a tax, fine,
burn, or balance debit on the excluded actor.

Let `R(t)` be funded direct-reward exposure, `L(t)` be scarcity upside whose
access is enforceably limited to the eligible branch, and `G(t)` be the complete
bounded deviation gain in V1's exact-optimizer model. The finite condition is:

```text
M(t) * [R(t) + L(t)] > G(t)
```

The original paper placed foregone upside as a negative "penalty" on the
excluded branch. In utility language that is an opportunity-cost encoding, not
a tax. Adding the same foregone amount to both alternatives gives the
equivalent no-debit expression above and preserves the choice ordering.
For positive `R + L`, the least strict integer multiplier is
`floor(G / (R + L)) + 1`. When `G = 0`, every positive multiplier is enough.

The paper's EETF tiers, direct reward, VCC scarcity path, exclusion term, and
bounded-deviation simulation are retained. Its printed indifference formula,
ambiguous implementation wording, universal-agent scope, objective-ethics
language, and runtime claims require the clarifications and corrections recorded
in the claim-boundary note.
The repository now contains a standalone Lean project, an exact integer model,
and a current-Tau 128-row admission packet for V1.

## Version 1.1: hyperdeflationary alignment

At epoch `t`, let `M(t)` be a finite purchasing-power multiplier, let
`K(t)` be the eligible reward exposure plus enforceably exclusive upside, and
let `B(t)` be the complete deviation-gain, compliance-cost, and optimizer-error
bound. The Version 1.1 condition is:

```text
M(t) * K(t) > B(t)
```

For fixed positive `K` and finite `B`, the exact integer threshold is
`floor(B / K) + 1`. If hyperdeflation eventually exceeds every finite bound,
then it eventually crosses this threshold. The relative-growth theorem also
allows `B(t)` to grow when `B(t) / K(t) < M(t)` eventually.

Version 1.1 generalizes V1's economic mechanism. It treats hyperdeflation as a
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

The original Version 1 paper remains recoverable as historical research. Its
old Lean file is not repository-replayable and its printed threshold derivation
does not follow from its own piecewise tier function. The reconstructed
opportunity-cost theorem is checked under `proofs/v1/`. Version 1.1 supplies an
abstract theorem with costs, optimizer error, and relative-growth cases. See
[V1_TO_V2_CORRECTIONS.md](docs/V1_TO_V2_CORRECTIONS.md) for the defect/scope
classification.

## Version 1 artifacts

| Path | Purpose |
| --- | --- |
| `proofs/v1/AlignmentTheoremV1.lean` | EETF tiers, opportunity-cost normalization, exact threshold and choice, unbounded-scarcity result, and common-upside boundary |
| `verification/run_lean_v1.py` | Placeholder-rejecting, axiom-audited, source-bound Lean replay |
| `verification/alignment_v1_model.py` | Exact bounded-integer EETF/exclusion reference model |
| `tau/v1/` | Exhaustive 128-row current-Tau eligibility packet |
| `tests/test_alignment_v1_model.py` | EETF BVA, normalization, exact threshold, overflow rejection, and common-upside boundary |
| `docs/alignment-theorem-v1-archive-notice.html` | Original-paper claim and provenance boundary |
| `docs/Alignment_Theorem_V1_Original_2025.pdf` | Frozen uncorrected 16-page academic paper from `a28695f` |
| `research/v1/ACADEMIC_PAPER_AUDIT.md` | Source-frozen reconstruction of the complete V1 mechanism and demonstrated corrections |

## Version 1.1 artifacts

| Path | Purpose |
| --- | --- |
| `docs/v1-1-hyperdeflationary-alignment.html` | Human-readable Version 1.1 paper |
| `docs/Alignment_Theorem_V1_1_Hyperdeflationary.pdf` | Rendered seven-page paper |
| `proofs/v1_1/AlignmentTheoremV1_1.lean` | Finite, asymptotic, and relative-growth theorems |
| `verification/alignment_v1_1_model.py` | Exact bounded-integer reference model |
| `tau/v1_1/` | Exhaustive 16-row finite semantic gate packet |
| `verification/capture_tau_v1_1_candidate.py` | Non-authoritative Runpod build-manifest capture |
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

## Compute dividend + household wealth-agent research

The current research packet asks whether a full-cost-recovery data-center rent
can fund a universal household floor, a prioritarian capped surplus allocation,
and a constrained personal wealth copilot.  The formal result is deliberately
narrow: exact rent/reserve conservation, a sufficient gross-rent threshold for
the floor, floor feasibility, discrete-concave transfer behavior, and
verifier-conditioned admission gates.  A true one-period loss bound also
preserves a declared protected floor, but the finite scenario gate does not
prove that premise.  The packet does not guarantee investment
returns, FIRE, generational wealth, identity integrity, real-world welfare, or
legal compliance.

The exact Python campaign checked 10,836 allocation instances against an
independent exhaustive oracle with zero mismatches.  Two complete 256-row Tau
semantic packets each accept only the all-true row.  Exact interpreter replay
of these packets—and the V1.1 packet—still requires the reviewed Tau executable;
the pending plan binds the current V1.1 packet, source/parser expectations,
binary identity, checker, generator, and output without pretending it is an
execution receipt.

Separately, a clean build at the expected source/parser pins produced candidate
`b2699306...` and natively matched the canonical V1.1 and both 256-row research
outputs.  Its binary hash and exact reported version differ from the reviewed
identity, and it used non-hermetic build-tree libraries, so the reviewed replay
correctly remains pending.

Read the [research note](research/compute_dividend/README.md),
[claim boundary](research/compute_dividend/CLAIM_BOUNDARY.md), and
[Tau replay handoff](research/compute_dividend/TAU_REPLAY.md).

## Intelligence-to-hyperdeflation flywheel research

The follow-up packet separates a hypothetical capability-doubling law from the
causal links it would need to affect the theorem.  Its normalized essential-
basket map is `P(t) = 1 - a*rho + a*rho/I(t)^eta`, with purchasing power
`M(t)=1/P(t)`.  If automation or pass-through is incomplete, the price floor is
positive and `M` is bounded even when capability doubles forever.  The positive
Lean theorem therefore requires explicit reward/deviation bounds and a strict
crossing witness; intelligence growth alone is formally insufficient.

The exact campaign tests direct doubling, compute-power scaling, logistic
saturation, conditional DAC reinvestment, partial pass-through, and rebound.
It checks 544 exact bridge cases, proves the key conditional and negative
results in Lean, and binds the same nine-fact predicate to a complete 512-row
Tau packet. The source-pinned current-Tau candidate at `9b191af...` matched
that packet. A direct native `o5` ABI probe at Tau Testnet revision
`9f9240...` also matched all 12
all-true, single-fault, missing-input, and sender-isolation cases.

That native result is not a node deployment, authenticated oracle path,
consensus-finality test, or production claim.  Custom `i17..i25` values are
submitter-supplied claims in the tested alpha.  Replay on the reviewed
`c4926740...` Tau binary remains pending; the strict runner rejects the local
candidate before execution.

Read the [GitHub Pages explainer](docs/intelligence-hyperdeflation-flywheel.html),
[mathematical model](research/intelligence_flywheel/MATHEMATICAL_MODEL.md),
[Tau Net replay boundary](research/intelligence_flywheel/TAU_NET_REPLAY.md), and
[claim boundary](research/intelligence_flywheel/CLAIM_BOUNDARY.md).

## Current Tau Language and Tau Net mapping

The [current integration matrix](docs/CURRENT_TAU_NET_INTEGRATION.md) maps V1,
V1.1, and V2 to the Tau Language `9b191af...` and Tau Testnet `9f9240...`
snapshots. A source-pinned local candidate replayed the 128-row V1, 16-row V1.1,
128-row V2, and 512-row flywheel packets byte-for-byte. This is executable
language evidence. A sender-scoped three-profile `o5` router also matched all 27
native-ABI cases: each profile's all-true row, every single-false mutation,
unknown-profile, absent-input, and other-sender controls. Its profile and fact
streams remain transaction-supplied claims. Consensus-authenticated economic
facts, enforceable exclusive entitlements, mounted settlement, and public-node
deployment remain open authority layers.

## Replay

Python reference and packet tests:

```bash
python3 -m unittest discover -s tests -v
```

Compute-dividend reference campaign:

```bash
python3 -m verification.run_compute_dividend_campaign --json
cd proofs/compute_dividend
lake build
```

Intelligence-flywheel reference and Lean campaigns:

```bash
python3 -m verification.run_intelligence_flywheel_campaign --json
python3 verification/run_lean_intelligence_flywheel.py --json
```

Lean 4.33.0 proof:

```bash
cd proofs/v2
lake build
```

Version 1 Lean proof:

```bash
cd proofs/v1
lake build
lake env lean AxiomAudit.lean
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
python3 verification/capture_tau_v1_1_candidate.py \
  --tau-source /path/to/tau-lang \
  --tau-bin /path/to/tau-lang/build-Release/tau \
  --runpod-image 'registry/image@sha256:<64-hex-digest>' \
  --build-command 'TAU_BUILD_JOBS=1 ./dev release' \
  --output /path/to/export/tau_v1_1_candidate.json \
  --json

python3 verification/run_tau_v1_1.py \
  --tau-bin /path/to/tau-lang/build-Release/tau \
  --output verification/receipts/tau_v1_1_fd137e8.json \
  --json

python3 verification/run_tau_v2.py \
  --tau-bin /path/to/tau-lang/build-Release/tau \
  --json
```

The Version 1 packet exhausts seven assumed propositions; the Version 1.1
packet exhausts four. Neither packet authenticates those propositions or
creates authority. The reviewed-binary runner checks the exact binary hash and version before execution, requires
byte-exact canonical output, and writes a receipt only after a passing replay.
The runner records that source-to-binary provenance and the host execution
environment are not independently attested by this replay. The pinned-binary
replay remains pending and is not claimed.  Its exact, non-executed handoff is
recorded at
`verification/pending/tau_v1_1_fd137e8_replay_plan.json`; a plan is not a
receipt.

The atom-by-atom allocator is reference-only and rejects budgets above 10,000
atoms; a scalable implementation needs a separate refinement proof.


## Evidence boundary

The checked artifacts establish restricted finite and asymptotic theorems,
exact reserve properties, a fail-closed Version 2 Boolean policy kernel on the
pinned Tau alpha, and non-authoritative reference-model behavior over the
tested domains. They do
not deploy a network, train an LLM, authenticate real-world evidence, prove
coalition bounds, forecast asset prices, or establish production readiness.
