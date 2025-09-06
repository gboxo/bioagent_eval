#!/bin/bash

# H9 Conformational Ensemble Analysis Pipeline
# This script processes all variant folders and calculates RMSF for conformational ensembles

echo "Starting H9 Conformational Ensemble Analysis"
echo "=============================================="

# Set the base directory
BASE_DIR=$(dirname "$(readlink -f "$0")")
cd "$BASE_DIR"

# Create data_output directory if it doesn't exist
mkdir -p data_output

# Initialize results file with header
RESULTS_FILE="results.csv"
echo "variant,result" > "$RESULTS_FILE"

# Process each variant folder
for variant_dir in variant_*; do
    if [ -d "$variant_dir" ]; then
        # Extract variant number from directory name
        variant_num=$(echo "$variant_dir" | sed 's/variant_//')
        
        echo "Processing $variant_dir (variant $variant_num)..."
        
        # Run the analysis
        result=$(python3 process_variant.py "$variant_dir" 2>&1 | grep "Result:" | cut -d' ' -f2)
        
        # Check if we got a valid result
        if [ -z "$result" ] || [ "$result" = "ERROR" ]; then
            echo "Error processing $variant_dir"
            result="ERROR"
        else
            echo "Result for variant $variant_num: $result"
        fi
        
        # Append to results file
        echo "$variant_num,$result" >> "$RESULTS_FILE"
        
        echo "Completed $variant_dir"
        echo ""
    fi
done

echo "Analysis complete. Results written to $RESULTS_FILE"
echo ""
echo "Summary of results:"
echo "===================="
cat "$RESULTS_FILE"