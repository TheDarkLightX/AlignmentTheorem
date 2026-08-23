# Reproducible Toolchain Pins

Version 1, Version 1.1, and Version 2 evidence is tied to exact source identities and to
binary identities wherever interpreter execution is claimed. A later tool
version must generate a new receipt rather than
inherit these results.

## Version 1

### Lean and exact model

- Lean release: `v4.33.0`
- Toolchain file: `proofs/v1/lean-toolchain`
- Standard library only

Replay:

```bash
python3 verification/run_lean_v1.py \
  --output verification/receipts/lean_v1_v4.33.0.json \
  --json
```

The project checks the original EETF tier boundaries, the equivalence between
the historical negative-opportunity-cost placement and the no-debit exclusion
normalization, the finite strict choice theorem, exact least integer threshold,
zero-deviation case, unbounded-scarcity implication, and the fact that scarcity
upside common to both alternatives cancels. `verification/alignment_v1_model.py`
provides the exact bounded-integer replay with the paper's thousandths EETF
scale.

### Tau packet

`tau/v1/` contains all 128 Boolean rows for seven host-derived obligations:
policy root, network EETF, candidate EETF, scarcity snapshot, reward funding,
enforceable exclusive upside, and the strict V1 margin. The packet applies no
punitive debit and accepts only the all-true row.

## Version 1.1

### Lean

- Lean release: `v4.33.0`
- Toolchain file: `proofs/v1_1/lean-toolchain`
- Standard library only

Replay:

```bash
python3 verification/run_lean_v1_1.py \
  --output verification/receipts/lean_v1_1_v4.33.0.json \
  --json
```

The receipt binds the paper utility bridge, exact least threshold, finite
choice, asymptotic bounded-deviation, and relative-growth theorem sources. It
also records the exact expected standard axiom dependencies.

### Claim-scoped assurance

```bash
python3 -m verification.run_v1_1_assurance \
  --output verification/receipts/v1_1_assurance.json \
  --json
```

This receipt binds the V1.1 proof, model, semantic Tau packet, replay runner,
tests, public pages, HTML paper, and rendered PDF. It records the Python/Tau
surfaces as reference-only. The stored receipt predates the current source
candidate replay and must be regenerated before it describes the current tree.
After generation, validate the stored receipt against the bound files:

```bash
python3 -m unittest tests.test_v1_1_assurance_receipt -v
```

### Tau

`tau/v1_1/` uses the same current declaration shape as the Version 2 packet and
contains all 16 Boolean rows for its four semantic facts. Static semantic parity
is tested. `verification/run_tau_v1_1.py` snapshots the candidate executable and
packet, checks the exact reviewed binary hash before execution, requires the
exact version string and byte-canonical 16-row output, and writes a receipt only
after every check passes.

Replay on the faster machine:

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
```

The candidate-manifest command does not execute Tau. It records source state,
submodules, the candidate binary hash, declared image/build identities, platform
shape, and tool versions. `capture_complete` means those fields were collected.
Every candidate manifest fixes `promotion_eligible` and `replay_executed` to
false. Keep the manifest outside `verification/receipts/` until review.

The accepted execution identity is the Tau version and Linux binary hash listed
below. The source and parser commits are expected provenance pins. This runner
does not rebuild the executable, attest the source-to-binary relationship, or
pin the host libraries and kernel. Its receipt records those boundaries
explicitly.

The capture tool replaces the following manual checklist. If the tool cannot
run, retain this evidence directly:

```bash
git -C /path/to/tau-lang rev-parse HEAD
git -C /path/to/tau-lang status --porcelain=v1
git -C /path/to/tau-lang submodule status --recursive
/path/to/tau-lang/build-Release/tau --version
sha256sum /path/to/tau-lang/build-Release/tau
cmake --version
c++ --version
ldd --version
uname -a
```

Also retain the Runpod image name and immutable image digest, build command,
CPU architecture, and build log. A rebuilt executable with different bytes is a
new candidate. Preserve its manifest and review the new pin intentionally; do
not edit the accepted hash solely to make the runner pass. No reviewed-binary
Version 1.1 interpreter receipt is currently promoted because the accepted executable was
unavailable during this update. An older available `401d756b` executable
segfaulted on the current declaration shape and supplies no evidence.

## Current Tau source-candidate snapshot

- Snapshot date: `2026-08-23`
- Repository: <https://github.com/IDNI/tau-lang>
- Source commit: `9b191af689abdb75f3e43f200e09d35c0e99a664`
- Parser submodule: `5dd036358e194e55a08fd2ec255441bedfe83765`
- Reported version: `Tau Language Framework version 0.7.0-alpha (9b191af)`
- Local candidate binary SHA-256:
  `f6e2bf674d1850f1f83461b1fa2a3a7428ac0e7ab1dc28f599c6f8480890cb73`
- Local native module SHA-256:
  `ec34baae7d6d603b689e10d8fc65a2759efdaa00dce4e7a0955d8c18659ea633`

Replay:

```bash
python3 verification/probe_current_tau_packets.py \
  --tau-bin /path/to/tau-lang/build-Release/tau \
  --tau-source /path/to/tau-lang \
  --build-command 'cmake --build build-Release --parallel 2' \
  --output research/current_tau/current_tau_packet_probe.json \
  --json
