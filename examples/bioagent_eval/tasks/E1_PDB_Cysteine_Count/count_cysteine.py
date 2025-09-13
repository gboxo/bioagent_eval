#!/usr/bin/env python3
"""
Script to count cysteine residues in PDB files.
Parses PDB file using Biopython and counts total cysteine residues across all chains.
"""

import sys
import os
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1

def count_cysteine_in_pdb(pdb_file_path: str) -> int:
    """
    Count total number of cysteine residues in a PDB file.
    
    Args:
        pdb_file_path: Path to the PDB file
        
    Returns:
        Total number of cysteine residues across all chains
    """
    parser = PDBParser(QUIET=True)
    
    # Extract structure name from filename
    structure_name = os.path.basename(pdb_file_path).split('.')[0]
    
    structure = parser.get_structure(structure_name, pdb_file_path)
    
    total_cysteine_count = 0
    
    # Iterate through all models (usually just one)
    for model in structure:
        # Iterate through all chains in the model
        for chain in model:
            # Count cysteine residues in this chain
            for residue in chain:
                # Check if the residue is an amino acid (not water, ion, etc.)
                if residue.get_id()[0] == ' ':  # Standard amino acid residue
                    residue_name = residue.get_resname()
                    # Check if it's cysteine (CYS)
                    if residue_name == 'CYS':
                        total_cysteine_count += 1
    
    return total_cysteine_count

def main():
    """Main function to process command line arguments and count cysteine residues."""
    if len(sys.argv) != 2:
        print("Usage: python count_cysteine.py <pdb_file_path>", file=sys.stderr)
        sys.exit(1)
    
    pdb_file_path = sys.argv[1]
    
    if not os.path.exists(pdb_file_path):
        print(f"Error: File {pdb_file_path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    cysteine_count = count_cysteine_in_pdb(pdb_file_path)
    print(f"<answer>{cysteine_count}</answer>")

if __name__ == "__main__":
    main()