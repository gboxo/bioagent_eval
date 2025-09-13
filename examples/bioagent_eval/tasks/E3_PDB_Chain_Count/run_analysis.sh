#!/bin/bash

# Analysis pipeline for PDB Chain Count task.
# Runs chain analysis for all PDB variants and generates results.csv.

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting PDB Chain Count analysis..."
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
        
        # Find the PDB file in the variant directory
        pdb_file=$(find "$variant_dir" -name "*.pdb" | head -1)
        
        if [[ -z "$pdb_file" ]]; then
            echo "Warning: No PDB file found in $variant_dir"
            echo "$variant_num," >> "$RESULTS_FILE"
            continue
        fi
        
        # Extract PDB ID from filename (remove .pdb extension)
        pdb_id=$(basename "$pdb_file" .pdb)
        echo "  PDB ID: $pdb_id"
        echo "  PDB file: $pdb_file"
        
        # Run the Python analysis script
        echo "  Running chain analysis..."
        result=$(python3 analyze_pdb_chains.py "$pdb_file" 2>/dev/null | grep -o '<answer>[^<]*</answer>' | sed 's/<answer>\([^<]*\)<\/answer>/\1/' || echo "")
        
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