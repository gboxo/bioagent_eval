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


def load_config(variant_dir: str) -> Optional[Dict]:
    """Load configuration from JSON file."""
    config_file = os.path.join(variant_dir, "config.json")
        
    with open(config_file, 'r') as f:
        config = json.load(f)
        
    return config


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
    
    # Try modern API structure first (uniProtKBCrossReferences)
    references = data.get('uniProtKBCrossReferences', [])
    
    for db_ref in references:
        # Check if this is a Pfam reference
        database = db_ref.get('database') or db_ref.get('type')
        if database == 'Pfam':
            pfam_id = db_ref.get('id')
            if pfam_id:
                pfam_ids.append(pfam_id)
                print(f"Found Pfam domain: {pfam_id}")
                
    return pfam_ids


def get_uniprot_ids_from_config(variant_folder: str) -> List[str]:
    """
    Get UniProt IDs from the configuration file.
    
    Args:
        variant_folder: Path to variant folder
        
    Returns:
        List of UniProt IDs
    """
    config = load_config(variant_folder)
    
    uniprot_ids = config.get("uniprot_ids", [])
    return uniprot_ids


def analyze_variant(variant_folder: str) -> Optional[str]:
    """
    Find the most common Pfam domain across all proteins in a variant.
    
    Args:
        variant_folder: Path to variant folder
        
    Returns:
        Most common Pfam accession ID or None if error
    """
    # Load configuration
    config = load_config(variant_folder)
    
    description = config.get("description", "Unknown protein set")
    print(f"Analyzing {description}")
    
    # Create data_output directory if it doesn't exist
    data_output_dir = os.path.join(variant_folder, "data_output")
    os.makedirs(data_output_dir, exist_ok=True)
    
    # Get UniProt IDs from configuration
    uniprot_ids = get_uniprot_ids_from_config(variant_folder)
    
        
    print(f"Processing UniProt IDs: {uniprot_ids}")
    
    # Collect all Pfam IDs from all proteins
    all_pfam_ids = []
    
    for uniprot_id in uniprot_ids:
        # Fetch UniProt data
        data = fetch_uniprot_data(uniprot_id, data_output_dir)
        
            
        # Extract Pfam domains
        pfam_ids = extract_pfam_domains(data)
        all_pfam_ids.extend(pfam_ids)
        
        
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
    
    result = analyze_variant(variant_folder)
    
    if result is not None:
        print(f"<answer>{result}</answer>")
        print(result)
    else:
        print("ERROR")
        


if __name__ == "__main__":
    main()