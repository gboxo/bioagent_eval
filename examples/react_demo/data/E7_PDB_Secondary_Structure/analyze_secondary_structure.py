#!/usr/bin/env python3
"""
Script to analyze secondary structure using DSSP.

This script runs DSSP analysis on PDB files and counts the number of beta sheets.
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from Bio.PDB import DSSP, PDBParser


def run_dssp(pdb_file: str, output_dir: str) -> str:
    """
    Run mkdssp command on PDB file to generate DSSP output.
    """
    # Check if mkdssp is available
    
    pdb_name = Path(pdb_file).stem
    dssp_output = os.path.join(output_dir, f"{pdb_name}.dssp")
    
    # Run DSSP command
    result = subprocess.run(
        ['mkdssp', pdb_file], 
        stdout=open(dssp_output, 'w'),
        stderr=subprocess.PIPE,
        timeout=120
    )
    
    if result.returncode == 0:
        print(f"DSSP analysis completed: {dssp_output}")
        return dssp_output
    else:
        print(f"DSSP failed: {result.stderr.decode()}")
            
    
    return None


def parse_dssp_with_biopython(pdb_file: str, dssp_file: str) -> int:
    """
    Parse DSSP output using Biopython and count beta sheets.
    """
    
    # Parse PDB structure
    parser = PDBParser(QUIET=True)
    pdb_name = Path(pdb_file).stem
    structure = parser.get_structure(pdb_name, pdb_file)
    
    # Get first model
    model = structure[0]
    
    # Run DSSP analysis using Biopython
    dssp = DSSP(model, dssp_file)
    
    # Count beta sheets by analyzing secondary structure
    sheet_ids = set()
    
    for key in dssp:
        residue_data = dssp[key]
        # residue_data format: (dssp_index, amino_acid, secondary_structure, 
        #                      accessibility, phi, psi, dssp_dict...)
        
        if len(residue_data) > 2:
            secondary_structure = residue_data[2]
            # Beta sheet structures are marked as 'E' (extended strand)
            if secondary_structure == 'E':
                # Try to get sheet identifier if available
                chain_id = key[0]
                res_id = key[1][1]
                sheet_id = f"{chain_id}_{res_id // 10}"  # Group nearby residues
                sheet_ids.add(sheet_id)
    
    # Alternative: count continuous beta strand regions
    
    print(f"Found {len(sheet_ids)} potential sheet regions")
    
    # Return the more conservative estimate, don't force minimum of 1
    return len(sheet_ids)
        


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Analyze secondary structure using DSSP')
    parser.add_argument('pdb_file', help='Input PDB file')
    parser.add_argument('--output-dir', '-o', default='.', help='Output directory')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.pdb_file):
        print(f"Error: PDB file {args.pdb_file} not found")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Analyzing {args.pdb_file}...")
    
    # Step 1: Run DSSP
    dssp_file = run_dssp(args.pdb_file, args.output_dir)
    
    sheet_count = 0
    
    # Step 2: Parse DSSP output
    # Try Biopython first
    sheet_count = parse_dssp_with_biopython(args.pdb_file, dssp_file)
    
    
    print(f"Final result: {sheet_count} beta sheets")
    print(f"<answer>{sheet_count}</answer>")
    
    return sheet_count


if __name__ == "__main__":
    main()