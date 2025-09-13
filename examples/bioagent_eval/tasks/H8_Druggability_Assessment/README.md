**Task**
You are given a list of 5 target protein PDB IDs. For each protein, you must run the `fpocket` command-line tool to detect binding cavities. After running `fpocket`, you need to parse its output to find the 'Druggability Score' for the top-ranked pocket of each protein. Your goal is to identify which of the 5 proteins has the pocket with the highest druggability score. Return the PDB ID of this protein. Format: <answer>str</answer>.

**Steps**
1) For each PDB ID, download the .pdb file.
2) Run the `fpocket -f {pdb_file}` command for each structure. This will create an output directory.
3) In each output directory, parse the main information file (e.g., `{pdb_id}_info.txt`) to find the table of pockets and their properties.
4) Extract the 'Druggability Score' for the first pocket listed (Pocket 1), which is the top-ranked one.
5) Keep track of the PDB ID that yields the highest druggability score.
6) After processing all 5 proteins, return the PDB ID with the overall best score.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

['1A3N', '2LYZ', '1HTM', '1UBQ', '1CRN']
