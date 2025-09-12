#!/bin/bash

# Analysis pipeline for FASTA Length Statistics task.
# Runs sequence length analysis for all variants and generates results.csv.

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting FASTA Length Statistics analysis..."
echo "Working directory: $SCRIPT_DIR"

# Initialize results file
RESULTS_FILE="results.csv"
echo "variant,result" > "$RESULTS_FILE"

# Process each variant folder
for variant_dir in variant_*; do
    if [[ -d "$variant_dir" ]]; then
        echo "Processing $variant_dir..."
        
        # Extract variant number from directory name
        variant_num=$(echo "$variant_dir" | sed 's/variant_//')
        
        # Check if variant directory contains FASTA files
        fasta_count=$(find "$variant_dir" -name "*.fasta" | wc -l)
        
        if [[ $fasta_count -eq 0 ]]; then
            echo "Warning: No FASTA files found in $variant_dir"
            echo "$variant_num,0" >> "$RESULTS_FILE"
            continue
        fi
        
        echo "  Found $fasta_count FASTA files"
        
        # Run the Python analysis script
        echo "  Running length analysis..."
        result=$(python3 analyze_fasta_lengths.py "$variant_dir" 2>/dev/null | grep -o '<answer>[^<]*</answer>' | sed 's/<answer>\([^<]*\)<\/answer>/\1/' || echo "0")
        
        echo "  Result: $result"
        echo "$variant_num,$result" >> "$RESULTS_FILE"
        
        echo "  Completed $variant_dir"
        echo ""
    fi
done

echo "Analysis completed!"
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "Final results:"
cat "$RESULTS_FILE"