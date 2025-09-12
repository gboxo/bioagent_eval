**Task**
For a given list of UniProt IDs, you need to fetch the protein sequence for each one. After collecting all sequences, calculate the mean (average) length of these sequences. The final answer must be the mean value rounded to the nearest integer, returned in the format <answer>int</answer>.

**Steps**
1) For each UniProt ID in the input list, make an API call to UniProt (e.g., https://www.uniprot.org/uniprot/{ID}.fasta) to get its FASTA sequence.
2) Use Biopython's SeqIO to parse each retrieved sequence and get its length.
3) Store all lengths in a Python list.
4) Calculate the sum of the lengths and divide by the number of sequences to get the mean.
5) Use Python's round() function to round the mean to the nearest integer.
6) Return the result.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

['P00533', 'P04626', 'P21860', 'Q15303', 'P08581']
