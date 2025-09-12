#!/usr/bin/env python3
"""
Variant Structural Mapping - RSA Analysis
Analyzes PDB structures to find the variant with the lowest RSA (most buried residue).
"""

import os
import sys
import json
import subprocess
import glob
from typing import Dict, List, Optional, Tuple
from Bio.PDB import PDBParser, DSSP


def run_dssp(pdb_file: str) -> str:
    """Run mkdssp on a PDB file to generate DSSP output."""
    dssp_file = pdb_file.replace(".pdb", ".dssp")

    # Run mkdssp command (newer syntax: mkdssp input-file output-file)
    result = subprocess.run(
        ["mkdssp", pdb_file, dssp_file], capture_output=True, text=True, check=True
    )

    return dssp_file


def parse_variant_data(variant_dir: str) -> Optional[Dict]:
    """Parse variant data from directory JSON configuration file."""

    # Find PDB file
    pdb_files = glob.glob(os.path.join(variant_dir, "*.pdb"))

    pdb_file = pdb_files[0]
    pdb_id = os.path.basename(pdb_file).replace(".pdb", "")

    # Load configuration from JSON file
    config_file = os.path.join(variant_dir, "config.json")

    with open(config_file, "r") as f:
        config = json.load(f)

    # Validate required fields
    required_fields = ["pdb_id", "chain_id", "variants"]
    for field in required_fields:
        if field not in config:
            print(f"Error: Missing required field '{field}' in {config_file}")
            return None

    return {
        "pdb_file": pdb_file,
        "pdb_id": config["pdb_id"],
        "chain_id": config["chain_id"],
        "variants": config["variants"],
    }


def parse_variants(variants: List[str]) -> List[Tuple[int, str, str]]:
    """Parse variant strings to extract residue information."""
    parsed = []
    for variant in variants:
        if len(variant) < 3:
            continue
        # Extract: original AA, residue number, new AA
        original_aa = variant[0]
        new_aa = variant[-1]
        residue_num = int(variant[1:-1])
        parsed.append((residue_num, original_aa, variant))
    return parsed


def analyze_rsa(pdb_file: str, chain_id: str, variants: List[str]) -> Optional[str]:
    """Analyze RSA values and find the variant with the lowest RSA."""

    # Run DSSP
    dssp_file = run_dssp(pdb_file)

    # Parse PDB structure
    parser = PDBParser()
    structure = parser.get_structure("protein", pdb_file)

    # Create DSSP object
    model = structure[0]
    dssp = DSSP(model, dssp_file)

    # Parse variants
    parsed_variants = parse_variants(variants)

    # Track minimum RSA and corresponding variant
    min_rsa = float("inf")
    min_variant = None

    print(f"Analyzing {len(parsed_variants)} variants:")

    for residue_num, original_aa, variant in parsed_variants:
        # DSSP key format: (chain_id, (' ', residue_number, ' '))
        key = (chain_id, (" ", residue_num, " "))

        if key in dssp:
            dssp_data = dssp[key]
            rsa = dssp_data[3]  # Relative solvent accessibility

            print(f"  {variant}: RSA = {rsa:.3f}")

            if rsa < min_rsa:
                min_rsa = rsa
                min_variant = variant
        else:
            print(f"  {variant}: Residue not found in DSSP data")

    # After processing all variants, print result and return
    if min_variant:
        print(f"Lowest RSA variant: {min_variant} (RSA = {min_rsa:.3f})")
    else:
        print("No valid variants found")

    return min_variant


def analyze_variant(variant_dir: str) -> Optional[str]:
    """Analyze a single variant directory."""

    # Parse variant data
    data = parse_variant_data(variant_dir)

    print(f"Processing PDB {data['pdb_id']} chain {data['chain_id']}")
    print(f"Variants: {data['variants']}")

    # Analyze RSA
    result = analyze_rsa(data["pdb_file"], data["chain_id"], data["variants"])

    return result


def main():
    variant_dir = sys.argv[1]
    result = analyze_variant(variant_dir)

    if result:
        print(f"<answer>{result}</answer>")
    else:
        print("ERROR")


if __name__ == "__main__":
    main()
