#!/bin/bash
# ============================================================================
# VIRTUE SHARES DEMO - HEX-Style Time Locking
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
printf "\e[1;97m VIRTUE SHARES DEMO\e[0m\n"
printf "\e[1;96m==============================================\e[0m\n\n"

printf "\e[1;92m▶ Running virtue_shares_demo.tau\e[0m\n"
"$TAU_BIN" < virtue_shares_demo.tau > /dev/null
printf "   ✅ Complete\n\n"

print_series() {
    local label="$1" file="$2"
    if [ -f "$file" ]; then
        printf "\e[1;94m%-16s\e[0m %s\n" "$label" "$(tr '\n' ' ' < "$file")"
    else
        printf "\e[1;91m%-16s missing (%s)\e[0m\n" "$label" "$file"
    fi
}

printf "\e[1;95mLOCK STATES\e[0m\n"
print_series "Lock Active" "outputs/lock_active.out"
print_series "Expired" "outputs/lock_expired.out"
print_series "Penalty" "outputs/penalty_triggered.out"
printf "\n"

printf "\e[1;95mVShares & Voting Power\e[0m\n"
print_series "vShares" "outputs/vshares.out"
print_series "Voting" "outputs/voting_power.out"
print_series "Remaining" "outputs/remaining.out"
print_series "Boost" "outputs/boost.out"
printf "\n"

cat <<'ASCII'
FSM Walkthrough:
  UNLOCKED → LOCKED → EXITED
Early exit triggers penalty & expired state.
ASCII
printf "\nOutputs saved under \e[1moutputs/\e[0m\n"
