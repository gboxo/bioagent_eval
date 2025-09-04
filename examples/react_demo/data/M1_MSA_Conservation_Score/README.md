**Task**
    You are given a list of UniProt IDs for homologous proteins. Perform a Multiple Sequence Alignment (MSA) on them. Then, calculate the conservation for each column in the alignment. Conservation is defined as the frequency of the most common amino acid. Return an integer count of the number of columns with a conservation score greater than 80% (0.8), in the format <answer>int</answer>.

    **Steps**
    1) Fetch the FASTA sequence for each UniProt ID.
2) Combine all sequences into a single multi-FASTA file.
3) Run the `muscle` command-line tool on the FASTA file to generate an alignment file (e.g., in Clustal format).
4) Parse the alignment file using Biopython's `AlignIO`.
5) Initialize a counter for highly conserved columns.
6) Iterate through each column of the alignment.
7) For each column, count the occurrences of each amino acid and find the count of the most frequent one.
8) Calculate the frequency (most_frequent_count / number_of_sequences).
9) If the frequency is > 0.8, increment the counter.
10) Return the final count.

    **Variant**
    We don't need to download the data, the data is already in variant_1 folder

    ['P00533', 'P04626', 'P21860', 'Q15303', 'P08581']
