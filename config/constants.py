"""
Configuration constants for Excel Fuzzy Matching Pipeline.
"""
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# File paths (relative to project root)
INPUT_FILE_1 = str(PROJECT_ROOT / "data" / "input" / "source_descriptions_amounts.xlsx")
INPUT_FILE_2 = str(PROJECT_ROOT / "data" / "input" / "reference_descriptions_codes.xlsx")
OUTPUT_FILE = str(PROJECT_ROOT / "data" / "output" / "matched_results.xlsx")
AUDIT_LOG_FILE = str(PROJECT_ROOT / "data" / "output" / "audit_log.xlsx")

# Matching parameters
FUZZY_THRESHOLD = 70  # Minimum fuzzy match score (0-100)
AMOUNT_TOLERANCE_PERCENT = 5  # Percentage tolerance for numeric matching
EXACT_MATCH_BONUS = 20  # Bonus points for exact numeric match

# Column names for input files
# File 1: Description and Amount
SOURCE_DESC_COL = "Description"
SOURCE_AMOUNT_COL = "Amount"

# File 2: Description and Code
REF_DESC_COL = "Description"
REF_CODE_COL = "Code"

# Output column names
OUTPUT_DESC_COL = "Description"
OUTPUT_AMOUNT_COL = "Amount"
OUTPUT_CODE_COL = "Matched_Code"
OUTPUT_SCORE_COL = "Match_Score"
OUTPUT_MATCH_TYPE_COL = "Match_Type"

# Audit log columns
AUDIT_SOURCE_DESC = "Source_Description"
AUDIT_SOURCE_AMOUNT = "Source_Amount"
AUDIT_MATCHED_DESC = "Matched_Description"
AUDIT_MATCHED_CODE = "Matched_Code"
AUDIT_TEXT_SCORE = "Text_Match_Score"
AUDIT_NUMERIC_MATCH = "Numeric_Match"
AUDIT_FINAL_SCORE = "Final_Score"
AUDIT_MATCH_TYPE = "Match_Type"
AUDIT_EXPLANATION = "Explanation"

# Logging
LOG_LEVEL = "INFO"
