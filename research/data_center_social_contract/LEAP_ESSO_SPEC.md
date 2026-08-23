# LEAP / ESSO Finite-State Obligation

This packet follows the public LEAP and ESSO discipline without claiming that either MCP was executed in this environment.

## State

`(phase, obligations_mask, distributable_reserve, required_transfer, payout, reserve_post)`

Phases:

`PROPOSED`, `REJECTED`, `ADMITTED`, `OPERATING`, `CURTAILED`, `SETTLEMENT_DUE`, `SETTLED`, `DEFAULTED`, `REVOKED`.

The obligations mask has ten bits corresponding exactly to the Tau packet.

## Canonical transitions

- `admit`: `PROPOSED -> ADMITTED` iff all ten bits are true and reserve is at least the exact hybrid requirement; otherwise `REJECTED`.
- `start`: `ADMITTED -> OPERATING`.
- `fail(j)`: `ADMITTED|OPERATING -> CURTAILED` after clearing obligation `j`.
- `close`: `OPERATING -> SETTLEMENT_DUE` only while all obligations remain true; otherwise `CURTAILED`.
- `settle`: `SETTLEMENT_DUE -> SETTLED` with exact reserve conservation; an invalid/underfunded state goes to `DEFAULTED` with zero payout.

## Safety invariants

1. No admitted or operating state lacks any constitutional obligation.
2. No admitted state has reserve below the exact transfer requirement.
3. Every detected obligation failure forces curtailment before further operation.
4. A settled state pays exactly the required amount.
5. `payout + reserve_post = reserve_pre`.
6. Rejection/default does not create a payout.

## Bounded domain and result

The executed explorer covered all 1,024 masks and every reserve/requirement pair in `[0,3]^2`: 16,384 scenarios. Ten states were admissible (the ten `reserve >= requirement` pairs for the all-true mask), all ten settled, 16,374 rejected, and 100 injected obligation failures curtailed. No invariant violation occurred.

## Mutants killed

- drop any one of ten obligations (ten mutants);
- replace conjunction with disjunction;
- ignore the reserve threshold.

Each mutant has a canonical finite witness. This is bounded mutant killing, not an unrestricted model-checking theorem.
