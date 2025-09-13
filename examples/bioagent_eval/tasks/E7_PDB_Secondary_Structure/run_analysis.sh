#!/bin/bash

# PDB Secondary Structure Analysis Pipeline
# This script analyzes PDB files to count beta sheets using DSSP

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Output file
RESULTS_FILE="$SCRIPT_DIR/results.csv"

echo "Starting PDB secondary structure analysis pipeline..."
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
        
        # Create working directory for this variant
        work_dir="$SCRIPT_DIR/data_output/variant_$variant"
        mkdir -p "$work_dir"
        
        # Find PDB file in variant folder
        pdb_file=$(find "$variant_folder" -name "*.pdb" -type f | head -n 1)
        
        if [[ -n "$pdb_file" ]]; then
            pdb_name=$(basename "$pdb_file" .pdb)
            echo "Found PDB file: $pdb_name"
            
            # Run secondary structure analysis
            echo "Analyzing secondary structure..."
            result=$(python3 "$SCRIPT_DIR/analyze_secondary_structure.py" "$pdb_file" --output-dir "$work_dir" | grep -o '<answer>.*</answer>' | sed 's/<answer>\(.*\)<\/answer>/\1/' 2>/dev/null || echo "ERROR")
            
            if [[ "$result" != "ERROR" && -n "$result" ]]; then
                echo "$variant,$result" >> "$RESULTS_FILE"
                echo "Variant $variant result: $result beta sheets"
            else
                echo "Error: Failed to analyze structure for variant $variant"
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