**Task**
Download a PDB file and identify all bound ligands. Water molecules should be excluded. Your task is to count the number of unique types of ligands present. For example, if there are three ATP molecules and two MG ions, the answer is 2. Return this count as an integer in the format <answer>int</answer>.

**Steps**
1) Download the PDB file.
2) Parse the structure using Biopython's PDBParser.
3) Create an empty set to store the names of unique ligands.
4) Iterate through all residues in the structure.
5) For each residue, check if its ID's first element starts with 'H_' (indicating a HETATM) and is not 'W' (for water).
6) If it's a non-water HETATM, add its residue name (e.g., 'ATP', 'MG') to the set.
7) The final count is the size of the set. Return this value.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

1HTM
