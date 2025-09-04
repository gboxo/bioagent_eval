**Task**
    Given two PDB IDs, download their structures. Perform a structural alignment focusing on the C-alpha atoms of the proteins. Calculate and return the Root Mean Square Deviation (RMSD) between the two structures after alignment. The output should be a float rounded to three decimal places, in the format <answer>float</answer>.

    **Steps**
    1) Download the PDB files for both IDs.
2) Parse both structures using Biopython's `PDBParser`.
3) From each structure, extract a list of all C-alpha atoms.
4) Create an instance of Biopython's `Superimposer` class.
5) Use the `set_atoms()` method of the superimposer, providing the two lists of C-alpha atoms.
6) The RMSD is now available in the `superimposer.rmsd` attribute.
7) Return this value, rounded to three decimal places.

    **Variant**
    We don't need to download the data, the data is already in variant_1 folder

    ['1A3N', '1A3O']
