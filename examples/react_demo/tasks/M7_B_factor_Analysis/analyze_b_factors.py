#!/usr/bin/env python3
"""
Analyze C-alpha B-factors from a PDB file and output the average B-factor
of the residues that fall into the top 10% by B-factor, rounded to two
decimal places.

- No external dependencies (parses fixed-width PDB format directly)
- Prints a single float to stdout with two decimal places

Usage:
  python3 analyze_b_factors.py --pdb path/to/structure.pdb
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List


def parse_ca_b_factors(pdb_path: Path) -> List[float]:
    """Extract B-factors for C-alpha atoms from a PDB file.

    PDB fixed-width fields (relevant slices, 0-based):
      - record name:  0:6 == 'ATOM  ' or 'HETATM'
      - atom name:   12:16 (e.g., ' CA ')
      - tempFactor:  60:66 (B-factor)
    """
    b_factors: List[float] = []

    with pdb_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if not line.startswith("ATOM"):
                continue
            atom_name = line[12:16].strip()
            if atom_name != "CA":
                continue
            # Defensive parsing for short/irregular lines
            try:
                raw_b = line[60:66].strip()
                if raw_b:
                    b_factors.append(float(raw_b))
            except Exception:
                continue

    return b_factors


def compute_top_ten_percent_average(b_factors: List[float]) -> float:
    """Return the average B-factor among the top 10% of residues by B-factor.

    Steps:
      - Sort B-factors in descending order
      - Take the top k where k = int(n * 0.1) with a minimum of 1
      - Return the arithmetic mean of these top-k values
    """
    n = len(b_factors)
    if n == 0:
        return 0.0
    k = int(n * 0.1)
    if k < 1:
        k = 1
    top_k = sorted(b_factors, reverse=True)[: k + 1]
    return sum(top_k) / float(len(top_k))


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze C-alpha B-factors")
    parser.add_argument("--pdb", type=Path, required=True, help="Path to PDB file")
    args = parser.parse_args()

    if not args.pdb.exists():
        raise FileNotFoundError(f"PDB file not found: {args.pdb}")

    b_factors = parse_ca_b_factors(args.pdb)
    result = compute_top_ten_percent_average(b_factors)
    result = round(result, 2)
    print(result)


if __name__ == "__main__":
    main()
