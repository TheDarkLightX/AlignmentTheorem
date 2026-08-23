# Compute Dividend + Household Wealth Agent

**Research status:** bounded formal and executable evidence; real-world mechanism
under test.  Base revision: `b44540b69231a8dbadaaf86cb507220465c06ca0`.
Research date: 2026-08-22.

## Result first

The strongest result supported here is narrower than “data centers make
everyone rich.”  Given authenticated integer inputs and a fixed public policy:

1. gross data-center rent can be partitioned without overdraft into senior grid
   costs, a public reserve, and a distributable balance;
2. a universal household floor is feasible exactly when its aggregate cost is
   funded (and, with a share cap, when the floor also fits below that cap);
3. a discrete concave, prioritarian allocator matches an independent exhaustive
   optimum in the checked 10,836-case finite domain; and
4. an arbitrary proposal engine cannot make this reference selector commit a
   plan that fails the modeled consent, custody, leverage/short, concentration,
   finite-scenario tail-loss, fee, or turnover checks.

Lean also proves the purely arithmetic safety implication
\(\ell\le w-f\Rightarrow f\le w-\ell\), given \(f\le w\): a *true* one-period
loss bound preserves a declared protected floor.  The finite scenario gate does
not establish that its modeled loss is such a true bound.

Those are accounting, allocation, and verifier-conditioned claims.  They are
not source-to-binary attestations, investment-return guarantees, legal advice,
identity proofs, or evidence that a real data-center bargain improves welfare.
The atom-by-atom Python reference rejects budgets above 10,000 atoms; scalable
implementation and unrestricted optimality are separate obligations.

## Why this is a live U.S. question

The 2024 Lawrence Berkeley National Laboratory report estimates that U.S. data
centers used 176 TWh, or about 4.4% of national electricity, in 2023 and gives a
2028 scenario range of 325–580 TWh, or 6.7%–12.0%.  The range is a scenario,
not a point forecast.  In June 2026, FERC directed regional grid operators to
justify or reform large-load rules and highlighted cost-recovery agreements
designed to protect customers from stranded costs.  FERC also distinguishes
federal transmission cost shifting from state retail cost allocation.  GAO
separately emphasizes that the portion attributable specifically to generative
AI and the scale of environmental effects remain uncertain.

Primary sources:

