#!/bin/bash

# PDB Ligand Identification Pipeline
# Analyzes PDB files to count unique bound ligands

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Initialize results file
echo "variant,result" > results.csv

# Create data_output directory if it doesn't exist
mkdir -p data_output

# Function to check dependencies
check_dependencies() {
    echo "Checking dependencies..."
    
    # Check for Python and Biopython library
    if ! python3 -c "from Bio.PDB import PDBParser" &> /dev/null; then
        echo "Error: Biopython library is not installed"
        echo "Please install Biopython: pip install biopython"
        exit 1
    fi
    
    echo "Dependencies are available."
}

# Function to run analysis for a single variant
run_variant_analysis() {
    local variant_num=$1
    local variant_dir="variant_$variant_num"
    
    echo "Processing $variant_dir..."
    
    if [ ! -d "$variant_dir" ]; then
        echo "Warning: $variant_dir not found, skipping..."
        return
    fi
    
    # Check if config.json exists
    if [ ! -f "$variant_dir/config.json" ]; then
        echo "Warning: No config.json found in $variant_dir, skipping..."
        return
    fi
    
    echo "Found configuration in $variant_dir"
    
    # Run the ligand analysis
    result=$(python3 analyze_ligands.py "$variant_dir" | tail -1)
    
    if [ $? -eq 0 ] && [ "$result" != "ERROR" ] && [ -n "$result" ]; then
        # Check if result is a number
        if [[ "$result" =~ ^[0-9]+$ ]]; then
            echo "Result for variant $variant_num: $result"
            echo "$variant_num,$result" >> results.csv
        else
            echo "Error: Invalid result format for $variant_dir"
            echo "$variant_num,ERROR" >> results.csv
        fi
    else
        echo "Error: Failed to analyze $variant_dir"
        echo "$variant_num,ERROR" >> results.csv
    fi
    
    echo "Completed processing $variant_dir"
    echo
}

echo "Starting PDB Ligand Identification Pipeline"
echo "==========================================="
echo

# Check dependencies
check_dependencies
echo

# Make Python script executable
chmod +x analyze_ligands.py

# Process each variant (only process existing variants)
for variant in 1 2 3 4 5; do
    if [ -d "variant_$variant" ]; then
        run_variant_analysis $variant
    else
        echo "Skipping variant_$variant (directory not found)"
    fi
done

echo "==========================================="
echo "Analysis complete. Results saved to results.csv"
echo

# Display final results
echo "Final Results:"
cat results.csv

echo
echo "Pipeline completed successfully."