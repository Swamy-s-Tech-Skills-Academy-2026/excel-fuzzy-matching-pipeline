# Usage Guide: Excel Fuzzy Matching Pipeline

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Swamy-s-Tech-Skills-Academy-2026/excel-fuzzy-matching-pipeline.git
cd excel-fuzzy-matching-pipeline

## Creating the Virtual environment
uv venv

# Install dependencies
# Using uv (recommended - faster)
uv pip install -r requirements.txt

# Or using traditional pip
pip install -r requirements.txt
```

### 2. Prepare Your Data

Create two Excel files in `data/input/`:

**File 1: source_descriptions_amounts.xlsx**

```
| Description                          | Amount   |
|--------------------------------------|----------|
| Office supplies purchase             | 150.00   |
| Software license renewal             | 299.99   |
```

**File 2: reference_descriptions_codes.xlsx**

```
| Description                              | Code      |
|------------------------------------------|-----------|
| Office supplies and stationery           | SUPP-001  |
| Software licensing fees                  | SOFT-002  |
```

### 3. Run the Pipeline

```bash
cd src
python main.py
```

### 4. Check Results

Find your outputs in `data/output/`:

- **matched_results.xlsx** - Final mappings with scores
- **audit_log.xlsx** - Detailed explanations for each match
- **pipeline.log** - Execution log

## Customization

### Adjusting Match Sensitivity

Edit `config/constants.py`:

```python
# Lower threshold = more matches (less strict)
FUZZY_THRESHOLD = 60

# Higher threshold = fewer matches (more strict)
FUZZY_THRESHOLD = 85
```

### Adjusting Numeric Tolerance

```python
# More lenient numeric matching
AMOUNT_TOLERANCE_PERCENT = 10

# Stricter numeric matching
AMOUNT_TOLERANCE_PERCENT = 2
```

### Custom Column Names

If your Excel files use different column names:

```python
# Source file columns
SOURCE_DESC_COL = "Transaction Description"
SOURCE_AMOUNT_COL = "Transaction Amount"

# Reference file columns
REF_DESC_COL = "Item Description"
REF_CODE_COL = "GL Code"
```

## Understanding the Output

### Matched Results File

| Column | Description |
|--------|-------------|
| Description | Original description from source file |
| Amount | Original amount from source file |
| Matched_Code | Assigned code from reference file (NO_MATCH if below threshold) |
| Match_Score | Final matching score (0-100) |
| Match_Type | Quality classification (High/Medium/Low Confidence, Poor Match, No Match) |

### Audit Log File

| Column | Description |
|--------|-------------|
| Source_Description | Original source description |
| Source_Amount | Original source amount |
| Matched_Description | Best matching reference description |
| Matched_Code | Assigned code |
| Text_Match_Score | Text similarity score (0-100) |
| Numeric_Match | Whether numeric consistency was satisfied |
| Final_Score | Combined score after numeric adjustment |
| Match_Type | Quality classification |
| Explanation | Human-readable reason for the match decision |

## Match Quality Levels

- **High Confidence (90-100)**: Very strong match, both text and numbers align well
- **Medium Confidence (70-89)**: Good match, acceptable for most use cases
- **Low Confidence (50-69)**: Weak match, may need manual review
- **Poor Match (<50)**: Very poor match, below threshold but shown for reference
- **No Match**: Score below FUZZY_THRESHOLD, code assigned as "NO_MATCH"

## Examples

### Example 1: Perfect Match with Numeric Consistency

**Source:** "Office supplies 150"  
**Reference:** "Office supplies and stationery 150"  
**Amount:** 150.00

- Text Score: ~75%
- Numeric Bonus: +20 (exact match)
- Final Score: 95%
- Result: **High Confidence** → Matched

### Example 2: Good Text Match but Numeric Mismatch

**Source:** "Office supplies 200"  
**Reference:** "Office supplies and stationery 150"  
**Amount:** 200.00

- Text Score: ~75%
- Numeric Penalty: -50 (mismatch)
- Final Score: 25%
- Result: **Poor Match** → NO_MATCH

### Example 3: Moderate Text Match with No Numbers

**Source:** "Employee training"  
**Reference:** "Employee development and training"  
**Amount:** 450.00

- Text Score: ~72%
- Numeric Bonus: 0 (no numbers in reference)
- Final Score: 72%
- Result: **Medium Confidence** → Matched

## Troubleshooting

### Issue: All matches are NO_MATCH

**Solution:** Lower the `FUZZY_THRESHOLD` in `config/constants.py`

### Issue: Too many false matches

**Solution:** Increase the `FUZZY_THRESHOLD` or decrease `AMOUNT_TOLERANCE_PERCENT`

### Issue: Numbers not being recognized

**Solution:** Check that amounts are in numeric format in Excel, not text

### Issue: File not found error

**Solution:** Ensure your Excel files are in `data/input/` with exact names specified in config

## Testing

Run the test suite to verify the installation:

```bash
cd tests
python test_scorer.py
```

## Advanced Usage

### Programmatic Integration

```python
from src.fuzzy_matcher import ExcelDataLoader, FuzzyMatcher

# Load data
source_df = ExcelDataLoader.load_source_data(
    "path/to/source.xlsx", "Description", "Amount"
)
reference_df = ExcelDataLoader.load_reference_data(
    "path/to/reference.xlsx", "Description", "Code"
)

# Create matcher
matcher = FuzzyMatcher(threshold=70, amount_tolerance=5, exact_match_bonus=20)

# Perform matching
results_df = matcher.match_datasets(source_df, reference_df)
audit_df = matcher.get_audit_log()

# Access results
print(results_df)
print(audit_df)
```

### Batch Processing

Process multiple file pairs:

```python
file_pairs = [
    ("january.xlsx", "ref_january.xlsx"),
    ("february.xlsx", "ref_february.xlsx"),
]

for source_file, ref_file in file_pairs:
    # Load and process each pair
    # ...
```

## Best Practices

1. **Data Quality**: Clean your source data before processing
   - Remove empty rows
   - Standardize amount formats
   - Fix obvious typos

2. **Threshold Tuning**: Start with default threshold (70) and adjust based on results

3. **Manual Review**: Always review Low Confidence matches manually

4. **Audit Trail**: Keep audit logs for compliance and debugging

5. **Iterative Refinement**: Use audit logs to identify patterns and improve reference data

## Support

For issues or questions:

- Check the [main README](../README.md)
- Review audit logs for specific match explanations
- Open an issue on GitHub
