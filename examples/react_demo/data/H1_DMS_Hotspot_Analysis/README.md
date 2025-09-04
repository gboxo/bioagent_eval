**Task**
    Analyze a Deep Mutational Scanning (DMS) dataset from a CSV file. You need to identify 'hotspot' positions that are sensitive to mutation. A position is a hotspot if more than 50% of the mutations at that position result in a greater than 3-fold loss of fitness (fitness score < 0.33). From these hotspots, find the top 10 that have the lowest average fitness score. Return these 10 positions as a comma-separated string of integers, sorted from lowest average fitness to highest. Format: <answer>str</answer>.

    **Steps**
    1) Load the specified CSV file into a pandas DataFrame.
2) Group the DataFrame by the 'position' column.
3) For each position group, calculate two things: the mean of the 'fitness' column, and the fraction of rows where 'fitness' is less than 0.33.
4) Filter these aggregated results to keep only the positions where the calculated fraction is greater than 0.5.
5) Sort the filtered DataFrame by the mean fitness in ascending order.
6) Select the top 10 rows.
7) Extract the 'position' values, convert them to integers, and join them into a single comma-separated string.
8) Return the string.

    **Variant**
    We don't need to download the data, the data is already in variant_1 folder

    ProteinGym_DMS:UBE4B_MOUSE_Starr_2021
