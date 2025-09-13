**Task**
You are given a list of five PDB IDs. For each ID, you must find its experimental resolution. Your goal is to identify which of the structures has the best (i.e., numerically lowest) resolution. Return the PDB ID of this highest-resolution structure as a string in the format <answer>str</answer>. Note: If a structure was not determined by X-ray crystallography (e.g., it is an NMR structure), it will not have a resolution value and should be ignored in the comparison.

**Steps**
1) Initialize a variable for the best PDB ID and set the best resolution to a very high number (e.g., infinity).
2) Loop through each PDB ID in the list.
3) Download the PDB file.
4) Use Biopython's PDBParser to parse the file and access the header information, specifically the 'resolution' key.
5) If a resolution value exists and is lower than the current best resolution, update the best resolution and best PDB ID variables.
6) After checking all PDB IDs, return the one stored as the best.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

['1UBQ', '2LYZ', '1A3N', '1HTM', '1CRN']
