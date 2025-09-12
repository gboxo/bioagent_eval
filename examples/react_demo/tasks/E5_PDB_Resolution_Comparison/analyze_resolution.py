#!/usr/bin/env python3
"""
PDB Resolution Comparison Analysis

This script analyzes PDB files to find the structure with the best (lowest) resolution.
Only structures determined by X-ray crystallography are considered.
"""

import os
import sys
from typing import Optional
from Bio.PDB import PDBParser
import glob


def get_resolution_from_pdb(pdb_file: str) -> Optional[float]:
    """
    Extract resolution from PDB file header.
    
    Args:
        pdb_file: Path to PDB file
        
    Returns:
        Resolution value if available, None otherwise
    """
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('structure', pdb_file)
        
        # Get resolution from header
        resolution = structure.header.get('resolution')
        
        # Return resolution if it exists and is a valid number
        if resolution is not None:
            return float(resolution)
        
        return None
        
    except Exception as e:
        print(f"Error processing {pdb_file}: {e}", file=sys.stderr)
        return None


def find_best_resolution_structure(variant_folder: str) -> str:
    """
    Find the PDB structure with the best (lowest) resolution in a variant folder.
    
    Args:
        variant_folder: Path to folder containing PDB files
        
    Returns:
        PDB ID of the structure with best resolution
    """
    best_pdb_id = None
    best_resolution = float('inf')
    
    # Find all PDB files in the variant folder
    pdb_files = glob.glob(os.path.join(variant_folder, "*.pdb"))
    
    for pdb_file in pdb_files:
        # Extract PDB ID from filename
        pdb_id = os.path.basename(pdb_file).replace('.pdb', '')
        
        # Get resolution
        resolution = get_resolution_from_pdb(pdb_file)
        
        if resolution is not None and resolution < best_resolution:
            best_resolution = resolution
            best_pdb_id = pdb_id
            
    return best_pdb_id if best_pdb_id else "No valid resolution found"


def main():
    """Main analysis function."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_resolution.py <variant_folder>")
        sys.exit(1)
        
    variant_folder = sys.argv[1]
    
    if not os.path.exists(variant_folder):
        print(f"Error: Variant folder {variant_folder} does not exist")
        sys.exit(1)
        
    result = find_best_resolution_structure(variant_folder)
    print(result)


if __name__ == "__main__":
    main()