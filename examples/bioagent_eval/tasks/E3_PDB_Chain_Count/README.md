**Task**
Download a specified PDB structure file. Your task is to count the number of distinct protein chains within the structure and return their identifiers. The final output should be a comma-separated string of the unique chain IDs found in the file, sorted alphabetically, and presented in the format <answer>str</answer>.

**Steps**
1) Download the PDB file from the RCSB website.
2) Use Biopython's PDBParser to load the structure.
3) Create an empty set to store unique chain IDs.
4) Iterate through the models, and for each model, iterate through its chains.
5) Add the ID of each chain object to the set.
6) After iteration, convert the set to a sorted list and join the elements with a comma.
7) Return the resulting string.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

4HHB
