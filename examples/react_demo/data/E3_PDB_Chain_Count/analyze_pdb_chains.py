#!/usr/bin/env python3
"""
Script to analyze PDB files and count distinct protein chains.
Uses Biopython to parse PDB structures and extract chain identifiers.
"""

import sys
import os
from typing import Set, List
from Bio.PDB import PDBParser


def analyze_pdb_chains(pdb_file_path: str) -> str:
    """
    Analyze a PDB file to extract unique chain identifiers.
    
    Args:
        pdb_file_path: Path to the PDB file
        
    Returns:
        Comma-separated string of sorted chain IDs
        
    Raises:
        FileNotFoundError: If PDB file doesn't exist
        Exception: If PDB parsing fails
    """
    
    # Initialize PDB parser
    parser = PDBParser(QUIET=True)  # QUIET=True suppresses warnings
    
    # Parse the structure
    structure = parser.get_structure("structure", pdb_file_path)
    
    # Set to store unique chain IDs
    chain_ids: Set[str] = set()
    
    # Iterate through models and chains
    for model in structure:
        for chain in model:
            chain_ids.add(chain.id)
    
    # Convert to sorted list and join with commas
    sorted_chains: List[str] = sorted(list(chain_ids))
    result = ",".join(sorted_chains)
    
    print(f"Found chains: {sorted_chains}")
    return result
    


def main():
    """Main function to process PDB file and extract chain identifiers."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_pdb_chains.py <pdb_file_path>")
        sys.exit(1)
    
    pdb_file_path = sys.argv[1]
    
    # Analyze PDB chains
    print(f"Analyzing PDB file: {pdb_file_path}")
    result = analyze_pdb_chains(pdb_file_path)
    
    print(f"Chain identifiers: {result}")
    print(f"<answer>{result}</answer>")
    
    return result
        


if __name__ == "__main__":
    main()