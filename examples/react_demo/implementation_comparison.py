"""
Tooling for comparing an implementation against a reference.

This module now includes a small CLI utility for reading any Inspect AI
evaluation log (".eval" native format or ".json") using the official
Inspect API. This will be used as step 1 of the comparison workflow.

Usage example:
  uv run python examples/react_demo/implementation_comparison.py /path/to/log.eval
"""

from __future__ import annotations

import pandas as pd
import argparse
import sys
import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
from inspect_ai.analysis import messages_df
from openai import AsyncOpenAI


# Ensure local repo src/ is importable so examples can import inspect_ai
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"

from typing import Any, Dict, List, Tuple, no_type_check

from inspect_ai.log import (  # type: ignore  # noqa: E402
    EvalLog,
    EvalSampleSummary,
    read_eval_log,
    read_eval_log_sample_summaries,
)


def load_eval_log(
    eval_path: Path,
    *,
    header_only: bool = True,
    resolve_attachments: bool = False,
) -> EvalLog:
    """Load an Inspect AI evaluation log.

    Args:
        eval_path: Path to a .eval or .json log file. May be local or remote
            (e.g., S3), as supported by Inspect AI.
        header_only: If True, read only the header (no samples/logging).
        resolve_attachments: If True, resolve attachments (e.g., images) to full content.
        format: "auto" (default) detects by extension; override with "eval" or "json".

    Returns:
        The loaded `EvalLog` object.
    """
    log = read_eval_log(
        eval_path.as_posix(),
        header_only=header_only,
        resolve_attachments=resolve_attachments,
        format="auto",
    )
    # Ensure location is set for reading summaries when header_only is True
    if not getattr(log, "location", None):
        log.location = eval_path.as_posix()
    return log




def _resolve_sample_task(metadata: Dict[str, Any] | None, default_task: str) -> str:
    """Resolve task name for a sample from its metadata.

    Looks for common keys like "task_name" or "task" and falls back to
    the eval-level task if not present.
    """
    if not metadata:
        return default_task
    task = metadata.get("task_name") or metadata.get("task")
    return str(task) if isinstance(task, str) and task else default_task


def group_samples_by_task(log: EvalLog) -> Dict[str, List[Tuple[int | str, int, str]]]:
    """Group samples in an eval log by task name.

    Returns a mapping of task_name -> list of (sample_id, epoch) tuples.
    Works whether full samples were loaded or only headers (using summaries).
    """
    default_task = log.eval.task

    # Prefer summaries when header_only was used or samples not present
    summaries: List[EvalSampleSummary] = read_eval_log_sample_summaries(
        log.location or "",
        format="auto",
    )
    groups: Dict[str, List[Tuple[int | str, int, str]]] = {}
    for s in summaries:
        task_name = _resolve_sample_task(s.metadata, default_task)
        groups.setdefault(task_name, []).append((s.id, s.epoch, s.uuid))
    return groups



def parse_messages_to_markdown(log_path: Path) -> dict:
    """Parse messages from an eval log and convert to markdown format.

    Groups messages by sample using only dataframe columns, converts content to markdown,
    and aggregates into a final markdown string. Tool calls are truncated to 1000 characters.

    Args:
        log_path: Path to the eval log file

    Returns:
        Aggregated markdown string containing all messages grouped by sample
    """

    # Get messages dataframe
    df = messages_df(log_path)


    markdown_sections = {}

    # Group by sample_id directly from the dataframe
    for sample_id in df['sample_id'].unique():
        sample_list = []
        sample_messages = df[df['sample_id'] == sample_id]

        if not sample_messages.empty:
            sample_list.append(f"# Sample {sample_id}\n")

            # Process each message in chronological order (sorted by order column)
            sample_messages_sorted = sample_messages.sort_values('order')
            for _, message in sample_messages_sorted.iterrows():
                import pandas as pd


                role = message['role'] if 'role' in message and not pd.isna(message['role']) else 'unknown'
                content = message['content'] if 'content' in message and not pd.isna(message['content']) else ''
                tool_calls = message['tool_calls'] if 'tool_calls' in message and not pd.isna(message['tool_calls']) else ''
                tool_call_id = message['tool_call_id'] if 'tool_call_id' in message and not pd.isna(message['tool_call_id']) else ''

                # Create markdown for this message
                sample_list.append(f"## {role.title()} Message\n")

                if tool_call_id:
                    sample_list.append(f"**Tool Call ID:** `{tool_call_id}`\n")

                if content:
                    # Escape markdown special characters in content
                    escaped_content = content.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
                    if role == "tool":
                        sample_list.append(f"**Content:**\n```\n{escaped_content[:1000]}\n... TRUNCATED\n```\n")
                    else:
                        sample_list.append(f"**Content:**\n{escaped_content}\n")

                if tool_calls:
                    # Truncate tool calls to 1000 characters
                    if len(tool_calls) > 1000:
                        truncated_calls = tool_calls[:1000] + "\n... TRUNCATED"
                    else:
                        truncated_calls = tool_calls

                    sample_list.append(f"**Tool Calls:**\n```\n{truncated_calls}\n```\n")

                sample_list.append("\n---\n")

            sample_list.append("\n" + "="*50 + "\n")
        markdown_sections[sample_id]="\n".join(sample_list)

    return markdown_sections


