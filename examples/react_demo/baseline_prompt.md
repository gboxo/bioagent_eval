## Bioinformatic's task




You will be provided with a task that requires performing multiple steps like, data acquisition, analysis and processing.

<example-task>
  "E1_PDB_Cysteine_Count": {
    "description": "You need to download a .pdb file from the Protein Data Bank (PDB) website, then you will need to extract amino acid sequence (if there are multiple chains present select the first one), and finally count number of cysteine residues. After that you will return a single integer value for the number of cysteine residues in the following format <answer>int</answer>",
    "variants": {
      "variant_1": "1UBQ",
      "variant_2": "1A3N",
      "variant_3": "2LYZ",
      "variant_4": "1HTM",
      "variant_5": "1CRN"
    }
  },
</example-task>


For a given task you will need to perform the following steps:

1) Analyze the task description and return the following items:
a) What is the main data source? 
b) What is the input format?
c) What is the expected output?
d) What are the steps to perform this task?
e) What programs and python libraries are required to perform this task.
2) Acquire the data. Create a bash script to:
a) Create a folder with the task name
b) Download the required data and store it in the folder under the subfolder task_name/variant_i
3) Create the necessary python scripts to perform the task and the order and a bash script to run the python scripts
a) Create the necessary scripts to perform the task for any variant, the script should be agnostic to the variant.
b) Create a bash script to run sequentially the python files


<example-task-analysis>
Based on the example task "E1_PDB_Cysteine_Count":

**a) Main data source:** Protein Data Bank (PDB) - specifically protein structure files in PDB format

**b) Input format:** PDB structure files (typically .pdb files) accessed via PDB IDs (e.g., 1UBQ, 1A3N, etc.)

**c) Expected output:** Count of cysteine residues in each protein structure

**d) Steps to perform this task:**
1. Download PDB structure files using the provided PDB IDs
2. Parse the PDB files to extract amino acid sequences
3. Identify and count cysteine residues (single letter code: C)
4. Output the results for each variant

**e) Required programs and Python libraries:**
- `wget` or `curl` (for downloading)
- Python libraries: `requests`, `biopython`, `pandas` (optional for output formatting)

</example-task-analysis>


<example-data-acquisition>

```{bash}[acquire_data.sh ]
#!/bin/bash

# Data acquisition script for PDB Cysteine Count task
# Usage: ./acquire_data.sh <task_name> <pdb_id1> <pdb_id2> ...

TASK_NAME=$1
shift  # Remove first argument, rest are PDB IDs
PDB_IDS=("$@")

# Create main task folder
mkdir -p "$TASK_NAME"
echo "Created task folder: $TASK_NAME"

# Download PDB files for each variant
for i in "${!PDB_IDS[@]}"; do
    variant_num=$((i + 1))
    variant_folder="${TASK_NAME}/variant_${variant_num}"
    pdb_id="${PDB_IDS[$i]}"
    
    # Create variant subfolder
    mkdir -p "$variant_folder"
    echo "Processing variant_${variant_num}: ${pdb_id}"
    
    # Download PDB file from RCSB PDB
    pdb_url="https://files.rcsb.org/download/${pdb_id}.pdb"
    output_file="${variant_folder}/${pdb_id}.pdb"
    
    if wget -q "$pdb_url" -O "$output_file"; then
        echo "Successfully downloaded ${pdb_id}.pdb to ${variant_folder}/"
    else
        echo "Error: Failed to download ${pdb_id}.pdb"
        # Try alternative URL format
        pdb_url_alt="https://files.rcsb.org/view/${pdb_id}.pdb"
        if wget -q "$pdb_url_alt" -O "$output_file"; then
            echo "Successfully downloaded ${pdb_id}.pdb using alternative URL"
        else
            echo "Error: Both download attempts failed for ${pdb_id}"
        fi
    fi
done

echo "Data acquisition completed for task: $TASK_NAME"
```

</example-data-acquisition>



<example-task-script>

