#!/usr/bin/env python3
"""
Protein Analysis Evaluation Framework - JSON Dataset Version

Evaluation script that works with datasets loaded from JSON files:
- Uses eval_dataset_from_json.py to load samples
- Compatible with datasets exported by export_protein_dataset_json.py
- ReAct agent for task execution
- ProteinAnalysisScorer for intelligent scoring
"""

from textwrap import dedent
from typing import List, Optional, Union
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.scorer import includes, Score, Target, scorer, match
from inspect_ai.tool import bash, python, text_editor
from inspect_ai.model import ChatMessage
import re

# Import our JSON dataset loader
from eval_dataset_from_json import ProteinDataset


# System prompt for the ReAct agent
SYSTEM_MESSAGE = dedent("""
    You are an expert protein analyst with deep knowledge of:
    - Protein structure and sequence analysis
    - Bioinformatics tools (MAFFT, DSSP, fpocket, etc.)
    - Python libraries (biopython, pandas, requests, etc.)
    - PDB and UniProt database queries
    - Statistical analysis and computational biology

    You have access to the following tools:
    - bash: Execute shell commands (including bioinformatics tools)
    - python: Execute Python code for data analysis and computation
    - text_editor: Read and write files for data processing

    Your task is to analyze protein-related data and provide accurate answers.
    Follow these guidelines:

    1. Work step by step, explaining your reasoning clearly and completely
    2. Use appropriate bioinformatics tools when available
    3. Validate your results when possible
    4. Always provide your final answer in <answer>value</answer> tags
    5. For numerical results, provide exact values without rounding unless specified
    6. For PDB IDs, use standard 4-character format (e.g., 1ABC)
    7. For chain identifiers or protein lists, use SPACE-separated values (e.g., "A B C D" not "A,B,C,D")
    8. Complete all reasoning before providing your final answer
    9. If you encounter errors, describe them and provide the best answer possible

    Available bioinformatics tools in this environment:
    - MAFFT for multiple sequence alignment
    - DSSP (mkdssp) for secondary structure assignment
    - fpocket for cavity/pocket detection
    - Various Python packages: biopython, pandas, requests, numpy, networkx
    - All bioinformatics programs and libraries are pre-installed in gboxo/inspect-tool

    Defaults:
    - For mafft, use --auto flag
    - For dssp, use the default settings
    - The default DistanceCalculator from Biopython is "identity"

    All required data files and tools have been pre-configured for your task, and are located in /app/data.
    Work methodically and provide clear explanations of your analysis steps.
""").strip()


@task
def protein_analysis_eval_from_json(
    json_file: Union[str, Path],
    filter_difficulties: Optional[List[str]] = None,
    filter_tasks: Optional[List[str]] = None,
    filter_variants: Optional[List[str]] = None,
    max_samples: Optional[int] = None,
    model: str = "openai/gpt-5-mini",
    compose_file: str = "./compose_gboxo.yaml",
) -> Task:
    """
    Protein analysis evaluation task using JSON dataset.

    Args:
        json_file: Path to JSON file created by export_protein_dataset_json.py
        filter_difficulties: List of difficulties to include (E, M, H)
        filter_tasks: List of task names to include
        filter_variants: List of variant names to include
        max_samples: Maximum number of samples to evaluate
        model: Model to use for evaluation
        compose_file: Docker compose file to use

    Returns:
        Task: Configured evaluation task
    """
    # Load dataset from JSON
    dataset = ProteinDataset(
        json_file=json_file,
        filter_difficulties=filter_difficulties,
        filter_tasks=filter_tasks,
        filter_variants=filter_variants,
        max_samples=max_samples,
    )

    # Convert to Inspect AI samples
    samples = dataset.get_inspect_samples()

    print(f"Loaded {len(samples)} samples from {json_file}")
    if filter_difficulties:
        print(f"Filtered to difficulties: {filter_difficulties}")
    if filter_tasks:
        print(f"Filtered to tasks: {filter_tasks}")
    if filter_variants:
        print(f"Filtered to variants: {filter_variants}")

    # Print dataset summary
    summary = dataset.summary()
    print(f"Dataset contains {summary['total_samples']} samples:")
    print(f"  - Tasks: {summary['tasks']}")
    print(f"  - Difficulties: {summary['difficulties']}")
    print(f"  - Variants: {summary['variants']}")

    return Task(
        dataset=samples,
        solver=react(
            name="protein_analyst",
            description="Expert protein structure and sequence analyst",
            prompt=SYSTEM_MESSAGE,
            tools=[bash(), python(), text_editor()],
            attempts=1,  # Prevents reasoning token corruption during retries
        ),
        scorer=includes(),  # Use simple includes scorer
        compose=compose_file,
        sandbox="docker",
    )