def convert_task_files_to_markdown(task_types: set[str], base_folder: Path = Path(".")) -> tuple[dict[str, str], dict[str, str]]:
    """Convert .py, .sh, and README.md files from task-specific folders to markdown format.

    Args:
        task_types: Set of task type names to look for
        base_folder: Base directory to search for task folders

    Returns:
        Tuple of (task_markdown, task_readmes) dictionaries
    """
    task_markdown = {}
    task_readmes = {}

    for task_type in task_types:
        task_folder = base_folder / task_type
        print(task_folder)
        markdown_sections = []

        if task_folder.exists() and task_folder.is_dir():
            markdown_sections.append(f"# {task_type} Implementation Files\n")

            # Check for README.md first
            readme_path = task_folder / "README.md"
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            task_readmes[task_type] = readme_content

            # Find all .py and .sh files in the task folder
            py_files = list(task_folder.glob("*.py"))
            sh_files = list(task_folder.glob("*.sh"))
            all_files = sorted(py_files + sh_files)

            for file_path in all_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Determine language for syntax highlighting
                    language = "python" if file_path.suffix == ".py" else "bash"

                    markdown_sections.append(f"## {file_path.name}\n")
                    markdown_sections.append(f"```{language}\n{content}\n```\n")
                    markdown_sections.append("---\n")

                except Exception as e:
                    markdown_sections.append(f"## {file_path.name}\n")
                    markdown_sections.append(f"*Error reading file: {e}*\n")
                    markdown_sections.append("---\n")
        else:
            markdown_sections.append(f"# {task_type} Implementation Files\n")
            markdown_sections.append(f"*No folder found for task type: {task_type}*\n")
            task_readmes[task_type] = "No folder found"

        task_markdown[task_type] = "\n".join(markdown_sections)

    return task_markdown, task_readmes


