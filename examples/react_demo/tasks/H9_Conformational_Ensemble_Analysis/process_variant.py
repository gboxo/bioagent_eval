#!/usr/bin/env python3

import sys
import os
import glob

def process_variant_folder(variant_folder):
    """
    Process a variant folder and find the PDB file to analyze.
    
    Args:
        variant_folder (str): Path to variant folder
        
    Returns:
        str: Result from RMSF analysis
    """
    if not os.path.exists(variant_folder):
        raise ValueError(f"Variant folder {variant_folder} does not exist")
    
    # Find PDB files in the variant folder
    pdb_files = glob.glob(os.path.join(variant_folder, "*.pdb"))
    
    if not pdb_files:
        raise ValueError(f"No PDB files found in {variant_folder}")
    
    if len(pdb_files) > 1:
        print(f"Warning: Multiple PDB files found in {variant_folder}, using {pdb_files[0]}")
    
    pdb_file = pdb_files[0]
    print(f"Processing PDB file: {pdb_file}")
    
    # Import the analyze_rmsf module
    sys.path.append(os.path.dirname(__file__))
    from analyze_rmsf import calculate_rmsf_from_pdb
    
    try:
        result = calculate_rmsf_from_pdb(pdb_file)
        return str(result)
    except Exception as e:
        print(f"Error processing {pdb_file}: {e}")
        return "ERROR"

def main():
    if len(sys.argv) != 2:
        print("Usage: python process_variant.py <variant_folder>")
        sys.exit(1)
    
    variant_folder = sys.argv[1]
    
    try:
        result = process_variant_folder(variant_folder)
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()