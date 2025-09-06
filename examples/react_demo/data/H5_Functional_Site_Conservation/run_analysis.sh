#!/bin/bash

# Functional Site Conservation Analysis Pipeline
# This script runs the conservation analysis for all variants sequentially

set -e  # Exit on any error

# Configuration
BASE_DIR="/Users/gerard/inspect_ai/examples/react_demo/data/H5_Functional_Site_Conservation"
PYTHON_SCRIPT="$BASE_DIR/analyze_conservation.py"
RESULTS_FILE="$BASE_DIR/results.csv"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Check if MAFFT is available
if ! command -v mafft &> /dev/null; then
    echo "Error: MAFFT is not installed or not in PATH"
    echo "Please install MAFFT: https://mafft.cbrc.jp/alignment/software/"
    exit 1
fi

# Create results CSV file header
echo "variant,result" > "$RESULTS_FILE"

echo "Starting Functional Site Conservation Analysis..."
echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Process each variant
for variant in 1 2 3 4 5; do
    echo "======================================="
    echo "Processing Variant $variant"
    echo "======================================="
    
    variant_dir="$BASE_DIR/variant_$variant"
    
    # Check if variant directory exists
    if [ ! -d "$variant_dir" ]; then
        echo "Warning: Variant directory $variant_dir does not exist, skipping..."
        echo "$variant,ERROR: Directory not found" >> "$RESULTS_FILE"
        continue
    fi
    
    # Count FASTA files in variant directory
    fasta_count=$(find "$variant_dir" -name "*.fasta" | wc -l)
    echo "Found $fasta_count FASTA files in variant_$variant"
    
    if [ $fasta_count -eq 0 ]; then
        echo "Warning: No FASTA files found in variant_$variant, skipping..."
        echo "$variant,ERROR: No FASTA files found" >> "$RESULTS_FILE"
        continue
    fi
    
    # Run Python analysis script
    echo "Running conservation analysis..."
    
    if result=$(python3 "$PYTHON_SCRIPT" "$variant" 2>&1); then
        # Extract the result line
        result_line=$(echo "$result" | grep "Result for variant" | sed "s/.*: //")
        if [ -z "$result_line" ]; then
            result_line=""
        fi
        
        echo "Analysis completed successfully"
        echo "Result: $result_line"
        echo "$variant,$result_line" >> "$RESULTS_FILE"
    else
        echo "Error running analysis for variant $variant:"
        echo "$result"
        echo "$variant,ERROR: Analysis failed" >> "$RESULTS_FILE"
    fi
    
    echo ""
done

echo "======================================="
echo "Analysis Complete!"
echo "======================================="
echo ""
echo "Results summary:"
cat "$RESULTS_FILE"

echo ""
echo "Detailed results saved to: $RESULTS_FILE"