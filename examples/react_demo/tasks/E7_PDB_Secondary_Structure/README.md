**Task**
Download a PDB structure and analyze its secondary structure using the DSSP algorithm. Your task is to count the total number of beta strand residues across all chains in the structure. Beta strands are individual secondary structure elements marked as 'E' (extended) in DSSP output. You must count all beta strand residues in the entire structural assembly. Return the count as an integer in the format <answer>int</answer>.

**Methodology for Counting Beta Strands**
Beta strands are identified using DSSP's secondary structure assignments:
1) Extract all residues marked as 'E' (extended/beta strand) in DSSP output across all chains
2) Count the total number of residues with secondary structure 'E'
3) This approach counts individual beta strand residues rather than grouping them into sheets

**Steps**
1) Download the PDB file.
2) Run the `mkdssp` command-line tool on the PDB file to generate a .dssp file.
3) Parse the output DSSP file to extract secondary structure assignments.
4) Identify all residues with secondary structure 'E' (beta strand) across all chains.
5) Count the total number of beta strand residues across the entire structure.
6) Return the total count of beta strand residues.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

1A3N
