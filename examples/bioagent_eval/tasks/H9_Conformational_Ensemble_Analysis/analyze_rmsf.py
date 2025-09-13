#!/usr/bin/env python3

import sys
import os
import numpy as np
from Bio import PDB
from Bio.PDB import Superimposer
import argparse

def calculate_rmsf_from_pdb(pdb_file):
    """
    Calculate RMSF for each residue from an NMR ensemble PDB file.
    
    Args:
        pdb_file (str): Path to the PDB file containing multiple models
        
    Returns:
        int: Starting residue number of the most flexible contiguous region (≥5 residues)
    """
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure('protein', pdb_file)
    
    # Get all models
    models = list(structure.get_models())
    num_models = len(models)
    
    if num_models < 2:
        raise ValueError(f"Need at least 2 models for RMSF calculation, found {num_models}")
    
    print(f"Processing {num_models} models from {pdb_file}")
    
    # Get the first model as reference
    ref_model = models[0]
    
    # Extract C-alpha atoms and residue numbers from the reference model
    ref_ca_atoms = []
    residue_numbers = []
    
    for chain in ref_model:
        for residue in chain:
            if 'CA' in residue:
                ref_ca_atoms.append(residue['CA'])
                residue_numbers.append(residue.id[1])
    
    num_residues = len(ref_ca_atoms)
    print(f"Found {num_residues} residues with C-alpha atoms")
    
    if num_residues == 0:
        raise ValueError("No C-alpha atoms found in the reference model")
    
    # Initialize arrays to store coordinates for all models
    all_coords = np.zeros((num_models, num_residues, 3))
    
    # Extract coordinates from all models after superposition
    superimposer = Superimposer()
    
    for model_idx, model in enumerate(models):
        # Get C-alpha atoms for this model
        model_ca_atoms = []
        
        for chain in model:
            for residue in chain:
                if 'CA' in residue:
                    model_ca_atoms.append(residue['CA'])
        
        if len(model_ca_atoms) != num_residues:
            print(f"Warning: Model {model_idx + 1} has {len(model_ca_atoms)} C-alpha atoms, expected {num_residues}")
            continue
        
        if model_idx == 0:
            # Reference model - no superposition needed
            for i, atom in enumerate(model_ca_atoms):
                all_coords[model_idx, i] = atom.get_coord()
        else:
            # Superimpose this model onto the reference
            superimposer.set_atoms(ref_ca_atoms, model_ca_atoms)
            superimposer.apply(model_ca_atoms)
            
            # Store superposed coordinates
            for i, atom in enumerate(model_ca_atoms):
                all_coords[model_idx, i] = atom.get_coord()
    
    # Calculate RMSF for each residue
    rmsf_values = np.zeros(num_residues)
    
    for residue_idx in range(num_residues):
        # Get coordinates for this residue across all models
        residue_coords = all_coords[:, residue_idx, :]
        
        # Calculate mean position
        mean_pos = np.mean(residue_coords, axis=0)
        
        # Calculate RMSF (root mean square fluctuation)
        fluctuations = np.linalg.norm(residue_coords - mean_pos, axis=1)
        rmsf_values[residue_idx] = np.sqrt(np.mean(fluctuations**2))
    
    print(f"RMSF values calculated for {num_residues} residues")
    print(f"RMSF range: {np.min(rmsf_values):.3f} - {np.max(rmsf_values):.3f} Å")
    
    # Find the most flexible contiguous region of 5 or more residues
    window_size = 5
    max_avg_rmsf = -1
    tied_start_indices = []
    
    # First pass: find the maximum average RMSF
    for i in range(num_residues - window_size + 1):
        window_rmsf = rmsf_values[i:i + window_size]
        avg_rmsf = np.mean(window_rmsf)
        
        if avg_rmsf > max_avg_rmsf:
            max_avg_rmsf = avg_rmsf
    
    # Second pass: collect all indices that achieve the maximum
    for i in range(num_residues - window_size + 1):
        window_rmsf = rmsf_values[i:i + window_size]
        avg_rmsf = np.mean(window_rmsf)
        
        if abs(avg_rmsf - max_avg_rmsf) < 1e-10:  # Handle floating point precision
            tied_start_indices.append(i)
    
    if not tied_start_indices:
        raise ValueError("Could not find a contiguous region of 5 residues")
    
    # Convert from array indices to residue numbers
    tied_residue_numbers = [residue_numbers[idx] for idx in tied_start_indices]
    tied_residue_numbers.sort()  # Sort in ascending order
    
    if len(tied_residue_numbers) == 1:
        result = str(tied_residue_numbers[0])
        print(f"Most flexible region starts at residue {tied_residue_numbers[0]}")
    else:
        result = ','.join(map(str, tied_residue_numbers))
        print(f"Multiple equally flexible regions found starting at residues: {tied_residue_numbers}")
    
    print(f"Average RMSF in flexible region(s): {max_avg_rmsf:.3f} Å")
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Calculate RMSF from NMR ensemble PDB file')
    parser.add_argument('pdb_file', help='Path to PDB file')
    parser.add_argument('--output', '-o', help='Output file for results')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdb_file):
        print(f"Error: PDB file {args.pdb_file} not found")
        sys.exit(1)
    
    try:
        result = calculate_rmsf_from_pdb(args.pdb_file)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(f"{result}\n")
        else:
            print(f"<answer>{result}</answer>")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()