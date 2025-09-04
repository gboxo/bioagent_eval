**Task**
Download a PDB structure and analyze its secondary structure using the DSSP algorithm. Your task is to count the total number of beta sheets in the protein. A beta sheet can consist of multiple beta strands. You must count the distinct sheets. Return the count as an integer in the format <answer>int</answer>.

**Steps**
1) Download the PDB file.
2) Run the `mkdssp` command-line tool on the PDB file to generate a .dssp file.
3) Parse the output DSSP file using Biopython's `DSSP` module.
4) The Biopython DSSP parser provides access to beta bridges. A beta sheet is a network of residues connected by beta bridges.
5) Iterate through the parsed DSSP data to identify all unique sheet identifiers.
6) Return the number of unique sheets found.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

1A3N
