#!/usr/bin/env python3
"""
Implementation Comparison Scorer - Fixed Version

Based on the official scorer.py example from Inspect AI.
Uses proper imports and model calling patterns.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState
from inspect_ai.model import get_model


@scorer(metrics=[accuracy(), stderr()])
def implementation_comparison_scorer():
    """
    Custom scorer that compares model's implementation with reference implementation.
    
    Returns a Score with:
    - value: CORRECT/INCORRECT or float score based on implementation quality
    - answer: The extracted answer from model's response  
    - explanation: Detailed comparison analysis
    """
    
    async def score(state: TaskState, target: Target) -> Score:
        try:
            # Extract task name from state
            task_name = extract_task_name(state)
            if not task_name:
                return Score(
                    value=INCORRECT,
                    answer="",
                    explanation="Could not extract task name from task state"
                )
            
            # Extract model's answer
            model_answer = extract_model_answer(state)
            
            # Find reference implementation files
            reference_files = await find_reference_files(task_name)
            if not reference_files:
                # If no reference found, fall back to basic correctness check
                target_answer = str(target.text) if hasattr(target, 'text') else str(target)
                is_correct = model_answer.strip() == target_answer.strip()
                return Score(
                    value=CORRECT if is_correct else INCORRECT,
                    answer=model_answer,
                    explanation=f"No reference implementation found for {task_name}. Using basic answer matching."
                )
            
            # Convert reference files to analysis format
            reference_md = convert_files_to_markdown(reference_files)
            
            # Get model's full implementation for comparison
            model_implementation = state.output.completion if hasattr(state.output, 'completion') else str(state)
            
            # Use model to compare implementations
            comparison_result = await compare_implementations_with_model(
                task_name=task_name,
                model_implementation=model_implementation,
                reference_implementation=reference_md,
                target_answer=str(target.text) if hasattr(target, 'text') else str(target),
                model_answer=model_answer
            )
            
            return comparison_result
            
        except Exception as e:
            return Score(
                value=INCORRECT,
                answer="",
                explanation=f"Error in implementation comparison: {str(e)[:200]}"
            )
    
    return score


def extract_task_name(state: TaskState) -> Optional[str]:
    """Extract task name from TaskState."""
    # Try metadata first
    if hasattr(state, 'metadata') and state.metadata:
        task_name = state.metadata.get('task_name')
        if task_name:
            return task_name
    
    # Try sample metadata
    if hasattr(state, 'sample') and hasattr(state.sample, 'metadata'):
        task_name = state.sample.metadata.get('task_name')
        if task_name:
            return task_name
    
    # Try to extract from user input
    if hasattr(state, 'user_message') and state.user_message:
        content = str(state.user_message.content)
        task_match = re.search(r'(E\d+_[A-Za-z_]+|M\d+_[A-Za-z_]+|H\d+_[A-Za-z_]+)', content)
        if task_match:
            return task_match.group(1)
    
    # Try messages as fallback
    if hasattr(state, 'messages') and state.messages:
        for msg in state.messages:
            if hasattr(msg, 'content'):
                content = str(msg.content)
                task_match = re.search(r'(E\d+_[A-Za-z_]+|M\d+_[A-Za-z_]+|H\d+_[A-Za-z_]+)', content)
                if task_match:
                    return task_match.group(1)
    
    return None


def extract_model_answer(state: TaskState) -> str:
    """Extract the final answer from model's response using answer patterns."""
    response_text = ""
    
    # Get the completion text
    if hasattr(state, 'output') and hasattr(state.output, 'completion'):
        response_text = state.output.completion
    
    if not response_text:
        return ""
    
    # Try to extract answer from <answer>...</answer> tags
    answer_match = re.search(r'<answer>(.*?)</answer>', response_text, re.IGNORECASE | re.DOTALL)
    if answer_match:
        return answer_match.group(1).strip()
    
    # Fallback: try to find answer patterns like "ANSWER: value"
    answer_patterns = [
        r'ANSWER:\s*(.+?)(?:\n|$)',
        r'Answer:\s*(.+?)(?:\n|$)',
        r'Final answer:\s*(.+?)(?:\n|$)',
        r'Result:\s*(.+?)(?:\n|$)'
    ]
    
    for pattern in answer_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return ""


