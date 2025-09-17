#!/usr/bin/env python3
"""
Script to analyze Deep Mutational Scanning (DMS) data for epistasis prediction.

This script processes DMS CSV files to fit an additive model on single mutations
and predict epistasis for multi-mutations, then calculates Spearman correlation
between observed and predicted fitness values.
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from pathlib import Path
from typing import Tuple, Dict


def load_dms_data(csv_file: str) -> pd.DataFrame:
    """
    Load DMS data from CSV file.
    """
    df = pd.read_csv(csv_file)
    print(f"Loaded DMS data: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    return df


def normalize_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DMS scores using Z-score standardization.
    """
    df = df.copy()
    scores = df['DMS_score']
    mean_score = scores.mean()
    std_score = scores.std()
    df['normalized_score'] = (scores - mean_score) / std_score
    return df

def separate_singles_multiples(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Separate dataframe into singles and multiples based on mutation format.
    Multi-mutants are identified by the presence of ':' delimiter.
    """
    singles = df[~df['mutant'].str.contains(':')].copy()
    multiples = df[df['mutant'].str.contains(':')].copy()
    return singles, multiples


def build_additive_model(singles_df: pd.DataFrame) -> Dict[str, float]:
    """
    Build additive model dictionary mapping single mutations to normalized scores.
    """
    model = {}
    for _, row in singles_df.iterrows():
        mutation = row['mutant']
        score = row['normalized_score']
        model[mutation] = score
    return model


def predict_multiples(multiples_df: pd.DataFrame, model: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Predict scores for multi-mutants using additive model.
    """
    predictions = []
    observed = []
    
    for _, row in multiples_df.iterrows():
        mutant = row['mutant']
        observed_score = row['normalized_score']
        
        # Parse multi-mutant string to get individual mutations
        individual_mutations = mutant.split(':')
        
        # Calculate predicted score as sum of individual effects
        predicted_score = 0.0
        for mutation in individual_mutations:
            if mutation in model:
                predicted_score += model[mutation]
            # If mutation not found, assume effect is 0 (as specified in instructions)
        
        predictions.append(predicted_score)
        observed.append(observed_score)
    
    return np.array(observed), np.array(predictions)


def calculate_spearman_correlation(observed: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate Spearman correlation between observed and predicted scores.
    """
    if len(observed) == 0 or len(predicted) == 0:
        return np.nan
    
    correlation, _ = spearmanr(observed, predicted)
    return correlation

def analyze_epistasis(df: pd.DataFrame) -> str:
    """
    Analyze DMS data for epistasis prediction using additive model.
    
    Returns correlation coefficient rounded to 2 decimal places as string.
    """
    # Normalize scores
    df = normalize_scores(df)
    
    # Separate singles and multiples
    singles, multiples = separate_singles_multiples(df)
    
    print(f"Total entries: {len(df)}")
    print(f"Single mutants: {len(singles)}")
    print(f"Multi-mutants: {len(multiples)}")
    
    # Check if we have both singles and multiples
    if len(singles) == 0:
        print("No single mutants found. Cannot build additive model.")
        return "nan"
    
    if len(multiples) == 0:
        print("No multi-mutants found. Cannot predict epistasis.")
        return "nan"
    
    # Build additive model
    model = build_additive_model(singles)
    print(f"Built model with {len(model)} single mutations")
    
    # Predict multi-mutants
    observed, predicted = predict_multiples(multiples, model)
    
    # Calculate Spearman correlation
    correlation = calculate_spearman_correlation(observed, predicted)
    
    print(f"Spearman correlation: {correlation:.3f}")
    
    if np.isnan(correlation):
        return "nan"
    else:
        return f"{correlation:.2f}"


def main():
    parser = argparse.ArgumentParser(description='Analyze DMS data for epistasis prediction')
    parser.add_argument('csv_file', help='Path to CSV file containing DMS data')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    try:
        # Load and analyze data
        df = load_dms_data(args.csv_file)
        result = analyze_epistasis(df)
        
        # Output result in required format
        print(f"<answer>{result}</answer>")
        
    except FileNotFoundError:
        print(f"Error: File not found: {args.csv_file}")
        print("<answer>ERROR</answer>")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing {args.csv_file}: {str(e)}")
        print("<answer>ERROR</answer>")
        sys.exit(1)


if __name__ == "__main__":
    main()