```

The local candidate matched the V1 128-row, V1.1 16-row, V2 128-row, and
flywheel 512-row packets byte-for-byte. Each accepted only row zero, the
deliberate all-true row. The source status and parser pin were clean. This is
source-pinned candidate evidence. The build relation was declared rather than
independently attested, host dependencies were not hermetic, and no public Tau
Net publication, authenticated fact, settlement, or value authority follows.

## Version 2 source baseline

- AlignmentTheorem Version 1 baseline: `cf8d2c05219c5287af77872998983c303947832e`
- Version 2 development branch: `codex/alignment-theorem-v2-20260819`

## Reviewed Tau execution baseline

The following older identity remains the exact binary accepted by the strict
reviewed runners. It is retained as a historical execution baseline and is not
described as the current upstream source revision.

- Repository: <https://github.com/IDNI/tau-lang>
- Source commit: `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`
- Parser submodule: `5dd036358e194e55a08fd2ec255441bedfe83765`
- Reported version: `Tau Language Framework version 0.7.0-alpha (fd137e8)`
- Linux binary SHA-256:
  `c49267404e07a1f540c941b618e786710f70001eecbd05bb7c6d8eec0c5645fa`
- Build date: 2026-08-19
- Build command: `TAU_BUILD_JOBS=1 ./dev release`

Replay the policy truth table:

```bash
python3 verification/run_tau_v2.py \
  --tau-bin /path/to/tau-lang/build-Release/tau \
  --output verification/receipts/tau_v2_fd137e8.json
```

The receipt binds the executable, specification, inputs, and expected output
through an ordered packet hash. Tau 0.7 remains an alpha release. Passing this
bounded policy packet does not establish Tau Net deployment, mainnet
availability, cryptographic authentication, or settlement authority.

## Lean

- Lean release: `v4.33.0`
- Toolchain file: `proofs/v2/lean-toolchain`
- Standard library only; Version 2 intentionally has no Mathlib dependency.

Replay:

```bash
python3 verification/run_lean_v2.py \
  --output verification/receipts/lean_v2_v4.33.0.json \
  --json
```

The runner executes `lake build`, rejects proof placeholders and user-added
axioms, checks the exact declared standard `propext`/`Quot.sound` dependencies,
and binds the Lean source, project, manifest, and toolchain hashes.

The original Version 1 Lean file is retained in Git history as provenance. Its
old `lake build` claim was not repository-replayable because the project and
dependency pins were absent. The reconstructed, standard-library-only V1
project and replay commands are recorded at the start of this document.

## Compute-dividend research kernel

### Lean

- Lean release: `v4.33.0`
- toolchain file: `proofs/compute_dividend/lean-toolchain`
- standard library only

Replay:

```bash
python3 verification/run_lean_compute_dividend.py \
  --output verification/receipts/lean_compute_dividend_v4.33.0.json \
  --json
