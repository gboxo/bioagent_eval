#!/bin/bash

# Evolutionary Rate Analysis Pipeline
# This script runs dN/dS analysis to detect positive selection in protein evolution

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Output file
RESULTS_FILE="$SCRIPT_DIR/results.csv"

echo "Starting evolutionary rate analysis pipeline..."
echo "Results will be saved to: $RESULTS_FILE"

# Create results file with header
echo "variant,result" > "$RESULTS_FILE"

# Process each variant folder
for variant in 1 2 3 4 5; do
    variant_folder="$SCRIPT_DIR/variant_$variant"
    
    if [[ -d "$variant_folder" ]]; then
        echo ""
        echo "Processing variant_$variant..."
        echo "======================================"
        
        # Create working directory for this variant
        work_dir="$SCRIPT_DIR/data_output/variant_$variant"
        mkdir -p "$work_dir"
        cd "$work_dir"
        
        echo "Working directory: $work_dir"
        
        # Step 1: Retrieve CDS sequences
        echo "Step 1: Retrieving CDS sequences..."
        python "$SCRIPT_DIR/retrieve_cds.py" "$variant_folder" --output "$work_dir" || {
            echo "Warning: CDS retrieval failed for variant $variant"
        }
        
        # Step 2: Consolidate sequences
        echo "Step 2: Consolidating sequences..."
        python "$SCRIPT_DIR/consolidate_sequences.py" "$variant_folder" --output "$work_dir" || {
            echo "Error: Sequence consolidation failed for variant $variant"
            echo "$variant,ERROR_CONSOLIDATION" >> "$RESULTS_FILE"
            continue
        }
        
        # Step 3: Create protein MSA
        echo "Step 3: Creating protein MSA..."
        python "$SCRIPT_DIR/create_msa.py" "$work_dir/proteins.fasta" "$work_dir/proteins_aligned.fasta" || {
            echo "Error: MSA creation failed for variant $variant"
            echo "$variant,ERROR_MSA" >> "$RESULTS_FILE"
            continue
        }
        
        # Step 4: Create codon alignment
        echo "Step 4: Creating codon alignment..."
        python "$SCRIPT_DIR/create_codon_alignment.py" "$work_dir/proteins_aligned.fasta" "$work_dir/cds.fasta" "$work_dir/codon_alignment.phy" || {
            echo "Error: Codon alignment failed for variant $variant"
            echo "$variant,ERROR_CODON_ALIGNMENT" >> "$RESULTS_FILE"
            continue
        }
        
        # Step 5: Build phylogenetic tree
        echo "Step 5: Building phylogenetic tree..."
        python "$SCRIPT_DIR/build_tree.py" "$work_dir/proteins_aligned.fasta" "$work_dir/tree.nwk" || {
            echo "Error: Tree building failed for variant $variant"
            echo "$variant,ERROR_TREE" >> "$RESULTS_FILE"
            continue
        }
        
        # Step 6: Run PAML analysis
        echo "Step 6: Running PAML analysis..."
        python "$SCRIPT_DIR/run_paml.py" "$work_dir/codon_alignment.phy" "$work_dir/tree.nwk" --mock || {
            echo "Error: PAML analysis failed for variant $variant"
            echo "$variant,ERROR_PAML" >> "$RESULTS_FILE"
            continue
        }
        
        # Step 7: Parse results
        echo "Step 7: Parsing results..."
        result=$(python "$SCRIPT_DIR/parse_paml_results.py" --mlc-file "$work_dir/mlc" | grep -o '<answer>.*</answer>' | sed 's/<answer>\(.*\)<\/answer>/\1/' 2>/dev/null || echo "ERROR")
        
        if [[ "$result" != "ERROR" && -n "$result" ]]; then
            echo "$variant,$result" >> "$RESULTS_FILE"
            echo "Variant $variant result: $result branches with positive selection"
        else
            echo "Error: Failed to parse results for variant $variant"
            echo "$variant,ERROR_PARSING" >> "$RESULTS_FILE"
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

# Clean up temporary files in data_output if needed
echo ""
echo "Analysis pipeline completed."
echo "Working files can be found in: $SCRIPT_DIR/data_output/"