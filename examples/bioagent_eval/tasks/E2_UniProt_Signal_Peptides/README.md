**Task**
Retrieve a specific protein entry from the UniProt database using its accession ID. From the entry's feature annotations, you must identify all features explicitly labeled as 'Signal peptide'. Calculate the length of each signal peptide and sum them to get a total length. Return this sum as an integer in the format <answer>int</answer>. If no signal peptides are found, the answer should be 0.

**Steps**
1) Use the requests library to query the UniProt REST API for the given ID (e.g., https://rest.uniprot.org/uniprotkb/{ID}.json).
2) Parse the resulting JSON data.
3) Navigate to the 'features' key.
4) Iterate through the list of features, filtering for entries where the 'type' is 'Signal peptide'.
5) For each matching feature, calculate its length by subtracting 'location.start.value' from 'location.end.value' and adding 1.
6) Sum the lengths of all found signal peptides.
7) Return the total.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

P04637
