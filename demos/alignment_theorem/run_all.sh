#!/bin/bash
# ============================================================================
# ALIGNMENT THEOREM DEMO - Run All Specs
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAU_BIN="${SCRIPT_DIR}/../../tau-lang-latest/build-Release/tau"

if ! command -v column >/dev/null 2>&1; then
    column() { cat; }
fi

if [ ! -x "$TAU_BIN" ]; then
    echo "❌ Tau binary not found at: $TAU_BIN"
    echo "   (build it via tau-lang-latest/build.sh or adjust TAU_BIN)"
    exit 1
fi

printf "\n\e[1;96m======================================================\e[0m\n"
printf "\e[1;97m ALIGNMENT THEOREM DEMO  —  DEFALTIONARY ECONOMICS \e[0m\n"
printf "\e[1;96m======================================================\e[0m\n\n"

cd "$SCRIPT_DIR"
rm -rf outputs/*

SPECS=(
  "01_scarcity_calculator.tau|Scarcity Multiplier"
  "02_economic_pressure.tau|Economic Pressure"
  "03_ethical_reward.tau|Ethical Reward (Compounding)"
  "04_burn_engine.tau|Deflationary Burn Engine"
)

for entry in "${SPECS[@]}"; do
    spec="${entry%%|*}"; title="${entry#*|}"
    printf "\e[1;92m▶ %s\e[0m (%s)\n" "$spec" "$title"
    "$TAU_BIN" < "$spec" > /dev/null
    printf "   ✅ Completed\n\n"
    sleep 0.1
finally done

printf "\n\e[1;95m==============================================\e[0m\n"
printf "\e[1;97m RESULTS SNAPSHOT\e[0m\n"
printf "\e[1;95m==============================================\e[0m\n\n"

print_series() {
    local label="$1" file="$2"
    if [ -f "$file" ]; then
        printf "\e[1;94m%-18s\e[0m %s\n" "$label" "$(tr '\n' ' ' < "$file")"
    else
        printf "\e[1;91m%-18s missing (%s)\e[0m\n" "$label" "$file"
    fi
}

print_series "Supply" "inputs/supply.in"
print_series "Scarcity" "outputs/scarcity_mult.out"
print_series "Pressure" "outputs/pressure.out"
print_series "Ethical Reward" "outputs/cumulative_reward.out"
print_series "Burn Rate" "outputs/burn_rate.out"
print_series "Total Burned" "outputs/total_burned.out"
printf "\n"

printf "\e[1;95m==============================================\e[0m\n"
printf "\e[1;97m VIRTUOUS CYCLE (Alignment)\e[0m\n"
printf "\e[1;95m==============================================\e[0m\n"
cat <<'ASCII'
    Scarcity ↑          Ethics ↑
        │                   │
        ├── Pressure ───────┘
        │
    Burns ↑ → Supply ↓ → Scarcity ↑ (loop)
ASCII
printf "\nDone. Charts and CSV exports live under \e[1moutputs/\e[0m\n"
