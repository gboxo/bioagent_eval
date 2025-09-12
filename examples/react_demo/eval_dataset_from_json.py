#!/usr/bin/env python3
"""
Load ProteinAnalysisDataset from JSON file created by export_protein_dataset_json.py.

- Reconstructs ProteinDataset object from flattened JSON samples
- Does NOT require Inspect AI to be installed (adds repo src/ to sys.path)
- Provides interface to access samples, metadata, and task information

Usage:
  python examples/react_demo/eval_dataset_from_json.py \
    --input examples/react_demo/protein_dataset_flat.json \
    [--filter-difficulty E M H] [--filter-tasks task1 task2] [--max-samples N]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

# Ensure local repo src/ is importable so examples can import inspect_ai
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from inspect_ai.dataset import Sample

@dataclass
class ProteinSample:
    """A protein analysis sample with associated metadata."""

    input: str
    target: str
    metadata: Dict[str, Any]
    sandbox: Union[str, List[str], None]
    id: Optional[str] = None
    choices: Optional[List[str]] = None
    files: Optional[List[str]] = None
    setup: Optional[str] = None

    @property
    def task_name(self) -> str:
        """Extract task name from metadata."""
        return self.metadata.get("task_name", "unknown")

    @property
    def variant(self) -> str:
        """Extract variant from metadata."""
        return self.metadata.get("variant", "unknown")

    @property
    def difficulty(self) -> str:
        """Extract difficulty level from metadata."""
        return self.metadata.get("difficulty", "unknown")

    def to_inspect_sample(self) -> Sample:
        """Convert to Inspect AI Sample object."""
        return Sample(
            input=self.input,
            target=self.target,
            metadata=self.metadata,
            id=self.id,
            choices=self.choices,
            files=self.files,
            setup=self.setup,
        )


class ProteinDataset:
    """
    Dataset class for loading protein analysis evaluation tasks from JSON.

    This is the inverse of export_protein_dataset_json.py - it loads the
    flattened JSON samples back into a structured dataset object.
    """

    def __init__(
        self,
        json_file: Union[str, Path],
        filter_difficulties: Optional[List[str]] = None,
        filter_tasks: Optional[List[str]] = None,
        filter_variants: Optional[List[str]] = None,
        max_samples: Optional[int] = None,
    ):
        """
        Initialize dataset from JSON file.

        Args:
            json_file: Path to JSON file created by export_protein_dataset_json.py
            filter_difficulties: List of difficulties to include (e.g., ['E', 'M'])
            filter_tasks: List of task names to include
            filter_variants: List of variants to include (e.g., ['variant_1'])
            max_samples: Maximum number of samples to load
        """
        self.json_file = Path(json_file)
        self.filter_difficulties = filter_difficulties
        self.filter_tasks = filter_tasks
        self.filter_variants = filter_variants
        self.max_samples = max_samples

        # Load and parse JSON data
        self._load_data()

    def _load_data(self) -> None:
        """Load JSON data and create ProteinSample objects."""
        if not self.json_file.exists():
            raise FileNotFoundError(f"JSON file not found: {self.json_file}")

        with open(self.json_file, "r", encoding="utf-8") as f:
            raw_samples = json.load(f)

        # Convert JSON records to ProteinSample objects
        samples = []
        for record in raw_samples:
            sample = ProteinSample(
                input=record["input"],
                target=record["target"],
                metadata=record.get("metadata", {}),
                sandbox=record.get("sandbox"),
                id=record.get("id"),
                choices=record.get("choices"),
                files=record.get("files"),
                setup=record.get("setup"),
            )

            # Apply filters
            if self._should_include_sample(sample):
                samples.append(sample)

        # Apply max_samples limit
        if self.max_samples is not None:
            samples = samples[:self.max_samples]

        self.samples = samples

    def _should_include_sample(self, sample: ProteinSample) -> bool:
        """Check if sample should be included based on filters."""
        # Filter by difficulty
        if (self.filter_difficulties is not None and
            sample.difficulty not in self.filter_difficulties):
            return False

        # Filter by task name
        if (self.filter_tasks is not None and
            sample.task_name not in self.filter_tasks):
            return False

        # Filter by variant
        if (self.filter_variants is not None and
            sample.variant not in self.filter_variants):
            return False

        return True

    def get_samples(self) -> List[ProteinSample]:
        """Get all loaded samples."""
        return self.samples

    def get_inspect_samples(self) -> List[Sample]:
        """Get samples as Inspect AI Sample objects."""
        return [sample.to_inspect_sample() for sample in self.samples]

    def get_tasks(self) -> List[str]:
        """Get unique task names in the dataset."""
        return sorted(set(sample.task_name for sample in self.samples))

    def get_difficulties(self) -> List[str]:
        """Get unique difficulty levels in the dataset."""
        return sorted(set(sample.difficulty for sample in self.samples))

    def get_variants(self) -> List[str]:
        """Get unique variants in the dataset."""
        return sorted(set(sample.variant for sample in self.samples))

    def filter_samples(
        self,
        difficulties: Optional[List[str]] = None,
        tasks: Optional[List[str]] = None,
        variants: Optional[List[str]] = None,
    ) -> List[ProteinSample]:
        """Filter samples by criteria and return matching samples."""
        filtered = []
        for sample in self.samples:
            # Check difficulty filter
            if difficulties and sample.difficulty not in difficulties:
                continue
            # Check task filter
            if tasks and sample.task_name not in tasks:
                continue
            # Check variant filter
            if variants and sample.variant not in variants:
                continue
            filtered.append(sample)

        return filtered

    def get_sample_by_id(self, sample_id: str) -> Optional[ProteinSample]:
        """Get a specific sample by its ID."""
        for sample in self.samples:
            if sample.id == sample_id:
                return sample
        return None

    def get_samples_by_task(self, task_name: str) -> List[ProteinSample]:
        """Get all samples for a specific task."""
        return [s for s in self.samples if s.task_name == task_name]

    def get_samples_by_difficulty(self, difficulty: str) -> List[ProteinSample]:
        """Get all samples for a specific difficulty level."""
        return [s for s in self.samples if s.difficulty == difficulty]

    def summary(self) -> Dict[str, Any]:
        """Get dataset summary statistics."""
        return {
            "total_samples": len(self.samples),
            "tasks": self.get_tasks(),
            "difficulties": self.get_difficulties(),
            "variants": self.get_variants(),
            "samples_by_difficulty": {
                d: len(self.get_samples_by_difficulty(d))
                for d in self.get_difficulties()
            },
            "samples_by_task": {
                t: len(self.get_samples_by_task(t))
                for t in self.get_tasks()
            },
        }

    def __len__(self) -> int:
        """Return number of samples in the dataset."""
        return len(self.samples)

    def __iter__(self):
        """Iterate over samples."""
        return iter(self.samples)

    def __getitem__(self, index: int) -> ProteinSample:
        """Get sample by index."""
        return self.samples[index]


def main() -> None:
    """Command-line interface for loading and inspecting protein datasets from JSON."""
    parser = argparse.ArgumentParser(description="Load protein dataset from JSON")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input JSON file path (created by export_protein_dataset_json.py)",
    )
    parser.add_argument(
        "--filter-difficulties",
        nargs="*",
        choices=["E", "M", "H"],
        help="Filter by difficulties",
    )
    parser.add_argument(
        "--filter-tasks",
        nargs="*",
        help="Filter by task names",
    )
    parser.add_argument(
        "--filter-variants",
        nargs="*",
        help="Filter by variants (e.g., variant_1 variant_2)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        help="Maximum number of samples to load",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print dataset summary",
    )
    parser.add_argument(
        "--list-samples",
        action="store_true",
        help="List all sample IDs",
    )

    args = parser.parse_args()

    # Load dataset
    dataset = ProteinDataset(
        json_file=args.input,
        filter_difficulties=args.filter_difficulties,
        filter_tasks=args.filter_tasks,
        filter_variants=args.filter_variants,
        max_samples=args.max_samples,
    )

    print(f"Loaded {len(dataset)} samples from {args.input}")

    if args.summary:
        print("\nDataset Summary:")
        print("================")
        summary = dataset.summary()
        for key, value in summary.items():
            print(f"{key}: {value}")

    if args.list_samples:
        print("\nSample IDs:")
        print("===========")
        for i, sample in enumerate(dataset.get_samples()):
            print(f"{i+1:3d}. {sample.id} ({sample.task_name}, {sample.difficulty}, {sample.variant})")


if __name__ == "__main__":
    main()
