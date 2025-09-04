**Task**
You are given a list of UniProt IDs. Fetch the sequence for the first UniProt ID in the list. Calculate the percentage of hydrophobic residues (A, I, L, M, F, P, V, W) in this sequence. Return the result as a float rounded to two decimal places, in the format <answer>float</answer>.

**Steps**
1) Take the first ID from the input list.
2) Fetch its FASTA sequence from UniProt.
3) Define the set of single-letter codes for hydrophobic amino acids.
4) Count the total number of residues in the sequence.
5) Count the number of residues that are in the hydrophobic set.
6) Calculate the percentage: (hydrophobic_count / total_count) * 100.
7) Round the result to two decimal places and return it.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

['P0DPA2', 'P0DPA3', 'P0DPA4', 'P0DPA5', 'P0DPA6']
