#!/bin/bash

# Epistasis Network Analysis Pipeline
# Analyzes epistatic interactions for each variant dataset

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Initialize results file
echo "variant,result" > results.csv

# Create data_output directory if it doesn't exist
mkdir -p data_output

# Function to run analysis for a single variant
run_variant_analysis() {
    local variant_num=$1
    local variant_dir="variant_$variant_num"
    
    echo "Processing $variant_dir..."
    
    if [ ! -d "$variant_dir" ]; then
        echo "Warning: $variant_dir not found, skipping..."
        return
    fi
    
    # Find the CSV file in the variant directory
    csv_file=$(find "$variant_dir" -name "*.csv" -type f | head -1)
    
    if [ -z "$csv_file" ]; then
        echo "Warning: No CSV file found in $variant_dir, skipping..."
        return
    fi
    
    echo "Found CSV file: $csv_file"
    
    # Run the epistasis analysis
    result=$(python3 analyze_epistasis.py "$csv_file")
    
    if [ $? -eq 0 ] && [ -n "$result" ]; then
        echo "Result for variant $variant_num: $result"
        echo "$variant_num,$result" >> results.csv
    else
        echo "Error: Failed to analyze $variant_dir"
        echo "$variant_num,ERROR" >> results.csv
    fi
    
    echo "Completed processing $variant_dir"
    echo
}

echo "Starting Epistasis Network Analysis Pipeline"
echo "============================================="
echo

# Process each variant
for variant in 1 2 3 4 5; do
    run_variant_analysis $variant
done

echo "============================================="
echo "Analysis complete. Results saved to results.csv"
echo

# Display final results
echo "Final Results:"
cat results.csv