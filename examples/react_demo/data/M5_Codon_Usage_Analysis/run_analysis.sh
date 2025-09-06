#!/bin/bash

# Run codon usage analysis for all variants
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_FILE="${SCRIPT_DIR}/results.csv"

echo "M5 Codon Usage Analysis Pipeline"
echo "Results: $RESULTS_FILE"

# Initialize results file
echo "variant,result" > "$RESULTS_FILE"
mkdir -p "${SCRIPT_DIR}/data_output"
chmod +x "${SCRIPT_DIR}/process_variant.sh"

# Process variants 1-5
for variant in {1..5}; do
    echo "Processing variant $variant..."
    
    if [ -d "${SCRIPT_DIR}/variant_${variant}" ]; then
        RESULT=$(bash "${SCRIPT_DIR}/process_variant.sh" "$variant" 2>&1 | tail -1)
        echo "${variant},${RESULT:-No_Result}" >> "$RESULTS_FILE"
        echo "Variant $variant: $RESULT"
    else
        echo "${variant},Variant_Not_Found" >> "$RESULTS_FILE"
        echo "Variant $variant: Not found"
    fi
done

echo
echo "Final Results:"
cat "$RESULTS_FILE"