#!/bin/bash

# Druggability Assessment Pipeline
# Runs fpocket analysis on each variant to find the protein with highest druggability score

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
    
    # Check if there are PDB files in the variant directory
    pdb_count=$(find "$variant_dir" -name "*.pdb" -type f | wc -l)
    
    if [ "$pdb_count" -eq 0 ]; then
        echo "Warning: No PDB files found in $variant_dir, skipping..."
        return
    fi
    
    echo "Found $pdb_count PDB files in $variant_dir"
    
    # Run the druggability analysis
    result=$(python3 analyze_druggability.py "$variant_dir")
    
    if [ $? -eq 0 ] && [ "$result" != "ERROR" ] && [ -n "$result" ]; then
        echo "Result for variant $variant_num: $result"
        echo "$variant_num,$result" >> results.csv
    else
        echo "Error: Failed to analyze $variant_dir"
        echo "$variant_num,ERROR" >> results.csv
    fi
    
    echo "Completed processing $variant_dir"
    echo
}

echo "Starting Druggability Assessment Pipeline"
echo "=========================================="
echo

# Check if fpocket is available
if ! command -v fpocket &> /dev/null; then
    echo "Error: fpocket is not installed or not in PATH"
    exit 1
fi

echo "fpocket found: $(which fpocket)"
echo

# Process each variant
for variant in 1 2 3 4 5; do
    run_variant_analysis $variant
done

echo "=========================================="
echo "Analysis complete. Results saved to results.csv"
echo

# Display final results
echo "Final Results:"
cat results.csv

# Clean up any temporary files (optional)
echo
echo "Cleaning up temporary files..."
# Note: We keep the fpocket output directories as they may be useful for further analysis