```{python}[pdb_cysteine_counter.py]
#!/usr/bin/env python3
"""
PDB Parser and Cysteine Counter
Extracts amino acid sequences from PDB files and counts cysteine residues
"""

import os
import sys
import glob
from collections import defaultdict
import argparse

def parse_pdb_file(pdb_file_path):
    """
    Parse a PDB file and extract amino acid sequences
    Returns a dictionary with chain IDs as keys and sequences as values
    """
    sequences = defaultdict(str)
    
    try:
        with open(pdb_file_path, 'r') as file:
            for line in file:
                # Parse ATOM records for amino acids
                if line.startswith('ATOM'):
                    # Extract relevant fields
                    atom_name = line[12:16].strip()
                    residue_name = line[17:20].strip()
                    chain_id = line[21:22].strip()
                    residue_number = line[22:26].strip()
                    
                    # Only consider CA atoms (one per residue) to avoid duplicates
                    if atom_name == 'CA':
                        # Convert 3-letter code to 1-letter code
                        aa_code = three_to_one_letter(residue_name)
                        if aa_code:
                            # Use residue number to maintain order and avoid duplicates
                            key = f"{chain_id}_{residue_number}"
                            if key not in sequences:
                                sequences[chain_id] += aa_code
                            
    except FileNotFoundError:
        print(f"Error: File {pdb_file_path} not found")
        return {}
    except Exception as e:
        print(f"Error parsing {pdb_file_path}: {e}")
        return {}
    
    return dict(sequences)

def three_to_one_letter(three_letter_code):
    """Convert 3-letter amino acid code to 1-letter code"""
    conversion_dict = {
        'ALA': 'A', 'CYS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F',
        'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K', 'LEU': 'L',
        'MET': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R',
        'SER': 'S', 'THR': 'T', 'VAL': 'V', 'TRP': 'W', 'TYR': 'Y'
    }
    return conversion_dict.get(three_letter_code.upper(), None)

def count_cysteine_residues(sequence):
    """Count the number of cysteine residues (C) in a sequence"""
    return sequence.count('C')

def process_variant(variant_path, variant_name):
    """Process a single variant folder"""
    results = []
    
    # Find PDB files in the variant folder
    pdb_files = glob.glob(os.path.join(variant_path, "*.pdb"))
    
    if not pdb_files:
        print(f"Warning: No PDB files found in {variant_path}")
        return results
    
    for pdb_file in pdb_files:
        pdb_id = os.path.basename(pdb_file).replace('.pdb', '')
        print(f"Processing {pdb_id}...")
        
        # Parse the PDB file
        sequences = parse_pdb_file(pdb_file)
        
        if not sequences:
            print(f"Warning: No sequences extracted from {pdb_file}")
            continue
        
        # Count cysteines for each chain
        total_cysteines = 0
        chain_details = []
        
        for chain_id, sequence in sequences.items():
            cys_count = count_cysteine_residues(sequence)
            total_cysteines += cys_count
            chain_details.append({
                'chain_id': chain_id,
                'sequence_length': len(sequence),
                'cysteine_count': cys_count,
                'sequence': sequence
            })
        
        result = {
            'variant': variant_name,
            'pdb_id': pdb_id,
            'total_cysteine_count': total_cysteines,
            'chains': chain_details
        }
        
        results.append(result)
        
        print(f"  Total cysteine residues: {total_cysteines}")
        for chain in chain_details:
            print(f"  Chain {chain['chain_id']}: {chain['cysteine_count']} cysteines (length: {chain['sequence_length']})")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Count cysteine residues in PDB files')
    parser.add_argument('task_folder', help='Path to the task folder containing variants')
    parser.add_argument('--output', '-o', default='results.txt', help='Output file name')
    
    args = parser.parse_args()
    
    task_folder = args.task_folder
    output_file = args.output
    
    if not os.path.exists(task_folder):
        print(f"Error: Task folder {task_folder} does not exist")
        sys.exit(1)
    
    all_results = []
    
    # Find all variant folders
    variant_folders = glob.glob(os.path.join(task_folder, "variant_*"))
    variant_folders.sort()  # Sort to ensure consistent order
    
    if not variant_folders:
        print(f"Warning: No variant folders found in {task_folder}")
        sys.exit(1)
    
    print(f"Found {len(variant_folders)} variant folders")
    
    # Process each variant
    for variant_path in variant_folders:
        variant_name = os.path.basename(variant_path)
        print(f"\n--- Processing {variant_name} ---")
        
        variant_results = process_variant(variant_path, variant_name)
        all_results.extend(variant_results)
    
    # Write results to file
    output_path = os.path.join(task_folder, output_file)
    with open(output_path, 'w') as f:
        f.write("PDB Cysteine Count Results\n")
        f.write("=" * 50 + "\n\n")
        
        for result in all_results:
            f.write(f"Variant: {result['variant']}\n")
            f.write(f"PDB ID: {result['pdb_id']}\n")
            f.write(f"Total Cysteine Count: {result['total_cysteine_count']}\n")
            f.write(f"Number of Chains: {len(result['chains'])}\n")
            
            for chain in result['chains']:
                f.write(f"  Chain {chain['chain_id']}: {chain['cysteine_count']} cysteines (length: {chain['sequence_length']})\n")
            
            f.write("\n" + "-" * 30 + "\n\n")
    
    print(f"\nResults written to: {output_path}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for result in all_results:
        print(f"{result['variant']} ({result['pdb_id']}): {result['total_cysteine_count']} cysteines")

if __name__ == "__main__":
    main()
```

