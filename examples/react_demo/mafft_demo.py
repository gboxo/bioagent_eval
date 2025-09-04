"""
ReAct Agent Demo - PDB File Download

This demo showcases a ReAct agent that can download and analyze PDB files
using bash, python, and file I/O tools in a Docker container with internet access.
"""

from textwrap import dedent

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.tool import bash, python, text_editor


# System prompt for the ReAct agent
SYSTEM_MESSAGE = dedent("""
    You are a scientific research assistant with expertise in protein structure analysis.
    Your task is to analyze csv file with `training-alpha_amylase.csv` and return the number of MSA columns.


    You have access to the following tools:
    - bash: Execute shell commands (including curl, wget, etc.)
    - python: Execute Python code for data analysis
    - text_editor: Read and write files
    - mafft: Execute MAFFT with bash tool

    Your current objective is to:
    1. Locate and analyze the csv file `training-alpha_amylase.csv`
    2. Run MAFFT on the csv file and return the number of MSA columns
    3. Return the number of MSA columns in between <answer>int</answer>.

    The csv file can be found in the sandbox at: /app/training-alpha_amylase.csv

    Work step by step, explaining your reasoning and actions.
    When you have successfully completed the task, use the submit() function with the answer, wrapped in xml tags.
""").strip()


@task
def react_mafft_demo():
    """
    ReAct agent demo that downloads and analyzes the 1BAG PDB file.

    Returns:
        Task: Configured task with ReAct agent, tools, and Docker sandbox
    """
    return Task(
        dataset=[
            Sample(
                input="Locate and analyze the csv file `training-alpha_amylase.csv` and return the number of MSA columns in between <answer>int</answer>.",
                target="<answer>425</answer>",
            )
        ],
        solver=react(
            name="mafft_analyst",
            description="Expert at analyzing csv files",
            prompt=SYSTEM_MESSAGE,
            tools=[bash(), python(), text_editor()],
            attempts=3,
        ),
        scorer=match(),
        sandbox="docker",
    )


if __name__ == "__main__":
    # Run the demo task
    import asyncio
    from inspect_ai import eval

    async def main():
        result = await eval(react_mafft_demo(), model="openai-api/deepseek/reasoner ")
        print("Demo completed!")
        print(f"Score: {result.scorer}")

    asyncio.run(main())
