#!/usr/bin/env python3
"""
Script to parse PAML results and count branches with positive selection.

This script reads the PAML output file and counts branches with dN/dS > 1.0.
"""

import os
import sys
import argparse
import re


def parse_mlc_file(mlc_file: str) -> int:
    """
    Parse the PAML mlc output file and count branches with dN/dS > 1.0.
    """
    if not os.path.exists(mlc_file):
        print(f"Error: PAML output file {mlc_file} not found")
        return -1
    
    positive_selection_count = 0
    dnds_values = []
    
    try:
        with open(mlc_file, 'r') as f:
            content = f.read()
        
        # Look for the branch results table
        # Pattern to match lines with branch data and dN/dS values
        branch_pattern = r'^\s*\d+\.\.\d+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+'
        
        lines = content.split('\n')
        in_branch_section = False
        
        for line in lines:
            # Look for branch results section
            if 'dN/dS' in line and ('branch' in line.lower() or 'w' in line):
                in_branch_section = True
                continue
            
            if in_branch_section:
                # Try to extract dN/dS value from branch line
                match = re.search(branch_pattern, line)
                if match:
                    dnds_value = float(match.group(1))
                    dnds_values.append(dnds_value)
                    if dnds_value > 1.0:
                        positive_selection_count += 1
                    print(f"Branch dN/dS: {dnds_value}")
                
                # Alternative pattern for different output formats
                elif re.search(r'^\s*\d+\.\.\d+', line):
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            # dN/dS is typically the 5th column (index 4)
                            dnds_value = float(parts[4])
                            dnds_values.append(dnds_value)
                            if dnds_value > 1.0:
                                positive_selection_count += 1
                            print(f"Branch dN/dS: {dnds_value}")
                        except (ValueError, IndexError):
                            continue
                
                # Stop if we hit another major section
                elif line.strip() and not line.startswith(' ') and 'tree' in line.lower():
                    break
        
        # If no branches found with the above method, try alternative parsing
        if not dnds_values:
            print("Primary parsing failed. Trying alternative method...")
            positive_selection_count = parse_mlc_alternative(content)
        
        print(f"Total branches analyzed: {len(dnds_values)}")
        print(f"Branches with positive selection (dN/dS > 1): {positive_selection_count}")
        
        return positive_selection_count
        
    except Exception as e:
        print(f"Error parsing PAML results: {e}")
        return -1


def parse_mlc_alternative(content: str) -> int:
    """
    Alternative parsing method for PAML results.
    """
    positive_count = 0
    
    # Look for omega or w values greater than 1
    omega_patterns = [
        r'omega\s*=\s*([\d.]+)',
        r'w\s*=\s*([\d.]+)',
        r'dN/dS\s*=\s*([\d.]+)'
    ]
    
    for pattern in omega_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            try:
                value = float(match)
                if value > 1.0:
                    positive_count += 1
                print(f"Found omega/dN/dS value: {value}")
            except ValueError:
                continue
    
    if positive_count == 0:
        # Last resort: look for any decimal numbers > 1 in lines mentioning dN/dS
        lines = content.split('\n')
        for line in lines:
            if 'dn/ds' in line.lower() or 'dnds' in line.lower():
                numbers = re.findall(r'[\d.]+', line)
                for num in numbers:
                    try:
                        value = float(num)
                        if value > 1.0 and value < 10.0:  # Reasonable range for dN/dS
                            positive_count += 1
                            print(f"Potential dN/dS > 1: {value}")
                    except ValueError:
                        continue
    
    return positive_count


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Parse PAML results and count positive selection')
    parser.add_argument('--mlc-file', default='mlc', help='PAML output file')
    
    args = parser.parse_args()
    
    # Parse results
    count = parse_mlc_file(args.mlc_file)
    
    if count >= 0:
        print(f"\n<answer>{count}</answer>")
        return count
    else:
        print("Failed to parse results")
        sys.exit(1)


if __name__ == "__main__":
    main()