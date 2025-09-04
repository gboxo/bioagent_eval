#!/usr/bin/env python3
"""
Script to analyze PDB structure and find the variant with the lowest RSA (most buried residue).
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from Bio.PDB import DSSP


def parse_variants(variants: List[str]) -> List[Tuple[int, str]]:
    """Parse variant strings to extract residue numbers.
    
    Args:
        variants: List of variant strings like 'A123G'
        
    Returns:
        List of tuples (residue_number, variant_string)
    """
    parsed = []
    for variant in variants:
        # Extract residue number from variant string (e.g., 'A123G' -> 123)
        residue_num = int(variant[1:-1])
        parsed.append((residue_num, variant))
    return parsed


def find_lowest_rsa_variant(pdb_file: str, chain_id: str, variants: List[str]) -> str:
    """Find the variant with the lowest RSA value.
    
    Args:
        pdb_file: Path to PDB file
        chain_id: Chain identifier
        variants: List of variant strings
        
    Returns:
        Variant string with the lowest RSA
    """
    # Parse variants to get residue numbers
    parsed_variants = parse_variants(variants)
    
    # Load DSSP data
    dssp_file = pdb_file.replace('.pdb', '.dssp')
    if not Path(dssp_file).exists():
        raise FileNotFoundError(f"DSSP file not found: {dssp_file}")
    
    # Parse DSSP output
    dssp_dict = DSSP.read_dssp_file(dssp_file)
    
    # Track minimum RSA and corresponding variant
    min_rsa = float('inf')
    min_variant = None
    
    # Check each variant
    for residue_num, variant in parsed_variants:
        # Create residue key for DSSP dictionary
        # DSSP keys are typically (chain_id, residue_number)
        key = (chain_id, residue_num)
        
        if key in dssp_dict:
            rsa = dssp_dict[key][3]  # RSA is at index 3 in DSSP data
            
            if rsa < min_rsa:
                min_rsa = rsa
                min_variant = variant
        else:
            print(f"Warning: Residue {residue_num} in chain {chain_id} not found in DSSP data")
    
    if min_variant is None:
        raise ValueError("No valid variants found in DSSP data")
    
    return min_variant


def main():
    """Main function to process variant data and find lowest RSA variant."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_structure.py <variant_folder>")
        sys.exit(1)
    
    variant_folder = sys.argv[1]
    variant_path = Path(variant_folder)
    
    if not variant_path.exists():
        print(f"Error: Variant folder {variant_folder} not found")
        sys.exit(1)
    
    # Find PDB file in the variant folder
    pdb_files = list(variant_path.glob("*.pdb"))
    if not pdb_files:
        print(f"Error: No PDB file found in {variant_folder}")
        sys.exit(1)
    
    pdb_file = str(pdb_files[0])
    pdb_id = pdb_files[0].stem
    
    # Load variant configuration
    config = {
        "variant_1": {"pdb_id": "2LYZ", "chain_id": "A",
                     "variants": ["R21G", "D52N", "W63Y", "A95V", "L129F"]}
    }
    
    # Determine which variant we're processing based on PDB ID
    variant_key = None
    for key, data in config.items():
        if data["pdb_id"] == pdb_id:
            variant_key = key
            break
    
    if variant_key is None:
        print(f"Error: No configuration found for PDB ID {pdb_id}")
        sys.exit(1)
    
    variant_config = config[variant_key]
    chain_id = variant_config["chain_id"]
    variants = variant_config["variants"]
    
    try:
        # Find the variant with lowest RSA
        result = find_lowest_rsa_variant(pdb_file, chain_id, variants)
        print(f"<answer>{result}</answer>")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()