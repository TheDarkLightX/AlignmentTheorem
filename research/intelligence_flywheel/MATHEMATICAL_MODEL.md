# Mathematical model and tested maps

## 1. Separate capability from the theorem variables

Let `I_t > 0` be a normalized, verified capability index.  It must be tied to a
declared task distribution and success metric; “general intelligence” is not a
directly observed scalar here.  The V1.1 margin is still

\[
  \operatorname{Aligned}(t) \iff B_t < M_t K_t.
\]

An intelligence law can influence the right-hand side only through explicit
bridge assumptions.

## 2. Essential-basket bridge

Normalize the initial basket price to one.  Let `a in [0,1]` be the automatable
basket share, `rho in [0,1]` the household price pass-through, and integer
`eta >= 1` the automated-unit-cost elasticity.  The tested exact map is

\[
  P_t = (1-a) + a\left[(1-\rho)+\rho I_t^{-\eta}\right]
      = 1-a\rho+a\rho I_t^{-\eta},
  \qquad M_t=P_t^{-1}.
\]

This equation is a hypothesis, not a measured law.  It exposes a decisive
necessary condition for indefinite basket hyperdeflation: if
`delta = 1-a*rho > 0`, then

\[
  P_t \ge \delta, \qquad M_t \le \delta^{-1}.
\]

Thus intelligence can grow without bound while household purchasing power is
bounded.  Only the model's full bridge (`a=rho=1`) removes this particular
floor.  With `I_t=2^{gt}`, the full bridge gives

\[
  P_t=2^{-\eta gt}, \qquad M_t=2^{\eta gt}.
\]

“Hyperdeflation” in this packet means an exponential decline of this declared
essential-basket index.  It does not mean every CPI component declines, and it
does not make deflation automatically beneficial when nominal debts exist.

## 3. Alignment crossing

Suppose for one witness epoch `n`

\[
 B_n \le B_0 b^n,
 \qquad R_0 r^n \le M_nK_n,
 \qquad B_0b^n < R_0r^n.
\]

Then `B_n < M_n K_n`.  Lean proves exactly this transitive bound.  If the
inequalities hold for all epochs and `r>b`, elementary geometric growth can
eventually supply a witness, but this project does not smuggle that growth-rate
premise into “intelligence doubles.”

Lean also proves a constructive special case: if `M_B=2^B`, `K_B>=1`, and
deviation is the fixed natural number `B`, then epoch `B` is strictly aligned
because `B < 2^B <= 2^B K_B`.  It separately proves that an arbitrary
intelligence trajectory is insufficient when `M=K=1` and `B=2`.

## 4. Tested alternative maps

| Map | Exact assumption | Result in the finite campaign |
|---|---|---|
| Direct doubling/full bridge | `I_t=2^t`, `a=rho=eta=1`, `K=1`, `B=8` | First strict crossing at epoch 4 |
| Direct doubling/partial bridge | `a=3/4`, `rho=4/5`, `K=1`, `B=3` | `P>2/5`, `M<5/2`; no crossing through epoch 32 |
| Compute-power | `I/I0=(C/C0)^(1/2)` | Capability doubles every two compute doublings, not every one |
| Logistic | carrying capacity 8, full bridge, `K=1`, `B=9` | Bounded below the deviation; no crossing through epoch 32 |
| DAC reinvestment | `I_{t+1}=I_t(1+s r)`, `s=r=1/2` | Factor `5/4`; first crossing of fixed `B=4` at epoch 7 |
| Rebound | full-bridge core saving plus surcharge `1-2^-t` | Adjusted basket price remains 1; no crossing |

The campaign exhaustively checked 544 finite combinations of automation share,
pass-through, elasticity, and epoch against the price-floor and full-bridge
identities.  It is a bounded model check, not empirical validation.

## 5. Prioritarian populist objective

The distributional layer inherited from the compute-dividend packet maximizes
a separable concave household objective after funding a universal minimum and
before exceeding a per-household concentration cap.  One discrete form is

\[
  W(x)=\sum_h w_h\sum_{j=1}^{x_h}\frac{1}{c_h+j},
\]

subject to `x_h >= floor`, exact budget conservation, and allocation caps.
Concavity gives diminishing marginal welfare, but unequal political weights
can overturn literal poor-first ordering; that negative result is retained.

For a “personal Buffett” agent, the theorem can govern admission—consent,
custody, no leverage/shorting, diversification/concentration, modeled tail
loss, and fee/turnover limits.  It cannot prove returns, suitability, fiduciary
compliance, FIRE timing, or out-of-sample capital preservation.

## 6. Ethical and macro guardrails

The Tau gate requires independently derived facts for a funded universal
benefit floor, concentration cap, grid/externality budget, nominal-debt
guardrail, and strict alignment margin.  Deflation is therefore neither the
ethical objective nor sufficient evidence.  The objective is protected,
widely distributed real benefit under explicit harm constraints.
