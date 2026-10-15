#!/usr/bin/env bash
# Pilot: run the two-stage pipeline on Buffett, Marks and Soros (style contrast).
# Every input is the master's own first-hand writing.
# Needs ANTHROPIC_API_KEY + ANTHROPIC_MODEL, or LLM_PROVIDER=openai with OPENAI_*.
# Usage: scripts/pilot_run.sh [OUT_DIR] [extra cli args, e.g. --dry-run]
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=${1:-/mnt/project-files/guru-rubrics/runs/pilot_20261015}; shift || true
MAT=${MATERIALS:-/mnt/project-files/guru-rubrics/materials_20261015/text}
B=corpus/buffett/processed

run() {
  local slug=$1 master=$2; shift 2
  python3 -m rubric_pipeline.cli --master "$master" --framework configs/tradebank.json \
    --out "$OUT/$slug" --documents "$@" ${EXTRA_ARGS:-} "${CLI_ARGS[@]}"
}
CLI_ARGS=("$@")

# Buffett: letters with the most marketable-securities content (Mr. Market, risk, concentration).
run buffett "Warren Buffett" $B/1987.txt $B/1992.txt $B/1993.txt $B/1996.txt
# Marks: four memos covering market psychology, cycles/temperature, value and forecasting.
# (The Indispensability of Risk is left out: much of it quotes a chess article.)
run marks "Howard Marks" $MAT/marks/marks.mr_market_miscalculates.txt \
  $MAT/marks/marks.taking_the_temperature.txt $MAT/marks/marks.the_calculus_of_value.txt \
  $MAT/marks/marks.the_folly_of_certainty.txt
# Soros: 2014 reflexivity essay (georgesoros.com). O'Neil waits for his own books.
run soros "George Soros" $MAT/soros/soros.fallibility_reflexivity_2014.txt
