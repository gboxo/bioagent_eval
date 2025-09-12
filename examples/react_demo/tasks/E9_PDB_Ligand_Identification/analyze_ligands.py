#!/usr/bin/env python3
"""
PDB Ligand Identification
Identifies all bound ligands in a PDB file, excluding water molecules.
"""

import os
import sys
import json
from typing import Dict, Optional
from Bio.PDB import PDBParser


def load_config(variant_dir: str) -> Optional[Dict]:
    """Load configuration from JSON file."""
    
    config_file = os.path.join(variant_dir, "config.json")
        
    with open(config_file, 'r') as f:
        config = json.load(f)
        
    return config


def find_pdb_file(variant_dir: str, pdb_id: str) -> Optional[str]:
    """Find the PDB file in the variant directory."""
    pdb_file = os.path.join(variant_dir, f"{pdb_id}.pdb")
    
    return pdb_file


def count_unique_ligands(pdb_file: str) -> int:
    """Count unique ligand types in a PDB file."""
    parser = PDBParser(QUIET=True)
    
    structure = parser.get_structure("structure", pdb_file)

    
    # Set to store unique ligand names
    unique_ligands = set()
    
    # Iterate through all residues in the structure
    for model in structure:
        for chain in model:
            for residue in chain:
                # Get residue ID tuple (hetero_flag, sequence_id, insertion_code)
                res_id = residue.get_id()
                
                # Check if this is a HETATM (hetero_flag starts with 'H_') and not water ('W')
                if res_id[0] != ' ' and res_id[0] != 'W':
                    ligand_name = residue.get_resname().strip()
                    unique_ligands.add(ligand_name)
    
    print(f"Total unique ligands: {len(unique_ligands)}")
    return len(unique_ligands)


def analyze_variant(variant_dir: str) -> Optional[int]:
    """Analyze ligands for a variant."""
    # Load configuration
    config = load_config(variant_dir)
    
    pdb_id = config["pdb_id"]
    description = config.get("description", "Unknown protein")
    
    print(f"Analyzing {description} (PDB ID: {pdb_id})")
    
    # Find PDB file
    pdb_file = find_pdb_file(variant_dir, pdb_id)
    
    # Count unique ligands
    ligand_count = count_unique_ligands(pdb_file)
    
    return ligand_count


def main():
    
    variant_dir = sys.argv[1]
    result = analyze_variant(variant_dir)
    
    if result is not None:
        print(f"<answer>{result}</answer>")
        print(result)
    else:
        print("ERROR")


if __name__ == "__main__":
    main()