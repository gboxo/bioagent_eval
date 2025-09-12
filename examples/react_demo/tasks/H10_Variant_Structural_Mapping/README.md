**Task**
Given a PDB ID, a chain ID, and a list of single-residue variants (e.g., 'A123G'), you need to determine the structural context of each variant's original residue. Specifically, calculate the Relative Solvent Accessibility (RSA) for each specified wild-type residue. Your goal is to find the variant corresponding to the most buried residue (lowest RSA). Return this variant's name as a string. Format: <answer>str</answer>.

**Steps**
1) For the pdb file in variant_1 folder 
2) Run `mkdssp` on the PDB file to calculate secondary structure and accessibility.
3) Parse the DSSP output file using Biopython's `DSSP` module. This creates a dictionary mapping residue identifiers to their properties.
4) Initialize variables to track the minimum RSA and the corresponding variant.
5) For each variant string in the input list, parse out the residue number.
6) Look up this residue (using the chain ID and residue number) in the parsed DSSP data to get its RSA value.
7) If this RSA is lower than the current minimum, update the minimum RSA and store the current variant string.
8) After checking all variants, return the one associated with the lowest RSA.


```{json}
{
"variant_1": {"pdb_id": "2LYZ", "chain_id": "A",
"variants": ["R21G", "D52N", "W63Y", "A95V", "L129F"]},
}
```

