#!/usr/bin/env python3
"""
Script to create multiple sequence alignment using MAFFT.

This script performs multiple sequence alignment of protein sequences using MAFFT.
"""

import os
import sys
import subprocess
import argparse


def run_mafft_alignment(input_file: str, output_file: str) -> bool:
    """
    Run MAFFT alignment using command line.
    """
    try:
        # Run MAFFT command
        with open(output_file, 'w') as outf:
            cmd = ['mafft', '--auto', input_file]
            result = subprocess.run(cmd, stdout=outf, stderr=subprocess.PIPE, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"MAFFT alignment completed: {output_file}")
            return True
        else:
            print(f"MAFFT error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("Error: MAFFT not found in PATH. Please install MAFFT.")
        return False
    except subprocess.TimeoutExpired:
        print("MAFFT alignment timed out")
        return False
    except Exception as e:
        print(f"Error running MAFFT: {e}")
        return False


def validate_alignment(alignment_file: str) -> bool:
    """
    Validate that the alignment file is properly formatted.
    """
    try:
        sequences = {}
        with open(alignment_file, 'r') as f:
            current_id = None
            current_seq = ""
            
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_id:
                        sequences[current_id] = len(current_seq)
                    current_id = line[1:]
                    current_seq = ""
                else:
                    current_seq += line
            
            if current_id:
                sequences[current_id] = len(current_seq)
        
        # Check all sequences have same length
        lengths = list(sequences.values())
        if len(set(lengths)) == 1 and len(sequences) > 0:
            print(f"Alignment validation passed: {len(sequences)} sequences, length {lengths[0]}")
            return True
        else:
            print(f"Alignment validation failed: sequences have different lengths {set(lengths)}")
            return False
            
    except Exception as e:
        print(f"Error validating alignment: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Create multiple sequence alignment using MAFFT')
    parser.add_argument('input_file', help='Input protein FASTA file')
    parser.add_argument('output_file', help='Output alignment file')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file {args.input_file} not found")
        sys.exit(1)
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output_file) or '.', exist_ok=True)
    
    # Run MAFFT alignment
    success = run_mafft_alignment(args.input_file, args.output_file)
    
    if success:
        validate_alignment(args.output_file)
        print("MSA creation completed successfully.")
    else:
        print("Failed to create alignment.")
        sys.exit(1)


if __name__ == "__main__":
    main()