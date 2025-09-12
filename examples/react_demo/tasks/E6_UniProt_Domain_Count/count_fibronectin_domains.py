#!/usr/bin/env python3
"""
UniProt Fibronectin Type-III Domain Counter

This script fetches UniProt data for a protein and counts the number of 
'Fibronectin type-III' domains in its feature annotations.
"""

import json
import sys
import os
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


def fetch_uniprot_data(uniprot_id: str, output_dir: str) -> Optional[Dict[Any, Any]]:
    """
    Fetch UniProt data in JSON format from the UniProt API.
    
    Args:
        uniprot_id: UniProt accession ID
        output_dir: Directory to save the JSON data
        
    Returns:
        Parsed JSON data or None if failed
    """
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    json_file = os.path.join(output_dir, f"{uniprot_id}.json")
    
    try:
        # Check if JSON file already exists
        if os.path.exists(json_file):
            print(f"Loading cached data from {json_file}")
            with open(json_file, 'r') as f:
                return json.load(f)
        
        print(f"Fetching data for {uniprot_id} from UniProt API...")
        
        # Fetch data from UniProt API
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
        # Save the JSON data to the output directory
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"Data saved to {json_file}")
        return data
        
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} for {uniprot_id}")
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason} for {uniprot_id}")
        return None
    except Exception as e:
        print(f"Error fetching data for {uniprot_id}: {e}")
        return None


def count_fibronectin_domains(data: Dict[Any, Any]) -> int:
    """
    Count Fibronectin type-III domains in UniProt feature data.
    
    Args:
        data: UniProt JSON data
        
    Returns:
        Number of Fibronectin type-III domains
    """
    count = 0
    
    # Get features from the data
    features = data.get('features', [])
    
    for feature in features:
        # Check if feature type is 'Domain'
        if feature.get('type') == 'Domain':
            # Check if description contains 'Fibronectin type-III'
            description = feature.get('description', '')
            if 'Fibronectin type-III' in description:
                count += 1
                print(f"Found Fibronectin type-III domain: {description}")
                
    return count


def extract_uniprot_id_from_fasta(fasta_file: str) -> Optional[str]:
    """
    Extract UniProt ID from FASTA file header.
    
    Args:
        fasta_file: Path to FASTA file
        
    Returns:
        UniProt ID or None if not found
    """
    try:
        with open(fasta_file, 'r') as f:
            first_line = f.readline().strip()
            
        # Parse UniProt ID from header like >sp|P06213|INSR_HUMAN
        if first_line.startswith('>sp|'):
            parts = first_line.split('|')
            if len(parts) >= 2:
                return parts[1]
                
        return None
        
    except Exception as e:
        print(f"Error reading FASTA file {fasta_file}: {e}")
        return None


def main():
    """Main analysis function."""
    if len(sys.argv) != 2:
        print("Usage: python count_fibronectin_domains.py <variant_folder>")
        sys.exit(1)
        
    variant_folder = sys.argv[1]
    
    if not os.path.exists(variant_folder):
        print(f"Error: Variant folder {variant_folder} does not exist")
        sys.exit(1)
        
    # Find FASTA file in the variant folder
    fasta_files = [f for f in os.listdir(variant_folder) if f.endswith('.fasta')]
    
    if not fasta_files:
        print(f"Error: No FASTA file found in {variant_folder}")
        sys.exit(1)
        
    fasta_file = os.path.join(variant_folder, fasta_files[0])
    
    # Extract UniProt ID from FASTA file
    uniprot_id = extract_uniprot_id_from_fasta(fasta_file)
    
    if not uniprot_id:
        print(f"Error: Could not extract UniProt ID from {fasta_file}")
        sys.exit(1)
        
    print(f"Processing UniProt ID: {uniprot_id}")
    
    # Fetch UniProt data
    data = fetch_uniprot_data(uniprot_id, variant_folder)
    
    if data is None:
        print(f"Error: Could not fetch data for {uniprot_id}")
        sys.exit(1)
        
    # Count Fibronectin type-III domains
    count = count_fibronectin_domains(data)
    
    print(f"Total Fibronectin type-III domains found: {count}")
    print(count)


if __name__ == "__main__":
    main()