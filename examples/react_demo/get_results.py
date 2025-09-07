#!/usr/bin/env python3
"""
Script to collect all results.csv files from [E,M,H]{d}_... folders
and combine them into a single JSON file called task_results.json
Handles multi-column CSV data and verbose outputs properly.
"""

import os
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def find_task_folders(data_dir: Path) -> List[Path]:
    """Find all folders matching pattern [E,M,H]{d}_..."""
    pattern = re.compile(r'^[EMH]\d+_')
    folders = []
    
    for item in data_dir.iterdir():
        if item.is_dir() and pattern.match(item.name):
            results_csv = item / 'results.csv'
            if results_csv.exists():
                folders.append(item)
    
    return sorted(folders)


def extract_final_result_from_verbose(task_name: str, lines: List[str]) -> Optional[str]:
    """Extract final result from verbose output based on task type."""
    
    if task_name == 'H8_Druggability_Assessment':
        # Look for final PDB ID results like "1A3N", "3PBL", etc.
        for line in reversed(lines):
            line = line.strip()
            # Match PDB ID pattern (4 characters, alphanumeric)
            if re.match(r'^[A-Z0-9]{4}$', line):
                return line
    
    elif task_name == 'H10_variant_Structural_Mapping':
        # Look for final variant results like "A95V", "D23N", etc.
        for line in reversed(lines):
            line = line.strip()
            # Match variant pattern (letter+number+letter)
            if re.match(r'^[A-Z]\d+[A-Z]$', line):
                return line
    
    return None


def clean_multi_column_result(row_data: List[str]) -> str:
    """Clean and combine multi-column results into a single string."""
    # Remove empty strings and None values
    cleaned = [str(item).strip() for item in row_data if item and str(item).strip()]
    
    if len(cleaned) == 1:
        return cleaned[0]
    elif len(cleaned) > 1:
        # Join multiple values with commas
        return ','.join(cleaned)
    else:
        return ""


def parse_verbose_csv(lines: List[str], task_name: str) -> List[Dict[str, Any]]:
    """Parse verbose CSV files that contain debug output."""
    results = []
    current_variant = None
    variant_lines = []
    
    for line_num, line in enumerate(lines):
        if line_num == 0:  # Skip header
            continue
            
        line = line.strip()
        if not line:
            continue
        
        # Check if line starts with a variant number
        variant_match = re.match(r'^(\d+),(.*)$', line)
        if variant_match:
            # Process previous variant if exists
            if current_variant is not None:
                final_result = extract_final_result_from_verbose(task_name, variant_lines)
                results.append({
                    'variant': current_variant,
                    'result': final_result or "NO_RESULT"
                })
            
            # Start new variant
            current_variant = int(variant_match.group(1))
            variant_lines = [variant_match.group(2)]
        else:
            # Add to current variant's lines
            if current_variant is not None:
                variant_lines.append(line)
    
    # Process the last variant
    if current_variant is not None:
        final_result = extract_final_result_from_verbose(task_name, variant_lines)
        results.append({
            'variant': current_variant,
            'result': final_result or "NO_RESULT"
        })
    
    return results


def read_results_csv(csv_path: Path, task_name: str) -> List[Dict[str, Any]]:
    """Read a results.csv file and return list of dictionaries with improved parsing."""
    results = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        if len(lines) <= 1:
            print(f"  Warning: Empty or header-only CSV file")
            return results
        
        # Check if this is a verbose output file (H8, H10 types)
        if task_name in ['H8_Druggability_Assessment', 'H10_variant_Structural_Mapping']:
            return parse_verbose_csv(lines, task_name)
        
        # Normal CSV parsing with multi-column support
        csv_reader = csv.reader(lines)
        header = next(csv_reader)  # Skip header
        
        current_variant = None
        variant_lines = []
        
        for row in csv_reader:
            if not row:  # Skip empty rows
                continue
                
            # Check if first column is a variant number
            try:
                variant_num = int(row[0])
                # Process previous variant if exists
                if current_variant is not None:
                    result_data = clean_multi_column_result(variant_lines)
                    if result_data or current_variant <= 5:  # Include empty results for variants 1-5
                        results.append({
                            'variant': current_variant,
                            'result': result_data
                        })
                
                # Start new variant
                current_variant = variant_num
                variant_lines = row[1:] if len(row) > 1 else [""]
                
            except (ValueError, IndexError):
                # Not a variant number, treat as continuation of current variant
                if current_variant is not None:
                    variant_lines.extend(row)
        
        # Process the last variant
        if current_variant is not None:
            result_data = clean_multi_column_result(variant_lines)
            if result_data or current_variant <= 5:
                results.append({
                    'variant': current_variant,
                    'result': result_data
                })
                
    except Exception as e:
        print(f"  Error reading {csv_path}: {e}")
        
    return results


def validate_results(task_name: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate and clean results to ensure proper format."""
    validated = []
    
    # Ensure we have exactly variants 1-5
    variant_dict = {r['variant']: r['result'] for r in results if isinstance(r.get('variant'), int)}
    
    for variant_num in [1, 2, 3, 4, 5]:
        result_value = variant_dict.get(variant_num, "")
        
        # Clean up result value
        if isinstance(result_value, str):
            result_value = result_value.strip()
        
        validated.append({
            'variant': variant_num,
            'result': result_value
        })
    
    return validated


def main():
    """Main function to collect and convert results."""
    script_dir = Path(__file__).parent
    data_dir = script_dir / 'data'
    
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return
    
    # Find all task folders
    task_folders = find_task_folders(data_dir)
    print(f"Found {len(task_folders)} task folders with results.csv files")
    
    # Collect all results
    all_results = {}
    issues_found = []
    
    for folder in task_folders:
        task_name = folder.name
        csv_path = folder / 'results.csv'
        
        print(f"Processing {task_name}...")
        raw_results = read_results_csv(csv_path, task_name)
        
        if raw_results:
            # Validate and standardize results
            validated_results = validate_results(task_name, raw_results)
            all_results[task_name] = validated_results
            
            # Check for issues
            if len(raw_results) != 5:
                issues_found.append(f"{task_name}: Expected 5 variants, got {len(raw_results)}")
                
            empty_results = sum(1 for r in validated_results if not r['result'])
            if empty_results > 0:
                issues_found.append(f"{task_name}: {empty_results} empty results")
                
        else:
            print(f"  Warning: No data found in {csv_path}")
            # Create empty entries for missing data
            all_results[task_name] = validate_results(task_name, [])
            issues_found.append(f"{task_name}: No data in CSV file")
    
    # Write to JSON file
    output_path = script_dir / 'task_results.json'
    
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(all_results, file, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully created {output_path}")
        print(f"Total tasks processed: {len(all_results)}")
        
        # Print summary
        total_variants = sum(len(results) for results in all_results.values())
        print(f"Total variant results: {total_variants}")
        
        # Report issues
        if issues_found:
            print(f"\nIssues found ({len(issues_found)}):")
            for issue in issues_found:
                print(f"  - {issue}")
        else:
            print(f"\n✅ All tasks processed successfully with proper format!")
        
    except Exception as e:
        print(f"Error writing JSON file: {e}")


if __name__ == '__main__':
    main()