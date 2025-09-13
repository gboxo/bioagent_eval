#!/usr/bin/env python3
"""
Export ProteinAnalysisDataset to a single JSON file of Samples.

- Flattens prompts, results, and per-sample metadata into one JSON array
- Does NOT require Inspect AI to be installed (adds repo src/ to sys.path)
- Sets sandbox to ["docker", ".compose.yaml"] so Inspect auto-generates a compose file
  (note: this default compose uses a minimal image without internet; for the
   full bioinformatics toolchain, run your Task with compose="./compose_gboxo.yaml")

Usage:
  uv run python examples/bioagent_eval/export_protein_dataset_json.py \
    --output examples/bioagent_eval/protein_dataset_flat.json \
    [--difficulties E M H] [--variants variant_1 variant_2 ...] [--max-samples N]
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from protein_dataset import export_samples_to_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Export protein dataset to JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("examples/bioagent_eval/protein_dataset_flat.json"),
        help="Output JSON file path",
    )
    parser.add_argument(
        "--difficulties",
        nargs="*",
        choices=["E", "M", "H"],
        default=["E", "M", "H"],
        help="Difficulties to include",
    )
    parser.add_argument(
        "--variants",
        nargs="*",
        default=[f"variant_{i}" for i in range(1, 6)],
        help="Variants to include (e.g., variant_1 variant_2)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Maximum number of samples to export",
    )

    args = parser.parse_args()

    export_samples_to_json(
        args.output,
        difficulties_filter=list(args.difficulties) if args.difficulties else None,
        variants_filter=list(args.variants) if args.variants else None,
        tasks_filter=None,
        max_samples=args.max_samples,
    )


if __name__ == "__main__":
    main()
