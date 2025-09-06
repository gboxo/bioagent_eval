#!/bin/bash

# Process a single variant
if [ $# -ne 1 ]; then
    echo "Usage: $0 <variant_number>"
    exit 1
fi

VARIANT_NUM=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANT_DIR="${SCRIPT_DIR}/variant_${VARIANT_NUM}"

echo "Processing variant $VARIANT_NUM..."

# Run analysis and extract result from <answer> tags
RESULT=$(python3 "${SCRIPT_DIR}/analyze_codon_usage.py" "$VARIANT_DIR" 2>&1 | sed -n 's/.*<answer>\(.*\)<\/answer>.*/\1/p')

echo "Result: $RESULT"
echo "$RESULT"