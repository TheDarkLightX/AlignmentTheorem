# 🔐 Virtue Shares Demo

> **Demonstrating HEX-style time-locking with vShares calculation in Tau**

This demo shows a simplified version of the Virtue Shares library - a core primitive for the VCC (Virtuous Cycle Compounder) architecture.

## 📁 Structure

```
demos/virtue_shares/
├── inputs/
│   ├── create_lock.in   # Signal to create lock
│   ├── early_exit.in    # Signal for early exit
│   ├── eetf_high.in     # Network ethics factor
│   └── time.in          # Time counter (bv[16])
├── outputs/             # Generated traces
├── virtue_shares_demo.tau
└── README.md
```

## 🚀 Quick Start

```bash
cd demos/virtue_shares
../../tau-lang-latest/build-Release/tau < virtue_shares_demo.tau
```

## 📊 Example Execution

```
INPUTS
Create Lock: 1 0 0 0 0 0 0 0 0 0
Early Exit:  0 0 0 0 0 0 1 0 0 0

OUTPUTS
Lock Active:   0 1 1 1 1 1 1 0 0 0 0 
Lock Expired:  0 0 0 0 0 0 0 1 0 0 0 
vShares:       0 100 200 300 400 500 600 700 800 900 1000 
Boost:         100 110 120 130 140 150 160 170 180 190 200 
FSM Unlocked:  0 0 0 0 0 0 0 0 1 1 1 
FSM Locked:    0 1 1 1 1 1 1 0 0 0 0 
FSM Exited:    0 0 0 0 0 0 0 1 0 0 0 
```

## 🔄 FSM States

| State | Description | Transition |
|-------|-------------|------------|
| UNLOCKED | No active lock | → LOCKED on create |
| LOCKED | Lock is active, vShares accumulating | → EXITED on early_exit |
| EXITED | Lock terminated (penalty applies) | → UNLOCKED after |

## 📐 Core Formulas

```
vShares[t] = vShares[t-1] + 100 (while locked)
Boost[t] = Boost[t-1] + 10 (while locked)
```

In the full library:
- `vShares = Amount × sqrt(Duration/MaxDuration) × DecayFactor × EETF`
- `Boost = 100 + 150 × (vShares_ratio / 256)` (max 250)

## 🔗 Connection to VCC

This primitive feeds into:
1. **Voting Power** - vShares determine governance weight
2. **Fee Share** - Proportional to vShares
3. **Burn Engine** - Penalties go to burn (not redistributed)

---

*Part of the Deflationary Agent Project*

