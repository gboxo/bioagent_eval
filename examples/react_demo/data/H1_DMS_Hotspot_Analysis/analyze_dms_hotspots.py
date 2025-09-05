#!/usr/bin/env python3
"""
Script to analyze Deep Mutational Scanning (DMS) data and identify hotspot positions.

This script processes DMS CSV files to identify positions where more than 50% of mutations
result in greater than 3-fold loss of fitness (fitness < 0.33), then returns the top 10
hotspots with lowest average fitness scores.
"""

import os
import sys
import argparse
import pandas as pd
from pathlib import Path


def load_dms_data(csv_file: str) -> pd.DataFrame:
    """
    Load DMS data from CSV file.
    """
    df = pd.read_csv(csv_file)
    print(f"Loaded DMS data: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    return df


def analyze_hotspots(df: pd.DataFrame) -> str:
    """
    Analyze DMS data to identify hotspot positions.
    
    Returns comma-separated string of top 10 hotspot positions.
    """
    
    # Check for different possible column formats
    # ProteinGym format - extract position from mutant string
    print("Detected ProteinGym format - extracting positions from mutant strings")
    df = df.copy()
    
    # Extract position from mutant strings (e.g., "A149D" -> 149)
    df['position'] = df['mutant'].str.extract(r'[A-Z](\d+)[A-Z]').astype(int)
    
    # Use DMS_score as fitness (may need normalization)
    df['fitness'] = df['DMS_score']
    
    # Normalize fitness scores to 0-1 range where lower is worse
    # Assuming higher DMS_score is better, so normalize and invert
    max_score = df['fitness'].max()
    min_score = df['fitness'].min()
    if max_score != min_score:
        df['fitness'] = (df['fitness'] - min_score) / (max_score - min_score)
    
    position_col = 'position'
    fitness_col = 'fitness'
    
    print(f"Normalized fitness range: {df['fitness'].min():.3f} to {df['fitness'].max():.3f}")
        
    
    
    print(f"Total mutations: {len(df)}")
    print(f"Unique positions: {df[position_col].nunique()}")
    print(f"Fitness range: {df[fitness_col].min():.3f} to {df[fitness_col].max():.3f}")
    
    # Group by position and calculate statistics
    position_stats = df.groupby(position_col).agg({
        fitness_col: ['mean', lambda x: (x < 0.33).mean(), 'count']
    }).reset_index()
    
    # Flatten column names
    position_stats.columns = ['position', 'mean_fitness', 'fraction_low_fitness', 'mutation_count']
    
    print(f"\nPosition statistics calculated for {len(position_stats)} positions")
    print(f"Positions with >50% low fitness mutations: {(position_stats['fraction_low_fitness'] > 0.5).sum()}")
    
    # Filter hotspots: positions where >50% of mutations have fitness < 0.33
    hotspots = position_stats[position_stats['fraction_low_fitness'] > 0.5].copy()
    
    if hotspots.empty:
        print("No hotspot positions found (no positions with >50% low fitness mutations)")
        print("<answer>NO_HOTSPOTS</answer>")
        return "NO_HOTSPOTS"
    
    print(f"Found {len(hotspots)} hotspot positions")
    
    # Sort by mean fitness (ascending) and take top 10
    hotspots_sorted = hotspots.sort_values('mean_fitness', ascending=True)
    top_10_hotspots = hotspots_sorted.head(10)
    
    print(f"\nTop 10 hotspots:")
    for idx, row in top_10_hotspots.iterrows():
        print(f"Position {int(row['position'])}: mean_fitness={row['mean_fitness']:.3f}, "
              f"low_fitness_fraction={row['fraction_low_fitness']:.3f}, "
              f"mutations={int(row['mutation_count'])}")
    
    # Extract positions as integers and join as comma-separated string
    hotspot_positions = top_10_hotspots['position'].astype(int).tolist()
    result_string = ','.join(map(str, hotspot_positions))
    
    print(f"\nResult: {result_string}")
    return result_string


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Analyze DMS data for hotspot positions')
    parser.add_argument('csv_file', help='Input CSV file with DMS data')
    
    args = parser.parse_args()
    
    
    print(f"Analyzing DMS data from: {args.csv_file}")
    
    # Load data
    df = load_dms_data(args.csv_file)
    
    # Analyze hotspots
    result = analyze_hotspots(df)
    
    if result != "NO_HOTSPOTS":
        print(f"\n<answer>{result}</answer>")
    return result


if __name__ == "__main__":
    main()