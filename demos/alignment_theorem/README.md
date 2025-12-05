# 🎯 Alignment Theorem Demo

> **"When scarcity grows without bound and ethics is wired into rewards, being good stops being a choice. It becomes the only way to win."**

Executable Tau Language specifications demonstrating the **Alignment Theorem**.

## 📁 Structure

```
demos/alignment_theorem/
├── inputs/                        # Input data
│   ├── supply.in                 # Token supply (decreasing)
│   ├── eetf.in                   # Ethics factor (100-300)
│   ├── is_ethical.in             # Boolean ethical flag
│   └── participation.in          # Network participation
├── outputs/                       # Generated outputs
├── 01_scarcity_calculator.tau    # Scarcity increases as supply drops
├── 02_economic_pressure.tau      # Pressure = Scarcity × EETF
├── 03_ethical_reward.tau         # Rewards compound under pressure
├── 04_burn_engine.tau            # Burns accelerate with ethics
├── run_all.sh                    # Run all demos
└── README.md
```

## 🚀 Quick Start

```bash
chmod +x run_all.sh
./run_all.sh
```

Or run individually:
```bash
tau < 01_scarcity_calculator.tau
cat outputs/scarcity_mult.out
```

## 📊 Results

### Scarcity Calculator
```
Supply:   1000 980 960 940 920 900 880 860 840 820
Scarcity:   60  61  62  63  65  66  68  69  71  73
```

### Economic Pressure
```
EETF:     100 120 150 180 200 220 250 280 300 300
Pressure:  60  73  93 113 130 145 170 193 213 219
```

### Cumulative Rewards
```
60 → 133 → 226 → 339 → 469 → 614 → 784 → 977 → 1190 → 1409
```

### Burn Dynamics
```
Burn Rate:   20  24  30  36  40  44  50  56  60  60
Total Burned: 20  43  71 104 140 179 223 271 321 370
```

## 🔄 The Virtuous Cycle

```
┌─────────────────────────────────────────────────┐
│  Higher EETF → More Burns → Less Supply        │
│       ↑                          ↓             │
│  Ethics Profitable ← Pressure ← Scarcity       │
└─────────────────────────────────────────────────┘
```

## 📐 Core Equations

- **Scarcity**: `M(t) = 60000 / Supply(t)`
- **Pressure**: `P(t) = M(t) × EETF(t) / 100`
- **Burn Rate**: `R(t) = 20 × EETF(t) / 100` (%)
- **Cumulative**: `C(t) = C(t-1) + Reward(t)`

---

*Part of the Deflationary Agent Project*
