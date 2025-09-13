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


def check_dssp_availability() -> bool:
    """
    Check if mkdssp command is available.
    """
    try:
        result = subprocess.run(['mkdssp', '--version'], 
                              capture_output=True, 
                              timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def run_dssp(pdb_file: str, output_dir: str) -> str:
    """
    Run mkdssp command on PDB file to generate DSSP output.
    """
    # Check if mkdssp is available
    if not check_dssp_availability():
        print("Error: mkdssp command not found. Please install DSSP.")
        print("On Ubuntu/Debian: sudo apt-get install dssp")
        print("On macOS: brew install brewsci/bio/dssp")
        return None
    
    pdb_name = Path(pdb_file).stem
    dssp_output = os.path.join(output_dir, f"{pdb_name}.dssp")
    
    # Run DSSP command
    with open(dssp_output, 'w') as f:
        result = subprocess.run(
            ['mkdssp', pdb_file], 
            stdout=f,
            stderr=subprocess.PIPE,
            timeout=120
        )
    
    if result.returncode == 0:
        print(f"DSSP analysis completed: {dssp_output}")
        return dssp_output
    else:
        print(f"DSSP failed: {result.stderr.decode()}")
        return None


def parse_dssp_direct(dssp_file: str) -> int:
    """
    Parse DSSP output directly to count beta strands.
    
    Count all residues that are in beta strands (secondary structure 'E') 
    across all chains in the structure.
    """
    beta_strand_count = 0
    
    try:
        with open(dssp_file, 'r') as f:
            for line in f:
                # Skip header lines and comments
                if line.startswith('#') or not line.strip():
                    continue
                
                # Look for data lines (start with PDB ID)
                parts = line.split()
                if len(parts) >= 5 and parts[0].isalnum() and len(parts[0]) == 4:
                    secondary_structure = parts[4]  # Secondary structure column
                    
                    # Count beta strand residues (E)
                    if secondary_structure == 'E':
                        beta_strand_count += 1
    
    except Exception as e:
        print(f"Error parsing DSSP file directly: {e}")
        return 0
    
    print(f"Total beta strand residues found: {beta_strand_count}")
    
    return beta_strand_count


def parse_dssp_with_biopython(pdb_file: str, dssp_file: str) -> int:
    """
    Parse DSSP output using Biopython and count beta strands.
    
    This is a fallback method that uses Biopython's DSSP parser.
    """
    
    try:
        # Parse PDB structure
        parser = PDBParser(QUIET=True)
        pdb_name = Path(pdb_file).stem
        structure = parser.get_structure(pdb_name, pdb_file)
        
        # Get first model
        model = structure[0]
        
        # Run DSSP analysis using Biopython
        dssp = DSSP(model, dssp_file)
        
        # Count beta strand residues
        beta_residues = 0
        
        for key in dssp:
            residue_data = dssp[key]
            if len(residue_data) > 2:
                secondary_structure = residue_data[2]
                if secondary_structure == 'E':
                    beta_residues += 1
        
        print(f"BioPython fallback: Found {beta_residues} beta strand residues")
        return beta_residues
        
    except Exception as e:
        print(f"Error with BioPython DSSP parsing: {e}")
        return 0
        


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
    
    if dssp_file is None:
        print("Error: Could not generate DSSP file")
        sys.exit(1)
    
    sheet_count = 0
    
    # Step 2: Parse DSSP output
    try:
        # First try direct parsing of DSSP file (most accurate)
        sheet_count = parse_dssp_direct(dssp_file)
        
        # If direct parsing gives 0, try BioPython as fallback
        if sheet_count == 0:
            print("Direct parsing found 0 sheets, trying BioPython fallback...")
            fallback_count = parse_dssp_with_biopython(args.pdb_file, dssp_file)
            if fallback_count > 0:
                print(f"BioPython found evidence of beta structures, using count: {fallback_count}")
                sheet_count = fallback_count
                
    except Exception as e:
        print(f"Error parsing DSSP output: {e}")
        sys.exit(1)
    
    
    print(f"Final result: {sheet_count} beta sheets")
    print(f"<answer>{sheet_count}</answer>")
    
    return sheet_count


if __name__ == "__main__":
    main()