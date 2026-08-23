# Alignment Theorem profiles on current Tau Language and Tau Net

Snapshot date: 2026-08-23

This note maps three distinct Alignment Theorem profiles onto the current
public Alpha repositories:

- Tau Language: `9b191af689abdb75f3e43f200e09d35c0e99a664`
- Tau parser: `5dd036358e194e55a08fd2ec255441bedfe83765`
- Tau Testnet: `9f9240ded9fd7ff246f4bbd45343c64eef9a1751`

The local build reported `Tau Language Framework version 0.7.0-alpha
(9b191af)`. Its executable SHA-256 was `f6e2bf674d1850f1f83461b1fa2a3a7428ac0e7ab1dc28f599c6f8480890cb73`.
The native Python module SHA-256 was
`ec34baae7d6d603b689e10d8fc65a2759efdaa00dce4e7a0955d8c18659ea633`.
These are local candidate identities. The build relation and host environment
were recorded and were not independently attested.

## Profile selection

| Profile | Exact useful case | Required premise | Current Tau role | External authority still required |
| --- | --- | --- | --- | --- |
| V1 EETF/VCC exclusion | EETF eligibility controls access to direct rewards and scarcity-amplified upside; exclusion applies no punitive debit. | `G(t) < M(t) * [R(t) + L(t)]`, exact maximization, and enforceable denial of `R` and `L` to the excluded branch. | Conjoin the policy root, authenticated network/candidate EETF, authenticated scarcity snapshot, funded reward, enforceable exclusive access, and verified strict margin. | EETF aggregation and evidence authentication, scarcity/value binding, access enforcement, deviation bound, optimizer premise, reserve custody, and settlement. |
| V1.1 hyperdeflationary | The concrete V1 comparison is generalized to arbitrary exposure, costs, optimizer error, and relative growth. | `B(t) < M(t) * K(t)`, with every runtime quantity finite and `K(t) > 0`. | Admit only when authenticated classification, funded reward, exclusive-access premise, and a host-verified strict margin are all true. | Authenticated prices and exposures, bounded deviation estimate, integer overflow/scale policy, reserve custody, and settlement. |
| V2 finite policy | A finite policy-relative advantage makes every epsilon-optimal modeled choice compliant. | `R_c - R_n + enforcement > G + C + epsilon`. | Enforce the seven-fact publication gate over a versioned policy and authenticated evidence. | Evidence verifier, nonce/nullifier state, reserve-backed effect application, recovery, and finality. |

V1 is the concrete EETF/VCC theorem. Its historical negative “penalty” is
foregone scarcity upside: adding that value to both alternatives gives the
equivalent no-debit comparison `M(R+L) > G`. If `G=0`, every positive scarcity
multiplier suffices; otherwise V1 has the exact integer threshold
`floor(G/(R+L))+1`. V1.1 abstracts this mechanism and adds costs, optimizer
error, and relative-growth cases. V2 removes the macroeconomic premise and adds
the finite policy, publication, and settlement envelope.

A practical composition can use the V2 gate and reserve-safe settlement as the
outer protocol while selecting V1 or V1.1 as the declared incentive profile.

## Executable evidence

`verification/probe_current_tau_packets.py` replayed four complete semantic
packets on the source-pinned local candidate:

| Packet | Rows | Accepted rows | Result |
| --- | ---: | --- | --- |
| V1 EETF/VCC exclusion | 128 | `[0]` | byte-exact match |
| V1.1 hyperdeflationary | 16 | `[0]` | byte-exact match |
| V2 finite policy | 128 | `[0]` | byte-exact match |
| Intelligence flywheel | 512 | `[0]` | byte-exact match |

Row zero is intentionally the all-true row. Each packet places its named
single-fault mutations immediately after it and then covers every remaining
Boolean row. The receipt is
`research/current_tau/current_tau_packet_probe.json`.

The intelligence-flywheel sender-scoped `o5` rule was also executed through
the current Tau Testnet `TauInterface`. All 12 all-true, single-fault,
missing-input, and other-sender cases matched. That receipt is
`research/intelligence_flywheel/tau_net_native_probe.json`.

The three-profile sender-scoped router was executed through the same pinned
native ABI. Its 27 cases covered one all-true case and each of seven
single-false facts for V1, V1.1, and V2, plus unknown-profile, absent-input, and
other-sender controls. Every case matched. The receipt is
`research/current_tau/profile_router_native_probe.json`.

## Current Tau Net boundary

The Alpha testnet can execute a sender-scoped application policy at transaction
admission and block application. The tested rule uses host-injected `i12` for
sender identity and emits `o5`. A zero verdict blocks; a one verdict allows.
Malformed output is parsed fail-closed.

The tested flywheel custom streams `i17..i25` and profile-router streams
`i17..i24` remain transaction-supplied values. Their truth is therefore a claim
by the submitter. The profile ID is also unauthenticated. Conjoining those
values in Tau does not authenticate capability, prices, policy roots, reserve
balances, identity, consent, measurements, exclusive entitlements, or economic
bounds.

V1 additionally requires an enforceable entitlement boundary. If an excluded
actor can still claim the reward or scarcity-sensitive benefit, the decisive
`L` term is zero. General token appreciation available equally to both branches
cancels and cannot establish V1.

The authoritative dataflow needs this shape:

```text
canonical evidence
  -> consensus-recognized verifier
  -> typed facts bound to sender + action + epoch + policy root
  -> Tau policy verdict
  -> reserve/nullifier/nonce checker
  -> canonical effect plan
  -> atomic application + replay receipt
```

The current Alpha provides the Tau verdict lane and an extralogical host API.
The repository does not yet provide the consensus-recognized evidence verifier,
reserved authenticated fact streams, mounted reserve settlement, multi-node
admission/apply parity harness, or finality evidence. Until those layers exist,
the safe deployment mode is a non-value-moving shadow policy.

## Minimal staged deployment

1. Shadow replay: publish exact policy roots, packet hashes, facts, verdicts,
   and non-value-moving receipts.
2. Authenticated fact adapter: derive closed typed facts from canonical,
   fresh, signer-authorized evidence. Reject missing, stale, malformed,
   disputed, or cross-policy evidence.
3. Consensus binding: reserve protocol inputs for verifier-derived facts so a
   transaction cannot override them. Test admission and block-apply parity on
   multiple pinned nodes.
4. Settlement shell: apply a V2-style reserve, nonce, task-nullifier, and
   reject-without-effect transition around the selected incentive profile.
5. Governance: admit policy revisions only through a separately checked
   constitution and publish replayable state-root receipts.

## Claim boundary

The current evidence establishes local language execution and bounded native
ABI probes at exact public source revisions. It does not establish public-node
deployment, authenticated real-world facts, legal authority, production
readiness, settlement safety, objective ethics, universal agent alignment, or
source-to-binary provenance.

Upstream references:

- <https://github.com/IDNI/tau-lang>
- <https://github.com/IDNI/tau-testnet>
- <https://tau.net/tau-language/>
- <https://tau.net/tau-net/>
