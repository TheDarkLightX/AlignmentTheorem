# Current Tau Net profile router

`alignment_profiles_o5.tau` demonstrates one sender-scoped `o5` policy for all
three Alignment Theorem profiles on the pinned Tau Net Alpha ABI.

| Stream | V1 | V1.1 | V2 |
| --- | --- | --- | --- |
| `i17` | profile `1` | profile `2` | profile `3` |
| `i18` | policy root | policy root | policy root |
| `i19` | network EETF authenticated | EETF evidence authenticated | evidence authenticated |
| `i20` | candidate EETF authenticated | action eligible | action known |
| `i21` | scarcity snapshot authenticated | scarcity snapshot authenticated | action policy compliant |
| `i22` | reward funded | eligible exposure funded | nonce fresh |
| `i23` | exclusive upside enforceable | exclusive upside enforceable or coefficient zero | task unclaimed |
| `i24` | strict V1 margin | strict V1.1 margin | reward funded and finite V2 margin |

Every slot is required so the runtime envelope stays uniform. A V1.1 mechanism
with zero exclusive-upside coefficient supplies a checked zero-coefficient
witness at `i23`; otherwise the entitlement must be enforceably unavailable to
the excluded branch.

The current Alpha treats `i17..i24` as transaction-supplied custom inputs. The
rule therefore has no authority to establish these propositions. A safe mount
must derive the profile and seven facts from canonical, context-bound receipts
through a consensus-recognized verifier, then atomically couple the Tau verdict
to replay-safe reserve settlement. Unknown profiles, false facts, and missing
facts fail closed in the bounded native-ABI probe.

`verification/probe_tau_net_alignment_profiles.py` ran 27 cases through the
pinned native `TauInterface`: one all-true case and seven single-false cases for
each profile, plus unknown-profile, absent-input, and other-sender controls. The
source-bound receipt is
`research/current_tau/profile_router_native_probe.json`. This demonstrates the
router predicate only. In particular, the V1 `i23` claim does not create the
exclusive entitlement or remove value from an excluded actor.
