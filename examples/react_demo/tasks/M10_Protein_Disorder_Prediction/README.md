**Task**
You are given a list of UniProt IDs for transcription factors. For each protein, predict the amount of intrinsic disorder. Use the IUPred3 web service to get per-residue disorder scores. A residue is considered disordered if its score is > 0.5. Calculate the percentage of disordered residues for each protein. Return the UniProt ID of the protein with the highest percentage of disorder, in the format <answer>str</answer>.

**Steps**
1) For each UniProt ID, fetch its FASTA sequence.
2) Submit each sequence to the IUPred3 REST API.
3) Parse the JSON response to get the list of per-residue disorder scores.
4) For each protein, count the number of residues with a score greater than 0.5.
5) Calculate the percentage of disordered residues (disordered_count / total_length * 100).
6) Keep track of the UniProt ID with the highest calculated percentage.
7) Return the UniProt ID with the highest disorder percentage.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

['P04637', 'P03070', 'Q01094', 'P10275', 'P01112', 'P01116']
