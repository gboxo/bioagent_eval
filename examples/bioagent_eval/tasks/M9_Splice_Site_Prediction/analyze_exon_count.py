#!/usr/bin/env python3
"""
Analyze exon count for a given gene using Ensembl REST API.
This script finds all protein-coding transcripts for a gene and returns the maximum exon count.
"""

import json
import sys
import requests
from typing import Dict, Any, Optional


def get_gene_id(
    gene_name: str, server: str = "https://rest.ensembl.org"
) -> Optional[str]:
    """
    Get Ensembl Gene ID for a given gene symbol.

    Args:
        gene_name: The gene symbol (e.g., 'BRCA1')
        server: Ensembl REST API server URL

    Returns:
        Ensembl Gene ID or None if not found
    """
    url = f"{server}/lookup/symbol/homo_sapiens/{gene_name}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("id")
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving gene ID for {gene_name}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response for {gene_name}: {e}")
        return None


def get_gene_info(
    gene_id: str, server: str = "https://rest.ensembl.org"
) -> Optional[Dict[str, Any]]:
    """
    Get detailed gene information including transcripts and exons.

    Args:
        gene_id: Ensembl Gene ID
        server: Ensembl REST API server URL

    Returns:
        Gene information dictionary or None if error
    """
    url = f"{server}/lookup/id/{gene_id}"
    headers = {"Content-Type": "application/json"}
    params = {"expand": "1"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving gene info for {gene_id}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response for gene {gene_id}: {e}")
        return None


def save_gene_data(gene_name: str, gene_info: Dict[str, Any], output_dir: str) -> None:
    """
    Save gene information to JSON file in data_output directory.

    Args:
        gene_name: Gene symbol
        gene_info: Gene information dictionary
        output_dir: Output directory path
    """
    import os

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{gene_name}_gene_info.json")

    with open(output_file, "w") as f:
        json.dump(gene_info, f, indent=2)

    print(f"Gene information saved to: {output_file}")


def main():
    """Main function to run the analysis."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_exon_count.py <gene_name>")
        print("<answer>0</answer>")
        sys.exit(1)

    gene_name = sys.argv[1]
    max_exons = 0

    try:
        # Get gene ID first
        gene_id = get_gene_id(gene_name)

        # Get detailed gene information
        gene_info = get_gene_info(gene_id)

        # Save gene data to data_output directory
        output_dir = "data_output"
        save_gene_data(gene_name, gene_info, output_dir)

        # Analyze exon count using the retrieved data
        max_exons = 0
        transcripts = gene_info.get("Transcript", [])
        protein_coding_count = 0

        for transcript in transcripts:
            # Only consider protein-coding transcripts
            if transcript.get("biotype") == "protein_coding":
                protein_coding_count += 1
                exons = transcript.get("Exon", [])
                exon_count = len(exons)

                print(
                    f"Transcript {transcript.get('id', 'unknown')}: {exon_count} exons"
                )

                if exon_count > max_exons:
                    max_exons = exon_count

        print(
            f"Found {protein_coding_count} protein-coding transcripts for {gene_name}"
        )
        print(f"Maximum exon count: {max_exons}")

    except Exception as e:
        print(f"Unexpected error: {e}")
        max_exons = 0

    print(f"<answer>{max_exons}</answer>")
    return max_exons


if __name__ == "__main__":
    main()
