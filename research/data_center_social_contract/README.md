# Data-Center Social Contract and Post-AGI Distribution Theorem

## Research target

The original Alignment Theorem asks when an ethical reward can dominate an unethical payoff and when productive abundance can become deflationary. The compute-dividend branch adds a universal household floor and constrained wealth-agent layer. This extension addresses the missing distributional question raised by the U.S. data-center debate:

> Under what exact conditions can a data-center/AGI project be admitted without shifting modeled costs onto households, while still giving every household a minimum share of the resulting abundance?

The answer is not “some dividend exists.” A project can fund an equal dividend and still leave the household facing the largest electricity, water, land, tax, displacement, or labor-market loss worse off.

## 1. Minimal universal-floor plus no-harm theorem

For household \(i\), let:

- \(L_i\ge 0\): authenticated project-caused loss during the settlement epoch;
- \(B_i\ge 0\): authenticated direct project benefit that reaches that household;
- \(m\ge 0\): universal cash floor;
- \(d_i=(L_i-B_i)_+\): the household's uncompensated deficit.

Define the transfer

\[
h_i=\max\{m,d_i\}.
\]

### Theorem A — pointwise least protective transfer

For every household:

\[
h_i\ge m,
\qquad
B_i+h_i\ge L_i.
\]

Moreover, if another transfer \(x_i\) satisfies both \(x_i\ge m\) and \(B_i+x_i\ge L_i\), then

\[
x_i\ge h_i.
\]

So \(h_i\) is not merely sufficient. It is the unique pointwise minimum compatible with the universal floor and modeled no-harm.

### Corollary A1 — exact aggregate threshold

For \(n\) households, the least cash reserve is

\[
H(m)=\sum_{i=1}^{n}\max\{m,d_i\}.
\]

An admissible transfer vector exists if and only if the distributable cash reserve \(R\) satisfies

\[
R\ge H(m).
\]

### Corollary A2 — universal base plus targeted top-ups

The same threshold decomposes as

\[
H(m)=nm+\sum_{i=1}^{n}(d_i-m)_+.
\]

This is the clean “utilitarian populist” structure:

1. everyone receives the universal base \(m\);
2. households with authenticated deficits above \(m\) receive the exact additional top-up;
3. only the remaining surplus is optimized prioritarianly.

### Corollary A3 — uniform-only payments are weakly more expensive

If every household must receive the same payment, the least required reserve is

\[
U(m)=n\max\{m,\max_i d_i\}.
\]

Always \(H(m)\le U(m)\), with strict inequality whenever the worst household deficit is not shared by everyone. The bounded campaign found strict savings in 28,452 of 65,100 profiles.

### Smallest positive-floor counterexample

One household has \(L=2\), \(B=0\), and \(m=1\). The project can fully fund the advertised one-atom dividend, but the household is still one atom worse off. The protective threshold is \(h=2\), not \(1\).

## 2. Welfare consequence

Let \(w_i\) be baseline household resources and

\[
w_i'=w_i+B_i+h_i-L_i.
\]

Theorem A gives \(w_i'\ge w_i\). Therefore every componentwise nondecreasing social-welfare function weakly improves. In particular, for nonnegative priority weights \(\omega_i\) and increasing utilities \(u_i\),

\[
W'=\sum_i \omega_i u_i(w_i')\ge
W=\sum_i \omega_i u_i(w_i).
\]

Concavity is **not** needed for the no-harm result. Concavity becomes relevant only when allocating the surplus \(R-H(m)\). This cleanly separates a rights-like household floor from a prioritarian welfare optimizer.

## 3. Full-cost project admission

Let gross public rent be \(G\). Before any dividend is counted, reserve senior project claims:

\[
C=C_{grid}+C_{reliability}+C_{water/env}+C_{decommission}+C_{admin/security}.
\]

The distributable cash reserve is

\[
R=(G-C)_+.
\]

A one-epoch cash contract is feasible exactly when

\[
G\ge C+H(m).
\]

