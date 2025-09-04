#!/usr/bin/env python3
"""
Multiple Sequence Alignment Conservation Score Calculator

This script combines FASTA files, performs MSA using MAFFT, and calculates
conservation scores to count highly conserved columns (>80% conservation).
"""

import os
import sys
import subprocess
import tempfile
from collections import Counter
from typing import List, Optional
from Bio import AlignIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO


def combine_fasta_files(variant_folder: str) -> str:
    """
    Combine all FASTA files in the variant folder into a single multi-FASTA file.
    
    Args:
        variant_folder: Path to variant folder containing FASTA files
        
    Returns:
        Path to the combined FASTA file
    """
    combined_fasta = os.path.join(variant_folder, "combined.fasta")
    
    # Get all FASTA files in the folder, excluding intermediate files
    excluded_files = {'combined.fasta', 'alignment.fasta'}
    fasta_files = [f for f in os.listdir(variant_folder) 
                   if f.endswith('.fasta') and f not in excluded_files]
    fasta_files.sort()  # Ensure consistent ordering
    
    with open(combined_fasta, 'w') as outfile:
        for fasta_file in fasta_files:
            fasta_path = os.path.join(variant_folder, fasta_file)
            
            # Read each FASTA file and write to combined file
            for record in SeqIO.parse(fasta_path, "fasta"):
                SeqIO.write(record, outfile, "fasta")
    
    print(f"Combined {len(fasta_files)} FASTA files into {combined_fasta}")
    return combined_fasta


def run_mafft_alignment(input_fasta: str, variant_folder: str) -> str:
    """
    Run MAFFT multiple sequence alignment on the combined FASTA file.
    
    Args:
        input_fasta: Path to input FASTA file
        variant_folder: Path to variant folder for output
        
    Returns:
        Path to alignment file
    """
    alignment_file = os.path.join(variant_folder, "alignment.fasta")
    
    try:
        # Run MAFFT command
        cmd = ["mafft", "--auto", input_fasta]
        
        with open(alignment_file, 'w') as outfile:
            result = subprocess.run(cmd, stdout=outfile, stderr=subprocess.PIPE, 
                                  text=True, check=True)
        
        print(f"MAFFT alignment completed: {alignment_file}")
        return alignment_file
        
    except subprocess.CalledProcessError as e:
        print(f"MAFFT error: {e.stderr}")
        raise
    except FileNotFoundError:
        print("Error: MAFFT not found. Please install MAFFT.")
        raise


def calculate_conservation_scores(alignment_file: str) -> int:
    """
    Calculate conservation scores and count columns with >80% conservation.
    
    Args:
        alignment_file: Path to alignment file
        
    Returns:
        Number of columns with conservation > 0.8
    """
    # Read the alignment
    alignment = AlignIO.read(alignment_file, "fasta")
    
    num_sequences = len(alignment)
    alignment_length = alignment.get_alignment_length()
    
    print(f"Alignment: {num_sequences} sequences, {alignment_length} positions")
    
    highly_conserved_count = 0
    
    # Iterate through each column in the alignment
    for col_idx in range(alignment_length):
        # Get all residues in this column
        column_residues = [alignment[seq_idx][col_idx] for seq_idx in range(num_sequences)]
        
        # Count occurrences of each residue (excluding gaps)
        residue_counts = Counter()
        valid_residues = 0
        
        for residue in column_residues:
            if residue != '-':  # Skip gaps
                residue_counts[residue] += 1
                valid_residues += 1
        
        # Calculate conservation as frequency of most common residue
        if valid_residues > 0:
            most_common_count = residue_counts.most_common(1)[0][1]
            conservation_score = most_common_count / num_sequences
            
            # Check if conservation > 0.8
            if conservation_score > 0.8:
                highly_conserved_count += 1
    
    print(f"Highly conserved columns (>80%): {highly_conserved_count}")
    return highly_conserved_count


def main():
    """Main analysis function."""
    if len(sys.argv) != 2:
        print("Usage: python calculate_msa_conservation.py <variant_folder>")
        sys.exit(1)
        
    variant_folder = sys.argv[1]
    
    if not os.path.exists(variant_folder):
        print(f"Error: Variant folder {variant_folder} does not exist")
        sys.exit(1)
        
    try:
        # Step 1: Combine FASTA files
        combined_fasta = combine_fasta_files(variant_folder)
        
        # Step 2: Run MAFFT alignment
        alignment_file = run_mafft_alignment(combined_fasta, variant_folder)
        
        # Step 3: Calculate conservation scores
        conserved_count = calculate_conservation_scores(alignment_file)
        
        print(f"Final result: {conserved_count}")
        print(conserved_count)
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()