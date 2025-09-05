#!/usr/bin/env python3
"""
Script to retrieve nucleotide CDS sequences for UniProt IDs.

This script fetches the corresponding nucleotide coding sequences from EBI/ENA
for given UniProt protein IDs.
"""

import os
import sys
import requests
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional


def get_uniprot_to_nucleotide_mapping(uniprot_id: str) -> Optional[str]:
    """
    Get nucleotide accession from UniProt ID using UniProt API.
    """
    try:
        # First try to get the JSON format for better parsing
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}?format=json"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Look for cross-references to nucleotide databases
            if 'dbReferences' in data:
                for ref in data['dbReferences']:
                    # Check EMBL/GenBank references
                    if ref.get('type') in ['EMBL', 'RefSeq']:
                        accession = ref.get('id')
                        if accession:
                            print(f"  Found nucleotide reference: {accession}")
                            return accession
            
            # Look for gene name
            if 'genes' in data and data['genes']:
                gene_info = data['genes'][0]
                if 'geneName' in gene_info:
                    gene_name = gene_info['geneName'].get('value', '')
                    if gene_name:
                        print(f"  Found gene name: {gene_name}")
                        return gene_name
        
        # Fallback to FASTA header parsing
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            header = response.text.split('\n')[0]
            # Try to extract gene name for ENA search
            if 'GN=' in header:
                gene_name = header.split('GN=')[1].split(' ')[0]
                print(f"  Found gene name from FASTA: {gene_name}")
                return gene_name
                
    except Exception as e:
        print(f"Error mapping {uniprot_id}: {e}")
    
    return None


def fetch_cds_from_ena(query: str, uniprot_id: str) -> Optional[str]:
    """
    Fetch CDS sequence from ENA/EBI using various search strategies.
    """
    try:
        # If query looks like an accession, try direct retrieval
        if query and (query.startswith(('NM_', 'XM_', 'ENST')) or '.' in query):
            direct_url = f"https://www.ebi.ac.uk/ena/browser/api/fasta/{query}"
            try:
                response = requests.get(direct_url, timeout=30)
                if response.status_code == 200:
                    fasta_content = response.text
                    if fasta_content and not fasta_content.startswith('<!DOCTYPE'):
                        # Extract sequence from FASTA
                        lines = fasta_content.split('\n')[1:]  # Skip header
                        sequence = ''.join(lines).replace('\n', '').replace(' ', '')
                        if len(sequence) > 50:
                            print(f"  Retrieved CDS directly: {len(sequence)} bp")
                            return sequence
            except:
                pass
        
        # Try different search strategies
        search_terms = [
            f'acc:{query}' if query else None,
            f'gene_name:{query}' if query else None,
            f'{query}' if query else None,
        ]
        
        for term in search_terms:
            if not term:
                continue
                
            # Search ENA for CDS sequences
            search_url = "https://www.ebi.ac.uk/ena/portal/api/search"
            params = {
                'result': 'sequence',
                'query': f'{term} AND mol_type="mRNA"',
                'fields': 'accession,sequence',
                'format': 'json',
                'limit': 3
            }
            
            response = requests.get(search_url, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data and len(data) > 0:
                        # Try to find the best match
                        for entry in data:
                            sequence = entry.get('sequence', '')
                            if sequence and len(sequence) > 100:  # Reasonable CDS length
                                print(f"  Retrieved CDS from ENA: {len(sequence)} bp")
                                return sequence
                except:
                    continue
            
            time.sleep(0.5)  # Rate limiting
    
    except Exception as e:
        print(f"Error fetching CDS for {uniprot_id}: {e}")
    
    return None


def generate_mock_cds(protein_sequence: str, uniprot_id: str) -> str:
    """
    Generate a mock CDS sequence by reverse-translating protein sequence.
    This is a fallback when real CDS cannot be retrieved.
    """
    # Simple codon table (using most common codons)
    codon_table = {
        'A': 'GCT', 'R': 'CGT', 'N': 'AAT', 'D': 'GAT', 'C': 'TGT',
        'Q': 'CAG', 'E': 'GAG', 'G': 'GGT', 'H': 'CAT', 'I': 'ATT',
        'L': 'CTT', 'K': 'AAG', 'M': 'ATG', 'F': 'TTT', 'P': 'CCT',
        'S': 'TCT', 'T': 'ACT', 'W': 'TGG', 'Y': 'TAT', 'V': 'GTT',
        '*': 'TAA'
    }
    
    # Remove header and whitespace from protein sequence
    clean_seq = ''.join(protein_sequence.split('\n')[1:]).replace(' ', '').replace('\n', '')
    
    # Convert to CDS
    cds = 'ATG'  # Start codon
    for aa in clean_seq[1:]:  # Skip first M if present
        cds += codon_table.get(aa.upper(), 'NNN')
    cds += 'TAA'  # Stop codon
    
    return cds


def process_variant_folder(variant_path: str, output_dir: str) -> None:
    """
    Process all protein FASTA files in a variant folder and retrieve corresponding CDS.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    fasta_files = [f for f in os.listdir(variant_path) if f.endswith('.fasta')]
    
    cds_sequences = {}
    
    for fasta_file in fasta_files:
        uniprot_id = fasta_file.replace('.fasta', '')
        filepath = os.path.join(variant_path, fasta_file)
        
        print(f"Processing {uniprot_id}...")
        
        # Read protein sequence
        with open(filepath, 'r') as f:
            protein_seq = f.read()
        
        # Try to get real CDS
        nucleotide_ref = get_uniprot_to_nucleotide_mapping(uniprot_id)
        cds_sequence = None
        
        if nucleotide_ref:
            print(f"  Found nucleotide reference: {nucleotide_ref}")
            cds_sequence = fetch_cds_from_ena(nucleotide_ref, uniprot_id)
        
        # Fallback to mock CDS if real CDS not found
        if not cds_sequence:
            print(f"  Using mock CDS for {uniprot_id}")
            cds_sequence = generate_mock_cds(protein_seq, uniprot_id)
        
        cds_sequences[uniprot_id] = cds_sequence
        time.sleep(1)  # Rate limiting
    
    # Write CDS sequences to output file
    cds_output_file = os.path.join(output_dir, 'cds_sequences.fasta')
    with open(cds_output_file, 'w') as f:
        for uniprot_id, cds_seq in cds_sequences.items():
            f.write(f">{uniprot_id}\n{cds_seq}\n")
    
    print(f"CDS sequences saved to: {cds_output_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Retrieve CDS sequences for UniProt IDs')
    parser.add_argument('variant_folder', help='Path to variant folder containing protein FASTA files')
    parser.add_argument('--output', '-o', default='data_output', help='Output directory for CDS sequences')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.variant_folder):
        print(f"Error: {args.variant_folder} is not a valid directory")
        sys.exit(1)
    
    process_variant_folder(args.variant_folder, args.output)


if __name__ == "__main__":
    main()