#!/usr/bin/env python3
"""
Export ProteinAnalysisDataset to a single JSON file of Samples.

- Flattens prompts, results, and per-sample metadata into one JSON array
- Does NOT require Inspect AI to be installed (adds repo src/ to sys.path)
- Sets sandbox to ["docker", ".compose.yaml"] so Inspect auto-generates a compose file
  (note: this default compose uses a minimal image without internet; for the
   full bioinformatics toolchain, run your Task with compose="./compose_gboxo.yaml")

Usage:
  uv run python examples/react_demo/export_protein_dataset_json.py \
    --output examples/react_demo/protein_dataset_flat.json \
    [--difficulties E M H] [--variants variant_1 variant_2 ...] [--max-samples N]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure local repo src/ is importable so examples can import inspect_ai
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from protein_dataset import ProteinAnalysisDataset


def sample_to_record(sample) -> Dict[str, Any]:
    """Convert an Inspect Sample to a JSON-serializable record for json_dataset()."""
    # Ensure input is a string (ProteinAnalysisDataset generates str prompts)
    if not isinstance(sample.input, str):
        raise ValueError("Expected string input in sample")

    # json_dataset expects sandbox as str or [type, config] list, not dict
    sandbox: List[str] | str | None
    sandbox = ["docker", ".compose.yaml"]

    record: Dict[str, Any] = {
        "input": sample.input,
        "target": sample.target,
        "metadata": sample.metadata or {},
        "sandbox": sandbox,
    }

    # Preserve id if present
    if getattr(sample, "id", None) is not None:
        record["id"] = sample.id

    # Include choices/files/setup if present (none by default for this dataset)
    if getattr(sample, "choices", None):
        record["choices"] = sample.choices
    if getattr(sample, "files", None):
        record["files"] = sample.files
    if getattr(sample, "setup", None):
        record["setup"] = sample.setup

    # Add helpful hint to metadata about recommended compose
    md = record["metadata"]
    md.setdefault("compose_hint", "Use compose_gboxo.yaml for full bioinformatics stack")

    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Export protein dataset to JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("examples/react_demo/protein_dataset_flat.json"),
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
        "--tasks",
        nargs="*",
        default=None,
        help="Optional list of task names to include",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Optional maximum number of samples",
    )

    args = parser.parse_args()

    # Configure dataset with requested filters
    tasks_filter = None
    if args.tasks:
        tasks_filter = list(args.tasks)

    dataset = ProteinAnalysisDataset(
        tasks_filter=tasks_filter,
        variants_filter=list(args.variants),
        difficulties_filter=list(args.difficulties),
    )

    samples = dataset.create_samples()
    if args.max_samples is not None:
        samples = samples[: args.max_samples]

    # Convert to records
    records = [sample_to_record(s) for s in samples]

    # Ensure parent exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON array
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(records)} samples to {args.output}")


if __name__ == "__main__":
    main()
