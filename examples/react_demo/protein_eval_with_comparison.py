#!/usr/bin/env python3
"""
Protein Analysis Evaluation Framework with Implementation Comparison

This version uses a custom scorer that compares the model's implementation
with the reference implementation using GPT-5-mini analysis.
"""

from textwrap import dedent
from typing import Callable, List, Optional, Union

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.scorer import match
from inspect_ai.tool import bash, python, text_editor

# Import our custom components
from protein_dataset import ProteinAnalysisDataset
from implementation_comparison_scorer import implementation_comparison_scorer


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
def protein_analysis_eval_with_comparison(
    task_filter: Optional[Union[str, List[str], Callable[[str], bool]]] = None,
    variant_filter: Optional[List[str]] = None,
    difficulty_filter: Optional[List[str]] = None,
    model: str = "openai/gpt-5-mini",
    max_samples: Optional[int] = None,
    use_implementation_comparison: bool = True,
) -> Task:
    """
    Protein analysis evaluation task with implementation comparison scoring.

    Args:
        task_filter: Filter tasks by name(s) or function
        variant_filter: List of variant names to include
        difficulty_filter: List of difficulties to include (E, M, H)
        model: Model to use for evaluation
        max_samples: Maximum number of samples to evaluate
        use_implementation_comparison: Whether to use implementation comparison scorer

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
    print(f"Using implementation comparison: {use_implementation_comparison}")

    # Choose scorer based on configuration
    if use_implementation_comparison:
        scorer = implementation_comparison_scorer()
        print("Using implementation comparison scorer with GPT-5-mini analysis")
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
def protein_easy_tasks_with_comparison(model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate only Easy (E) difficulty tasks with implementation comparison."""
    return protein_analysis_eval_with_comparison(
        difficulty_filter=["E"], 
        model=model,
        use_implementation_comparison=True
    )


@task
def protein_medium_tasks_with_comparison(model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate only Medium (M) difficulty tasks with implementation comparison."""
    return protein_analysis_eval_with_comparison(
        difficulty_filter=["M"], 
        model=model,
        use_implementation_comparison=True
    )


@task
def protein_hard_tasks_with_comparison(model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate only Hard (H) difficulty tasks with implementation comparison."""
    return protein_analysis_eval_with_comparison(
        difficulty_filter=["H"], 
        model=model,
        use_implementation_comparison=True
    )


@task
def protein_single_task_with_comparison(task_name: str, model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate a single specific task with implementation comparison."""
    return protein_analysis_eval_with_comparison(
        task_filter=[task_name], 
        model=model,
        use_implementation_comparison=True
    )


@task
def protein_sample_eval_with_comparison(model: str = "openai/gpt-5-mini") -> Task:
    """Quick evaluation with implementation comparison - just a few samples for testing."""
    return protein_analysis_eval_with_comparison(
        difficulty_filter=["E"],  # Easy tasks only
        variant_filter=["variant_1"],  # Single variant
        max_samples=3,  # Just 3 samples
        model=model,
        use_implementation_comparison=True
    )


# Standard versions without implementation comparison (for comparison)
@task
def protein_easy_tasks_standard(model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate only Easy (E) difficulty tasks with standard scoring."""
    return protein_analysis_eval_with_comparison(
        difficulty_filter=["E"], 
        model=model,
        use_implementation_comparison=False
    )


if __name__ == "__main__":
    print("Protein Analysis Evaluation Framework with Implementation Comparison")
    print("Usage examples:")
    print("- Standard scoring: uv run inspect eval protein_eval_with_comparison.py::protein_easy_tasks_standard")
    print("- With comparison: uv run inspect eval protein_eval_with_comparison.py::protein_easy_tasks_with_comparison")
    print("- Single task: uv run inspect eval protein_eval_with_comparison.py::protein_single_task_with_comparison -T task_name=E1_PDB_Cysteine_Count")