```

The recorded sandbox denied Lean's numeric `/proc/<pid>/exe` lookup while
permitting `/proc/self/exe`.  The replay therefore used the narrow, source-bound
compatibility shim at `verification/compat/lean_proc_self_compat.c`.  The
receipt records the loaded object hash and explicitly does not attest the host
kernel, libraries, sandbox, or Lean source-to-executable provenance.  Systems
without that sandbox restriction should run without the shim and produce a new
environment record.

### Tau packets

`tau/compute_dividend/dividend/` and `tau/compute_dividend/wealth/` each contain
all 256 Boolean rows for eight host-derived obligations.  Static vector parity
is source-bound by `verification/receipts/compute_dividend_campaign.json`.

Exact native replay intentionally uses the same reviewed Tau binary identity as
V1.1/V2 and does not accept a substitute candidate:

```bash
python3 verification/run_tau_compute_dividend.py \
  --gate dividend --tau-bin /path/to/reviewed/tau --json
python3 verification/run_tau_compute_dividend.py \
  --gate wealth --tau-bin /path/to/reviewed/tau --json
```

No compute-dividend native-Tau receipt is promoted until those commands pass on
the reviewed binary.  Source and parser revisions remain expected provenance
pins rather than a source-to-binary attestation.

An exact-source local build at the expected source/parser pins produced
candidate SHA-256 `b2699306d75c977ae4466e4f69237838efe6caafcc86bec62bbfb6517161ec19`
and reported `Tau Language Framework version 0.7.0-alpha (fd137e86)`.  It
natively matched the V1.1 and both compute-dividend packets.  Because its hash
and exact version differ from the reviewed identity, and because it executed
with locally built cvc5 plus unpinned host libraries, this is candidate evidence
only.  See `research/compute_dividend/tau_source_candidate_probe.json`.

## Intelligence-flywheel research kernel

### Lean and exact model

- Lean release: `v4.33.0`
- toolchain file: `proofs/intelligence_flywheel/lean-toolchain`
- standard library only
- exact model arithmetic: Python integers and `fractions.Fraction`

Replay:

```bash
python3 verification/run_lean_intelligence_flywheel.py \
  --output verification/receipts/lean_intelligence_flywheel_v4.33.0.json \
  --json
python3 -m verification.run_intelligence_flywheel_campaign --json
```

The same sandbox compatibility and non-attestation boundary described for the
compute-dividend Lean run applies.  The receipt reports the loaded shim when
used and does not attest the Lean executable's provenance or the host.

### Tau CLI packet

`tau/intelligence_flywheel/gate/` contains all 512 rows for nine obligations.
The current source-pinned local candidate `f6e2bf67...` produced byte-identical
output, but is not the reviewed identity. Reviewed replay is fail-closed:

```bash
python3 verification/run_tau_intelligence_flywheel_reviewed.py \
  --tau-bin /path/to/reviewed/tau \
  --output verification/receipts/tau_intelligence_flywheel_fd137e8.json \
  --json
```

Until an executable with exact SHA-256 `c4926740...` is supplied, the runner's
candidate preflight remains a negative result, not an execution receipt.

### Tau Testnet native ABI probe

- Tau Testnet source commit:
  `9f9240ded9fd7ff246f4bbd45343c64eef9a1751`
- Tau source/parser commits: the current `9b191af...` / `5dd036...` pins above
- local native module SHA-256:
  `ec34baae7d6d603b689e10d8fc65a2759efdaa00dce4e7a0955d8c18659ea633`

The direct `TauInterface` probe binds upstream source files, module bytes,
application-rule bytes, semantic stream mapping, and case results.  The module
was produced through a local non-hermetic build whose source-to-module relation
is declared but not independently attested.  Direct binding execution is not a
node/admission/block-apply/finality test, and custom input values do not
authenticate economic facts.

The three-profile router can be replayed against the same exact source and
module identity:

```bash
python3 verification/probe_tau_net_alignment_profiles.py \
  --tau-testnet-root /path/to/tau-testnet \
  --tau-source /path/to/tau-lang \
  --tau-module /path/to/tau-lang/build-Release/bindings/python/nanobind/tau.cpython-312-x86_64-linux-gnu.so \
  --library-dir /path/to/cvc5/lib \
  --output research/current_tau/profile_router_native_probe.json \
  --json
```

Its 27 cases cover V1, V1.1, and V2 all-true and single-false paths, an unknown
profile, absent custom inputs, and sender isolation. `i17..i24` are still
transaction-supplied. For V1, a true `exclusive_upside_enforceable` bit is only
a claim unless a consensus-recognized verifier binds it to an actual exclusive
entitlement. The predicate never debits the excluded branch.