</example-task-script>

<example-task-execution>

```{bash}[run_analysis.sh]
#!/bin/bash

# Master execution script for PDB Cysteine Count analysis
# Usage: ./run_analysis.sh <task_name> <pdb_id1> <pdb_id2> ...

# Check if sufficient arguments provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <task_name> <pdb_id1> <pdb_id2> ..."
    echo "Example: $0 E1_PDB_Cysteine_Count 1UBQ 1A3N 2LYZ 1HTM 1CRN"
    exit 1
fi

TASK_NAME=$1
shift
PDB_IDS=("$@")

echo "Starting PDB Cysteine Count Analysis"
echo "Task: $TASK_NAME"
echo "PDB IDs: ${PDB_IDS[*]}"
echo "----------------------------------------"

# Step 1: Data Acquisition
echo "Step 1: Acquiring data..."
if [ -f "acquire_data.sh" ]; then
    chmod +x acquire_data.sh
    ./acquire_data.sh "$TASK_NAME" "${PDB_IDS[@]}"
    
    if [ $? -eq 0 ]; then
        echo "✓ Data acquisition completed successfully"
    else
        echo "✗ Data acquisition failed"
        exit 1
    fi
else
    echo "✗ acquire_data.sh not found"
    exit 1
fi

echo ""

# Step 2: Analysis
echo "Step 2: Analyzing PDB files and counting cysteines..."
if [ -f "pdb_cysteine_counter.py" ]; then
    python3 pdb_cysteine_counter.py "$TASK_NAME" --output "cysteine_results.txt"
    
    if [ $? -eq 0 ]; then
        echo "✓ Analysis completed successfully"
    else
        echo "✗ Analysis failed"
        exit 1
    fi
else
    echo "✗ pdb_cysteine_counter.py not found"
    exit 1
fi

echo ""

# Step 3: Display results
echo "Step 3: Displaying results..."
if [ -f "${TASK_NAME}/cysteine_results.txt" ]; then
    echo "Results file created: ${TASK_NAME}/cysteine_results.txt"
    echo ""
    echo "Quick Summary:"
    grep -E "(Variant:|Total Cysteine Count:)" "${TASK_NAME}/cysteine_results.txt"
else
    echo "✗ Results file not found"
    exit 1
fi

echo ""
echo "Analysis pipeline completed successfully!"
echo "All files are stored in: $TASK_NAME/"
```

</example-task-execution>






