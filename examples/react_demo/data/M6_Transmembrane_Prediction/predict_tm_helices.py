#!/usr/bin/env python3
"""
Transmembrane helix prediction script using pytmhmm.

This script processes FASTA files to predict transmembrane helices and identifies
the protein with the highest number of transmembrane helices.
"""

import os
import sys
import argparse
from typing import Dict, Tuple
from pathlib import Path

try:
    import pyTMHMM as pytmhmm
except ImportError:
    print("Error: pyTMHMM library not found. Please install it with: pip install pytmhmm")
    sys.exit(1)


def read_fasta(filepath: str) -> str:
    """Read FASTA sequence from file."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Skip header line and concatenate sequence lines
    sequence = ''.join(line.strip() for line in lines if not line.startswith('>'))
    return sequence


def count_tm_helices(annotation: str) -> int:
    """
    Count transmembrane helices from TMHMM annotation string.
    Transmembrane segments are marked as 'M' in the annotation.
    """
    # Count transitions from non-M to M (start of transmembrane region)
    tm_count = 0
    prev_char = None
    for char in annotation:
        if char == 'M' and prev_char != 'M':
            tm_count += 1
        prev_char = char
    
    return tm_count


def process_variant_folder(variant_path: str) -> str:
    """
    Process all FASTA files in a variant folder and return the UniProt ID
    with the highest number of transmembrane helices.
    """
    fasta_files = [f for f in os.listdir(variant_path) if f.endswith('.fasta')]
    
    if not fasta_files:
        raise ValueError(f"No FASTA files found in {variant_path}")
    
    max_helices = -1
    best_protein = ""
    results = {}
    
    for fasta_file in fasta_files:
        uniprot_id = fasta_file.replace('.fasta', '')
        filepath = os.path.join(variant_path, fasta_file)
        
        try:
            # Read sequence
            sequence = read_fasta(filepath)
            
            # Predict transmembrane topology
            annotation, _ = pytmhmm.predict(sequence)
            
            # Count transmembrane helices
            tm_helices = count_tm_helices(annotation)
            results[uniprot_id] = tm_helices
            
            print(f"{uniprot_id}: {tm_helices} transmembrane helices")
            
            if tm_helices > max_helices:
                max_helices = tm_helices
                best_protein = uniprot_id
                
        except Exception as e:
            print(f"Error processing {uniprot_id}: {e}")
            continue
    
    print(f"\nBest protein: {best_protein} with {max_helices} transmembrane helices")
    return best_protein


def main():
    """Main function to process variant folder."""
    parser = argparse.ArgumentParser(description='Predict transmembrane helices for proteins')
    parser.add_argument('variant_folder', help='Path to variant folder containing FASTA files')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.variant_folder):
        print(args.variant_folder)
        print(f"Error: {args.variant_folder} is not a valid directory")
        sys.exit(1)
    
    try:
        result = process_variant_folder(args.variant_folder)
        print(f"<answer>{result}</answer>")
        return result
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()