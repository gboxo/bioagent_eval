#!/usr/bin/env python3
"""
Protein Analysis Dataset for Inspect AI
Integrates task prompts, expected results, and Docker configurations.

This module also provides utilities to:
- Convert Samples to/from JSON records
- Load samples either from source files or a flattened JSON export
- Export samples to a JSON file



 1 │# Export JSON
 2 │uv run python examples/react_demo/export_protein_dataset_json.py --output examples/react_demo/protein_dataset_flat.json
 3 │
 4 │# Evaluate using JSON via unified entrypoint
 5 │uv run inspect eval examples/react_demo/protein_eval.py::protein_analysis_eval --json_file examples/react_demo/protein_dataset_flat.json

"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, Literal
from dataclasses import dataclass

from inspect_ai.dataset import Sample


@dataclass
class TaskMetadata:
    """Metadata for a protein analysis task."""

    task_name: str
    variant: str
    difficulty: str  # E/M/H
    compose_file: str
    dependencies: Dict[str, Any]


class ProteinAnalysisDataset:
    """
    Dataset class for protein analysis evaluation tasks.

    Integrates:
    - task_prompts.json: Template prompts with variables
    - task_results.json: Expected answers for each task/variant
    - compose_files/: Docker configurations per task
    - task_dependencies.json: Dependency information
    """

    def __init__(
        self,
        data_dir: Optional[Union[str, Path]] = None,
        tasks_filter: Optional[Union[List[str], Callable[[str], bool]]] = None,
        variants_filter: Optional[List[str]] = None,
        difficulties_filter: Optional[List[str]] = None,
    ):
        """
        Initialize the protein analysis dataset.

        Args:
            data_dir: Directory containing data files (defaults to current directory)
            tasks_filter: List of task names or callable to filter tasks
            variants_filter: List of variant names to include (e.g., ['variant_1', 'variant_2'])
            difficulties_filter: List of difficulties to include (e.g., ['E', 'M'])
        """
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent
        self.tasks_filter = tasks_filter
        self.variants_filter = variants_filter or [
            "variant_1",
            "variant_2",
            "variant_3",
            "variant_4",
            "variant_5",
        ]
        self.difficulties_filter = difficulties_filter or ["E", "M", "H"]

        # Load data files
        self._load_data()

    def _load_data(self) -> None:
        """Load all required data files."""
        # Load task prompts
        prompts_file = self.data_dir / "task_prompts.json"
        if not prompts_file.exists():
            raise FileNotFoundError(f"Task prompts file not found: {prompts_file}")

        with open(prompts_file, "r", encoding="utf-8") as f:
            self.prompts = json.load(f)

        # Load expected results
        results_file = self.data_dir / "task_results.json"
        if not results_file.exists():
            raise FileNotFoundError(f"Task results file not found: {results_file}")

        with open(results_file, "r", encoding="utf-8") as f:
            self.results = json.load(f)

        # Load task dependencies (optional)
        dependencies_file = self.data_dir / "task_dependencies.json"
        if dependencies_file.exists():
            with open(dependencies_file, "r", encoding="utf-8") as f:
                self.dependencies = json.load(f)
        else:
            self.dependencies = {}


    def _should_include_task(self, task_name: str) -> bool:
        """Check if task should be included based on filters."""
        # Check difficulty filter
        difficulty = task_name[0]  # First character (E/M/H)
        if difficulty not in self.difficulties_filter:
            return False

        # Check task filter
        if self.tasks_filter is not None:
            if callable(self.tasks_filter):
                return self.tasks_filter(task_name)
            elif isinstance(self.tasks_filter, list):
                return task_name in self.tasks_filter

        return True

    def _generate_prompt(self, template: str, variables: Dict[str, Any]) -> str:
        """Generate a prompt from template and variables."""
        try:
            return template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    def _get_expected_result(self, task_name: str, variant: str) -> str:
        """Get expected result for a task/variant combination."""
        if task_name not in self.results:
            raise ValueError(f"No results found for task: {task_name}")

        # Find the variant result
        variant_num = int(variant.split("_")[1])  # Extract number from 'variant_N'

        for result_entry in self.results[task_name]:
            if result_entry.get("variant") == variant_num:
                result_value = result_entry.get("result", "")
                # Wrap result in answer tags if not already wrapped
                if not result_value.startswith("<answer>"):
                    # result_value = f"<answer>{result_value}</answer>"
                    result_value = result_value
                return result_value

        raise ValueError(f"No result found for {task_name} {variant}")

    def create_samples(self) -> List[Sample]:
        """
        Generate Sample objects for all filtered tasks and variants.

        Returns:
            List of Sample objects ready for evaluation
        """
        samples = []

        for task_name, task_config in self.prompts.items():
            # Apply task filter
            if not self._should_include_task(task_name):
                continue

            if "template" not in task_config or "template_entries" not in task_config:
                print(
                    f"Warning: Skipping {task_name} - missing template or template_entries"
                )
                continue

            template = task_config["template"]

            for variant_name, variables in task_config["template_entries"].items():
                # Apply variant filter
                if variant_name not in self.variants_filter:
                    continue

                try:
                    # Generate prompt from template
                    prompt = self._generate_prompt(template, variables)

                    # Get expected result
                    target = self._get_expected_result(task_name, variant_name)

                    # Get compose file path
                    compose_file = "/Users/gerard/inspect_ai/examples/react_demo/compose_gboxo.yaml"

                    # Create sample
                    sample = Sample(
                        input=prompt,
                        target=target,
                        metadata={
                            "task_name": task_name,
                            "variant": variant_name,
                            "difficulty": task_name[0],
                            "compose_file": compose_file,
                            "dependencies": self.dependencies.get(task_name, {}),
                            "template_variables": variables,
                        },
                        # Ensure each task uses its own Docker Compose file
                        sandbox=("docker", compose_file),
                    )

                    samples.append(sample)

                except Exception as e:
                    print(f"Error creating sample for {task_name} {variant_name}: {e}")
                    continue

        print(f"Created {len(samples)} samples from {len(self.prompts)} tasks")
        return samples

    def get_task_metadata(self, task_name: str) -> Dict[str, Any]:
        """Get metadata for a specific task."""
        return {
            "task_name": task_name,
            "difficulty": task_name[0],
            "compose_file": "/Users/gerard/inspect_ai/examples/react_demo/compose_gboxo.yaml",
            "dependencies": self.dependencies.get(task_name, {}),
            "prompt_template": self.prompts.get(task_name, {}).get("template", ""),
            "variants_count": len(
                self.prompts.get(task_name, {}).get("template_entries", {})
            ),
        }

    def validate_data_integrity(self) -> Dict[str, List[str]]:
        """
        Validate data integrity across all files.

        Returns:
            Dictionary with any validation errors found
        """
        errors = {
            "missing_results": [],
            "template_errors": [],
            "missing_variants": [],
        }

        for task_name, task_config in self.prompts.items():
            # Check if results exist for this task
            if task_name not in self.results:
                errors["missing_results"].append(task_name)
                continue


            # Check template structure
            if "template" not in task_config:
                errors["template_errors"].append(f"{task_name}: missing template")
            if "template_entries" not in task_config:
                errors["template_errors"].append(
                    f"{task_name}: missing template_entries"
                )
                continue

            # Check if all variants have results
            template_variants = set(task_config["template_entries"].keys())
            result_variants = set()

            for result_entry in self.results[task_name]:
                variant_num = result_entry.get("variant")
                if variant_num:
                    result_variants.add(f"variant_{variant_num}")

            missing_variants = template_variants - result_variants
            if missing_variants:
                errors["missing_variants"].append(
                    f"{task_name}: {list(missing_variants)}"
                )

        return errors

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics about the dataset."""
        total_tasks = len(
            [t for t in self.prompts.keys() if self._should_include_task(t)]
        )

        difficulty_counts = {"E": 0, "M": 0, "H": 0}
        for task_name in self.prompts.keys():
            if self._should_include_task(task_name):
                difficulty_counts[task_name[0]] += 1

        samples = self.create_samples()

        return {
            "total_tasks": total_tasks,
            "total_samples": len(samples),
            "difficulty_breakdown": difficulty_counts,
            "variants_per_task": len(self.variants_filter),
            "filtered_difficulties": self.difficulties_filter,
            "data_files_loaded": {
                "prompts": len(self.prompts),
                "results": len(self.results),
                "dependencies": len(self.dependencies),
            },
        }
    def sample_to_record(self, sample: Sample) -> Dict[str, Any]:
        """Convert an Inspect Sample to a JSON-serializable record.

        Ensures compatibility with flattened JSON datasets consumed by external tools.
        """
        if not isinstance(sample.input, str):
            raise TypeError("Expected string input in sample")

        # Prefer generic sandbox hint for JSON exports; task-level compose will override.
        sandbox_value: Union[List[str], str, None] = ["docker", ".compose.yaml"]

        record: Dict[str, Any] = {
            "input": sample.input,
            "target": sample.target,
            "metadata": sample.metadata or {},
            "sandbox": sandbox_value,
        }

        # Optional fields
        if getattr(sample, "id", None) is not None:
            record["id"] = sample.id
        if getattr(sample, "choices", None):
            record["choices"] = sample.choices
        if getattr(sample, "files", None):
            record["files"] = sample.files
        if getattr(sample, "setup", None):
            record["setup"] = sample.setup

        # Add helpful hint to metadata about recommended compose
        record["metadata"].setdefault(
            "compose_hint",
            "Use compose_gboxo.yaml for full bioinformatics stack",
        )

        return record

    def record_to_sample(self, record: Dict[str, Any]) -> Sample:
        """Convert a JSON record back to an Inspect Sample."""
        input_value = record.get("input")
        target_value = record.get("target")
        if not isinstance(input_value, str) or target_value is None:
            raise ValueError("Record must contain 'input' (str) and 'target'")

        metadata_value: Dict[str, Any] = record.get("metadata", {})

        # Normalize sandbox: allow str, list, or tuple; keep as-is if provided
        sandbox_value: Union[str, tuple, None]
        raw_sandbox = record.get("sandbox")
        if isinstance(raw_sandbox, list):
            sandbox_value = tuple(raw_sandbox)
        elif isinstance(raw_sandbox, tuple) or isinstance(raw_sandbox, str):
            sandbox_value = raw_sandbox  # type: ignore[assignment]
        else:
            sandbox_value = None

        return Sample(
            input=input_value,
            target=target_value,
            metadata=metadata_value,
            id=record.get("id"),
            choices=record.get("choices"),
            files=record.get("files"),
            setup=record.get("setup"),
            sandbox=sandbox_value,  # type: ignore[arg-type]
        )


    def load_samples(
        self,
        source: Literal["files", "json"],
        *,
        json_path: Optional[Path] = None,
        tasks_filter: Optional[Union[List[str], Callable[[str], bool]]] = None,
        variants_filter: Optional[List[str]] = None,
        difficulties_filter: Optional[List[str]] = None,
        max_samples: Optional[int] = None,
    ) -> List[Sample]:
        """Load samples from source files or from a JSON export.

        Args:
            source: "files" to build from prompts/results, "json" to load from file
            json_path: Path to JSON file when source="json"
            tasks_filter: Filter tasks by names or predicate (applied post-load for JSON)
            variants_filter: Filter variants (e.g., ["variant_1"]) (post-load for JSON)
            difficulties_filter: Filter difficulties (e.g., ["E", "M"]) (post-load for JSON)
            max_samples: Optional cap on number of samples returned
        """

        if source == "files":
            dataset = ProteinAnalysisDataset(
                tasks_filter=tasks_filter,
                variants_filter=variants_filter,
                difficulties_filter=difficulties_filter,
            )
            samples = dataset.create_samples()
            return samples[:max_samples] if max_samples is not None else samples

        if source == "json":
            if json_path is None:
                raise ValueError("json_path is required when source='json'")
            with open(json_path, "r", encoding="utf-8") as f:
                records: List[Dict[str, Any]] = json.load(f)
            samples = [self.record_to_sample(record) for record in records]

            # Apply filters post-load
            if tasks_filter is not None:
                if callable(tasks_filter):
                    samples = [
                        s for s in samples if tasks_filter(s.metadata.get("task_name", ""))
                    ]
                else:
                    allowed_tasks = set(tasks_filter)
                    samples = [
                        s
                        for s in samples
                        if s.metadata.get("task_name", "") in allowed_tasks
                    ]
            if variants_filter is not None:
                allowed_variants = set(variants_filter)
                samples = [
                    s for s in samples if s.metadata.get("variant", "") in allowed_variants
                ]
            if difficulties_filter is not None:
                allowed_difficulties = set(difficulties_filter)
                samples = [
                    s
                    for s in samples
                    if s.metadata.get("difficulty", "") in allowed_difficulties
                ]

            return samples[:max_samples] if max_samples is not None else samples

        raise ValueError("source must be either 'files' or 'json'")


