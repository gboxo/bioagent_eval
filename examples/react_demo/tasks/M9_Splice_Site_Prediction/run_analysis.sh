#!/bin/bash

# M9_Splice_Site_Prediction Analysis Pipeline
# This script processes all variants and generates results.csv

set -e  # Exit on any error

echo "=== M9 Splice Site Prediction Analysis ==="
echo "Starting analysis pipeline..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create results.csv header
echo "variant,result" > results.csv

# Initialize results array
declare -a results

# Process each variant
for variant_num in {1..5}; do
    echo ""
    echo "=== Processing Variant $variant_num ==="
    
    variant_dir="variant_$variant_num"
    
    if [ ! -d "$variant_dir" ]; then
        echo "Warning: $variant_dir directory not found, skipping..."
        results[$variant_num]=0
        continue
    fi
    
    if [ ! -f "$variant_dir/config.json" ]; then
        echo "Warning: config.json not found in $variant_dir, skipping..."
        results[$variant_num]=0
        continue
    fi
    
    # Read gene name from config.json
    gene_name=$(python3 -c "
import json
with open('$variant_dir/config.json', 'r') as f:
    config = json.load(f)
print(config.get('gene_name', 'UNKNOWN'))
")
    
    echo "Processing gene: $gene_name"
    
    # Run the analysis
    if output=$(python3 analyze_exon_count.py "$gene_name" 2>&1); then
        result=$(echo "$output" | sed -n 's/.*<answer>\([0-9]*\)<\/answer>.*/\1/p')
        if [ -z "$result" ]; then
            result=0
        fi
        if [[ "$result" =~ ^[0-9]+$ ]]; then
            results[$variant_num]=$result
            echo "Variant $variant_num ($gene_name): $result exons"
        else
            echo "Error: Invalid result for variant $variant_num, setting to 0"
            results[$variant_num]=0
        fi
    else
        echo "Error: Failed to analyze variant $variant_num, setting to 0"
        results[$variant_num]=0
    fi
done

echo ""
echo "=== Writing Results ==="

# Write results to CSV
for variant_num in {1..5}; do
    echo "$variant_num,${results[$variant_num]}" >> results.csv
done

echo "Results written to results.csv"
echo ""
echo "=== Analysis Complete ==="
echo "Results summary:"
cat results.csv

# Display final summary
echo ""
echo "=== Final Summary ==="
echo "Variant 1 (BRCA1): ${results[1]} exons"
echo "Variant 2 (TP53): ${results[2]} exons"
echo "Variant 3 (CFTR): ${results[3]} exons"
echo "Variant 4 (DMD): ${results[4]} exons"
echo "Variant 5 (APOE): ${results[5]} exons"