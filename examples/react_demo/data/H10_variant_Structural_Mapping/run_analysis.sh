#!/bin/bash

# Variant Structural Mapping Analysis Pipeline
# Analyzes RSA values to find the most buried residue variant for each dataset

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
    
    # Check for mkdssp
    if ! command -v mkdssp &> /dev/null; then
        echo "Error: mkdssp is not installed or not in PATH"
        echo "Please install DSSP (Dictionary of Secondary Structure of Proteins)"
        exit 1
    fi
    
    # Check for Python and Biopython
    if ! python3 -c "import Bio.PDB" &> /dev/null; then
        echo "Error: Biopython is not installed"
        echo "Please install Biopython: pip install biopython"
        exit 1
    fi
    
    echo "All dependencies are available."
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
    
    # Check if there are PDB files in the variant directory
    pdb_count=$(find "$variant_dir" -name "*.pdb" -type f | wc -l)
    
    if [ "$pdb_count" -eq 0 ]; then
        echo "Warning: No PDB files found in $variant_dir, skipping..."
        return
    fi
    
    echo "Found $pdb_count PDB file(s) in $variant_dir"
    
    # Run the RSA analysis
    result=$(python3 analyze_rsa.py "$variant_dir")
    
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

echo "Starting Variant Structural Mapping Analysis"
echo "============================================="
echo

# Check dependencies
check_dependencies
echo

# Make Python script executable
chmod +x analyze_rsa.py

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

# Clean up temporary DSSP files (optional)
echo
echo "Cleaning up temporary files..."
find . -name "*.dssp" -delete 2>/dev/null || true
echo "Pipeline completed successfully."