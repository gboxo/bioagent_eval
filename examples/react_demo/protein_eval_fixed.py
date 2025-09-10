#!/usr/bin/env python3
"""
Protein Analysis Evaluation Framework - Fixed Version

Uses the corrected implementation comparison scorer that follows 
the official Inspect AI patterns from examples/scorer.py
"""

from textwrap import dedent
from typing import Callable, List, Optional, Union

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.scorer import match
from inspect_ai.tool import bash, python, text_editor

# Import our custom components
from protein_dataset import ProteinAnalysisDataset
from implementation_comparison_scorer_fixed import implementation_comparison_scorer


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
def protein_analysis_eval_fixed(
    task_filter: Optional[Union[str, List[str], Callable[[str], bool]]] = None,
    variant_filter: Optional[List[str]] = None,
    difficulty_filter: Optional[List[str]] = None,
    model: str = "openai/gpt-5-mini",
    max_samples: Optional[int] = None,
    scorer_type: str = "implementation_comparison",
) -> Task:
    """
    Protein analysis evaluation task - fixed version with proper scorer.

    Args:
        task_filter: Filter tasks by name(s) or function
        variant_filter: List of variant names to include
        difficulty_filter: List of difficulties to include (E, M, H)
        model: Model to use for evaluation
        max_samples: Maximum number of samples to evaluate
        scorer_type: Type of scorer to use ("match", "implementation_comparison")

    Returns:
        Task: Configured evaluation task
    """
    # Initialize components
    dataset = ProteinAnalysisDataset(
        tasks_filter=task_filter,
        variants_filter=variant_filter,
        difficulties_filter=difficulty_filter,
    )

    # Create samples
    samples = dataset.create_samples()

    if max_samples:
        samples = samples[:max_samples]

    print(f"Evaluating {len(samples)} samples with {model}")
    print(f"Using scorer: {scorer_type}")

    # Choose scorer based on configuration
    if scorer_type == "implementation_comparison":
        scorer = implementation_comparison_scorer()
        print("Using implementation comparison scorer (fixed version)")
        print("Compares model implementation with reference files using model judgment")
    else:
        scorer = match()
        print("Using standard match scorer")

    return Task(
        dataset=samples,
        solver=react(
            name="protein_analyst",
            description="Expert protein structure and sequence analyst",
            prompt=SYSTEM_MESSAGE,
            tools=[bash(), python(), text_editor()],
            attempts=1,  # Fixed: Prevents reasoning token corruption during retries with gpt-5-mini
        ),
        scorer=scorer,
        # Use gboxo/inspect-tool image with all programs pre-installed
        compose="./compose_gboxo.yaml",
        sandbox="docker",
    )


@task
def protein_single_task_fixed(task_name: str, model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate a single specific task with fixed implementation comparison."""
    return protein_analysis_eval_fixed(
        task_filter=[task_name], 
        model=model,
        scorer_type="implementation_comparison"
    )


@task
def protein_easy_tasks_fixed(model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate Easy (E) difficulty tasks with fixed implementation comparison."""
    return protein_analysis_eval_fixed(
        difficulty_filter=["E"], 
        model=model,
        scorer_type="implementation_comparison"
    )


@task
def protein_sample_test_fixed(model: str = "openai/gpt-5-mini") -> Task:
    """Quick test with just one sample to verify the fixed scorer works."""
    return protein_analysis_eval_fixed(
        difficulty_filter=["E"],
        variant_filter=["variant_1"],
        max_samples=1,
        model=model,
        scorer_type="implementation_comparison"
    )


if __name__ == "__main__":
    print("Protein Analysis Evaluation Framework - Fixed Version")
    print("Uses corrected implementation comparison scorer following official Inspect AI patterns")
    print()
    print("Usage examples:")
    print("- Test single sample: uv run inspect eval protein_eval_fixed.py::protein_sample_test_fixed")
    print("- Single task: uv run inspect eval protein_eval_fixed.py::protein_single_task_fixed -T task_name=E1_PDB_Cysteine_Count")
    print("- Easy tasks: uv run inspect eval protein_eval_fixed.py::protein_easy_tasks_fixed")