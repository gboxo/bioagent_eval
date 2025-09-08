#!/usr/bin/env python3
"""
Robust Protein Analysis Evaluation Framework with error handling for reasoning models.

This version includes error handling for malformed reasoning tokens that can occur
with reasoning models like gpt-5-mini.
"""

from textwrap import dedent
from typing import Callable, List, Optional, Union
import logging

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.scorer import match
from inspect_ai.tool import bash, python, text_editor
from inspect_ai.solver import Plan, solver, Generate
from inspect_ai.model import GenerateConfig

# Import our custom components
from protein_dataset import ProteinAnalysisDataset


# System prompt for the ReAct agent with reasoning model guidance
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
    10. Ensure your response is well-structured and complete

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
    
    IMPORTANT: Always complete your reasoning and provide a final answer. Do not leave responses incomplete.
""").strip()


@solver
def robust_react_solver(
    name: str = "protein_analyst",
    description: str = "Expert protein structure and sequence analyst",
    prompt: str = SYSTEM_MESSAGE,
    tools: list = None,
    attempts: int = 3,
    max_iterations: int = 15,
) -> Plan:
    """
    Robust ReAct solver with error handling for reasoning models.
    
    This solver adds error handling specifically for reasoning token issues
    that can occur with models like gpt-5-mini.
    """
    if tools is None:
        tools = [bash(), python(), text_editor()]
    
    async def solve(task, state):
        try:
            # Try the standard ReAct approach first
            react_solver = react(
                name=name,
                description=description,
                prompt=prompt,
                tools=tools,
                attempts=attempts,
                max_iterations=max_iterations,
            )
            return await react_solver(task, state)
            
        except Exception as e:
            error_msg = str(e)
            logging.warning(f"ReAct solver failed with error: {error_msg}")
            
            # Check if it's a reasoning token error
            if "reasoning" in error_msg.lower() and "required following item" in error_msg.lower():
                logging.info("Detected reasoning token error, attempting recovery")
                
                # Try a simpler generation approach
                try:
                    simple_prompt = f"""
                    {prompt}
                    
                    IMPORTANT: Provide a complete response with clear reasoning and a final answer.
                    Do not use complex reasoning structures - just think step by step and provide your answer.
                    """
                    
                    generate_config = GenerateConfig(
                        temperature=0.1,  # Lower temperature for more consistent output
                        max_tokens=4000,  # Reasonable limit
                    )
                    
                    simple_solver = Generate(config=generate_config)
                    return await simple_solver(task, state)
                    
                except Exception as recovery_error:
                    logging.error(f"Recovery attempt failed: {recovery_error}")
                    # Return a basic failure state
                    state.output.completion = "Error: Unable to complete analysis due to model issues."
                    return state
            else:
                # Re-raise non-reasoning errors
                raise e
    
    return solve


@task
def protein_analysis_eval_robust(
    task_filter: Optional[Union[str, List[str], Callable[[str], bool]]] = None,
    variant_filter: Optional[List[str]] = None,
    difficulty_filter: Optional[List[str]] = None,
    model: str = "openai/gpt-5-mini",
    max_samples: Optional[int] = None,
) -> Task:
    """
    Robust protein analysis evaluation task with error handling for reasoning models.

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

    print(f"Evaluating {len(samples)} samples with {model} (robust version)")

    # Use simple match scorer
    scorer = match()

    return Task(
        dataset=samples,
        solver=robust_react_solver(
            name="protein_analyst_robust",
            description="Expert protein structure analyst with error handling",
            prompt=SYSTEM_MESSAGE,
            tools=[bash(), python(), text_editor()],
            attempts=2,  # Fewer attempts since we have recovery logic
            max_iterations=15,
        ),
        scorer=scorer,
        # Use gboxo/inspect-tool image with all programs pre-installed
        compose="./compose_gboxo.yaml",
        sandbox="docker",
    )


@task
def protein_easy_tasks_robust(model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate only Easy (E) difficulty tasks with robust error handling."""
    return protein_analysis_eval_robust(difficulty_filter=["E"], model=model)


@task
def protein_single_task_robust(task_name: str, model: str = "openai/gpt-5-mini") -> Task:
    """Evaluate a single specific task with robust error handling."""
    return protein_analysis_eval_robust(task_filter=[task_name], model=model)


if __name__ == "__main__":
    print("Robust Protein Analysis Evaluation Framework")
    print("Includes error handling for reasoning model issues")
    print("Usage:")
    print("- uv run inspect eval protein_eval_robust.py::protein_easy_tasks_robust")
    print("- uv run inspect eval protein_eval_robust.py::protein_single_task_robust -T task_name=H5_Functional_Site_Conservation")