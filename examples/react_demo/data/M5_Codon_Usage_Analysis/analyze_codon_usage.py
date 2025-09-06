#!/usr/bin/env python3
"""
Codon Usage Analysis Script.

Analyzes codon usage and calculates Codon Adaptation Index (CAI) for E. coli genes.
"""

import json
import os
import sys
import time

from Bio import Entrez, SeqIO
from Bio.SeqUtils import CodonAdaptationIndex


def fetch_cds_sequences(genes, email="gerardboxocorominas@gmail.com"):
    """
    Fetch CDS sequences for given E. coli genes from NCBI.

    Args:
        genes: List of gene names
        email: Email for NCBI Entrez

    Returns:
        Dictionary mapping gene names to their CDS sequences
    """
    import re
    from io import StringIO

    Entrez.email = email
    sequences = {}

    for gene in genes:
        print(f"Fetching CDS for gene: {gene}")

        search_query = f'Escherichia coli[Orgn] AND "{gene} gene" AND CDS'

        # Search for the gene
        handle = Entrez.esearch(db="nucleotide", term=search_query, retmax=5)
        search_results = Entrez.read(handle)
        handle.close()

        if not search_results["IdList"]:
            print(f"  No results found for {gene}")
            continue

        # Try the first few results
        for seq_id in search_results["IdList"][:3]:
            # Get summary to check length
            handle = Entrez.esummary(db="nucleotide", id=seq_id)
            summary = Entrez.read(handle)
            handle.close()

            # Parse length from BioPython IntegerElement
            length_obj = summary[0].get("Length", 0)
            match = re.search(r"IntegerElement\((\d+)", str(length_obj))
            length = int(match.group(1)) if match else int(str(length_obj))

            # Skip very long sequences (whole genomes)
            if length > 50000:
                continue

            title = str(summary[0].get("Title", ""))
            print(f"  Trying {seq_id}: {title[:50]}... ({length} bp)")

            # Fetch the sequence
            handle = Entrez.efetch(
                db="nucleotide", id=seq_id, rettype="fasta", retmode="text"
            )
            fasta_content = handle.read()
            handle.close()

            # Parse FASTA content
            if len(fasta_content) > 100:
                records = list(SeqIO.parse(StringIO(fasta_content), "fasta"))
                if records and len(str(records[0].seq)) >= 300:
                    sequences[gene] = str(records[0].seq)
                    print(f"  Success: {gene} ({len(records[0].seq)} bp)")
                    break

        time.sleep(3)  # Be respectful to NCBI

    return sequences


def calculate_cai_scores(sequences):
    """
    Calculate CAI scores for the given sequences using E. coli reference genes.

    Args:
        sequences: Dictionary mapping gene names to CDS sequences

    Returns:
        Dictionary mapping gene names to their CAI scores
    """
    if not sequences:
        return {}

    # Clean and validate sequences
    valid_sequences = {}
    for gene, sequence in sequences.items():
        # Clean sequence - keep only DNA bases
        clean_seq = "".join(c for c in sequence.upper() if c in "ATGC")

        # Trim to multiple of 3
        if len(clean_seq) % 3 != 0:
            clean_seq = clean_seq[: len(clean_seq) - (len(clean_seq) % 3)]

        if len(clean_seq) >= 300:  # Minimum reasonable CDS length
            valid_sequences[gene] = clean_seq

    if not valid_sequences:
        return {}

    # Create CAI calculator and compute scores
    print("Creating codon adaptation index from reference sequences...")
    cai_calculator = CodonAdaptationIndex(list(valid_sequences.values()))

    cai_scores = {}
    for gene, sequence in valid_sequences.items():
        cai_score = cai_calculator.calculate(sequence)
        cai_scores[gene] = cai_score
        print(f"CAI for {gene}: {cai_score:.4f}")

    return cai_scores


def find_highest_cai_gene(cai_scores):
    """
    Find the gene with the highest CAI score.

    Args:
        cai_scores: Dictionary mapping gene names to CAI scores

    Returns:
        Gene name with highest CAI score
    """
    if not cai_scores:
        return "No genes analyzed"

    highest_gene = max(cai_scores, key=cai_scores.get)
    highest_score = cai_scores[highest_gene]

    print(f"\nHighest CAI score: {highest_gene} with CAI = {highest_score:.4f}")
    return highest_gene


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_codon_usage.py <variant_folder>")
        sys.exit(1)

    variant_folder = sys.argv[1]
    config_file = os.path.join(variant_folder, "config.json")

    # Load gene list from config
    with open(config_file, "r") as f:
        config = json.load(f)
    genes = config["genes"]
    print(f"Analyzing {len(genes)} genes: {genes}")

    # Create output directory
    data_output_dir = os.path.join(os.path.dirname(variant_folder), "data_output")
    os.makedirs(data_output_dir, exist_ok=True)

    # Fetch sequences and calculate CAI scores
    print("Fetching CDS sequences from NCBI...")
    sequences = fetch_cds_sequences(genes)
    
    print("\nCalculating CAI scores...")
    cai_scores = calculate_cai_scores(sequences)
    
    # Find highest CAI gene
    highest_cai_gene = find_highest_cai_gene(cai_scores)

    # Save results
    results_file = os.path.join(data_output_dir, f"{os.path.basename(variant_folder)}_detailed_results.json")
    detailed_results = {
        "genes": genes,
        "cai_scores": cai_scores,
        "highest_cai_gene": highest_cai_gene,
        "sequence_lengths": {gene: len(seq) for gene, seq in sequences.items()},
    }

    with open(results_file, "w") as f:
        json.dump(detailed_results, f, indent=2)

    print(f"\nDetailed results saved to: {results_file}")
    print(f"Result: {highest_cai_gene}")

    return highest_cai_gene


if __name__ == "__main__":
    result = main()
    print(f"<answer>{result}</answer>")
