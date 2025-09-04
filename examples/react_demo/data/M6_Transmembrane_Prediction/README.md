**Task**
    Given a list of UniProt IDs for membrane proteins, you must predict the transmembrane topology for each one. Using a tool that implements the TMHMM algorithm, count the number of transmembrane helices predicted for each protein. Return the UniProt ID of the protein with the highest number of predicted helices, in the format <answer>str</answer>.

    **Steps**
    1) Fetch the FASTA sequence for each UniProt ID.
2) Use a Python library such as `pytmhmm` which provides an interface to the TMHMM prediction model.
3) For each sequence, call the prediction function (e.g., `pytmhmm.predict`).
4) Parse the annotation string returned by the tool to count the number of regions labeled as transmembrane helices (often denoted by 'i' for inside, 'M' for membrane, 'o' for outside). Count the distinct 'M' segments.
5) Keep track of the UniProt ID with the highest helix count.
6) Return this UniProt ID.

    **Variant**
    We don't need to download the data, the data is already in variant_1 folder

    ['P35355', 'P35367', 'P35372', 'P41143', 'P41145', 'Q13639', 'Q96P88', 'Q9Y5N1']
