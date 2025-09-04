**Task**
    For a given UniProt ID, retrieve its Gene Ontology (GO) annotations. You need to count how many of these annotations belong to the 'Molecular Function' ontology. Return the count as an integer in the format <answer>int</answer>.

    **Steps**
    1) Query the UniProt API for the protein's JSON data.
2) Navigate to the 'dbReferences' key.
3) Filter this list for entries where the 'type' is 'GO'.
4) For each GO entry, access its 'properties' and check the 'GoTerm' value. The ontology is indicated by the first letter (P, F, or C).
5) Count how many of these terms start with 'F:' (for Molecular Function).
6) Return the final count.

    **Variant**
    We don't need to download the data, the data is already in variant_1 folder

    P62158
