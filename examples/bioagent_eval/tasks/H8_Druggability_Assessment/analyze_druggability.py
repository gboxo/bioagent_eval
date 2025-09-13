#!/usr/bin/env python3
"""
Druggability Assessment using fpocket
"""

import subprocess
import os
import sys
import re
from typing import Dict, Optional, Tuple
import glob


def run_fpocket(pdb_file: str) -> bool:
    """Run fpocket on a PDB file."""
    try:
        # Run fpocket command
        result = subprocess.run(['fpocket', '-f', pdb_file], 
                              capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running fpocket on {pdb_file}: {e}")
        return False
    except FileNotFoundError:
        print("Error: fpocket not found. Please install fpocket.")
        return False


def parse_fpocket_output(pdb_id: str, output_dir: str) -> Optional[float]:
    """Parse fpocket output to extract the highest druggability score from all pockets."""
    info_file = os.path.join(output_dir, f"{pdb_id}_info.txt")
    
    if not os.path.exists(info_file):
        print(f"Warning: Info file {info_file} not found")
        return None
    
    try:
        with open(info_file, 'r') as f:
            content = f.read()
        
        # Find all druggability scores
        pattern = r'Druggability Score : \t([\d.]+)'
        matches = re.findall(pattern, content)
        
        if matches:
            # Convert to floats and get the maximum
            scores = [float(score) for score in matches]
            max_score = max(scores)
            print(f"  Found {len(scores)} pockets, highest druggability score: {max_score}")
            return max_score
        else:
            print(f"Warning: Could not find druggability scores in {info_file}")
            return None
            
    except Exception as e:
        print(f"Error parsing {info_file}: {e}")
        return None


def analyze_variant(variant_dir: str) -> Optional[str]:
    """Analyze all PDB files in a variant directory and return the PDB ID with highest druggability."""
    if not os.path.exists(variant_dir):
        print(f"Error: Variant directory {variant_dir} not found")
        return None
    
    # Get all PDB files but exclude fpocket output files
    all_pdb_files = glob.glob(os.path.join(variant_dir, "*.pdb"))
    pdb_files = [f for f in all_pdb_files if not f.endswith("_out.pdb")]
    
    if not pdb_files:
        print(f"Error: No PDB files found in {variant_dir}")
        return None
    
    best_pdb_id = None
    best_score = -1.0
    
    for pdb_file in pdb_files:
        pdb_id = os.path.basename(pdb_file).replace('.pdb', '')
        print(f"Processing {pdb_id}...")
        
        # Run fpocket
        if not run_fpocket(pdb_file):
            print(f"Failed to run fpocket on {pdb_file}")
            continue
        
        # Parse output
        output_dir = os.path.join(variant_dir, f"{pdb_id}_out")
        score = parse_fpocket_output(pdb_id, output_dir)
        
        if score is not None:
            print(f"  Druggability score: {score}")
            if score > best_score:
                best_score = score
                best_pdb_id = pdb_id
        else:
            print(f"  No druggability score found")
    
    if best_pdb_id:
        print(f"Best PDB ID: {best_pdb_id} with score: {best_score}")
    else:
        print("No valid druggability scores found")
    
    return best_pdb_id


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_druggability.py <variant_directory>")
        sys.exit(1)
    
    variant_dir = sys.argv[1]
    result = analyze_variant(variant_dir)
    
    if result:
        print(f"<answer>{result}</answer>")
    else:
        print("<answer>ERROR</answer>")


if __name__ == "__main__":
    main()