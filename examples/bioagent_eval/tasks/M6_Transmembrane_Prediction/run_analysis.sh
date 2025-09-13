#!/bin/bash

# Transmembrane Helix Analysis Pipeline
# This script runs transmembrane helix prediction for all variant folders

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/predict_tm_helices.py"

# Output file
RESULTS_FILE="$SCRIPT_DIR/results.csv"

echo "Starting transmembrane helix analysis pipeline..."
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
        
        # Run the Python script and capture the result
        result=$(python "$PYTHON_SCRIPT" "$variant_folder" | grep -o '<answer>.*</answer>' | sed 's/<answer>\(.*\)<\/answer>/\1/')
        
        if [[ -n "$result" ]]; then
            echo "$variant,$result" >> "$RESULTS_FILE"
            echo "Variant $variant result: $result"
        else
            echo "Error: No result found for variant $variant"
            echo "$variant,ERROR" >> "$RESULTS_FILE"
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