#!/usr/bin/env python3
"""
Script to analyze signal peptides from UniProt protein entries.
Retrieves protein data from UniProt REST API and calculates total signal peptide length.
"""

import sys
import requests
import json
from typing import Dict, List, Any


def fetch_uniprot_data(uniprot_id: str) -> Dict[str, Any]:
    """
    Fetch protein data from UniProt REST API.
    
    Args:
        uniprot_id: UniProt accession ID
        
    Returns:
        JSON data from UniProt API
        
    Raises:
        requests.RequestException: If API request fails
    """
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to fetch data for {uniprot_id}: {e}")


def calculate_signal_peptide_length(protein_data: Dict[str, Any]) -> int:
    """
    Calculate total length of signal peptides from UniProt protein data.
    
    Args:
        protein_data: JSON data from UniProt API
        
    Returns:
        Total length of all signal peptides (0 if none found)
    """
    total_length = 0
    
    # Navigate to features
    features = protein_data.get('features', [])
    
    # Filter for signal peptide features
    for feature in features:
        if feature.get('type') == 'Signal':
            location = feature.get('location', {})
            start = location.get('start', {}).get('value')
            end = location.get('end', {}).get('value')
            
            if start is not None and end is not None:
                # Calculate length (end - start + 1)
                length = end - start + 1
                total_length += length
                print(f"Found signal peptide: positions {start}-{end}, length {length}")
    
    return total_length


def main():
    """Main function to process UniProt ID and calculate signal peptide length."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_signal_peptides.py <uniprot_id>")
        sys.exit(1)
    
    uniprot_id = sys.argv[1]
    
    try:
        # Fetch protein data
        print(f"Fetching data for UniProt ID: {uniprot_id}")
        protein_data = fetch_uniprot_data(uniprot_id)
        
        # Calculate signal peptide length
        total_length = calculate_signal_peptide_length(protein_data)
        
        print(f"Total signal peptide length: {total_length}")
        print(f"<answer>{total_length}</answer>")
        
        return total_length
        
    except Exception as e:
        print(f"Error processing {uniprot_id}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()