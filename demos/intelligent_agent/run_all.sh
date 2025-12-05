#!/bin/bash
# ============================================================================
# INTELLIGENT AGENT DEMO - Q-Learning FSM + Smart Entry/Exit
# ============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAU_BIN="${SCRIPT_DIR}/../../tau-lang-latest/build-Release/tau"

if [ ! -x "$TAU_BIN" ]; then
    echo "❌ Tau binary not found at $TAU_BIN" >&2
    exit 1
fi

cd "$SCRIPT_DIR"
rm -rf outputs/*

printf "\n\e[1;96m==============================================\e[0m\n"
printf "\e[1;97m INTELLIGENT DEFLATIONARY AGENT DEMO \e[0m\n"
printf "\e[1;96m==============================================\e[0m\n\n"

printf "\e[1;92m▶ Running intelligent_deflationary_agent.tau\e[0m\n"
"$TAU_BIN" < intelligent_deflationary_agent.tau > /dev/null
printf "   ✅ Complete\n\n"

print_series() {
    local label="$1" file="$2"
    if [ -f "$file" ]; then
        printf "\e[1;94m%-18s\e[0m %s\n" "$label" "$(tr '\n' ' ' < "$file")"
    else
        printf "\e[1;91m%-18s missing (%s)\e[0m\n" "$label" "$file"
    fi
}

printf "\e[1;95mINPUTS\e[0m\n"
print_series "Price" "inputs/price_signal.in"
print_series "EETF" "inputs/eetf_high.in"
print_series "Volume OK" "inputs/volume_ok.in"
print_series "Scarcity" "inputs/scarcity.in"
printf "\n"

printf "\e[1;95mDECISIONS\e[0m\n"
print_series "Position" "outputs/position.out"
print_series "Buy" "outputs/buy.out"
print_series "Sell" "outputs/sell.out"
print_series "SmartEntry" "outputs/smart_entry.out"
print_series "SmartExit" "outputs/smart_exit.out"
printf "\n"

printf "\e[1;95mFSM STATES\e[0m\n"
print_series "Idle_Low" "outputs/fsm_idle_low.out"
print_series "Idle_High" "outputs/fsm_idle_high.out"
print_series "Pos_Low" "outputs/fsm_pos_low.out"
print_series "Pos_High" "outputs/fsm_pos_high.out"
printf "\n"

printf "\e[1;95mCOUNTERS\e[0m\n"
print_series "Timer b0" "outputs/timer_b0.out"
print_series "Timer b1" "outputs/timer_b1.out"
print_series "Trades b0" "outputs/trade_b0.out"
print_series "Cumulative" "outputs/cumulative.out"
printf "\n"

printf "\e[1;95mTRADE SUMMARY\e[0m\n"
cat <<'ASCII'
Trade 1: Enter t=5 (scarcity=72) → Exit t=6 (scarcity=78)
Trade 2: Enter t=7 (scarcity=85) → Exit t=9 (scarcity=100)
Trade 3: Enter t=12 (scarcity=140) → Exit t=14 (scarcity=180)
Trade 4: Enter t=15 (scarcity=180) → Hold...
ASCII
printf "\nLogs written under \e[1moutputs/\e[0m\n"