def export_samples_to_json(
    output_path: Path,
    *,
    tasks_filter: Optional[Union[List[str], Callable[[str], bool]]] = None,
    variants_filter: Optional[List[str]] = None,
    difficulties_filter: Optional[List[str]] = None,
    max_samples: Optional[int] = None,
) -> None:
    """Export samples built from source files to a flattened JSON file.

    Args:
        output_path: Destination JSON file path
        tasks_filter: Optional task filter
        variants_filter: Optional variant filter
        difficulties_filter: Optional difficulty filter
        max_samples: Optional cap on number of samples
    """
    dataset = ProteinAnalysisDataset(
        tasks_filter=tasks_filter,
        variants_filter=variants_filter,
        difficulties_filter=difficulties_filter,
    )
    samples = dataset.create_samples()
    samples = samples[:max_samples] if max_samples is not None else samples
    records = [dataset.sample_to_record(s) for s in samples]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
# Convenience functions for common use cases
def create_easy_tasks_dataset(
    data_dir: Optional[Path] = None,
) -> ProteinAnalysisDataset:
    """Create dataset with only Easy (E) tasks."""
    return ProteinAnalysisDataset(data_dir=data_dir, difficulties_filter=["E"])


def create_medium_tasks_dataset(
    data_dir: Optional[Path] = None,
) -> ProteinAnalysisDataset:
    """Create dataset with only Medium (M) tasks."""
    return ProteinAnalysisDataset(data_dir=data_dir, difficulties_filter=["M"])


