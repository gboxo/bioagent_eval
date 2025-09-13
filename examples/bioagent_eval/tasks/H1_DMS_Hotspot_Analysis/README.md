**Task**
Analyze a Deep Mutational Scanning (DMS) dataset from a CSV file. You need to identify 'hotspot' positions that are sensitive to mutation. First, normalize the DMS scores using Z-score standardization (subtract mean, divide by standard deviation). A position is a hotspot if more than 50% of the mutations at that position have Z-scores below -1.0 (indicating significantly reduced fitness). From these hotspots, find the top 10 that have the lowest average Z-score. Return these 10 positions as a comma-separated string of integers, sorted from lowest average Z-score to highest. Format: <answer>str</answer>.

**Steps**
1) Load the specified CSV file into a pandas DataFrame.
2) Calculate Z-score normalization for the DMS_score column: Z = (score - mean) / standard_deviation.
3) Extract position numbers from the 'mutant' column and add as a 'position' column.
4) Group the DataFrame by the 'position' column.
5) For each position group, calculate two things: the mean Z-score, and the fraction of rows where Z-score is less than -1.0.
6) Filter these aggregated results to keep only the positions where the calculated fraction is greater than 0.5.
7) Sort the filtered DataFrame by the mean Z-score in ascending order.
8) Select the top 10 rows.
9) Extract the 'position' values, convert them to integers, and join them into a single comma-separated string.
10) Return the string.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

ProteinGym_DMS:B2L11_HUMAN_Dutta_2010_binding-Mcl-1
