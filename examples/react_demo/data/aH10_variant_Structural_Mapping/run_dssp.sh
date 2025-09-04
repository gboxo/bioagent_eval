#!/bin/bash
"""
Script to run mkdssp on PDB files to calculate secondary structure and accessibility.
"""

set -e  # Exit on any error

# Function to run mkdssp on a PDB file
run_dssp() {
    local pdb_file="$1"
    local dssp_file="${pdb_file%.pdb}.dssp"
    
    echo "Running mkdssp on: $pdb_file"
    
    # Check if PDB file exists
    if [[ ! -f "$pdb_file" ]]; then
        echo "Error: PDB file not found: $pdb_file"
        exit 1
    fi
    
    # Run mkdssp
    if command -v mkdssp &> /dev/null; then
        mkdssp -i "$pdb_file" -o "$dssp_file"
        echo "DSSP output written to: $dssp_file"
    else
        echo "Error: mkdssp command not found. Please install DSSP."
        exit 1
    fi
}

# Main function
main() {
    if [[ $# -ne 1 ]]; then
        echo "Usage: $0 <variant_folder>"
        exit 1
    fi
    
    local variant_folder="$1"
    
    # Check if variant folder exists
    if [[ ! -d "$variant_folder" ]]; then
        echo "Error: Variant folder not found: $variant_folder"
        exit 1
    fi
    
    # Find PDB files in the variant folder
    local pdb_files=($(find "$variant_folder" -name "*.pdb"))
    
    if [[ ${#pdb_files[@]} -eq 0 ]]; then
        echo "Error: No PDB files found in $variant_folder"
        exit 1
    fi
    
    # Process each PDB file
    for pdb_file in "${pdb_files[@]}"; do
        run_dssp "$pdb_file"
    done
    
    echo "DSSP processing completed successfully."
}

# Run main function with all arguments
main "$@"