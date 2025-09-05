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


def parse_pdb_structure(pdb_file: str) -> Optional[Structure]:
    """
    Parse a PDB file using Biopython's PDBParser.
    
    Args:
        pdb_file: Path to PDB file
        
    Returns:
        Parsed structure or None if failed
    """
    try:
        parser = PDBParser(QUIET=True)
        structure_id = os.path.basename(pdb_file).replace('.pdb', '')
        structure = parser.get_structure(structure_id, pdb_file)
        
        print(f"Successfully parsed {pdb_file}")
        return structure
        
    except Exception as e:
        print(f"Error parsing {pdb_file}: {e}")
        return None


def extract_ca_atoms(structure: Structure) -> List[Atom]:
    """
    Extract all C-alpha atoms from a protein structure.
    
    Args:
        structure: Biopython Structure object
        
    Returns:
        List of C-alpha atoms
    """
    ca_atoms = []
    
    for model in structure:
        for chain in model:
            for residue in chain:
                # Check if residue has a C-alpha atom
                if 'CA' in residue:
                    ca_atoms.append(residue['CA'])
                    
    print(f"Extracted {len(ca_atoms)} C-alpha atoms from {structure.id}")
    return ca_atoms


def calculate_rmsd(pdb_file1: str, pdb_file2: str) -> Optional[float]:
    """
    Calculate RMSD between two PDB structures using structural alignment.
    
    Args:
        pdb_file1: Path to first PDB file
        pdb_file2: Path to second PDB file
        
    Returns:
        RMSD value rounded to 3 decimal places, or None if failed
    """
    # Parse both structures
    structure1 = parse_pdb_structure(pdb_file1)
    structure2 = parse_pdb_structure(pdb_file2)
    
    if structure1 is None or structure2 is None:
        return None
        
    # Extract C-alpha atoms from both structures
    ca_atoms1 = extract_ca_atoms(structure1)
    ca_atoms2 = extract_ca_atoms(structure2)
    
    if not ca_atoms1 or not ca_atoms2:
        print("Error: No C-alpha atoms found in one or both structures")
        return None
        
    # Ensure both structures have the same number of C-alpha atoms
    min_atoms = min(len(ca_atoms1), len(ca_atoms2))
    if len(ca_atoms1) != len(ca_atoms2):
        print(f"Warning: Different number of C-alpha atoms ({len(ca_atoms1)} vs {len(ca_atoms2)})")
        print(f"Using first {min_atoms} atoms from each structure")
        ca_atoms1 = ca_atoms1[:min_atoms]
        ca_atoms2 = ca_atoms2[:min_atoms]
    
    # Create superimposer and set atoms
    superimposer = Superimposer()
    superimposer.set_atoms(ca_atoms1, ca_atoms2)
    
    # Get RMSD
    rmsd = superimposer.rms
    
    print(f"Structural alignment completed")
    print(f"RMSD: {rmsd:.3f} Å")
    
    return round(rmsd, 3)


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
    
    if pdb_file1 is None or pdb_file2 is None:
        print(f"Error: Could not find two PDB files in {variant_folder}")
        sys.exit(1)
        
    # Calculate RMSD
    rmsd = calculate_rmsd(pdb_file1, pdb_file2)
    
    if rmsd is None:
        print("Error: Could not calculate RMSD")
        sys.exit(1)
        
    print(f"Final result: {rmsd}")
    print(rmsd)


if __name__ == "__main__":
    main()