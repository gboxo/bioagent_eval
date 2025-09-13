**Task**
For a given UniProt entry, count the number of 'Fibronectin type-III' domains. You will need to retrieve the protein's annotations and parse its features to find all domain regions, then filter them by description. Return the final count as an integer in the format <answer>int</answer>.

**Steps**
1) Fetch the protein's data in JSON format from the UniProt API.
2) Parse the JSON and locate the 'features' list.
3) Iterate through the features.
4) Filter for features where 'type' is 'Domain'.
5) For these domain features, check if the 'description' field contains the string 'Fibronectin type-III'.
6) Maintain a counter for matching domains.
7) Return the final count.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

P06213