async def find_reference_files(task_name: str) -> List[Dict[str, str]]:
    """Find reference .py and .sh files for a given task."""
    base_path = Path(__file__).parent / "data" / task_name
    
    if not base_path.exists():
        return []
    
    reference_files = []
    
    # Look for Python and shell script files
    for pattern in ["*.py", "*.sh"]:
        for file_path in base_path.rglob(pattern):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    file_type = 'python' if pattern == "*.py" else 'shell'
                    reference_files.append({
                        'filename': file_path.name,
                        'type': file_type,
                        'content': content
                    })
                except Exception:
                    continue
    
    return reference_files


def convert_files_to_markdown(files: List[Dict[str, str]]) -> str:
    """Convert reference files to markdown format."""
    if not files:
        return "No reference files found."
    
    markdown_content = ["Reference Implementation:"]
    
    for file_info in files:
        filename = file_info['filename']
        file_type = file_info['type']
        content = file_info['content'][:1000]  # Limit content to avoid huge prompts
        
        # Determine language for syntax highlighting
        lang = 'python' if file_type == 'python' else 'bash'
        
        markdown_content.append(f"\n{filename}:")
        markdown_content.append(f"```{lang}")
        markdown_content.append(content)
        markdown_content.append("```")
    
    return '\n'.join(markdown_content)


async def compare_implementations_with_model(
    task_name: str,
    model_implementation: str,
    reference_implementation: str,
    target_answer: str,
    model_answer: str
) -> Score:
    """Use the model to compare implementations - following the scorer.py pattern."""
    
    # Create a comparison prompt similar to the EQUIVALENCE_TEMPLATE pattern
    comparison_prompt = f"""Compare these two implementations for the bioinformatics task {task_name}:

REFERENCE IMPLEMENTATION:
{reference_implementation}

MODEL'S IMPLEMENTATION:
{model_implementation}

Expected Answer: {target_answer}
Model's Answer: {model_answer}

Judge whether the model's implementation approach is reasonable and likely to produce correct results. Consider:
1. Use of appropriate libraries (BioPython, pandas, etc.)
2. Correct methodology for the task
3. Proper data processing steps
4. Answer correctness

Respond with only "Good" if the implementation approach is sound and likely correct, or "Poor" if it has significant issues or wrong approach. Do not include explanation."""
    
    try:
        # Use the model to judge implementation quality - following scorer.py pattern
        result = await get_model().generate(comparison_prompt)
        response = result.completion.strip().lower()
        
        # Determine if implementation is good
        is_good_implementation = "good" in response
        
        # Create explanation combining both correctness and approach assessment
        explanation = f"""Implementation Comparison for {task_name}:

Reference files analyzed: {len(reference_implementation.split('```')) // 2}
Model's answer: {model_answer}
Expected answer: {target_answer}
Implementation assessment: {result.completion}

Full model response:
{model_implementation[:500]}..."""

        return Score(
            value=CORRECT if is_good_implementation else INCORRECT,
            answer=model_answer,
            explanation=explanation
        )
        
    except Exception as e:
        # Fallback to basic answer matching if comparison fails
        is_correct = model_answer.strip() == target_answer.strip()
        
        return Score(
            value=CORRECT if is_correct else INCORRECT,
            answer=model_answer,
            explanation=f"Implementation comparison failed ({str(e)[:100]}). Using basic answer matching."
        )


if __name__ == "__main__":
    print("Implementation Comparison Scorer - Fixed Version")
    print("Based on official Inspect AI scorer patterns")