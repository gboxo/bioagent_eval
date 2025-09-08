#!/usr/bin/env python3
"""
Protein Analysis Dataset for Inspect AI
Integrates task prompts, expected results, and Docker configurations
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable, Any
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

        # Validate compose files directory
        self.compose_dir = self.data_dir / "compose_files"
        if not self.compose_dir.exists():
            raise FileNotFoundError(
                f"Compose files directory not found: {self.compose_dir}"
            )

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

    def _get_compose_file(self, task_name: str) -> str:
        """Get compose file path for a task."""
        compose_file = self.compose_dir / f"{task_name}_compose.yaml"
        if compose_file.exists():
            return str(compose_file)
        else:
            # Fallback to a default compose file if task-specific one doesn't exist
            default_compose = self.compose_dir / "default_compose.yaml"
            if default_compose.exists():
                return str(default_compose)
            else:
                raise FileNotFoundError(f"No compose file found for task: {task_name}")

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
                    compose_file = self._get_compose_file(task_name)

                    # Create metadata
                    metadata = TaskMetadata(
                        task_name=task_name,
                        variant=variant_name,
                        difficulty=task_name[0],
                        compose_file=compose_file,
                        dependencies=self.dependencies.get(task_name, {}),
                    )

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
            "compose_file": self._get_compose_file(task_name),
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
            "missing_compose_files": [],
            "template_errors": [],
            "missing_variants": [],
        }

        for task_name, task_config in self.prompts.items():
            # Check if results exist for this task
            if task_name not in self.results:
                errors["missing_results"].append(task_name)
                continue

            # Check compose file
            try:
                self._get_compose_file(task_name)
            except FileNotFoundError:
                errors["missing_compose_files"].append(task_name)

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