async def compare_implementations_with_openai(
    sample_uuid: str,
    task_type: str,
    implementation_markdown: str,
    conversation_markdown: str,
    readme_content: str,
    client: AsyncOpenAI
) -> dict[str, str]:
    """Compare implementation with conversation using OpenAI API.

    Args:
        sample_uuid: UUID of the sample
        task_type: Type of task being analyzed
        implementation_markdown: Markdown content of implementation files
        conversation_markdown: Markdown content of the conversation
        readme_content: Content of the task README.md file
        client: AsyncOpenAI client instance

    Returns:
        Dictionary with comparison results
    """
    system_prompt = f"""You are an expert code reviewer and AI conversation analyst. You specialize in analyzing how well AI agents perform on coding tasks.

**TASK INFORMATION:**
{readme_content}

Your job is to compare the reference implementation with an AI agent's conversation log to assess how well the agent performed the task. Pay special attention to:
- Whether the agent understood the task requirements
- How the agent's approach compares to the reference implementation
- The quality and correctness of the agent's work
- Any significant deviations or improvements

Provide detailed, structured analysis comparing implementations with AI conversations."""

    user_prompt = f"""
**Task Type:** {task_type}
**Sample UUID:** {sample_uuid}

**Reference Implementation:**
{implementation_markdown}

**AI Agent Conversation:**
{conversation_markdown}

Please analyze and compare these two pieces of information:

1. **Task Understanding**: Based on the README, did the AI agent correctly understand what it was supposed to do?

2. **Implementation Analysis**: What does the reference implementation actually do? What are its key components and functionality?

3. **Conversation Analysis**: What was the AI agent trying to accomplish in the conversation? What tools did it use and what was the outcome?

4. **Comparison**: How well does the agent's conversation align with the reference implementation? Are there discrepancies, improvements, or issues?

5. **Assessment**: Rate the agent's performance (1-10) and provide detailed reasoning.

Please provide a structured analysis in markdown format.
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.1,
            max_tokens=4000
        )

        return {
            "sample_uuid": sample_uuid,
            "task_type": task_type,
            "readme_content": readme_content,
            "implementation_markdown": implementation_markdown,
            "conversation_markdown": conversation_markdown,
            "analysis": response.choices[0].message.content,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "sample_uuid": sample_uuid,
            "task_type": task_type,
            "readme_content": readme_content,
            "implementation_markdown": implementation_markdown,
            "conversation_markdown": conversation_markdown,
            "analysis": f"Error during analysis: {str(e)}",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }


async def run_all_comparisons(
    inverse_grouped: dict[str, str],
    task_files_markdown: dict[str, str],
    task_readmes: dict[str, str],
    markdown_output: dict[str, str]
) -> list[dict[str, str]]:
    """Run OpenAI comparisons for all samples concurrently.

    Args:
        inverse_grouped: Mapping of sample UUID to task type
        task_files_markdown: Task implementation files as markdown
        task_readmes: Task README contents
        markdown_output: Sample conversations as markdown

    Returns:
        List of comparison results
    """
    # Initialize OpenAI client
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Create tasks for all comparisons
    tasks = []
    for sample_uuid, task_type in inverse_grouped.items():
        if sample_uuid in markdown_output:
            implementation_markdown = task_files_markdown.get(task_type, f"No implementation found for {task_type}")
            readme_content = task_readmes.get(task_type, "No README found")
            conversation_markdown = markdown_output[sample_uuid]

            task = compare_implementations_with_openai(
                sample_uuid,
                task_type,
                implementation_markdown,
                conversation_markdown,
                readme_content,
                client
            )
            tasks.append(task)

    print(f"Running {len(tasks)} OpenAI comparisons...")

    # Run all comparisons concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions and return results
    valid_results = []
    for result in results:
        if isinstance(result, dict):
            valid_results.append(result)
        else:
            print(f"Error in comparison: {result}")

    return valid_results


def save_results_to_json(results: list[dict[str, str]], output_path: Path) -> None:
    """Save comparison results to a JSON file.

    Args:
        results: List of comparison results
        output_path: Path where to save the JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")
    except Exception as e:
        print(f"Error saving results to JSON: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Read an Inspect AI .eval/.json log using the official Inspect API."
        )
    )
    parser.add_argument(
        "eval_file",
        type=Path,
        help="Path to a .eval (or .json) evaluation log",
    )

    args = parser.parse_args()
    path = args.eval_file

    log = load_eval_log(path, header_only=True, resolve_attachments=True)
    grouped = group_samples_by_task(log)
    inverse_grouped = {v[-1]: k for k, vs in grouped.items() for v in vs}

    # Get unique task types
    task_types = set(inverse_grouped.values())
    print(f"Found task types: {task_types}")

    # Convert task implementation files to markdown
    task_files_markdown, task_readmes = convert_task_files_to_markdown(task_types, base_folder=REPO_ROOT / "examples/react_demo/data")

    # Get messages markdown
    markdown_output = parse_messages_to_markdown(path)

    # Run OpenAI comparisons
    print("Starting OpenAI API comparisons...")
    comparison_results = asyncio.run(run_all_comparisons(inverse_grouped, task_files_markdown, task_readmes, markdown_output))

    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_name = path.stem
    output_filename = f"comparison_results_{log_name}_{timestamp}.json"
    output_path = Path(output_filename)

    # Save results to JSON
    save_results_to_json(comparison_results, output_path)

    # Display summary
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY:")
    print(f"{'='*60}")
    print(f"Total samples processed: {len(comparison_results)}")
    print(f"Successful analyses: {sum(1 for r in comparison_results if r['status'] == 'success')}")
    print(f"Failed analyses: {sum(1 for r in comparison_results if r['status'] == 'error')}")
    print(f"Results saved to: {output_path}")

    # Display brief results
    print(f"\n{'='*60}")
    print("BRIEF RESULTS:")
    print(f"{'='*60}")

    for result in comparison_results:
        print(f"\nSample: {result['sample_uuid'][:8]}...")
        print(f"Task: {result['task_type']}")
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            # Extract rating from analysis if possible
            analysis = result['analysis']
            if 'rating' in analysis.lower() or 'score' in analysis.lower():
                lines = analysis.split('\n')
                rating_line = next((line for line in lines if any(word in line.lower() for word in ['rating', 'score', '/10', 'assessment'])), "Rating not found")
                print(f"Assessment: {rating_line.strip()}")
        print("-" * 40)


if __name__ == "__main__":
    main()