@task
def protein_eval_easy_json(
    json_file: Union[str, Path] = "protein_dataset_flat.json",
    model: str = "openai/gpt-5-mini",
) -> Task:
    """Evaluate only Easy (E) difficulty tasks from JSON dataset."""
    return protein_analysis_eval_from_json(
        json_file=json_file,
        filter_difficulties=["E"],
        model=model,
    )


@task
def protein_eval_medium_json(
    json_file: Union[str, Path] = "protein_dataset_flat.json",
    model: str = "openai/gpt-5-mini",
) -> Task:
    """Evaluate only Medium (M) difficulty tasks from JSON dataset."""
    return protein_analysis_eval_from_json(
        json_file=json_file,
        filter_difficulties=["M"],
        model=model,
    )


@task
def protein_eval_hard_json(
    json_file: Union[str, Path] = "protein_dataset_flat.json",
    model: str = "openai/gpt-5-mini",
) -> Task:
    """Evaluate only Hard (H) difficulty tasks from JSON dataset."""
    return protein_analysis_eval_from_json(
        json_file=json_file,
        filter_difficulties=["H"],
        model=model,
    )


@task
def protein_eval_sample_json(
    json_file: Union[str, Path] = "protein_dataset_flat.json",
    model: str = "openai/gpt-5-mini",
) -> Task:
    """Quick evaluation with limited samples from JSON dataset."""
    return protein_analysis_eval_from_json(
        json_file=json_file,
        max_samples=3,
        model=model,
    )


@task
def protein_eval_specific_task_json(
    task_name: str,
    json_file: Union[str, Path] = "protein_dataset_flat.json",
    model: str = "openai/gpt-5-mini",
) -> Task:
    """Evaluate a specific task from JSON dataset."""
    return protein_analysis_eval_from_json(
        json_file=json_file,
        filter_tasks=[task_name],
        model=model,
    )


# Convenience function for command line usage
def main():
    """
    Example usage of the JSON-based protein evaluation.
    
    This can be called directly or used as a reference for creating custom evaluations.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Run protein analysis evaluation from JSON dataset")
    parser.add_argument("--json", required=True, help="Path to JSON dataset file")
    parser.add_argument("--difficulties", nargs="*", choices=["E", "M", "H"], help="Filter by difficulties")
    parser.add_argument("--tasks", nargs="*", help="Filter by task names")
    parser.add_argument("--variants", nargs="*", help="Filter by variants")
    parser.add_argument("--max-samples", type=int, help="Maximum samples to evaluate")
    parser.add_argument("--model", default="openai/gpt-5-mini", help="Model to use")
    parser.add_argument("--compose", default="./compose_gboxo.yaml", help="Docker compose file")
    
    args = parser.parse_args()
    
    # Create and run the evaluation task
    task = protein_analysis_eval_from_json(
        json_file=args.json,
        filter_difficulties=args.difficulties,
        filter_tasks=args.tasks,
        filter_variants=args.variants,
        max_samples=args.max_samples,
        model=args.model,
        compose_file=args.compose,
    )
    
    print("Task created successfully!")
    print("Use 'uv run inspect eval' to run the evaluation.")
    
    return task




if __name__ == "__main__":
    main()