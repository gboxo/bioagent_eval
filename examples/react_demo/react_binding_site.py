"""
ReAct Agent Demo - Protein Binding Site Analysis

This demo showcases a ReAct agent that can download and analyze a PDB file
to calculate the average hydrophobicity of a ligand-binding site.
"""

from textwrap import dedent

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.tool import bash, python, text_editor

# System prompt for the ReAct agent
SYSTEM_MESSAGE = dedent("""
    You are an expert computational biologist. Your task is to analyze the binding site of a protein-ligand complex from a PDB file and calculate its average hydrophobicity.

    You have access to the following tools:
    - bash: Execute shell commands (e.g., `wget` to download files).
    - python: Execute Python code for parsing and analysis.
    - text_editor: Read and write files.

    Here is the Kyte-Doolittle hydrophobicity scale you MUST use:
    {'ALA': 1.8, 'ARG': -4.5, 'ASN': -3.5, 'ASP': -3.5, 'CYS': 2.5,
     'GLN': -3.5, 'GLU': -3.5, 'GLY': -0.4, 'HIS': -3.2, 'ILE': 4.5,
     'LEU': 3.8, 'LYS': -3.9, 'MET': 1.9, 'PHE': 2.8, 'PRO': -1.6,
     'SER': -0.8, 'THR': -0.7, 'TRP': -0.9, 'TYR': -1.3, 'VAL': 4.2}

    Your current objective is to perform the following steps:
    1.  Download the PDB file for the PDB ID '1UYD' from the RCSB PDB database. The URL format is `https://files.rcsb.org/download/PDBID.pdb`.
    2.  Using Python, parse the downloaded PDB file.
    3.  Identify the coordinates of all atoms belonging to the ligand with the residue name 'ACR'.
    4.  Identify all protein amino acid residues where any atom is within 5.0 Angstroms of any atom of the 'ACR' ligand. A residue is in the binding site if even one of its atoms meets the distance criteria.
    5.  Calculate the average Kyte-Doolittle hydrophobicity for the unique residues you identified.
    6.  Return the final calculated average, rounded to three decimal places, inside <answer> tags. For example: <answer>-0.123</answer>.

    Work step-by-step, using your tools to achieve the goal. When you have the final answer, submit it.
""").strip()


@task
def react_binding_site_analysis():
    """
    ReAct agent demo that analyzes the binding site of PDB ID 1UYD.
    """
    return Task(
        dataset=[
            Sample(
                input="Analyze the PDB file for 1UYD, find the binding site for the ligand 'ACR' (residues within 5.0 Å), and calculate the average Kyte-Doolittle hydrophobicity of those residues.",
                # The target value is pre-calculated by the task author to be the correct answer.
                target="<answer>-0.652</answer>",
            )
        ],
        solver=react(
            name="binding_site_analyst",
            description="Expert at protein structure analysis",
            prompt=SYSTEM_MESSAGE,
            tools=[bash(), python(), text_editor()],
            # This complex task may require more steps and attempts
            attempts=2,
        ),
        scorer=match(),
        # Docker sandbox is required for internet access (wget) and a consistent environment
        sandbox="docker",
    )


if __name__ == "__main__":
    # Run the demo task
    import asyncio
    from inspect_ai import eval

    async def main():
        # Make sure to have your model provider configured (e.g., OPENAI_API_KEY)
        result = await eval(react_binding_site_analysis(), model="openai/gpt-5-mini")
        print("Demo completed!")
        print(f"Score: {result.scorer}")

    asyncio.run(main())