- [LBNL, 2024 United States Data Center Energy Usage Report](https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report_1.pdf)
- [FERC, June 2026 large-load action](https://www.ferc.gov/news-events/news/ferc-launches-aggressive-targeted-action-speed-large-load-integration)
- [FERC fact sheet on jurisdiction and cost shifting](https://www.ferc.gov/news-events/news/fact-sheet-ferc-takes-action-supercharge-americas-grid-efficiency-reliability-and)
- [GAO-25-107172, Generative AI's Environmental and Human Effects](https://www.gao.gov/products/gao-25-107172)

This motivates a mechanism-design question: if a community permits scarce grid,
land, water, tax, or infrastructure capacity to support a large compute load,
can a contract first prevent cost shifting and then turn a separately negotiated
public rent into universal household cash and compute benefits?

## Post-AGI stress assumption: rents are not automatic

Nothing here assumes that AGI creates permanent monopoly profit.  In a highly
competitive abundance scenario, compute prices or accounting profit could fall
toward zero while grid, land, water, and reliability costs remain positive.  A
profit-share-only rule \(G_t=\tau\max(\Pi_t,0)\) therefore cannot universally
fund a positive floor: \(\Pi_t=0\) is an immediate countermodel.

A contract that is intended to support a floor needs a separately enforceable
minimum capacity/land/permit payment \(L_t\), an accumulated reserve, or both.
The same formal threshold applies:

\[
L_t + \tau\max(\Pi_t,0) \ge C_t+S_t+n_tm_t.
\]

This is a solvency condition, not a claim that the payment is efficient, lawful,
collectible, or greater than the opportunity cost of rejecting the facility.
It also makes the populist bargain falsifiable: if net authenticated rent does
not clear the threshold, the promised floor must not be advertised as funded.

## Mechanism boundary

For one accounting epoch, let:

- \(G\) be authenticated gross public rent paid into escrow;
- \(C\) be authenticated incremental grid/interconnection cost recovery;
- \(S\) be the required public stability reserve; and
- \(D\) be the distributable balance.

The reference model uses natural-number atoms and fails closed:

\[
D = \begin{cases}
G-C-S, & C+S\leq G,\\
0, & C+S>G.
\end{cases}
\]

Under \(C+S\leq G\), Lean proves the conservation identity

\[
C+S+D=G.
\]

For \(n\) eligible households and universal minimum \(m\), Lean also proves the
sufficient gross-rent threshold

\[
G\ge C+S+nm \quad\Longrightarrow\quad D\ge nm.
\]

This does not derive the rent, decide tax incidence, or show that a proposed
contract is lawful.  It says what follows after those integers are supplied by
an external, authenticated process.

## Prioritarian welfare with a floor and concentration limit

Let \(b_i\) be household \(i\)'s declared baseline resources and \(x_i\) its
epoch allocation.  For an earmarked budget \(D\), floor \(m\), and rational
share cap \(\kappa=p/q\), the feasible set is

\[
\mathcal F(D,m,\kappa)=\left\{x\in\mathbb Z_{\ge0}^n:
\sum_i x_i\le D,\;x_i\ge m,\;q x_i\le pD\;\forall i\right\}.
\]

The cap is relative to the original earmarked budget.  It is not a cap on total
household wealth, and without authenticated personhood it is not Sybil
resistance.  The combined floor is feasible exactly when

\[
nm\le D \quad\text{and}\quad m\le\left\lfloor\kappa D\right\rfloor.
\]

The default welfare objective uses equal civic weights and exact discrete
harmonic utility:

\[
W(x)=\sum_i\sum_{k=1}^{x_i}\frac{1}{b_i+k}.
\]

Its next-atom marginal benefit is \(1/(b_i+x_i+1)\).  The algorithm first pays
every floor, then repeatedly gives the next atom to the eligible household with
the greatest exact marginal benefit, breaking ties by canonical household ID.
It leaves budget unspent when all caps bind.

This is a prioritarian social welfare function in the limited sense that equal
increments have larger marginal value at lower resource levels.  If an atom is
moved from initial level \(r\) to initial level \(p\), the welfare change is

\[
\Delta=\frac{1}{p+1}-\frac{1}{r}.
\]

Thus \(\Delta\ge0\) when \(p<r\), and \(\Delta>0\) when \(p+1<r\).  Lean proves
the corresponding abstract one-step result for any utility satisfying discrete
diminishing returns.  Atkinson's inequality framework and proportional-fair
resource allocation motivate the concave objective; neither paper selects this
project's civic policy.

- [Atkinson, “On the Measurement of Inequality” (1970)](https://faculty.ucr.edu/~jorgea/econ261/atkinson_inequality.pdf)
- [Kelly, Maulloo, and Tan, “Rate Control for Communication Networks” (1998)](https://link.springer.com/article/10.1057/palgrave.jors.2600523)

### A decisive negative result

Concavity does not make arbitrary political weights prioritarian.  The checked
counterexample gives a resource-poor household weight 1 and a resource-rich
household weight 1,000; the rich household receives the next atom.  Equal
weights—or a separately justified, publicly reviewable weighting rule—must be
part of the constitution, not silently supplied by an operator.

## The “personal Warren Buffett” agent, stated safely

The nickname is not a theorem.  The implementable object is a **household
wealth copilot** with an explicit no-op baseline:

1. any model or human may propose plans;
2. the host derives eight Boolean obligations from authenticated evidence and
   exact checks;
3. only admitted plans may enter the selector;
4. the selector chooses the highest declared score above the no-op score; and
5. if no plan qualifies, it does nothing.

The modeled obligations are:

| External or derived fact | Exact reference meaning |
| --- | --- |
| Policy root | Current community/household policy identifier matches |
| Consent | Household authorization is current |
| Proposal evidence | The proposal record and model inputs are authenticated |
| Custody | The separately governed account permits this action |
| No leverage or short | Both declared exposures equal zero |
| Concentration | Issuer exposure is at or below the configured basis-point cap |
| Tail loss | Mean of the worst \(k\) supplied scenario losses is below the limit |
| Fee/turnover | Both exact basis-point bounds hold |

The tail statistic is an empirical expected-shortfall analogue over a finite,
declared scenario set.  Rockafellar and Uryasev motivate tail-risk optimization,
while distributionally robust Kelly work shows why a known-distribution log
growth model is not enough under model uncertainty.

- [Rockafellar and Uryasev, “Optimization of Conditional Value-at-Risk”](https://ideas.repec.org/a/rsk/journ4/2161159.html)
- [Sun and Boyd, “Distributional Robust Kelly Gambling”](https://web.stanford.edu/~boyd/papers/pdf/robust_kelly.pdf)
- [SEC guidance update on robo-advisers](https://www.sec.gov/investment/im-guidance-2017-02.pdf)

The reference campaign intentionally accepts a plan under its four supplied
loss scenarios and then posits an unmodeled loss 100,000 times the configured
tail limit.  That is a counterexample to any out-of-sample guarantee.  A real
service would also face securities law, fiduciary, suitability, tax, privacy,
cybersecurity, custody, model-risk, and licensing requirements that these gates
do not discharge.

## What Tau and Tau Net can contribute

Two complete 256-row Tau semantic packets express the dividend and wealth
action conjunctions.  Exactly one row in each packet admits: the all-true row.
The same facts are represented in Python and Lean.

Tau's appropriate role here is a small, inspectable constitutional kernel:

- publish the current rule and policy-root digest;
- reject when any required fact is false or missing;
- replay proposed rule revisions against named mutations; and
- make the allowed transition auditable before a separate settlement/custody
  adapter moves value.

Tau does **not** make a rent receipt true, identify a unique household, meter
compute, forecast returns, enforce U.S. law, or attest its own build.  Tau Net
deployment, governance, consensus, and value authority are outside this packet.

The exact reviewed Tau identity remains:

| Item | Pin |
| --- | --- |
| Source | `fd137e860b60083b36f9159ec8090cb1a3c3cb5a` |
| Parser submodule | `5dd036358e194e55a08fd2ec255441bedfe83765` |
| Version | `Tau Language Framework version 0.7.0-alpha (fd137e8)` |
| Reviewed Linux binary SHA-256 | `c49267404e07a1f540c941b618e786710f70001eecbd05bb7c6d8eec0c5645fa` |

That exact executable was not available in this run.  Therefore no exact
interpreter receipt has been promoted and the V1.1 replay remains pending.  See
`TAU_REPLAY.md` for the actual-Tau attempts, candidate boundary, and exact
handoff.

The existing V2 receipt is genuine same-binary evidence for its own seven-input
128-row conjunction.  It cannot substitute for execution of the byte-distinct
V1.1 or compute-dividend packets.

A clean exact-source build produced candidate `b2699306...`, reporting
`fd137e86`.  Native Tau execution on that candidate matched the canonical V1.1,
dividend, and wealth outputs (16/256/256 rows, accepting only row 0).  This is
stronger than static parity but is not the reviewed replay: its hash differs,
its exact version string differs, and it used non-hermetic build-tree
dependencies.  The candidate probe has no promotable `passed` field.

## Evidence obtained

| Lane | Result | Bounded claim |
| --- | --- | --- |
| Lean 4.33.0 | Pass, no placeholders, expected standard axioms only | Rent conservation/threshold, floor feasibility, settlement, conditional one-period protected-floor arithmetic, transfer, and gate implications |
| Exact Python allocator | 10,836 cases, zero exhaustive-oracle mismatches | Greedy optimum only on the enumerated domain |
| Transfer campaign | 1,024 pairs, zero formula/sign mismatches | Harmonic one-atom transfer on the enumerated domain |
| Python wealth selector | Unsafe high-score plan killed; no-op tested | Verifier-conditioned selection in the reference implementation |
| Tau static packets | 256 rows per gate; one accepting row each | Checked-in vectors equal the Boolean conjunctions |
| Exact-source Tau candidate | Native V1.1/dividend/wealth outputs all canonical | Candidate-only execution on `b2699306...`; no reviewed-binary, source-derivation, or environment claim |
| Exact reviewed Tau binary | Pending | No new interpreter-execution claim |

The Lean receipt records that this sandbox required a narrow `/proc/self/exe`
launcher compatibility shim and that the host kernel, libraries, sandbox, and
Lean source-to-executable relationship are not hermetically attested.

## A utilitarian-populist contract template

The mathematical proposal is a sequence of vetoes, not a blank check for data
center construction:

1. **Ratepayer veto:** incremental grid and stranded-asset costs must be funded
   before any dividend is counted.
2. **Ecological and reliability veto:** water, emissions, land, and reliability
   limits are external authenticated obligations; this research has not encoded
   or measured them.
3. **Universal floor:** every authenticated eligible household receives at
   least \(m\) cash atoms and a separately metered minimum compute entitlement.
4. **Prioritarian surplus:** remaining cash/compute is allocated with concave
   marginal utility under a per-household epoch cap.
5. **Concentration veto:** a binding share cap may leave surplus in the public
   reserve rather than concentrate it.
6. **Household agency:** compute entitlement can run the constrained copilot,
   but the household retains current consent and a no-op option.
7. **Public audit:** policy roots, receipts, packet hashes, rejections, and
   aggregate outcomes are published with privacy-preserving identifiers.

For a joint cash/compute objective one could write

\[
\sum_i u(b_i+x_i)+\beta v(q_i+c_i),
\]

with separate cash and metered-compute budgets.  Independent runs of the
allocator are justified only when the objective and constraints are separable.
Cash/compute complementarities, shared hardware queues, and strategic demand
make that decomposition an open optimization problem.

This resembles the high-level intergenerational idea of converting a scarce
resource rent into current and future public benefit, but it is not an empirical
endorsement of any specific fund.  The Alaska Permanent Fund is a useful public
precedent for studying transparent fund structure and citizen dividends:
[APFC fund structure](https://apfc.org/the-fund/fund-structure/).

## What would decide the real hypothesis

A pilot cannot be promoted from `under_test` until it supplies, at minimum:

- a legally reviewed rent/cost-recovery contract and audited escrow statements;
- counterfactual retail-rate, reliability, water, emissions, and land-impact
  measurements;
- an authenticated eligibility/personhood design with appeal and privacy paths;
- cash and compute floor delivery receipts;
- distributional outcomes by pre-registered household strata;
- randomized or credible quasi-experimental welfare evaluation;
- independent security, custody, and investment-adviser review; and
- loss, fee, turnover, abstention, complaint, and override telemetry.

The primary outcome should be a pre-registered concave household-welfare change
subject to hard floors and concentration guardrails.  Secondary outcomes should
include ratepayer bill impacts, service reliability, local environmental burden,
agent abstention, realized losses, and benefit capture by already-wealthy or
duplicate identities.

## Replay

```bash
python3 -m unittest tests.test_compute_dividend_model -v
python3 -m unittest tests.test_tau_compute_dividend -v
python3 -m unittest tests.test_compute_dividend_campaign_receipt -v
python3 -m verification.run_compute_dividend_campaign --json

cd proofs/compute_dividend
lake build
lake env lean AxiomAudit.lean
```

For the exact reviewed Tau binary only:

```bash
python3 verification/run_tau_v1_1.py \
  --tau-bin /path/to/reviewed/tau \
  --output verification/receipts/tau_v1_1_fd137e8.json \
  --json

python3 verification/run_tau_compute_dividend.py \
  --gate dividend \
  --tau-bin /path/to/reviewed/tau \
  --json
```

## Research Kernel / LEAP / ESSO / SAGE status

Research Kernel MCP, LEAP, ESSO, Morph, and SAGE adapters were not exposed in
this environment.  No run, promotion, or receipt from those systems is claimed.
The local ledgers follow the Research Kernel evidence discipline, and
`PROOF_OBLIGATIONS.md` gives exact handoffs for future independent lanes.  Lean,
finite reference-model enumeration, mutation vectors, and actual Tau build/run
attempts are the only executed decisive lanes in this packet.
