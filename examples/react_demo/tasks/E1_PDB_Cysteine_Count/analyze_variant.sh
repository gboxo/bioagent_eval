#!/bin/bash
#
# Script to analyze a single variant and count cysteine residues.
# Usage: ./analyze_variant.sh <variant_number>
#

set -e  # Exit on any error

# Check if variant number is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <variant_number>" >&2
    exit 1
fi

VARIANT_NUM=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANT_DIR="${SCRIPT_DIR}/variant_${VARIANT_NUM}"

# Check if variant directory exists
if [ ! -d "$VARIANT_DIR" ]; then
    echo "Error: Variant directory $VARIANT_DIR does not exist" >&2
    exit 1
fi

# Find PDB file in the variant directory
PDB_FILE=$(find "$VARIANT_DIR" -name "*.pdb" -type f | head -1)

if [ -z "$PDB_FILE" ]; then
    echo "Error: No PDB file found in $VARIANT_DIR" >&2
    exit 1
fi

# Run the Python script to count cysteine residues
RESULT=$(python3 "${SCRIPT_DIR}/count_cysteine.py" "$PDB_FILE")

# Extract the number from <answer>X</answer> format
CYSTEINE_COUNT=$(echo "$RESULT" | grep -o '<answer>[0-9]*</answer>' | sed 's/<answer>\([0-9]*\)<\/answer>/\1/')

echo "$CYSTEINE_COUNT"