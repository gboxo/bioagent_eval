#!/bin/bash

# Protein Complex Interface Analysis Pipeline
# This script analyzes inter-chain contacts in protein complexes

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Output file
RESULTS_FILE="$SCRIPT_DIR/results.csv"

echo "Starting protein complex interface analysis pipeline..."
echo "Results will be saved to: $RESULTS_FILE"

# Create results file with header
echo "variant,result" > "$RESULTS_FILE"

# Create data_output directory if needed
mkdir -p "$SCRIPT_DIR/data_output"

# Process each variant folder
for variant in 1 2 3 4 5; do
    variant_folder="$SCRIPT_DIR/variant_$variant"
    
    if [[ -d "$variant_folder" ]]; then
        echo ""
        echo "Processing variant_$variant..."
        echo "================================"
        
        # Find PDB file in variant folder
        pdb_file=$(find "$variant_folder" -name "*.pdb" -type f | head -n 1)
        
        if [[ -n "$pdb_file" ]]; then
            pdb_name=$(basename "$pdb_file" .pdb)
            echo "Found PDB file: $pdb_name"
            
            # Run interface analysis
            echo "Analyzing protein complex interface..."
            result=$(python3 "$SCRIPT_DIR/analyze_interface.py" "$pdb_file" | grep -o '<answer>.*</answer>' | sed 's/<answer>\(.*\)<\/answer>/\1/' 2>/dev/null || echo "ERROR")
            
            if [[ "$result" != "ERROR" && -n "$result" ]]; then
                echo "$variant,$result" >> "$RESULTS_FILE"
                echo "Variant $variant result: $result inter-chain contacts"
            else
                echo "Error: Failed to analyze interface for variant $variant"
                echo "$variant,ERROR" >> "$RESULTS_FILE"
            fi
        else
            echo "Error: No PDB file found in $variant_folder"
            echo "$variant,NO_PDB_FILE" >> "$RESULTS_FILE"
        fi
        
    else
        echo "Warning: variant_$variant folder not found"
        echo "$variant,FOLDER_NOT_FOUND" >> "$RESULTS_FILE"
    fi
done

echo ""
echo "Analysis complete!"
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "Final results:"
echo "=============="
cat "$RESULTS_FILE"

echo ""
echo "Analysis pipeline completed."
echo "Working files can be found in: $SCRIPT_DIR/data_output/"