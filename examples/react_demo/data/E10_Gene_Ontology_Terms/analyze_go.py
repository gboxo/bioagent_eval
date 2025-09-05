#!/usr/bin/env python3
"""
Gene Ontology Analysis
Retrieves GO annotations from UniProt and counts Molecular Function terms.
"""

import os
import sys
import json
import requests
from typing import Dict, Optional


def load_config(variant_dir: str) -> Optional[Dict]:
    """Load configuration from JSON file."""
    if not os.path.exists(variant_dir):
        print(f"Error: Variant directory {variant_dir} not found")
        return None
    
    config_file = os.path.join(variant_dir, "config.json")
    with open(config_file, 'r') as f:
        config = json.load(f)
        
        return config
        
    return config


def fetch_uniprot_data(uniprot_id: str) -> Optional[Dict]:
    """Fetch UniProt data from the API."""
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    
    try:
        print(f"Fetching data for UniProt ID: {uniprot_id}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Debug: if the entry is inactive, try to get a reason
        if "inactiveReason" in data:
            print(f"Warning: Entry {uniprot_id} is inactive: {data['inactiveReason']}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching UniProt data: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None


def count_molecular_function_terms(uniprot_data: Dict) -> int:
    """Count GO terms that belong to Molecular Function ontology."""
    
    references = uniprot_data["uniProtKBCrossReferences"]
    molecular_function_count = 0
    total_go_terms = 0
    
    for reference in references:
        # Check if this is a GO reference (database should be 'GO')
        if reference.get("database") == "GO":
            total_go_terms += 1
            
            # Check if it has properties with GoTerm
            if "properties" in reference:
                for prop in reference["properties"]:
                    if prop.get("key") == "GoTerm":
                        go_term = prop.get("value", "")
                        
                        # Molecular Function terms start with "F:"
                        if go_term.startswith("F:"):
                            molecular_function_count += 1
                            print(f"  Molecular Function: {go_term}")
                        break
    
    print(f"Total GO terms: {total_go_terms}")
    print(f"Molecular Function terms: {molecular_function_count}")
    
    return molecular_function_count


def analyze_variant(variant_dir: str) -> Optional[int]:
    """Analyze GO annotations for a variant."""
    # Load configuration
    config = load_config(variant_dir)
    
    uniprot_id = config["uniprot_id"]
    description = config.get("description", "Unknown protein")
    
    print(f"Analyzing {description} (UniProt ID: {uniprot_id})")
    
    # Fetch UniProt data
    uniprot_data = fetch_uniprot_data(uniprot_id)
    
    # Count Molecular Function terms
    mf_count = count_molecular_function_terms(uniprot_data)
    
    return mf_count


def main():
    
    variant_dir = sys.argv[1]
    result = analyze_variant(variant_dir)
    
    if result is not None:
        print(f"<answer>{result}</answer>")
        print(result)
    else:
        print("ERROR")


if __name__ == "__main__":
    main()