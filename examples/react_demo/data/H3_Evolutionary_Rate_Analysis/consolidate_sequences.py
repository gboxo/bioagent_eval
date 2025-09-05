#!/usr/bin/env python3
"""
Script to consolidate protein and CDS sequences into multi-FASTA files.

This script takes individual FASTA files and creates consolidated multi-FASTA files
for proteins and CDS sequences.
"""

import os
import sys
import argparse
from pathlib import Path


def consolidate_protein_sequences(variant_folder: str, output_dir: str) -> str:
    """
    Consolidate individual protein FASTA files into a single multi-FASTA file.
    """
    protein_output_file = os.path.join(output_dir, 'proteins.fasta')
    
    fasta_files = sorted([f for f in os.listdir(variant_folder) if f.endswith('.fasta')])
    
    with open(protein_output_file, 'w') as outfile:
        for fasta_file in fasta_files:
            uniprot_id = fasta_file.replace('.fasta', '')
            filepath = os.path.join(variant_folder, fasta_file)
            
            with open(filepath, 'r') as infile:
                lines = infile.readlines()
                
                # Write header with simplified UniProt ID
                outfile.write(f">{uniprot_id}\n")
                
                # Write sequence (skip original header)
                for line in lines[1:]:
                    if not line.startswith('>'):
                        outfile.write(line)
    
    print(f"Protein sequences consolidated to: {protein_output_file}")
    return protein_output_file


def consolidate_cds_sequences(cds_file: str, output_dir: str) -> str:
    """
    Copy and validate CDS sequences file.
    """
    if not os.path.exists(cds_file):
        print(f"Warning: CDS file not found at {cds_file}")
        return None
    
    cds_output_file = os.path.join(output_dir, 'cds.fasta')
    
    # Copy CDS file to output directory
    with open(cds_file, 'r') as infile:
        with open(cds_output_file, 'w') as outfile:
            outfile.write(infile.read())
    
    print(f"CDS sequences consolidated to: {cds_output_file}")
    return cds_output_file


def validate_sequences(protein_file: str, cds_file: str) -> bool:
    """
    Validate that protein and CDS files have matching sequences.
    """
    if not cds_file or not os.path.exists(cds_file):
        print("Warning: CDS file not available for validation")
        return False
    
    # Read protein IDs
    protein_ids = set()
    with open(protein_file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                protein_ids.add(line.strip()[1:])
    
    # Read CDS IDs
    cds_ids = set()
    with open(cds_file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                cds_ids.add(line.strip()[1:])
    
    # Check matching
    missing_cds = protein_ids - cds_ids
    extra_cds = cds_ids - protein_ids
    
    if missing_cds:
        print(f"Warning: Missing CDS for proteins: {missing_cds}")
    
    if extra_cds:
        print(f"Warning: Extra CDS sequences: {extra_cds}")
    
    print(f"Protein sequences: {len(protein_ids)}")
    print(f"CDS sequences: {len(cds_ids)}")
    print(f"Matching sequences: {len(protein_ids & cds_ids)}")
    
    return len(missing_cds) == 0


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Consolidate protein and CDS sequences')
    parser.add_argument('variant_folder', help='Path to variant folder containing protein FASTA files')
    parser.add_argument('--output', '-o', default='data_output', help='Output directory')
    parser.add_argument('--cds-file', help='Path to CDS sequences file')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.variant_folder):
        print(f"Error: {args.variant_folder} is not a valid directory")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Consolidate protein sequences
    protein_file = consolidate_protein_sequences(args.variant_folder, args.output)
    
    # Consolidate CDS sequences
    cds_file = args.cds_file
    if not cds_file:
        # Default CDS file location
        cds_file = os.path.join(args.output, 'cds_sequences.fasta')
    
    cds_output_file = consolidate_cds_sequences(cds_file, args.output)
    
    # Validate sequences
    if cds_output_file:
        validate_sequences(protein_file, cds_output_file)
    
    print("Sequence consolidation completed.")


if __name__ == "__main__":
    main()