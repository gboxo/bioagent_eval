#!/usr/bin/env python3
"""
Script to analyze FASTA files and calculate mean sequence length.
Uses Biopython to parse FASTA sequences and compute length statistics.
"""

import sys
import os
import glob
from typing import List
try:
    from Bio import SeqIO
except ImportError:
    print("Error: Biopython is required. Please install with: pip install biopython")
    sys.exit(1)


def calculate_mean_length(variant_dir: str) -> int:
    """
    Calculate the mean length of all FASTA sequences in a directory.
    
    Args:
        variant_dir: Path to the directory containing FASTA files
        
    Returns:
        Mean sequence length rounded to nearest integer
        
    Raises:
        FileNotFoundError: If directory doesn't exist or no FASTA files found
        Exception: If FASTA parsing fails
    """
    if not os.path.exists(variant_dir):
        raise FileNotFoundError(f"Directory not found: {variant_dir}")
    
    # Find all FASTA files in the directory
    fasta_files = glob.glob(os.path.join(variant_dir, "*.fasta"))
    
    if not fasta_files:
        raise FileNotFoundError(f"No FASTA files found in directory: {variant_dir}")
    
    print(f"Found {len(fasta_files)} FASTA files")
    
    # List to store sequence lengths
    lengths: List[int] = []
    
    try:
        # Process each FASTA file
        for fasta_file in sorted(fasta_files):
            print(f"Processing: {os.path.basename(fasta_file)}")
            
            # Parse FASTA file and extract sequence lengths
            for record in SeqIO.parse(fasta_file, "fasta"):
                seq_length = len(record.seq)
                lengths.append(seq_length)
                print(f"  {record.id}: {seq_length} amino acids")
        
        if not lengths:
            raise ValueError("No sequences found in FASTA files")
        
        # Calculate mean length
        total_length = sum(lengths)
        mean_length = total_length / len(lengths)
        rounded_mean = round(mean_length)
        
        print(f"Sequence lengths: {lengths}")
        print(f"Total sequences: {len(lengths)}")
        print(f"Total length: {total_length}")
        print(f"Mean length: {mean_length}")
        print(f"Rounded mean: {rounded_mean}")
        
        return rounded_mean
        
    except Exception as e:
        raise Exception(f"Error processing FASTA files in {variant_dir}: {e}")


def main():
    """Main function to process variant directory and calculate mean sequence length."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_fasta_lengths.py <variant_directory>")
        sys.exit(1)
    
    variant_dir = sys.argv[1]
    
    try:
        # Calculate mean sequence length
        print(f"Analyzing FASTA files in directory: {variant_dir}")
        result = calculate_mean_length(variant_dir)
        
        print(f"Mean sequence length: {result}")
        print(f"<answer>{result}</answer>")
        
        return result
        
    except Exception as e:
        print(f"Error processing {variant_dir}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()