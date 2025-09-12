#!/bin/bash
#
# Main analysis script that processes all variants and creates results.csv
# This script executes the cysteine counting analysis for all 5 variants.
#

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_FILE="${SCRIPT_DIR}/results.csv"

echo "Starting PDB Cysteine Count Analysis..."
echo "======================================="

# Create CSV header
echo "variant,result" > "$RESULTS_FILE"

# Process each variant (1-5)
for variant in {1..5}; do
    echo "Processing variant $variant..."
    
    # Run analysis for this variant
    result=$("${SCRIPT_DIR}/analyze_variant.sh" "$variant")
    
    # Check if result is a valid number
    if [[ "$result" =~ ^[0-9]+$ ]]; then
        echo "$variant,$result" >> "$RESULTS_FILE"
        echo "  -> Variant $variant: $result cysteine residues"
    else
        echo "  -> Error processing variant $variant: $result" >&2
        echo "$variant,ERROR" >> "$RESULTS_FILE"
    fi
done

echo ""
echo "Analysis complete! Results saved to: $RESULTS_FILE"
echo "======================================="
echo "Results summary:"
cat "$RESULTS_FILE"