#!/bin/bash

# Analysis pipeline for UniProt Signal Peptides task.
# Runs signal peptide analysis for all protein variants and generates results.csv.

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting UniProt Signal Peptides analysis..."
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
        
        # Find the UniProt ID from the FASTA file in the variant directory
        fasta_file=$(find "$variant_dir" -name "*.fasta" | head -1)
        
        if [[ -z "$fasta_file" ]]; then
            echo "Warning: No FASTA file found in $variant_dir"
            echo "$variant_num,0" >> "$RESULTS_FILE"
            continue
        fi
        
        # Extract UniProt ID from filename (remove .fasta extension)
        uniprot_id=$(basename "$fasta_file" .fasta)
        echo "  UniProt ID: $uniprot_id"
        
        # Run the Python analysis script
        echo "  Running signal peptide analysis..."
        result=$(python3 analyze_signal_peptides.py "$uniprot_id" 2>/dev/null | grep -o '<answer>[^<]*</answer>' | sed 's/<answer>\([^<]*\)<\/answer>/\1/' || echo "0")
        
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