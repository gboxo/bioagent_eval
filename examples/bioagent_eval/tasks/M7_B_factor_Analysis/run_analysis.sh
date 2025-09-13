#!/usr/bin/env bash
set -euo pipefail

# Orchestrate analysis across all variant folders and emit results.csv
# Layout expected:
#   examples/bioagent_eval/tasks/M7_B_factor_Analysis/
#     variant_1/*.pdb
#     variant_2/*.pdb
#     ...

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_DIR="$SCRIPT_DIR"
SCRIPTS_DIR="$TASK_DIR"

ANALYZER_PY="$SCRIPTS_DIR/analyze_b_factors.py"
PREP_SH="$SCRIPTS_DIR/prepare_data.sh"

RESULTS_CSV="$TASK_DIR/results.csv"

echo "variant, result" > "$RESULTS_CSV"

for VARIANT_DIR in "$TASK_DIR"/variant_*; do
  [ -d "$VARIANT_DIR" ] || continue
  VARIANT_NAME=$(basename "$VARIANT_DIR")
  VARIANT_NUM=${VARIANT_NAME##variant_}

  # Prepare data (if any retrieval/derivation is needed)
  bash "$PREP_SH" "$VARIANT_DIR"

  # Find a PDB file inside the variant directory
  PDB_FILE=$(ls "$VARIANT_DIR"/*.pdb 2>/dev/null | head -n 1 || true)
  if [[ -z "$PDB_FILE" ]]; then
    echo "Warning: No PDB file found in $VARIANT_DIR; writing 0" >&2
    RESULT=0
  else
    RESULT=$(python3 "$ANALYZER_PY" --pdb "$PDB_FILE")
  fi

  echo "$VARIANT_NUM, $RESULT" >> "$RESULTS_CSV"
  echo "Processed $VARIANT_NAME -> $RESULT"

done

echo "Results written to: $RESULTS_CSV"
