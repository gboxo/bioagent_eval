#!/usr/bin/env python3
"""
Script to analyze protein complex interfaces.

This script analyzes inter-chain contacts in multi-chain PDB structures
using a 4.5 Angstrom distance cutoff.
"""

import os
import sys
import argparse
from pathlib import Path
from Bio.PDB import PDBParser, NeighborSearch


def parse_pdb_structure(pdb_file: str):
    """
    Parse PDB file and return structure object.
    """
    parser = PDBParser(QUIET=True)
    pdb_id = Path(pdb_file).stem
    structure = parser.get_structure(pdb_id, pdb_file)
    print(f"Successfully parsed PDB structure: {pdb_id}")
    return structure


def get_all_atoms(structure):
    """
    Get list of all atoms in the structure.
    """
    atoms = []
    chain_count = {}
    
    for model in structure:
        for chain in model:
            chain_id = chain.get_id()
            chain_count[chain_id] = chain_count.get(chain_id, 0)
            
            for residue in chain:
                # Skip heteroatoms and water molecules
                if residue.get_id()[0] == ' ':  # Standard amino acid residues
                    for atom in residue:
                        atoms.append(atom)
                        chain_count[chain_id] += 1
    
    print(f"Found {len(atoms)} atoms across {len(chain_count)} chains")
    print(f"Chain composition: {dict(chain_count)}")
    
    return atoms


def analyze_inter_chain_contacts(structure, cutoff: float = 4.5) -> int:
    """
    Analyze inter-chain contacts using NeighborSearch.
    
    Returns the count of unique inter-chain residue pairs.
    """
    print(f"Analyzing inter-chain contacts with {cutoff} Å cutoff...")
    
    # Get all atoms
    atoms = get_all_atoms(structure)
    
    
    # Create NeighborSearch object
    neighbor_search = NeighborSearch(atoms)
    
    # Set to store unique inter-chain residue pairs
    inter_chain_contacts = set()
    
    # Find all atom pairs within cutoff distance
    print("Searching for neighboring atom pairs...")
    atom_pairs = neighbor_search.search_all(cutoff)
    
    print(f"Found {len(atom_pairs)} atom pairs within {cutoff} Å")
    
    # Process atom pairs to identify inter-chain contacts
    for atom1, atom2 in atom_pairs:
        # Get parent residues and chain IDs
        residue1 = atom1.get_parent()
        residue2 = atom2.get_parent()
        
        chain1 = residue1.get_parent()
        chain2 = residue2.get_parent()
        
        chain_id1 = chain1.get_id()
        chain_id2 = chain2.get_id()
        
        # Check if atoms are from different chains
        if chain_id1 != chain_id2:
            # Create unique residue pair identifier
            # Use (chain_id, residue_id) to uniquely identify each residue
            res_id1 = (chain_id1, residue1.get_id())
            res_id2 = (chain_id2, residue2.get_id())
            
            # Create sorted tuple to ensure uniqueness regardless of order
            residue_pair = tuple(sorted([res_id1, res_id2]))
            inter_chain_contacts.add(residue_pair)
    
    contact_count = len(inter_chain_contacts)
    print(f"Found {contact_count} unique inter-chain residue contacts")
    
    
    return contact_count


        


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Analyze protein complex interface')
    parser.add_argument('pdb_file', help='Input PDB file')
    
    args = parser.parse_args()
    
    
    print(f"Analyzing protein complex interface: {args.pdb_file}")
    
    # Parse structure
    structure = parse_pdb_structure(args.pdb_file)
    
    contact_count = analyze_inter_chain_contacts(structure)
    
    print(f"\nFinal result: {contact_count} inter-chain contacts")
    print(f"<answer>{contact_count}</answer>")
    
    return contact_count


if __name__ == "__main__":
    main()