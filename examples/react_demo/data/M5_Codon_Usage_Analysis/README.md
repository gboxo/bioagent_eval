**Task**
    You are given a list of 10 E. coli gene names. For each gene, you must find its coding sequence (CDS). Then, using a standard E. coli codon usage table as a reference, calculate the Codon Adaptation Index (CAI) for each gene. Return the name of the gene with the highest CAI value as a string in the format <answer>str</answer>.

    **Steps**
    1) Use Biopython's Entrez module to search the NCBI nucleotide database for each gene name (e.g., query: 'Escherichia coli[Orgn] AND {gene_name}[Gene]'). Fetch the CDS for each.
2) The `Bio.SeqUtils.CodonUsage` module contains pre-calculated codon usage indexes; use the one for E. coli.
3) Create an instance of `CodonAdaptationIndex`.
4) For each gene's CDS, calculate its CAI using the `cai_for_gene()` method.
5) Keep track of the gene name that corresponds to the highest calculated CAI.
6) Return the gene name with the highest score.

    **Variant**
    We don't need to download the data, the data is already in variant_1 folder

    ['dnaA', 'dnaN', 'recA', 'gyrB', 'rpoA', 'rpoB', 'rpoC', 'rpsL', 'rpsG', 'fusA']