A robust rent formula cannot depend only on accounting profit. A safe design combines a non-avoidable capacity/concession payment, full incremental-cost recovery, and only then a variable revenue or profit share. Profit-only funding has an immediate zero-profit countermodel.

## 4. Cash and compute are separate resources

Let \(c\) be a universal compute entitlement and \(Q\) the authenticated compute reserve. Without a defensible household-specific lower bound converting compute into cash-equivalent welfare, the safe condition is separable:

\[
R\ge H(m)
\qquad\text{and}\qquad
Q\ge nc.
\]

Compute cannot silently substitute for rent, groceries, electricity bills, displacement costs, or cash losses. A future joint optimizer may count compute only after proving a conservative conversion floor and household access/consent.

## 5. Intelligence growth is not itself a deflation theorem

Let:

- \(a_t>0\): effective productivity reaching the priced household bundle, after automation share, diffusion, access, and pass-through;
- \(r_t>0\): scarce-resource and infrastructure cost factor;
- \(\mu_t>0\): markup and rent-extraction factor.

A transparent multiplicative decomposition is

\[
\frac{P_{t+1}}{P_t}=\frac{r_t\mu_t}{a_t}.
\]

One-period deflation occurs if and only if

\[
a_t>r_t\mu_t.
\]

Raw intelligence doubling does not force \(a_t=2\). If diffusion is blocked, the automation share is small, infrastructure becomes scarcer, or monopoly rents rise, prices need not fall. Over \(T\) periods,

\[
\frac{P_T}{P_0}=\prod_{t<T}\frac{r_t\mu_t}{a_t}.
\]

For the modeled bundle, asymptotic price collapse requires the cumulative effective-productivity advantage to diverge:

\[
\sum_{t<T}\left(\log a_t-\log r_t-\log\mu_t\right)\to +\infty.
\]

Even that is not sufficient for household abundance: nominal income and asset ownership can fall faster than prices. The social-contract theorem supplies the missing distribution channel.

## 6. Tau constitutional gate

The research packet uses ten authenticated Boolean host facts:

1. policy root current;
2. project identity authenticated;
3. local consent authenticated;
4. incremental energy costs reserved;
5. reliability/curtailment plan valid;
6. water, emissions, and land limits valid;
7. decommissioning bond funded;
8. no-harm compensation funded;
9. universal cash/compute floor funded;
10. public audit receipt current.

Tau admits only their conjunction. The complete 1,024-row packet accepts only row 0, the all-true row. Every single-fault row rejects.

Tau does not create these facts. Meters, causal models, public records, identity systems, reserve custodians, environmental monitors, and local-government attestations remain outside the language boundary. Missing evidence must map to false.

## 7. Bounded evidence

The deterministic campaign used exact Python integers and fractions:

- 65,100 household/floor profiles;
- 1,348,200 pointwise-minimality checks;
- 319,417 cash-reserve boundary checks;
- 1,533,480 separate cash/compute threshold checks;
- 1,024 complete Tau truth-table rows;
- 16,384 project-state scenarios;
- 100 post-admission obligation-failure transitions;
- 12 killed gate/reserve mutants;
- zero modeled welfare regressions and zero lifecycle invariant violations.

The Lean file states and proves the unrestricted arithmetic theorems, but its local Lean 4.33 replay is a separate evidence obligation until a build receipt is captured. The new Tau packet is statically complete; native execution against the pinned candidate/reviewed Tau binaries is also a separate replay obligation.

## 8. Strongest claim

This extension supports a conditional theorem:

> If project losses and benefits are correctly authenticated, senior costs are fully reserved, the cash reserve meets \(H(m)\), the compute reserve meets \(nc\), and every constitutional fact is true, then the proposed transfer schedule is the least-cost schedule that supplies a universal floor and prevents every modeled household from being worse off during the epoch.

It does not prove that an actual project has measured every loss, that local consent is legitimate, that Tau authenticates evidence, that the Tau Testnet is production-ready, that AGI causes deflation, or that a wealth agent earns returns.
