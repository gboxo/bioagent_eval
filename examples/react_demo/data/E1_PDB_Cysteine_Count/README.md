**Task**
You need to download a .pdb file from the Protein Data Bank (PDB) website, then you will need to extract the amino acid sequence (if there are multiple chains present, process all of them), and finally count the total number of cysteine residues in the entire structure. After that, you will return a single integer value for the number of cysteine residues in the following format <answer>int</answer>.

**Steps**
1) Download the PDB file using curl or requests.
2) Create a Python script to parse the PDB file using Biopython's PDBParser.
3) Initialize a total cysteine count to zero.
4) Iterate through all chains in the structure.
5) For each chain, extract its amino acid sequence.
6) Count the occurrences of the character 'C' in the sequence and add it to the total.
7) Return the final integer count.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

1UBQ
