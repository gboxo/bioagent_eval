#!/bin/bash

# Phylogenetic Distance Analysis Pipeline
# This script runs the phylogenetic distance analysis for all variant folders and generates results.csv

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if MAFFT is installed
if ! command -v mafft &> /dev/null; then
    echo "Error: MAFFT is not installed or not in PATH"
    echo "Please install MAFFT to run this analysis"
    exit 1
fi

# Initialize results file
echo "variant,result" > results.csv

# Process each variant folder
for i in {1..5}; do
    variant_folder="variant_${i}"
    
    if [ -d "$variant_folder" ]; then
        echo "Processing $variant_folder..."
        
        # Run the Python analysis script
        # Capture only the final distance (last line of output)
        result=$(uv run python3 calculate_phylogenetic_distance.py "$variant_folder" 2>/dev/null | tail -n 1)
        echo "Result: $result"
        
        # Handle case where result might be empty or contain error
        if [ -z "$result" ]; then
            result="Error"
        fi
        
        # Append result to CSV
        echo "$i,$result" >> results.csv
        
        echo "Variant $i result: $result"
        echo ""
    else
        echo "Warning: $variant_folder not found, skipping..."
        echo "$i,Folder not found" >> results.csv
    fi
done

echo "Analysis complete. Results saved to results.csv"
echo ""
echo "Results summary:"
cat results.csv