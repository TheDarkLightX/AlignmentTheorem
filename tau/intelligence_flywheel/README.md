# Intelligence-flywheel Tau demos

`gate/intelligence_flywheel_gate.tau` is a complete nine-bit research packet.
Its 512 generated rows bind the Tau predicate to the Python and Lean predicate:
only the all-true row is admitted.

`tau_net/dac_treasury_o5.tau` maps the same nine-bit conjunction onto the
current Tau Testnet `o5` application-policy ABI.  The rule is scoped to a fixed
demonstration treasury through host-fed `i12`; other senders are unaffected.
The nine custom claims use `i17` through `i25`, avoiding the conditionally
reserved `i13` and current consensus streams.

The native ABI demo proves rule execution for supplied stream values.  Current
Tau Testnet lets the transaction submitter provide custom streams, so the demo
does **not** prove that capability, price, welfare, grid, debt, or receipt claims
are authentic.  A production design needs a consensus-recognized receipt/oracle
verifier and is outside the present alpha evidence.
