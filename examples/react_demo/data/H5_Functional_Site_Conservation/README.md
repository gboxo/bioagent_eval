**Task**
You are given a list of 25 UniProt IDs for a family of enzymes, along with a list of active site residue positions from the first sequence in the list. Your task is to identify which of these active site positions are poorly conserved across the family. A position is poorly conserved if the frequency of the most common amino acid at that position (in an MSA) is less than 50%. Return a comma-separated string of the poorly conserved active site positions. Format: <answer>str</answer>.

**Steps**
1) Fetch FASTA sequences for all 25 UniProt IDs and create a multi-FASTA file.
2) Run `mafft` to generate a multiple sequence alignment.
3) Parse the alignment.
4) Create a mapping from the reference sequence positions to the alignment column indices.
5) Initialize an empty list for poorly conserved positions.
6) For each active site position, find its corresponding alignment column.
7) Calculate the frequency of the most common amino acid in that column.
8) If the frequency is less than 0.5, add the original active site position to the list.
9) Sort the list and convert it to a comma-separated string.
10) Return the string.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

['P00766', 'P00767', 'P00768', 'P00769', 'P00770', 'P00771', 'P00772', 'P00773', 'P00774', 'P00775', 'P00776', 'P00777', 'P00778', 'P00779', 'P00780', 'P00781', 'P00782', 'P00783', 'P00784', 'P00785', 'P00786', 'P00787', 'P00788', 'P00789', 'P00790']
