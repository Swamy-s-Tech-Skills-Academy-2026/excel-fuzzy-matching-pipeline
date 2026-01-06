# Excel Fuzzy Matching Pipeline

End-to-end Excel automation pipeline for deterministic, numeric-aware fuzzy matching between descriptions and amounts. Handles numeric-sensitive matching using custom scoring logic, generates auditable Code–Amount mappings, and produces explainable outputs with detailed matching logs.

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Output Files](#output-files)
- [Example](#example)

## Problem Statement

Organizations often need to match financial transactions from one system (containing descriptions and amounts) with reference data from another system (containing descriptions and codes). Manual matching is:

- **Time-consuming**: Hundreds or thousands of records to match
- **Error-prone**: Human mistakes in matching similar descriptions
- **Inconsistent**: Different people may match differently
- **Not auditable**: No clear explanation for why matches were made

The challenge is compounded when:
- Descriptions use different wording for the same concept
- Numeric values must be consistent between matched pairs
- A deterministic, explainable process is required for compliance

## Solution Overview

This pipeline provides a **deterministic, numeric-aware fuzzy matching system** that:

1. **Loads two Excel files**:
   - Source file: Contains `Description` and `Amount` columns
   - Reference file: Contains `Description` and `Code` columns

2. **Performs intelligent matching**:
   - Uses RapidFuzz for fuzzy text matching
   - Enforces numeric consistency (amounts must match numbers in descriptions)
   - Applies custom scoring that penalizes numeric mismatches
   - Generates Code–Amount mappings

3. **Produces auditable outputs**:
   - Matched results Excel file with codes and scores
   - Detailed audit log explaining each match decision
   - Summary report with statistics

## Features

✅ **Numeric-Aware Matching**: Enforces consistency between amounts and numbers in descriptions  
✅ **Deterministic**: Same inputs always produce same outputs  
✅ **Configurable**: Adjust thresholds, tolerances, and scoring via configuration  
✅ **Explainable**: Every match includes detailed explanation in audit log  
✅ **Production-Ready**: Clean code structure, logging, error handling  
✅ **Zero Manual Work**: Fully automated pipeline from Excel to Excel  

## Project Structure

```
excel-fuzzy-matching-pipeline/
├── src/
│   ├── fuzzy_matcher/
│   │   ├── __init__.py
│   │   ├── data_loader.py      # Excel data loading
│   │   ├── scorer.py            # Numeric-aware scoring logic
│   │   ├── matcher.py           # Fuzzy matching engine
│   │   └── output_writer.py    # Excel output generation
│   └── main.py                  # Pipeline orchestrator
├── config/
│   ├── __init__.py
│   └── constants.py             # Configuration constants
├── data/
│   ├── input/                   # Input Excel files
│   │   ├── source_descriptions_amounts.xlsx
│   │   └── reference_descriptions_codes.xlsx
│   └── output/                  # Generated output files
│       ├── matched_results.xlsx
│       ├── audit_log.xlsx
│       └── pipeline.log
├── tests/                       # Test files (if needed)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Swamy-s-Tech-Skills-Academy-2026/excel-fuzzy-matching-pipeline.git
cd excel-fuzzy-matching-pipeline
```

2. **Install dependencies**:
```bash
# Using uv (recommended - faster)
uv pip install -r requirements.txt

# Or using traditional pip
pip install -r requirements.txt
```

Required packages:
- `pandas==2.1.4` - Data manipulation and Excel I/O
- `openpyxl==3.1.2` - Excel file handling
- `rapidfuzz==3.6.1` - Fast fuzzy string matching

## Usage

### Basic Usage

1. **Prepare your input files** in `data/input/`:
   - `source_descriptions_amounts.xlsx` - File with Description and Amount columns
   - `reference_descriptions_codes.xlsx` - File with Description and Code columns

2. **Run the pipeline**:
```bash
cd src
python main.py
```

3. **Check outputs** in `data/output/`:
   - `matched_results.xlsx` - Matched records with codes
   - `audit_log.xlsx` - Detailed matching explanations
   - `pipeline.log` - Execution log

### Using Sample Data

Sample data is included for testing. Just run:
```bash
cd src
python main.py
```

The pipeline will process the sample files and generate outputs.

## Configuration

Edit `config/constants.py` to customize behavior:

```python
# Matching thresholds
FUZZY_THRESHOLD = 70              # Minimum score to accept match (0-100)
AMOUNT_TOLERANCE_PERCENT = 5      # % tolerance for numeric matching
EXACT_MATCH_BONUS = 20            # Bonus points for exact numeric match

# File paths
INPUT_FILE_1 = "data/input/source_descriptions_amounts.xlsx"
INPUT_FILE_2 = "data/input/reference_descriptions_codes.xlsx"
OUTPUT_FILE = "data/output/matched_results.xlsx"
AUDIT_LOG_FILE = "data/output/audit_log.xlsx"

# Column names (customize for your Excel files)
SOURCE_DESC_COL = "Description"
SOURCE_AMOUNT_COL = "Amount"
REF_DESC_COL = "Description"
REF_CODE_COL = "Code"
```

## How It Works

### 1. Data Loading
- Reads Excel files using pandas
- Validates required columns exist
- Cleans and normalizes data (removes empty rows, trims whitespace)

### 2. Fuzzy Matching Process

For each source record:

a. **Text Similarity Calculation**:
   - Uses RapidFuzz's `token_sort_ratio` algorithm
   - Handles word order variations
   - Produces score 0-100

b. **Numeric Consistency Check**:
   - Extracts all numbers from reference description
   - Checks if source amount matches any extracted number
   - Applies tolerance (default 5%)
   - Awards bonus points for exact matches
   - Heavily penalizes numeric mismatches

c. **Final Score Calculation**:
   ```
   If numeric_consistent:
       final_score = text_score + numeric_bonus
   Else:
       final_score = text_score - 50  (heavy penalty)
   ```

d. **Match Decision**:
   - Accepts match if `final_score >= threshold`
   - Assigns corresponding code
   - Records detailed explanation

### 3. Output Generation

**Matched Results** (`matched_results.xlsx`):
| Description | Amount | Matched_Code | Match_Score | Match_Type |
|-------------|--------|--------------|-------------|------------|
| Office supplies... | 150.00 | SUPP-001 | 95.23 | High Confidence |

**Audit Log** (`audit_log.xlsx`):
| Source_Description | Source_Amount | Matched_Description | Matched_Code | Text_Match_Score | Numeric_Match | Final_Score | Match_Type | Explanation |
|-------------------|---------------|---------------------|--------------|------------------|---------------|-------------|------------|-------------|
| Office supplies... | 150.00 | Office supplies... 150 | SUPP-001 | 85.23 | True | 95.23 | High Confidence | Numeric match within 5% tolerance |

## Output Files

### 1. matched_results.xlsx
Contains the final mapping with:
- Original description and amount
- Matched code
- Match score (0-100)
- Match quality classification

### 2. audit_log.xlsx
Detailed explainability report with:
- Source and matched descriptions
- Text similarity score
- Numeric consistency flag
- Final combined score
- Plain English explanation of match decision

### 3. pipeline.log
Technical execution log for debugging

## Example

**Input Source File** (`source_descriptions_amounts.xlsx`):
```
| Description                          | Amount   |
|--------------------------------------|----------|
| Office supplies purchase 150.00      | 150.00   |
| Software license renewal             | 299.99   |
| Marketing campaign Q1 500            | 500.00   |
```

**Input Reference File** (`reference_descriptions_codes.xlsx`):
```
| Description                              | Code      |
|------------------------------------------|-----------|
| Office supplies and stationery 150       | SUPP-001  |
| Software licensing fees                  | SOFT-002  |
| Marketing and advertising expenses 500   | MRKT-004  |
```

**Output** (`matched_results.xlsx`):
```
| Description                          | Amount | Matched_Code | Match_Score | Match_Type        |
|--------------------------------------|--------|--------------|-------------|-------------------|
| Office supplies purchase 150.00      | 150.00 | SUPP-001     | 95.00       | High Confidence   |
| Software license renewal             | 299.99 | SOFT-002     | 87.50       | Medium Confidence |
| Marketing campaign Q1 500            | 500.00 | MRKT-004     | 98.00       | High Confidence   |
```

The numeric-aware scoring ensures that "Office supplies purchase 150.00" matches "Office supplies and stationery 150" with high confidence because:
1. Text similarity is high (~75%)
2. The amount 150.00 matches the number 150 in the reference description
3. Numeric consistency bonus boosts the final score to 95%

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub.
