**Task**
You are given a human gene name. Using the Ensembl database, find all known protein-coding transcripts for this gene. Your task is to identify which of these transcripts contains the highest number of exons. Return this maximum exon count as an integer in the format <answer>int</answer>.

**Steps**
1) Use the Ensembl 'lookup/symbol' REST API endpoint to find the Ensembl Gene ID for the given gene name.
2) Using this ID, query the 'lookup/id' endpoint with the `expand=1` parameter to retrieve all information about the gene, including its transcripts and exons.
3) Initialize a variable `max_exons` to 0.
4) Parse the JSON response and iterate through the list of transcripts ('Transcript' key).
5) For each transcript, get the number of exons by finding the length of its 'Exon' list.
6) If this count is greater than `max_exons`, update `max_exons`.
7) After checking all transcripts, return the final `max_exons` value.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

BRCA1
