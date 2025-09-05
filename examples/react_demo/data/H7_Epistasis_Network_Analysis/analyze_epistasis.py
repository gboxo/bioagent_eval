#!/usr/bin/env python3
"""
Analyze epistatic interactions from combinatorial mutagenesis data.
"""

import pandas as pd
import sys
import os
from typing import Dict, Tuple


def load_data(csv_file: str) -> pd.DataFrame:
    """Load the CSV file containing mutant data."""
    return pd.read_csv(csv_file)


def extract_single_mutants(df: pd.DataFrame) -> Dict[str, float]:
    """Extract single mutants and their fitness scores."""
    single_mutants = {}
    
    for _, row in df.iterrows():
        mutant = row['mutant']
        fitness = row['DMS_score']
        
        # Count number of mutations (separated by colons)
        mutations = mutant.split(':')
        
        # Only consider single mutants
        if len(mutations) == 1:
            single_mutants[mutant] = fitness
    
    return single_mutants


def extract_double_mutants(df: pd.DataFrame) -> pd.DataFrame:
    """Extract double mutants and their observed fitness."""
    double_mutants = []
    
    for _, row in df.iterrows():
        mutant = row['mutant']
        fitness = row['DMS_score']
        
        # Count number of mutations
        mutations = mutant.split(':')
        
        # Only consider double mutants
        if len(mutations) == 2:
            double_mutants.append({
                'mutant': mutant,
                'fitness': fitness,
                'mutation_1': mutations[0],
                'mutation_2': mutations[1]
            })
    
    return pd.DataFrame(double_mutants)


def calculate_epistasis(single_mutants: Dict[str, float], double_mutants: pd.DataFrame) -> Tuple[str, float]:
    """Calculate epistatic interactions and find the double mutant with highest epistasis."""
    max_epistasis = -1
    max_epistasis_mutant = ""
    
    for _, row in double_mutants.iterrows():
        mutant_name = row['mutant']
        observed_fitness = row['fitness']
        mutation_1 = row['mutation_1']
        mutation_2 = row['mutation_2']
        
        # Check if both single mutants exist in our dictionary
        if mutation_1 in single_mutants and mutation_2 in single_mutants:
            fitness_1 = single_mutants[mutation_1]
            fitness_2 = single_mutants[mutation_2]
            
            # Calculate expected fitness using multiplicative model
            expected_fitness = fitness_1 * fitness_2
            
            # Calculate epistasis as absolute difference
            epistasis = abs(observed_fitness - expected_fitness)
            
            # Update max if this is higher
            if epistasis > max_epistasis:
                max_epistasis = epistasis
                max_epistasis_mutant = mutant_name
    
    return max_epistasis_mutant, max_epistasis


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_epistasis.py <csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found")
        sys.exit(1)
    
    # Load data
    df = load_data(csv_file)
    
    # Extract single mutants
    single_mutants = extract_single_mutants(df)
    
    # Extract double mutants
    double_mutants = extract_double_mutants(df)
    
    # Calculate epistasis
    max_epistasis_mutant, max_epistasis_value = calculate_epistasis(single_mutants, double_mutants)
    
    if max_epistasis_mutant:
        # Convert colon-separated format to dash-separated format
        result = max_epistasis_mutant.replace(':', '-')
        print(result)
    else:
        print("No epistatic interactions found")


if __name__ == "__main__":
    main()