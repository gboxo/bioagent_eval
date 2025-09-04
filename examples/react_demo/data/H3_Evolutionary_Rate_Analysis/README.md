**Task**
You are given a list of orthologous protein UniProt IDs. Your goal is to determine how many branches in their evolutionary history show signs of positive selection. To do this, you must build a phylogenetic tree and calculate the dN/dS ratio (omega) for each branch. A dN/dS ratio > 1 indicates positive selection. You must return an integer count of the branches where omega > 1, as calculated by the PAML software package. The final output must be in the format <answer>int</answer>.

**Steps**
1) Data Retrieval: For each UniProt ID, fetch the protein FASTA and its corresponding nucleotide coding sequence (CDS) from UniProt and ENA/GenBank. Consolidate them into two multi-FASTA files (one for proteins, one for CDS).
2) Protein MSA: Use a command-line tool like MUSCLE to perform a multiple sequence alignment of the protein sequences.
3) Codon Alignment: Use the `pal2nal.pl` script, providing the protein MSA and the nucleotide FASTA file, to generate a codon-correct nucleotide alignment in PAML format.
4) Tree Building: Use Biopython to read the protein MSA, calculate a distance matrix, and construct a phylogenetic tree using the neighbor-joining algorithm. Save the tree in Newick format.
5) PAML Setup: Create a control file (`codeml.ctl`) for PAML's `codeml` program. Set `model = 2` to enable the branch model, which estimates a separate dN/dS ratio for each branch.
6) Run Analysis: Execute the `codeml` program from the command line.
7) Parse Results: Read the main output file (typically `mlc`) from `codeml`. Locate the section detailing the dN/dS ratios for each branch in the tree.
8) Count Branches: Iterate through the reported omega (dN/dS) values and count how many are greater than 1.0.
9) Return Count: Return the final integer count.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

['P69905', 'P01942', 'P01941', 'P02734', 'P02735', 'P02736', 'P02737', 'P02738', 'P02739', 'P02740', 'P02741', 'P02742', 'P02743', 'P02744', 'P02745']
