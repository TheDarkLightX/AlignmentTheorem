# Tau and Tau Net replay status

## Semantic packet

The canonical packet is `tau/intelligence_flywheel/gate`.  It enumerates all
`2^9 = 512` Boolean rows and accepts exactly row 0, the generator's all-true
row.  The ordered facts are:

1. policy root matches;
2. capability receipt is authenticated;
3. productivity bridge is verified;
4. essential-basket gain is verified;
5. universal benefit floor is funded;
6. concentration cap holds;
7. grid/externality budget holds;
8. nominal-debt guardrail holds; and
9. the strict V1.1 margin holds.

Lean, Python, the file-stream Tau packet, and the native Tau Testnet mapping use
this same order and conjunction.

## Tau candidate result

- Tau source: `9b191af689abdb75f3e43f200e09d35c0e99a664`
- parser: `5dd036358e194e55a08fd2ec255441bedfe83765`
- local candidate SHA-256: `f6e2bf674d1850f1f83461b1fa2a3a7428ac0e7ab1dc28f599c6f8480890cb73`
- candidate output: 512 canonical rows, accepted row `[0]`

The candidate has the exact current source/parser pins and version string. It
does not have the older reviewed binary identity. Matching Git revisions do not
attest which source produced the executable, and its build/runtime environment
is not hermetically attested.

## Reviewed binary result

The strict replay runner expects:

- SHA-256 `c49267404e07a1f540c941b618e786710f70001eecbd05bb7c6d8eec0c5645fa`
- version `Tau Language Framework version 0.7.0-alpha (fd137e8)`

That executable is not available in this workspace.  The runner rejects the
local candidate before execution, so the reviewed-binary replay remains
**pending**.  When the reviewed file is supplied, run:

```text
python3 verification/run_tau_intelligence_flywheel_reviewed.py \
  --tau-bin /absolute/path/to/reviewed/tau \
  --output verification/receipts/tau_intelligence_flywheel_fd137e8.json
```

The command is documentation, not an instruction embedded in a receipt.

## Tau Testnet native ABI result

At Tau Testnet source revision
`9f9240ded9fd7ff246f4bbd45343c64eef9a1751`, the direct native binding executed
`tau/intelligence_flywheel/tau_net/dac_treasury_o5.tau`:

- treasury/all true: allow;
- treasury/each one of `i17..i25` false: block;
- treasury/custom evidence absent: block; and
- another sender/all false: allow.

The native module SHA-256 is
`ec34baae7d6d603b689e10d8fc65a2759efdaa00dce4e7a0955d8c18659ea633`,
paired with current Tau source `9b191af...` and parser `5dd036...`.

The rule is scoped by host-fed sender `i12`.  Streams `i17..i25` are used to
avoid current reserved/conditional streams.  In the tested alpha, transaction
submitters supply custom inputs.  Therefore this proves direct native predicate
execution, not economic-fact authentication.  It is not an end-to-end node,
admission, block-apply, governance, deployment, finality, or real-funds test.
