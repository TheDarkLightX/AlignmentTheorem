# Tau replay and build handoff

## Reviewed execution identity

- source pin: `fd137e860b60083b36f9159ec8090cb1a3c3cb5a`
- parser submodule pin: `5dd036358e194e55a08fd2ec255441bedfe83765`
- exact version string: `Tau Language Framework version 0.7.0-alpha (fd137e8)`
- reviewed Linux binary SHA-256:
  `c49267404e07a1f540c941b618e786710f70001eecbd05bb7c6d8eec0c5645fa`

The exact reviewed executable was not present in this session.  The fail-closed
runner rejects any other hash before invoking `--version` or `-X`.  Consequently
`verification/receipts/tau_v1_1_fd137e8.json` remains absent and pending.

The repository does contain a passing older receipt for the exact reviewed
binary on the Version 2 seven-input conjunction:
`verification/receipts/tau_v2_fd137e8.json`.  It binds that executable, version,
V2 specification, 128-row packet, and output.  It is relevant same-shape native
Tau evidence, but it is not execution of the V1.1 16-row packet or either new
256-row packet and cannot be relabeled as such.

If the reviewed file is recovered, run:

```bash
sha256sum /path/to/tau
python3 verification/run_tau_v1_1.py \
  --tau-bin /path/to/tau \
  --output verification/receipts/tau_v1_1_fd137e8.json \
  --json
python3 verification/run_tau_compute_dividend.py \
  --gate dividend --tau-bin /path/to/tau --json
python3 verification/run_tau_compute_dividend.py \
  --gate wealth --tau-bin /path/to/tau --json
```

A passing V1.1 receipt would bind the exact 16-row semantic packet and canonical
output to that binary.  Passing research-gate replays would similarly bind each
256-row packet.  None of those receipts would attest the declared source or
parser pins, build process, host environment, external facts, or network
authority.

## Actual Tau attempt: public 2024 release

The public `v0.7-alpha` Debian package was downloaded and inspected:

- package SHA-256:
  `05386f8f331023b2152893284955a7d747f15cb995e98447683ceb9ceb821f72`
- executable SHA-256:
  `e0bb17543a0c9c0eb935034115597b1e1aebecfeedf818a6910f31e9dcd00f3e`
- reported identity: Tau 0.7, build `3912dcb`, 2024-11-16

It rejected the current runner interface with `Invalid option: -X` and returned
code 1.  This is a negative compatibility result, not evidence about the
reviewed 2026 executable.

## Exact-source candidate build

The exact source and parser pins were checked out cleanly.  Boost 1.86 built
successfully.  Tau's pinned `scripts/dep-cvc5.sh` exposed a path-order bug: it
computes `CVC5_SOURCE_DIR` and `CVC5_PREFIX` from `$HOME/.tau` before parsing
`-DTAU_SHARED_PREFIX`, then attempts the read-only `/root/.tau` path even though
it prints the supplied workspace prefix.  The same pinned cvc5 tag
`cvc5-1.3.1` (commit
`ea1b484fa54bfe56c0f8b3ac90a6e3e2f46441e7`) was therefore configured
manually outside the Tau checkout so the source tree stayed clean.  The Boost
1.86 dependency resolved to commit
`65c1319bb92fe7a9a4abd588eff5818d9c2bccf9`.

The exact-source build then completed with the reviewed one-job recipe and
produced this candidate:

- binary SHA-256:
  `b2699306d75c977ae4466e4f69237838efe6caafcc86bec62bbfb6517161ec19`;
- reported version:
  `Tau Language Framework version 0.7.0-alpha (fd137e86)`;
- V1.1: native return code 0, 16 canonical rows, accepting row `[0]`;
- dividend gate: native return code 0, 256 canonical rows, accepting row `[0]`;
- wealth gate: native return code 0, 256 canonical rows, accepting row `[0]`.

The source checkout was clean at both expected Git pins.  The complete
non-promotable record is `tau_source_candidate_probe.json`.  It intentionally
has no `passed` field.  The candidate hash differs from the reviewed
`c4926740...` hash, and its exact reported version has one additional hex digit.
It executed in the build tree with locally built cvc5 and system libraries.
Thus it is useful native semantic evidence, but neither the exact reviewed
replay, an independently attested source-to-binary derivation, nor a hermetic
environment attestation.  Never change the reviewed pin merely to make this
candidate promotable.

## Claim boundary

| Evidence | Establishes | Does not establish |
| --- | --- | --- |
| Exact reviewed-binary replay | Those exact bytes reported the exact version and produced canonical packet output | Source-to-binary provenance; hermetic host; external truth; authority |
| Existing V2 exact-binary receipt | Native execution of the V2 seven-input conjunction | Execution of V1.1 or either research packet |
| Clean source checkout | Git and submodule identities | Which bytes built the reviewed executable |
| Candidate native probe | Native output for all three packets on candidate `b2699306...` plus build metadata | Equivalence to reviewed binary; hermetic dependencies; independently attested source derivation |
| Static truth table | Complete conjunction semantics in checked files | Native Tau execution |
