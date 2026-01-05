"""
Data loader module for reading Excel files.
"""
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ExcelDataLoader:
    """Handles loading data from Excel files."""
    
    @staticmethod
    def load_source_data(filepath: str, desc_col: str, amount_col: str) -> pd.DataFrame:
        """
        Load source data with descriptions and amounts.
        
        Args:
            filepath: Path to the Excel file
            desc_col: Name of the description column
            amount_col: Name of the amount column
            
        Returns:
            DataFrame with Description and Amount columns
        """
        try:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"Source file not found: {filepath}")
            
            df = pd.read_excel(filepath)
            logger.info(f"Loaded {len(df)} rows from source file: {filepath}")
            
            # Validate required columns
            if desc_col not in df.columns or amount_col not in df.columns:
                raise ValueError(f"Required columns {desc_col} and/or {amount_col} not found in {filepath}")
            
            # Select and rename columns
            df = df[[desc_col, amount_col]].copy()
            df.columns = ['Description', 'Amount']
            
            # Clean data
            df['Description'] = df['Description'].fillna('').astype(str).str.strip()
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            
            # Remove rows with empty descriptions
            df = df[df['Description'] != ''].reset_index(drop=True)
            
            logger.info(f"Cleaned data: {len(df)} valid rows")
            return df
            
        except Exception as e:
            logger.error(f"Error loading source data from {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def load_reference_data(filepath: str, desc_col: str, code_col: str) -> pd.DataFrame:
        """
        Load reference data with descriptions and codes.
        
        Args:
            filepath: Path to the Excel file
            desc_col: Name of the description column
            code_col: Name of the code column
            
        Returns:
            DataFrame with Description and Code columns
        """
        try:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"Reference file not found: {filepath}")
            
            df = pd.read_excel(filepath)
            logger.info(f"Loaded {len(df)} rows from reference file: {filepath}")
            
            # Validate required columns
            if desc_col not in df.columns or code_col not in df.columns:
                raise ValueError(f"Required columns {desc_col} and/or {code_col} not found in {filepath}")
            
            # Select and rename columns
            df = df[[desc_col, code_col]].copy()
            df.columns = ['Description', 'Code']
            
            # Clean data
            df['Description'] = df['Description'].fillna('').astype(str).str.strip()
            df['Code'] = df['Code'].fillna('').astype(str).str.strip()
            
            # Remove rows with empty descriptions or codes
            df = df[(df['Description'] != '') & (df['Code'] != '')].reset_index(drop=True)
            
            logger.info(f"Cleaned reference data: {len(df)} valid rows")
            return df
            
        except Exception as e:
            logger.error(f"Error loading reference data from {filepath}: {str(e)}")
            raise
