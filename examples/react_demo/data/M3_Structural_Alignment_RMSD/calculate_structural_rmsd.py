#!/usr/bin/env python3
"""
Structural Alignment RMSD Calculator

This script performs structural alignment of two PDB structures focusing on C-alpha atoms
and calculates the Root Mean Square Deviation (RMSD) between them.
"""

import os
import sys
from typing import List, Optional, Tuple
from Bio.PDB import PDBParser, Superimposer
from Bio.PDB.Structure import Structure
from Bio.PDB.Atom import Atom

from Bio.PDB import PDBParser, Superimposer, is_aa


def load_structure(path):
    parser = PDBParser(QUIET=True)
    return parser.get_structure(os.path.basename(path).rsplit('.', 1)[0], path)

def get_ca_atoms(structure):
    """Return a list of all C-alpha atoms (first model only), in order."""
    model = next(structure.get_models())
    cas = []
    for chain in model:
        for res in chain:
            if not is_aa(res, standard=True):
                continue
            if 'CA' in res:
                cas.append(res['CA'])
    return cas



def find_pdb_files(variant_folder: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Find the two PDB files in the variant folder.
    
    Args:
        variant_folder: Path to variant folder
        
    Returns:
        Tuple of paths to the two PDB files, or (None, None) if not found
    """
    try:
        pdb_files = [f for f in os.listdir(variant_folder) if f.endswith('.pdb')]
        pdb_files.sort()  # Ensure consistent ordering
        
        if len(pdb_files) < 2:
            print(f"Error: Expected 2 PDB files, found {len(pdb_files)}")
            return None, None
            
        pdb_file1 = os.path.join(variant_folder, pdb_files[0])
        pdb_file2 = os.path.join(variant_folder, pdb_files[1])
        
        print(f"Found PDB files: {pdb_files[0]} and {pdb_files[1]}")
        
        return pdb_file1, pdb_file2
        
    except Exception as e:
        print(f"Error finding PDB files in {variant_folder}: {e}")
        return None, None


def main():
    """Main analysis function."""
    if len(sys.argv) != 2:
        print("Usage: python calculate_structural_rmsd.py <variant_folder>")
        sys.exit(1)
        
    variant_folder = sys.argv[1]
    
    if not os.path.exists(variant_folder):
        print(f"Error: Variant folder {variant_folder} does not exist")
        sys.exit(1)
        
    # Find the two PDB files in the variant folder
    pdb_file1, pdb_file2 = find_pdb_files(variant_folder)
    
    s1 = load_structure(pdb_file1)
    s2 = load_structure(pdb_file2)

    ca1 = get_ca_atoms(s1)
    ca2 = get_ca_atoms(s2)



    n = min(len(ca1), len(ca2))
    fixed, moving = ca1[:n], ca2[:n]

    sup = Superimposer()
    sup.set_atoms(fixed, moving)
    rmsd = getattr(sup, "rms", None)  # Biopython uses .rms
    if rmsd is None:
        raise AttributeError("Superimposer has no 'rms' attribute. Check your Biopython version.")

    print(f"<answer>{rmsd:.3f}</answer>")


if __name__ == "__main__":

    main()







