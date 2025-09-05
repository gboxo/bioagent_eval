#!/usr/bin/env python3
"""
Domain Architecture Analyzer

This script fetches UniProt data for proteins and analyzes their Pfam domain annotations
to find the most common domain across all proteins in a variant.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from collections import Counter
from typing import Dict, List, Optional, Any


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
            
        # Parse UniProt ID from header like >sp|P04637|P53_HUMAN
        if first_line.startswith('>sp|'):
            parts = first_line.split('|')
            if len(parts) >= 2:
                return parts[1]
        elif first_line.startswith('>'):
            # Sometimes the ID might be directly after >
            header_parts = first_line[1:].split()
            if header_parts:
                return header_parts[0]
                
        return None
        
    except Exception as e:
        print(f"Error reading FASTA file {fasta_file}: {e}")
        return None


def fetch_uniprot_data(uniprot_id: str, data_output_dir: str) -> Optional[Dict[Any, Any]]:
    """
    Fetch UniProt data in JSON format from the UniProt API.
    
    Args:
        uniprot_id: UniProt accession ID
        data_output_dir: Directory to save the JSON data
        
    Returns:
        Parsed JSON data or None if failed
    """
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    json_file = os.path.join(data_output_dir, f"{uniprot_id}.json")
    
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
            
        # Save the JSON data to the data_output directory
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


def extract_pfam_domains(data: Dict[Any, Any]) -> List[str]:
    """
    Extract Pfam domain IDs from UniProt JSON data.
    
    Args:
        data: UniProt JSON data
        
    Returns:
        List of Pfam accession IDs
    """
    pfam_ids = []
    
    # Get dbReferences from the data
    db_references = data.get('dbReferences', [])
    
    for db_ref in db_references:
        # Check if this is a Pfam reference
        if db_ref.get('type') == 'Pfam':
            pfam_id = db_ref.get('id')
            if pfam_id:
                pfam_ids.append(pfam_id)
                print(f"Found Pfam domain: {pfam_id}")
                
    return pfam_ids


def get_uniprot_ids_from_variant(variant_folder: str) -> List[str]:
    """
    Get UniProt IDs from all FASTA files in the variant folder.
    
    Args:
        variant_folder: Path to variant folder
        
    Returns:
        List of UniProt IDs
    """
    uniprot_ids = []
    
    # Get all FASTA files in the folder
    fasta_files = [f for f in os.listdir(variant_folder) if f.endswith('.fasta')]
    fasta_files.sort()  # Ensure consistent ordering
    
    for fasta_file in fasta_files:
        fasta_path = os.path.join(variant_folder, fasta_file)
        uniprot_id = extract_uniprot_id_from_fasta(fasta_path)
        
        if uniprot_id:
            uniprot_ids.append(uniprot_id)
        else:
            print(f"Warning: Could not extract UniProt ID from {fasta_file}")
            
    return uniprot_ids


def find_most_common_domain(variant_folder: str) -> str:
    """
    Find the most common Pfam domain across all proteins in a variant.
    
    Args:
        variant_folder: Path to variant folder
        
    Returns:
        Most common Pfam accession ID
    """
    # Create data_output directory if it doesn't exist
    data_output_dir = os.path.join(variant_folder, "data_output")
    os.makedirs(data_output_dir, exist_ok=True)
    
    # Get UniProt IDs from FASTA files
    uniprot_ids = get_uniprot_ids_from_variant(variant_folder)
    
    if not uniprot_ids:
        return "No UniProt IDs found"
        
    print(f"Processing UniProt IDs: {uniprot_ids}")
    
    # Collect all Pfam IDs from all proteins
    all_pfam_ids = []
    
    for uniprot_id in uniprot_ids:
        # Fetch UniProt data
        data = fetch_uniprot_data(uniprot_id, data_output_dir)
        
        if data is None:
            print(f"Warning: Could not fetch data for {uniprot_id}")
            continue
            
        # Extract Pfam domains
        pfam_ids = extract_pfam_domains(data)
        all_pfam_ids.extend(pfam_ids)
        
    if not all_pfam_ids:
        return "No Pfam domains found"
        
    # Count occurrences of each Pfam ID
    pfam_counter = Counter(all_pfam_ids)
    
    print(f"Pfam domain counts: {dict(pfam_counter)}")
    
    # Find the most common Pfam ID
    most_common = pfam_counter.most_common(1)[0]
    most_common_pfam = most_common[0]
    count = most_common[1]
    
    print(f"Most common Pfam domain: {most_common_pfam} (appears {count} times)")
    
    return most_common_pfam


def main():
    """Main analysis function."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_domain_architecture.py <variant_folder>")
        sys.exit(1)
        
    variant_folder = sys.argv[1]
    
    if not os.path.exists(variant_folder):
        print(f"Error: Variant folder {variant_folder} does not exist")
        sys.exit(1)
        
    try:
        result = find_most_common_domain(variant_folder)
        
        print(f"Final result: {result}")
        print(result)
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()