def create_hard_tasks_dataset(
    data_dir: Optional[Path] = None,
) -> ProteinAnalysisDataset:
    """Create dataset with only Hard (H) tasks."""
    return ProteinAnalysisDataset(data_dir=data_dir, difficulties_filter=["H"])


def create_single_task_dataset(
    task_name: str, data_dir: Optional[Path] = None
) -> ProteinAnalysisDataset:
    """Create dataset with a single task."""
    return ProteinAnalysisDataset(data_dir=data_dir, tasks_filter=[task_name])


if __name__ == "__main__":
    # Example usage and testing
    print("Testing ProteinAnalysisDataset...")

    # Create full dataset
    dataset = ProteinAnalysisDataset()

    # Print summary
    summary = dataset.get_summary()
    print(f"Dataset Summary: {summary}")

    # Validate data integrity
    errors = dataset.validate_data_integrity()
    print(f"Validation Errors: {errors}")

    # Create some samples
    samples = dataset.create_samples()
    print(f"Created {len(samples)} samples")

    # Show first few samples
    for i, sample in enumerate(samples[:3]):
        print(f"\nSample {i + 1}:")
        print(f"Input: {sample.input[:100]}...")
        print(f"Target: {sample.target}")
        print(f"Task: {sample.metadata['task_name']}")
        print(f"Variant: {sample.metadata['variant']}")
