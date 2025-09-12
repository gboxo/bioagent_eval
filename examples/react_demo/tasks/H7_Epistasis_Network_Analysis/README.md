**Task**
Analyze a combinatorial mutagenesis dataset (CSV) to find epistatic interactions. First, establish the fitness effects of all single mutations. Then, for each double mutant, calculate the expected fitness assuming a multiplicative model (fitness_expected = fitness_A * fitness_B). Epistasis is the absolute difference between observed and expected fitness. Identify the double mutant with the highest epistatic score. Return the mutation names for this pair as a string (e.g., 'A123G-V456C'). Format: <answer>str</answer>.

**Steps**
1) Load the CSV file using pandas. Assume it contains 'mutant' and 'fitness' columns.
2) Filter the DataFrame to create a dictionary mapping single mutants to their fitness scores.
3) Filter the DataFrame to get all double mutants and their observed fitness.
4) Initialize variables to track the max epistasis and the corresponding mutant name.
5) Iterate through the double mutants. For each one, parse its name to get the two single mutations.
6) Look up the fitness of each single mutation from the dictionary.
7) Calculate expected fitness and the epistasis value.
8) If this value is greater than the current max, update the max and the mutant name.
9) Return the name of the double mutant with the highest epistasis.

**Variant**
We don't need to download the data, the data is already in variant_1 folder

ProteinGym_Epistasis:GFP_SF9_Sarkisyan_2016
