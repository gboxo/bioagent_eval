**Task**
Download a PDB file and analyze the flexibility of its residues. Extract the B-factor for every C-alpha atom in the structure. Identify all residues whose C-alpha B-factors are in the top 10% of all C-alpha B-factors for that structure. Return the total count of these highly flexible residues as an integer in the format <answer>int</answer>.

**Steps**
1) Download and parse the PDB file using Biopython.
2) Create a list and populate it with the B-factor of every C-alpha atom found in the structure.
3) Sort the list of B-factors in descending order.
4) Calculate the number of residues that constitute the top 10% (i.e., `count = int(len(b_factor_list) * 0.1)`).
5) This count is the number of residues in the top 10%. Return this integer value.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

2LYZ
