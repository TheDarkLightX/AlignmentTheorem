# Reproducible Toolchain Pins

Version 1.1 and Version 2 evidence is tied to exact source identities and to
binary identities wherever interpreter execution is claimed. A later tool
version must generate a new receipt rather than
inherit these results.

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
surfaces as reference-only and records exact-current Tau interpreter replay as
pending.
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
python3 verification/run_tau_v1_1.py \
  --tau-bin /path/to/tau-lang/build-Release/tau \
  --output verification/receipts/tau_v1_1_fd137e8.json \
  --json
```

The accepted execution identity is the Tau version and Linux binary hash listed
below. The source and parser commits are expected provenance pins. This runner
does not rebuild the executable, attest the source-to-binary relationship, or
pin the host libraries and kernel. Its receipt records those boundaries
explicitly.

Before reviewing a different Runpod-built candidate, retain this evidence:

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
not edit the accepted hash solely to make the runner pass. No Version 1.1
interpreter receipt is currently promoted because the accepted executable was
unavailable during this update. An older available `401d756b` executable
segfaulted on the current declaration shape and supplies no evidence.

## Version 2 source baseline

- AlignmentTheorem Version 1 baseline: `cf8d2c05219c5287af77872998983c303947832e`
- Version 2 development branch: `codex/alignment-theorem-v2-20260819`

## Tau Language

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

The Version 1 Lean file is retained as historical research. Its old `lake
build` claim was not repository-replayable because the project and dependency
pins were absent.
