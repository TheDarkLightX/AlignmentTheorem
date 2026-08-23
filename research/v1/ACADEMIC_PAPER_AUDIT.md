# Version 1 academic-paper reconstruction

Audit date: 2026-08-23

## Frozen subject

The Version 1 subject is the initial repository import at commit
`a28695f`. The original artifacts have these SHA-256 identities:

| Artifact | SHA-256 |
| --- | --- |
| `docs/Alignment_Theorem_Academic.pdf` | `f5dca5a1e7bcd069441f16410664cdecac3eeebe4a5af8f128dd0efa7043c8bc` |
| `docs/Alignment_Theorem_Academic.tex` | `0225f63aceb439506a1b4a3be17746dae1b1823efed264cd4d35211cb6f434c8` |
| `proofs/AlignmentTheorem.lean` | `85da15c72c4358b4fee85f64ca9ab1daa467dd7c01cd7401262d17f3c43cd113` |
| `analysis/simulations/run_alignment_simulations.py` | `8f2beb00f42af6db54e7631a5e42cea4e2c74737b96a6b93fe82bbf0c2fbc84c` |

The PDF is 16 pages, dated 2025-12-03. It contains more than a
sign-separated payoff lemma. Its full architecture is:

```text
user ethical models
  -> Tau aggregation A
  -> network EETF E(t) in [0,3]
  -> account/action EETF e and reward tier(e) in {0,1,3,5}
  -> VCC burns and normalized supply S(t)
  -> scarcity M(t)=S0/S(t), pressure P(t)=M(t)E(t)
  -> reward/access comparison
  -> rational choice and claimed population convergence
```

## Intended V1 economic comparison

The paper writes a direct reward for EETF-eligible behavior and a negative term
for behavior below the EETF threshold. That second term is the value missed
because the branch is excluded from scarcity-linked upside. The current public
calculator reports the missed amount directly. The original simulation makes
the intended bounded-opposition structure explicit:

```text
u_eligible(t) = k_R * tier * M(t)
u_excluded(t) = g_max - k_C * X * M(t) * E(t)
```

The second scarcity term is foregone upside caused by exclusion. It is not a
tax, fine, burn, confiscation, or balance debit. Adding the foregone amount to
both alternatives preserves their ordering and yields the no-debit
normalization:

```text
R = direct reward coefficient
L = scarcity-upside coefficient available only under eligibility
G = bounded deviation gain

u_eligible(t) = M(t) * [R + L]
u_excluded(t) = G
```

The exact V1 condition is therefore:

```text
G < M(t) * [R + L].
```

For finite integers and `R+L > 0`, the least strict multiplier is
`floor(G/(R+L))+1`. When `G=0`, every positive multiplier suffices. If the
excluded branch can obtain `L`, or if `L` is appreciation shared equally by
both alternatives, the `L` term cancels and cannot support the theorem.

## Demonstrated corrections

| Original surface | Finding | Correction |
| --- | --- | --- |
| “Penalty” language | The utility term is valid as foregone upside, although the word risks a punitive implementation. This is an interpretation boundary rather than an algebraic flaw. | Preserve the ordering and treat the term as an eligibility-controlled positive entitlement; exclusion applies no debit. |
| Printed `e_th = 1 - B*tau/(10 X E)` | `M` cancels, a positive tier is used in the region where the piecewise tier equals zero, and the formula omits `g_max` used by the simulation. | Compare branches with `G < M(R+L)` and use the exact strict threshold above. |
| Common scarcity appreciation | A common term cannot change the argmax. | Bind `L` to an access-controlled reward, claim, service, capability, or other entitlement unavailable to the excluded branch. |
| Paper `r(t)` versus Lean supply path | The paper states a time-varying bounded rate; the Lean file proves a constant-rate geometric path. | Consume a finite `M` at runtime and require a separate checked witness for any claimed unbounded path. |
| Historical Lean replay | The file has no locked project and fails on the available Lean/Mathlib toolchain; one limit proof also describes a quadratic term although the formula is linear in `M`. | Use `proofs/v1/` for the reconstructed V1 kernel and preserve the old source only as provenance. |
| “all rational agents” | The proof assumes a complete declared utility and exact maximization over EETF alternatives. | Scope the conclusion to exact maximizers over the authenticated eligible/excluded alternatives and the stated gain bound. |

Modeling assumptions such as EETF aggregation, market value, evidence honesty,
identity, access enforcement, and reserve funding remain external premises.
They are not repaired by algebra.

## Current checked artifacts

- `proofs/v1/AlignmentTheoremV1.lean` checks EETF tiers, the opportunity-cost
  normalization, strict finite choice, the exact least threshold, the
  zero-deviation case, an unbounded-scarcity implication, and the common-upside
  cancellation boundary under Lean 4.33.0.
- `verification/alignment_v1_model.py` implements the paper's thousandths EETF
  scale and exact bounded-integer exclusion comparison.
- `tau/v1/exclusion_gate_v1.tau` requires seven named facts. Its complete
  128-row packet admits only the all-true row.
- `research/current_tau/current_tau_packet_probe.json` records a byte-exact
  replay on a local source-pinned Tau candidate. It supplies no evidence that
  the seven facts are authentic or that public Tau Net nodes enforce them.

## Version relationship

V1 remains the easiest concrete explanation because it names EETF, VCC,
rewards, scarcity upside, exclusion, and exact choice directly. V1.1 is useful
as the abstract theorem that adds compliance cost, optimizer error, and
time-varying relative-growth bounds. V2 is useful as the finite policy,
publication, replay, reserve, and settlement envelope. These are different
profiles rather than a quality ranking.
