#!/usr/bin/env python3
"""
Functional Site Conservation Analysis

Analyzes multiple sequence alignments to identify poorly conserved active site positions.
A position is poorly conserved if the frequency of the most common amino acid is < 50%.
"""

import os
import sys
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import List, Dict, Tuple


def read_fasta(filepath: str) -> Dict[str, str]:
    """Read FASTA file and return dict of header -> sequence."""
    sequences = {}
    current_header = None
    current_seq = []

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_header:
                    sequences[current_header] = "".join(current_seq)
                current_header = line[1:]  # Remove '>'
                current_seq = []
            else:
                current_seq.append(line)

        if current_header:
            sequences[current_header] = "".join(current_seq)

    return sequences


def create_multifasta(variant_dir: str, output_file: str) -> List[str]:
    """Create multi-FASTA file from individual FASTA files and return sequence IDs."""
    fasta_files = sorted(Path(variant_dir).glob("*.fasta"))
    sequence_ids = []

    with open(output_file, "w") as outf:
        for fasta_file in fasta_files:
            sequences = read_fasta(str(fasta_file))
            for header, seq in sequences.items():
                outf.write(f">{header}\n{seq}\n")
                if not sequence_ids:  # First sequence is reference
                    sequence_ids.append(header)
                else:
                    sequence_ids.append(header)

    return sequence_ids


def run_mafft(input_file: str, output_file: str) -> None:
    """Run MAFFT to generate multiple sequence alignment."""
    cmd = ["mafft", "--auto", input_file]

    with open(output_file, "w") as outf:
        result = subprocess.run(cmd, stdout=outf, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"MAFFT failed: {result.stderr}")


def parse_alignment(alignment_file: str) -> Dict[str, str]:
    """Parse MSA file and return aligned sequences."""
    return read_fasta(alignment_file)


def create_position_mapping(reference_seq: str) -> Dict[int, int]:
    """Create mapping from reference sequence positions to alignment column indices."""
    position_mapping = {}
    ref_pos = 1

    for col_idx, char in enumerate(reference_seq):
        if char != "-":  # Non-gap character
            position_mapping[ref_pos] = col_idx
            ref_pos += 1

    return position_mapping


def calculate_conservation(aligned_sequences: Dict[str, str], col_idx: int) -> float:
    """Calculate conservation at a specific alignment column."""
    amino_acids = []

    for seq in aligned_sequences.values():
        if col_idx < len(seq):
            aa = seq[col_idx]
            if aa != "-":  # Skip gaps
                amino_acids.append(aa)

    if not amino_acids:
        return 0.0

    # Count amino acid frequencies
    aa_counts = Counter(amino_acids)
    most_common_count = aa_counts.most_common(1)[0][1]

    return most_common_count / len(amino_acids)


def load_config(variant_dir: str) -> Dict:
    """Load configuration from config.json file in variant directory."""
    config_file = os.path.join(variant_dir, "config.json")

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, "r") as f:
        config = json.load(f)

    return config


def get_active_sites_from_config(variant_dir: str) -> List[int]:
    """Get active site positions from config.json file."""

    config = load_config(variant_dir)
    active_sites = config.get("active_sites", [])

    if not active_sites:
        print(f"Warning: No active sites defined in config for {variant_dir}")

    return active_sites


def analyze_variant(variant_dir: str, variant_num: int, base_dir: str = None) -> str:
    """Analyze a single variant and return poorly conserved positions."""
    print(f"Analyzing variant {variant_num}...")

    # Create output directory for this variant
    data_output_dir = os.path.join(variant_dir, "data_output")
    os.makedirs(data_output_dir, exist_ok=True)

    # Step 1: Create multi-FASTA file
    multifasta_file = os.path.join(
        data_output_dir, f"variant_{variant_num}_sequences.fasta"
    )
    sequence_ids = create_multifasta(variant_dir, multifasta_file)

    # Step 2: Run MAFFT alignment
    alignment_file = os.path.join(
        data_output_dir, f"variant_{variant_num}_alignment.fasta"
    )
    run_mafft(multifasta_file, alignment_file)

    # Step 3: Parse alignment
    aligned_sequences = parse_alignment(alignment_file)

    # Step 4: Get reference sequence (first one)
    reference_id = sequence_ids[0]
    reference_seq = aligned_sequences[reference_id]

    # Step 5: Create position mapping
    position_mapping = create_position_mapping(reference_seq)

    # Step 6: Get active site positions from config file
    active_sites = get_active_sites_from_config(variant_dir)

    # Load config for enzyme family information

    config = load_config(variant_dir)
    enzyme_family = config.get("enzyme_family", "unknown")
    print(f"  Enzyme family: {enzyme_family}")
    print(f"  Active sites to analyze: {active_sites}")

    # Step 7-8: Check conservation of active sites
    poorly_conserved = []

    for site_pos in active_sites:
        if site_pos in position_mapping:
            col_idx = position_mapping[site_pos]
            conservation = calculate_conservation(aligned_sequences, col_idx)

            print(f"  Position {site_pos}: conservation = {conservation:.3f}")

            if conservation < 0.5:
                poorly_conserved.append(site_pos)

    # Step 9: Sort and format result
    poorly_conserved.sort()
    result = ",".join(map(str, poorly_conserved)) if poorly_conserved else ""

    print(f"  Poorly conserved positions: {result if result else 'None'}")
    return result


def main():
    """Main analysis function."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_conservation.py <variant_number> [base_directory]")
        print("  variant_number: Number of the variant to analyze (1-5)")
        print("  base_directory: Optional base directory containing variant folders")
        print("                  If not provided, uses the script's directory")
        sys.exit(1)
    
    variant_num = int(sys.argv[1])
    
    # Use provided base directory or default to script's directory
    if len(sys.argv) >= 3:
        base_dir = sys.argv[2]
    else:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = script_dir
    
    variant_dir = os.path.join(base_dir, f"variant_{variant_num}")
    
    if not os.path.exists(variant_dir):
        print(f"Error: Variant directory {variant_dir} does not exist")
        sys.exit(1)

    result = analyze_variant(variant_dir, variant_num, base_dir)
    print(f"Result for variant {variant_num}: {result}")
    return result


if __name__ == "__main__":
    main()
