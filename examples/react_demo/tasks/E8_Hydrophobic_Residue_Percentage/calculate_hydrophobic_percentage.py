#!/usr/bin/env python3
"""
Hydrophobic Residue Percentage Calculator

This script calculates the percentage of hydrophobic residues in a protein sequence.
Hydrophobic residues are defined as: A, I, L, M, F, P, V, W
"""

import os
import sys
from typing import List, Optional


def read_fasta_sequence(fasta_file: str) -> Optional[str]:
    """
    Read protein sequence from FASTA file.
    
    Args:
        fasta_file: Path to FASTA file
        
    Returns:
        Protein sequence string or None if error
    """
    try:
        with open(fasta_file, 'r') as f:
            lines = f.readlines()
            
        # Skip header line and concatenate sequence lines
        sequence = ""
        for line in lines[1:]:  # Skip first line (header)
            sequence += line.strip()
            
        return sequence
        
    except Exception as e:
        print(f"Error reading FASTA file {fasta_file}: {e}", file=sys.stderr)
        return None


def calculate_hydrophobic_percentage(sequence: str) -> float:
    """
    Calculate the percentage of hydrophobic residues in a protein sequence.
    
    Args:
        sequence: Protein sequence string
        
    Returns:
        Percentage of hydrophobic residues (0-100)
    """
    # Define hydrophobic amino acids
    hydrophobic_residues = {'A', 'I', 'L', 'M', 'F', 'P', 'V', 'W'}
    
    # Count total residues
    total_count = len(sequence)
    
    if total_count == 0:
        return 0.0
        
    # Count hydrophobic residues
    hydrophobic_count = sum(1 for residue in sequence if residue in hydrophobic_residues)
    
    # Calculate percentage
    percentage = (hydrophobic_count / total_count) * 100
    
    return round(percentage, 2)


def get_first_uniprot_id(variant_folder: str) -> Optional[str]:
    """
    Get the first UniProt ID from the variant folder based on alphabetical order.
    
    Args:
        variant_folder: Path to variant folder
        
    Returns:
        First UniProt ID or None if no FASTA files found
    """
    try:
        # Get all FASTA files in the folder
        fasta_files = [f for f in os.listdir(variant_folder) if f.endswith('.fasta')]
        
        if not fasta_files:
            return None
            
        # Sort alphabetically and take the first one
        fasta_files.sort()
        first_file = fasta_files[0]
        
        # Extract UniProt ID from filename (remove .fasta extension)
        uniprot_id = first_file.replace('.fasta', '')
        
        return uniprot_id
        
    except Exception as e:
        print(f"Error getting UniProt ID from {variant_folder}: {e}", file=sys.stderr)
        return None


def main():
    """Main analysis function."""
    if len(sys.argv) != 2:
        print("Usage: python calculate_hydrophobic_percentage.py <variant_folder>")
        sys.exit(1)
        
    variant_folder = sys.argv[1]
    
    if not os.path.exists(variant_folder):
        print(f"Error: Variant folder {variant_folder} does not exist")
        sys.exit(1)
        
    # Get the first UniProt ID from the folder
    first_uniprot_id = get_first_uniprot_id(variant_folder)
    
    if not first_uniprot_id:
        print(f"Error: No FASTA files found in {variant_folder}")
        sys.exit(1)
        
    print(f"Processing first UniProt ID: {first_uniprot_id}")
    
    # Construct path to the FASTA file
    fasta_file = os.path.join(variant_folder, f"{first_uniprot_id}.fasta")
    
    if not os.path.exists(fasta_file):
        print(f"Error: FASTA file {fasta_file} does not exist")
        sys.exit(1)
        
    # Read the protein sequence
    sequence = read_fasta_sequence(fasta_file)
    
    if sequence is None:
        print(f"Error: Could not read sequence from {fasta_file}")
        sys.exit(1)
        
    # Calculate hydrophobic residue percentage
    percentage = calculate_hydrophobic_percentage(sequence)
    
    print(f"Sequence length: {len(sequence)} residues")
    print(f"Hydrophobic residue percentage: {percentage}%")
    print(percentage)


if __name__ == "__main__":
    main()