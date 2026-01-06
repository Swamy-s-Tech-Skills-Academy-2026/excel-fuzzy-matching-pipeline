#!/usr/bin/env python3
"""
Unit tests for ExcelDataLoader module.
"""
import unittest
import sys
import tempfile
import os
import logging
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Suppress logging during tests to reduce noise from expected errors
logging.getLogger('src.fuzzy_matcher.data_loader').setLevel(logging.CRITICAL)

# Suppress openpyxl deprecation warnings
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='openpyxl')

from src.fuzzy_matcher import ExcelDataLoader


class TestExcelDataLoader(unittest.TestCase):
    """Test cases for ExcelDataLoader."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_data.xlsx")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_excel(self, data, columns):
        """Helper to create test Excel file."""
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(self.test_file, index=False, engine='openpyxl')
        return self.test_file
    
    def test_load_source_data_success(self):
        """Test successful loading of source data."""
        data = {
            'Description': ['Office supplies', 'Software license', 'Marketing'],
            'Amount': [150.0, 299.99, 500.0]
        }
        self.create_test_excel(data, ['Description', 'Amount'])
        
        df = ExcelDataLoader.load_source_data(
            self.test_file, 'Description', 'Amount'
        )
        
        self.assertEqual(len(df), 3)
        self.assertIn('Description', df.columns)
        self.assertIn('Amount', df.columns)
        self.assertEqual(df.iloc[0]['Description'], 'Office supplies')
        self.assertEqual(df.iloc[0]['Amount'], 150.0)
    
    def test_load_source_data_cleans_whitespace(self):
        """Test that whitespace is trimmed from descriptions."""
        data = {
            'Description': ['  Office supplies  ', '  Software  ', 'Marketing'],
            'Amount': [150.0, 299.99, 500.0]
        }
        self.create_test_excel(data, ['Description', 'Amount'])
        
        df = ExcelDataLoader.load_source_data(
            self.test_file, 'Description', 'Amount'
        )
        
        self.assertEqual(df.iloc[0]['Description'], 'Office supplies')
        self.assertEqual(df.iloc[1]['Description'], 'Software')
    
    def test_load_source_data_removes_empty_descriptions(self):
        """Test that rows with empty descriptions are removed."""
        data = {
            'Description': ['Office supplies', '', '   ', 'Marketing'],
            'Amount': [150.0, 299.99, 500.0, 600.0]
        }
        self.create_test_excel(data, ['Description', 'Amount'])
        
        df = ExcelDataLoader.load_source_data(
            self.test_file, 'Description', 'Amount'
        )
        
        self.assertEqual(len(df), 2)  # Only 2 valid rows
        self.assertNotIn('', df['Description'].values)
    
    def test_load_source_data_handles_null_amounts(self):
        """Test that null amounts are converted to 0."""
        data = {
            'Description': ['Office supplies', 'Software license'],
            'Amount': [150.0, None]
        }
        self.create_test_excel(data, ['Description', 'Amount'])
        
        df = ExcelDataLoader.load_source_data(
            self.test_file, 'Description', 'Amount'
        )
        
        self.assertEqual(df.iloc[1]['Amount'], 0.0)
    
    def test_load_source_data_file_not_found(self):
        """Test error handling for missing file."""
        with self.assertRaises(FileNotFoundError):
            ExcelDataLoader.load_source_data(
                'nonexistent.xlsx', 'Description', 'Amount'
            )
    
    def test_load_source_data_missing_columns(self):
        """Test error handling for missing required columns."""
        data = {'Description': ['Office supplies'], 'Other': [150.0]}
        self.create_test_excel(data, ['Description', 'Other'])
        
        with self.assertRaises(ValueError) as context:
            ExcelDataLoader.load_source_data(
                self.test_file, 'Description', 'Amount'
            )
        
        self.assertIn('not found', str(context.exception))
    
    def test_load_reference_data_success(self):
        """Test successful loading of reference data."""
        data = {
            'Description': ['Office supplies', 'Software license'],
            'Code': ['SUPP-001', 'SOFT-002']
        }
        self.create_test_excel(data, ['Description', 'Code'])
        
        df = ExcelDataLoader.load_reference_data(
            self.test_file, 'Description', 'Code'
        )
        
        self.assertEqual(len(df), 2)
        self.assertIn('Description', df.columns)
        self.assertIn('Code', df.columns)
        self.assertEqual(df.iloc[0]['Code'], 'SUPP-001')
    
    def test_load_reference_data_removes_empty_codes(self):
        """Test that rows with empty codes are removed."""
        data = {
            'Description': ['Office supplies', 'Software license', 'Marketing'],
            'Code': ['SUPP-001', '', 'MRKT-003']
        }
        self.create_test_excel(data, ['Description', 'Code'])
        
        df = ExcelDataLoader.load_reference_data(
            self.test_file, 'Description', 'Code'
        )
        
        self.assertEqual(len(df), 2)  # Only 2 valid rows
        self.assertNotIn('', df['Code'].values)
    
    def test_load_reference_data_removes_empty_descriptions(self):
        """Test that rows with empty descriptions are removed."""
        data = {
            'Description': ['Office supplies', '', 'Marketing'],
            'Code': ['SUPP-001', 'SOFT-002', 'MRKT-003']
        }
        self.create_test_excel(data, ['Description', 'Code'])
        
        df = ExcelDataLoader.load_reference_data(
            self.test_file, 'Description', 'Code'
        )
        
        self.assertEqual(len(df), 2)  # Only 2 valid rows
    
    def test_load_reference_data_file_not_found(self):
        """Test error handling for missing reference file."""
        with self.assertRaises(FileNotFoundError):
            ExcelDataLoader.load_reference_data(
                'nonexistent.xlsx', 'Description', 'Code'
            )
    
    def test_load_reference_data_missing_columns(self):
        """Test error handling for missing required columns."""
        data = {'Description': ['Office supplies'], 'Other': ['SUPP-001']}
        self.create_test_excel(data, ['Description', 'Other'])
        
        with self.assertRaises(ValueError) as context:
            ExcelDataLoader.load_reference_data(
                self.test_file, 'Description', 'Code'
            )
        
        self.assertIn('not found', str(context.exception))


if __name__ == '__main__':
    unittest.main()

