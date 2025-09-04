**Task**
Given a FASTA file containing 15 homologous sequences, you must first align them, then create a phylogenetic tree using the neighbor-joining method. Finally, calculate the evolutionary distance between all pairs of sequences (leaves) in the tree and return the maximum pairwise distance found. The output should be a float rounded to four decimal places, in the format <answer>float</answer>.

**Steps**
1) Perform a multiple sequence alignment on the input FASTA file using `muscle`.
2) Parse the resulting alignment file.
3) Use Biopython's `DistanceCalculator` to create a distance matrix from the alignment.
4) Use `DistanceTreeConstructor` with the neighbor-joining ('nj') method to build the tree.
5) Get a list of all the terminal nodes (leaves) of the tree.
6) Iterate through all possible pairs of leaves.
7) For each pair, calculate the distance using the `tree.distance()` method.
8) Keep track of the maximum distance encountered.
9) Return the maximum distance, rounded to four decimal places.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

cytochrome_c_mammals_15_sequences.fasta
