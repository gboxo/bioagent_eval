#!/usr/bin/env python3
"""
Phylogenetic Distance Calculator

This script performs multiple sequence alignment using MAFFT, constructs a phylogenetic tree
using neighbor-joining method, and calculates the maximum pairwise distance between all leaves.
"""

import os
import sys
import subprocess
from itertools import combinations
from typing import Optional, List
from Bio import AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Phylo import BaseTree


def run_mafft_alignment(input_fasta: str, variant_folder: str) -> str:
    """
    Run MAFFT multiple sequence alignment on the input FASTA file.

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

        with open(alignment_file, "w") as outfile:
            result = subprocess.run(
                cmd, stdout=outfile, stderr=subprocess.PIPE, text=True, check=True
            )

        print(f"MAFFT alignment completed: {alignment_file}")
        return alignment_file

    except subprocess.CalledProcessError as e:
        print(f"MAFFT error: {e.stderr}")
        raise
    except FileNotFoundError:
        print("Error: MAFFT not found. Please install MAFFT.")
        raise


def calculate_maximum_phylogenetic_distance(alignment_file: str) -> float:
    """
    Calculate the maximum pairwise phylogenetic distance between all leaves in the tree.

    Args:
        alignment_file: Path to alignment file

    Returns:
        Maximum pairwise distance rounded to 4 decimal places
    """
    # Read the alignment
    alignment = AlignIO.read(alignment_file, "fasta")

    print(
        f"Alignment: {len(alignment)} sequences, {alignment.get_alignment_length()} positions"
    )

    # Create distance calculator
    calculator = DistanceCalculator("identity")
    distance_matrix = calculator.get_distance(alignment)

    print(f"Distance matrix created with {len(distance_matrix)} sequences")

    # Build phylogenetic tree using neighbor-joining
    constructor = DistanceTreeConstructor()
    tree = constructor.nj(distance_matrix)

    print("Phylogenetic tree constructed using neighbor-joining method")

    # Get all terminal nodes (leaves) of the tree
    leaves = tree.get_terminals()
    leaf_names = [leaf.name for leaf in leaves]

    print(f"Tree has {len(leaves)} terminal nodes (leaves)")

    # Calculate distances between all pairs of leaves
    max_distance = 0.0
    max_pair = None

    for leaf1, leaf2 in combinations(leaves, 2):
        distance = tree.distance(leaf1, leaf2)

        if distance > max_distance:
            max_distance = distance
            max_pair = (leaf1.name, leaf2.name)

    print(
        f"Maximum distance: {max_distance:.4f} between {max_pair[0]} and {max_pair[1]}"
    )

    return round(max_distance, 4)


def find_fasta_file(variant_folder: str) -> Optional[str]:
    """
    Find the FASTA file in the variant folder.

    Args:
        variant_folder: Path to variant folder

    Returns:
        Path to FASTA file or None if not found
    """
    try:
        # Look for FASTA files, excluding intermediate files
        excluded_files = {"alignment.fasta", "combined.fasta"}
        fasta_files = [
            f
            for f in os.listdir(variant_folder)
            if f.endswith(".fasta") and f not in excluded_files
        ]

        if not fasta_files:
            return None

        # Return the first FASTA file found
        fasta_file = os.path.join(variant_folder, fasta_files[0])
        print(f"Found FASTA file: {fasta_files[0]}")

        return fasta_file

    except Exception as e:
        print(f"Error finding FASTA file in {variant_folder}: {e}")
        return None


def main():
    """Main analysis function."""
    if len(sys.argv) != 2:
        print("Usage: python calculate_phylogenetic_distance.py <variant_folder>")
        sys.exit(1)

    variant_folder = sys.argv[1]

    if not os.path.exists(variant_folder):
        print(f"Error: Variant folder {variant_folder} does not exist")
        sys.exit(1)

    try:
        # Find the FASTA file in the variant folder
        input_fasta = find_fasta_file(variant_folder)

        if input_fasta is None:
            print(f"Error: No FASTA file found in {variant_folder}")
            sys.exit(1)

        # Step 1: Run MAFFT alignment
        alignment_file = run_mafft_alignment(input_fasta, variant_folder)

        # Step 2: Calculate maximum phylogenetic distance
        max_distance = calculate_maximum_phylogenetic_distance(alignment_file)

        print(f"Final result: {max_distance}")
        print(max_distance)

    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
