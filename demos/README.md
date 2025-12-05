# 🎮 Deflationary Agent Demos

> **Executable Tau Language specifications demonstrating the Alignment Theorem and intelligent agent behavior**

These demos showcase working Tau specifications that run on the Tau binary.

## 📁 Demo Folders

### 1. 🎯 [Alignment Theorem](alignment_theorem/)

Demonstrates the economic principles of the Alignment Theorem:
- Scarcity calculation
- Economic pressure
- Ethical rewards
- Deflationary burns

```bash
cd alignment_theorem && ./run_all.sh
```

### 2. 🤖 [Intelligent Agent](intelligent_agent/)

Q-Learning FSM + Smart Entry/Exit logic:
- 4-state FSM encoding
- Smart entry on favorable conditions
- Smart exit on profit signals
- Position timers and trade counters

```bash
cd intelligent_agent && ./run_all.sh
```

### 3. 🔐 [Virtue Shares](virtue_shares/)

HEX-style time-locking primitive:
- Lock/unlock FSM
- vShares accumulation
- Boost calculation
- Early exit penalties

```bash
cd virtue_shares
../../tau-lang-latest/build-Release/tau < virtue_shares_demo.tau
```

## 🔬 Key Learnings

### Tau Execution Mode Syntax

| Feature | Supported | Alternative |
|---------|-----------|-------------|
| Ternary `?` | ❌ No | Boolean algebra |
| BV comparisons `>` | ❌ No | Use in `solve` only |
| Enums | ❌ No | Explicit `bv[N]` constants |
| Mixed SBF/BV | ✅ Yes | Separate streams |
| Recurrence | ✅ Yes | `o[t] = ... && o[0] = init` |

### Working Patterns

```tau
# FSM state (SBF conjunctions)
state_A[t] = cond1 & cond2'

# Counter (toggle on event)
count[t] = (event & count[t-1]') | (event' & count[t-1])

# Conditional (boolean gating)
result[t] = (cond & val_true) | (cond' & val_false)

# Accumulator (bitvector sum)
sum[t] = sum[t-1] + value && sum[0] = {0}:bv[16]
```

## 📊 Results Summary

| Demo | States | Transitions | Coverage |
|------|--------|-------------|----------|
| Alignment | 4 | 4 | 100% |
| Intelligent Agent | 4 | 8 | 100% |
| Virtue Shares | 3 | 4 | 100% |

---

*Part of the Deflationary Agent Project - Formal Specifications for AI Alignment*
