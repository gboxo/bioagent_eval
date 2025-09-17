**Task**
We are analyzing a Deep Mutational Scanning dataset from the file corresponding to `{dms_dataset}` to fit an additive model on the single point mutations to predict epistasis. First, normalize the DMS scores using Z-score standardization (subtract mean, divide by standard deviation). Then fit a additive model on the single point mutants, to predict the epistasis of the multi residue mutant entries. Please fit the model and compute the spearman correlation between the real fitness and the predicted fitness. Return the spearman correlation with 2 decimals. Format: `<answer>str</answer>`.

**Steps**

1) Load the specified CSV dataset from ProteinGym into a pandas DataFrame. 
2) Identify the fitness column, which is typically 'DMS_score'. On the entire dataset, normalize this column using Z-score standardization (subtract the mean and divide by the standard deviation) and store the results in a new column named 'normalized_score'. 
3) Separate the DataFrame into two parts: a 'singles' DataFrame containing only variants with exactly one mutation, and a 'multiples' DataFrame containing variants with two or more mutations. You can determine this by counting the occurrences of mutation delimiters (e.g., ':') in the 'mutant' column. 
4) Create the additive fitness model: build a Python dictionary that maps each single mutation string (from the 'mutant' column of the 'singles' DataFrame) to its 'normalized_score'. This dictionary represents the measured effect of each individual mutation. 
5) Generate predictions for the 'multiples' DataFrame. For each row, parse its 'mutant' string to get the list of its constituent single mutations. 
6) The predicted score for a multi-mutant is the sum of the 'normalized_score' values of its constituent single mutations, looked up from the model dictionary created in step 4. If a constituent single mutation is not found in the dictionary (i.e., it was not measured individually in the dataset), its effect should be assumed to be zero. 
7) Create two arrays: one containing the observed 'normalized_score' values from the 'multiples' DataFrame, and another containing the corresponding predicted scores. 
8) Use `scipy.stats.spearmanr` to calculate the Spearman correlation coefficient between the observed and predicted scores. 
9) Return the correlation coefficient as a float, rounded to three decimal places.",



**Variants**
We don't need to download the data, the data is already in the variant folders

**Variant 1:** A4_HUMAN_Seuma_2022
**Variant 2:** BBC1_YEAST_Tsuboyama_2023_1TG0  
**Variant 3:** CATR_CHLRE_Tsuboyama_2023_2AMI
**Variant 4:** CBPA2_HUMAN_Tsuboyama_2023_1O6X
**Variant 5:** CSN4_MOUSE_Tsuboyama_2023_1UFM



