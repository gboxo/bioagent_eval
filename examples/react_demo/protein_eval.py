#!/usr/bin/env python3
"""
Protein Analysis Evaluation Framework

Main evaluation script that integrates all components:
- ProteinAnalysisDataset for sample generation
- ProteinAnalysisScorer for intelligent scoring
- DockerSandboxManager for environment management
- ReAct agent for task execution
"""

from textwrap import dedent
from typing import Callable, List, Optional, Union

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.scorer import match
from inspect_ai.tool import bash, python, text_editor

# Import our custom components
from protein_dataset import ProteinAnalysisDataset


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

    1. Work step by step, explaining your reasoning
    2. Use appropriate bioinformatics tools when available
    3. Validate your results when possible
    4. Provide your final answer in <answer>value</answer> tags
    5. For numerical results, provide exact values without rounding unless specified
    6. For PDB IDs, use standard 4-character format (e.g., 1ABC)
    7. For chain identifiers or protein lists, use SPACE-separated values (e.g., "A B C D" not "A,B,C,D")

    Available bioinformatics tools in this environment:
    - MAFFT for multiple sequence alignment
    - DSSP (mkdssp) for secondary structure assignment
    - fpocket for cavity/pocket detection
    - Various Python packages: biopython, pandas, requests, numpy


    Defaults:
    - For mafft, use --auto flag
    - For dssp, use the default settings
    - The default DistanceCalculator from Biopython is "identity" 

    All required data files and tools have been pre-configured for your task, and are localted in /app/data.
    Work methodically and provide clear explanations of your analysis steps.
""").strip()


@task
def protein_analysis_eval(
    task_filter: Optional[Union[str, List[str], Callable[[str], bool]]] = None,
    variant_filter: Optional[List[str]] = None,
    difficulty_filter: Optional[List[str]] = None,
    model: str = "openai/gpt-5-mini",
    max_samples: Optional[int] = None,
) -> Task:
    """
    Main protein analysis evaluation task.

    Args:
        task_filter: Filter tasks by name(s) or function
        variant_filter: List of variant names to include
        difficulty_filter: List of difficulties to include (E, M, H)
        model: Model to use for evaluation
        max_samples: Maximum number of samples to evaluate

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

    # Use simple match scorer for now - can enhance later
    scorer = match()

    return Task(
        dataset=samples,
        solver=react(
            name="protein_analyst",
            description="Expert protein structure and sequence analyst",
            prompt=SYSTEM_MESSAGE,
            tools=[bash(), python(), text_editor()],
            attempts=3,
        ),
        scorer=scorer,
        # Do not set a global compose; each sample provides its own compose
        sandbox="docker",
    )


@task
def protein_easy_tasks(model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate only Easy (E) difficulty tasks."""
    return protein_analysis_eval(difficulty_filter=["E"], model=model)


@task
def protein_medium_tasks(model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate only Medium (M) difficulty tasks."""
    return protein_analysis_eval(difficulty_filter=["M"], model=model)


@task
def protein_hard_tasks(model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate only Hard (H) difficulty tasks."""
    return protein_analysis_eval(difficulty_filter=["H"], model=model)


@task
def protein_single_task(task_name: str, model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate a single specific task."""
    return protein_analysis_eval(task_filter=[task_name], model=model)


@task
def protein_sample_eval(model: str = "openai/gpt-5-mini") -> Task:
    """Quick evaluation with just a few samples for testing."""
    return protein_analysis_eval(
        difficulty_filter=["E"],  # Easy tasks only
        variant_filter=["variant_1"],  # Single variant
        max_samples=5,  # Just 5 samples
        model=model,
    )


@task
def protein_e3_debug(model: str = "openai/gpt-5-mini") -> Task:
    """Debug E3_PDB_Chain_Count task specifically."""
    return protein_analysis_eval(task_filter=["E3_PDB_Chain_Count"], model=model)


# No main execution code needed - use uv run inspect eval
