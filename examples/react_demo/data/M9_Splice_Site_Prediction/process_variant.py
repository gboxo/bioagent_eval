#!/usr/bin/env python3
"""
Process a single variant by reading its config.json and analyzing exon count.
"""

import json
import sys
import os
import subprocess


def process_variant(variant_dir: str) -> int:
    """
    Process a variant directory by reading config.json and analyzing the gene.
    
    Args:
        variant_dir: Path to variant directory
        
    Returns:
        Maximum exon count for the gene
    """
    config_path = os.path.join(variant_dir, "config.json")
    
    if not os.path.exists(config_path):
        print(f"Error: config.json not found in {variant_dir}")
        return 0
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        gene_name = config.get("gene_name")
        if not gene_name:
            print(f"Error: gene_name not found in config.json")
            return 0
        
        print(f"Processing variant: {gene_name}")
        
        # Call the analyze_exon_count.py script
        try:
            result = subprocess.run(['python3', 'analyze_exon_count.py', gene_name], 
                                    capture_output=True, text=True, check=True)
            output = result.stdout
            
            # Extract the answer from the output
            import re
            match = re.search(r'<answer>(\d+)</answer>', output)
            if match:
                return int(match.group(1))
            else:
                print("Error: Could not find answer in output")
                return 0
                
        except subprocess.CalledProcessError as e:
            print(f"Error running analysis: {e}")
            return 0
        
    except json.JSONDecodeError as e:
        print(f"Error parsing config.json: {e}")
        return 0
    except Exception as e:
        print(f"Error processing variant: {e}")
        return 0


def main():
    """Main function to process a single variant."""
    if len(sys.argv) != 2:
        print("Usage: python process_variant.py <variant_directory>")
        sys.exit(1)
    
    variant_dir = sys.argv[1]
    result = process_variant(variant_dir)
    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    main()