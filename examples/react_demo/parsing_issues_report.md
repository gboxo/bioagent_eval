# Task Results Parsing Issues Report

## Summary
Analysis of `task_results.json` identified **3 tasks** with parsing issues out of 25 total tasks:

- **22 tasks (88%)** ✅ - Properly formatted with clean variant/result pairs
- **3 tasks (12%)** ❌ - Have structural or formatting issues

## Tasks with Issues

### 1. H10_variant_Structural_Mapping
**Issues:**
- Empty results.csv file (only header)
- This caused the CSV parser to create malformed entries with debug output instead of actual results

**Root Cause:** The results.csv file is empty, containing only the header row.

### 2. H8_Druggability_Assessment  
**Issues:**
- Multi-line verbose output stored as individual CSV rows
- Each line of debug output became a separate JSON entry
- Only the first line of each variant's output has the variant number
- Subsequent lines have text in the "variant" field instead of numbers

**Root Cause:** The analysis script output verbose logging directly to the CSV instead of just the final result.

**Example problematic rows:**
```csv
variant,result
1,Processing 1UBQ...
  Found 4 pockets, highest druggability score: 0.535
  Druggability score: 0.535
Processing 1HTM...
```

### 3. H5_Functional_Site_Conservation
**Issues:**
- Multiple values per result stored in separate columns
- CSV has extra unnamed columns that became "null" fields in JSON
- Inconsistent structure compared to other tasks

**Root Cause:** Results with multiple values were split across multiple CSV columns instead of being stored as a single comma-separated string.

**Example problematic row:**
```csv
variant,result,,
3,94,96,119
```

## Impact Assessment

### Data Integrity
- **Working properly:** 22/25 tasks (88%)
- **Partially usable:** 1/25 tasks (H5 - data exists but needs cleaning)
- **Unusable:** 2/25 tasks (H8, H10 - require source data fixes)

### JSON Structure Issues
- **241 total entries** across all tasks
- **~150+ malformed entries** from H8 and H10
- **~90 entries** with proper structure from the problematic tasks

## Recommendations

### Immediate Fixes Needed
1. **H10_variant_Structural_Mapping**: Re-run analysis to populate results.csv
2. **H8_Druggability_Assessment**: Extract only final results (e.g., "1A3N", "3PBL") from verbose output
3. **H5_Functional_Site_Conservation**: Combine multiple values into single comma-separated strings

### Script Improvements
1. Add validation to skip empty CSV files
2. Add option to extract only final results from verbose outputs
3. Handle multi-column CSV data properly
4. Add data quality checks before JSON conversion

### Data Quality Standards
For future CSV files:
- Only store final results, not debug output
- Use single result column with comma-separated values for multiple results
- Ensure all files have data beyond just headers
- Validate CSV structure before processing

## Expected Clean Structure
Each task should have exactly 5 entries (variants 1-5) with this structure:
```json
{
  "task_name": [
    {"variant": 1, "result": "value1"},
    {"variant": 2, "result": "value2"},
    {"variant": 3, "result": "value3"},
    {"variant": 4, "result": "value4"},
    {"variant": 5, "result": "value5"}
  ]
}
```