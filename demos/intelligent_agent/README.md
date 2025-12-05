# 🤖 Intelligent Deflationary Agent Demo

> **Demonstrating Q-Learning FSM concepts in Tau Language formal specifications**

This demo showcases an intelligent deflationary agent that makes strategic decisions based on market conditions, using concepts from reinforcement learning and pathfinding.

## 📁 Structure

```
demos/intelligent_agent/
├── inputs/
│   ├── price_signal.in   # 0=dip, 1=spike
│   ├── eetf_high.in      # Network ethics factor
│   ├── volume_ok.in      # Liquidity available
│   └── scarcity.in       # Scarcity multiplier (bv[16])
├── outputs/              # Generated traces
├── intelligent_deflationary_agent.tau
├── astar_agent.tau       # Simpler version
├── run_all.sh
└── README.md
```

## 🚀 Quick Start

```bash
chmod +x run_all.sh
./run_all.sh
```

## 🧠 Intelligence Features

### 1. Q-Learning State Encoding (4 states)

| State | Encoding | Description | Optimal Action |
|-------|----------|-------------|----------------|
| IDLE_LOW | `o0'&i1'` | No position, low EETF | WAIT |
| IDLE_HIGH | `o0'&i1` | No position, high EETF | **ENTER** on dip |
| POS_LOW | `o0&i1'` | In position, EETF dropped | **EXIT** |
| POS_HIGH | `o0&i1` | In position, high EETF | HOLD or EXIT on spike |

### 2. Smart Entry Logic

```tau
oC[t] = o0[t-1]' & i1[t] & i2[t] & i0[t]'
```
- Not already in position (`o0[t-1]'`)
- EETF is high (`i1[t]`) - ethics premium active
- Volume is OK (`i2[t]`) - liquidity available
- Price is dipping (`i0[t]'`) - buy low

### 3. Smart Exit Logic

```tau
oD[t] = o0[t-1] & i0[t]
```
- Currently in position (`o0[t-1]`)
- Price is spiking (`i0[t]`) - sell high

### 4. Position Timer

2-bit counter tracks holding duration:
```tau
o8[t] = o0[t] & o8[t-1]'                                    # bit 0
o9[t] = o0[t] & ((o9[t-1] & o8[t-1]') | (o9[t-1]' & o8[t-1])) # bit 1
```

### 5. Trade Counter

Tracks number of completed trades:
```tau
oA[t] = (o2[t] & oA[t-1]') | (o2[t]' & oA[t-1])  # bit 0
oB[t] = ...  # bit 1
```

## 📊 Example Execution

```
INPUTS (t=0..14)
Price Signal: 0 0 1 1 0 1 0 0 1 1 1 0 0 1 0  
EETF High:    0 0 0 1 1 1 1 1 1 1 1 1 1 1 1  
Scarcity:     60 61 62 65 68 72 78 85 92 100 110 125 140 160 180

AGENT DECISIONS
Position:     0 0 0 0 0 1 0 1 1 0 0 0 1 1 0 1
Buy Signal:   0 0 0 0 0 1 0 1 0 0 0 0 1 0 0 1
Sell Signal:  0 0 0 0 0 0 1 0 0 1 0 0 0 0 1 0

TRADES
Trade 1: Enter t=5 (scarcity=72) → Exit t=6 (scarcity=78)
Trade 2: Enter t=7 (scarcity=85) → Exit t=9 (scarcity=100)
Trade 3: Enter t=12 (scarcity=140) → Exit t=14 (scarcity=180)
```

## 🔬 Key Learnings

### Tau Language Execution Mode Limitations

1. **No ternary `?` operator** - Use boolean algebra instead
2. **No `>` comparison inline** - BV comparisons only in `solve`
3. **State must be SBF or BV** - No enums in execution
4. **Recurrence must be well-formed** - All outputs defined each step

### Working Patterns

```tau
# FSM state encoding (use SBF conjunctions)
state_A[t] = condition_1 & condition_2'

# Counters (toggle on event)
counter[t] = (event & counter[t-1]') | (event' & counter[t-1])

# Conditional logic (use gating)
result[t] = (condition & value_if_true) | (condition' & value_if_false)
```

## 📐 Mathematical Foundation

The agent implements concepts from:

1. **Q-Learning**: Pre-computed Q-values for state-action pairs
2. **A* Pathfinding**: State space navigation toward optimal (high scarcity) states
3. **Bellman Equation**: V(s) = max_a { R(s,a) + γV(s') }

### Optimal Policy (embedded in logic)

| State | Q(HOLD) | Q(ENTER) | Q(EXIT) | Best Action |
|-------|---------|----------|---------|-------------|
| IDLE_LOW | 50 | 10 | 0 | HOLD |
| IDLE_HIGH | 40 | **100** | 0 | ENTER |
| POS_LOW | 30 | 0 | **70** | EXIT |
| POS_HIGH | **80** | 0 | **90** | HOLD/EXIT |

## 🔗 Integration with Alignment Theorem

This agent demonstrates the economic principles:

1. **Scarcity Premium**: Agent captures increasing scarcity values
2. **EETF Awareness**: Only enters when network ethics is high
3. **Deflationary Benefit**: Cumulative value grows as scarcity increases
4. **Ethical Alignment**: Profits from ethical network behavior

---

*Part of the Deflationary Agent Project - Demonstrating AI Intelligence Through Formal Specifications*

