#!/usr/bin/env python3
"""
Script to build phylogenetic tree using Biopython.

This script reads protein MSA, calculates distance matrix, and constructs
a phylogenetic tree using neighbor-joining algorithm.
"""

import os
import sys
import argparse

from Bio import AlignIO, Phylo
from Bio.Align import MultipleSeqAlignment
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor


def read_alignment(alignment_file: str):
    """
    Read multiple sequence alignment from file.
    """
    try:
        # Try different formats
        for fmt in ["fasta", "clustal", "phylip"]:
            try:
                alignment = AlignIO.read(alignment_file, fmt)
                print(f"Successfully read alignment in {fmt} format")
                return alignment
            except:
                continue

        # Manual FASTA parsing as fallback
        sequences = []
        with open(alignment_file, "r") as f:
            current_id = None
            current_seq = ""

            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    if current_id:
                        sequences.append(SeqRecord(Seq(current_seq), id=current_id))
                    current_id = line[1:].split()[0]  # Take only first part of header
                    current_seq = ""
                else:
                    current_seq += line

            if current_id:
                sequences.append(SeqRecord(Seq(current_seq), id=current_id))

        if sequences:
            alignment = MultipleSeqAlignment(sequences)
            print(f"Manually parsed alignment: {len(sequences)} sequences")
            return alignment
        else:
            raise ValueError("No sequences found in alignment file")

    except Exception as e:
        print(f"Error reading alignment: {e}")
        return None


def build_nj_tree(alignment, output_file: str) -> bool:
    """
    Build neighbor-joining tree from alignment.
    """

    calculator = DistanceCalculator("identity")
    distance_matrix = calculator.get_distance(alignment)
    print(f"Distance matrix calculated for {len(distance_matrix.names)} sequences")

    # Build tree using neighbor-joining (UPGMA or NJ)
    constructor = DistanceTreeConstructor(calculator, "nj")  # 'nj' for neighbor-joining
    tree = constructor.build_tree(alignment)

    # Write tree in Newick format
    Phylo.write(tree, output_file, "newick")
    print(f"Phylogenetic tree saved: {output_file}")

    # Print tree structure
    print("Tree structure:")
    Phylo.draw_ascii(tree)

    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build phylogenetic tree from MSA")
    parser.add_argument("alignment_file", help="Input protein MSA file")
    parser.add_argument("output_file", help="Output tree file (Newick format)")

    args = parser.parse_args()

    if not os.path.isfile(args.alignment_file):
        print(f"Error: Alignment file {args.alignment_file} not found")
        sys.exit(1)

    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output_file) or ".", exist_ok=True)

    # Read alignment
    alignment = read_alignment(args.alignment_file)

    success = False
    if alignment:
        # Try to build NJ tree
        success = build_nj_tree(alignment, args.output_file)

    # Fallback to simple tree if NJ fails
    if not success:
        print("NJ tree construction failed. Creating simple tree...")
        success = create_simple_tree(args.alignment_file, args.output_file)

    if success:
        print("Tree construction completed successfully.")
    else:
        print("Failed to build tree.")
        sys.exit(1)


if __name__ == "__main__":
    main()
