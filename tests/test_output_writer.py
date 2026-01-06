#!/usr/bin/env python3
"""
Unit tests for ExcelOutputWriter module.
"""
import unittest
import sys
import tempfile
import os
import logging
import warnings
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Suppress logging during tests
logging.getLogger('src.fuzzy_matcher.output_writer').setLevel(logging.CRITICAL)

# Suppress openpyxl deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='openpyxl')

from src.fuzzy_matcher import ExcelOutputWriter


class TestExcelOutputWriter(unittest.TestCase):
    """Test cases for ExcelOutputWriter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_output_file = os.path.join(self.temp_dir, "test_output.xlsx")
        self.test_audit_file = os.path.join(self.temp_dir, "test_audit.xlsx")
        
        # Create test data
        self.results_df = pd.DataFrame({
            'Description': ['Office supplies', 'Software license'],
            'Amount': [150.0, 299.99],
            'Matched_Code': ['SUPP-001', 'SOFT-002'],
            'Match_Score': [95.0, 87.5],
            'Match_Type': ['High Confidence', 'Medium Confidence']
        })
        
        self.audit_df = pd.DataFrame({
            'Source_Description': ['Office supplies', 'Software license'],
            'Source_Amount': [150.0, 299.99],
            'Matched_Description': ['Office supplies 150', 'Software licensing'],
            'Matched_Code': ['SUPP-001', 'SOFT-002'],
            'Text_Match_Score': [85.0, 77.5],
            'Numeric_Match': [True, False],
            'Final_Score': [95.0, 87.5],
            'Match_Type': ['High Confidence', 'Medium Confidence'],
            'Explanation': ['Exact match', 'Good text match']
        })
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_ensure_output_directory(self):
        """Test that output directory is created."""
        nested_path = os.path.join(self.temp_dir, "nested", "path", "file.xlsx")
        ExcelOutputWriter.ensure_output_directory(nested_path)
        
        self.assertTrue(os.path.exists(os.path.dirname(nested_path)))
    
    def test_save_results_success(self):
        """Test successful saving of results."""
        ExcelOutputWriter.save_results(self.results_df, self.test_output_file)
        
        self.assertTrue(os.path.exists(self.test_output_file))
        
        # Verify file can be read back
        df_read = pd.read_excel(self.test_output_file, engine='openpyxl')
        self.assertEqual(len(df_read), 2)
        self.assertIn('Description', df_read.columns)
        self.assertIn('Matched_Code', df_read.columns)
    
    def test_save_results_creates_directory(self):
        """Test that save_results creates directory if needed."""
        nested_file = os.path.join(self.temp_dir, "nested", "results.xlsx")
        ExcelOutputWriter.save_results(self.results_df, nested_file)
        
        self.assertTrue(os.path.exists(nested_file))
    
    def test_save_audit_log_success(self):
        """Test successful saving of audit log."""
        ExcelOutputWriter.save_audit_log(self.audit_df, self.test_audit_file)
        
        self.assertTrue(os.path.exists(self.test_audit_file))
        
        # Verify file can be read back
        df_read = pd.read_excel(self.test_audit_file, sheet_name='Audit Log', engine='openpyxl')
        self.assertEqual(len(df_read), 2)
        self.assertIn('Source_Description', df_read.columns)
        self.assertIn('Explanation', df_read.columns)
    
    def test_save_audit_log_creates_directory(self):
        """Test that save_audit_log creates directory if needed."""
        nested_file = os.path.join(self.temp_dir, "nested", "audit.xlsx")
        ExcelOutputWriter.save_audit_log(self.audit_df, nested_file)
        
        self.assertTrue(os.path.exists(nested_file))
    
    def test_generate_summary_report(self):
        """Test summary report generation."""
        report = ExcelOutputWriter.generate_summary_report(self.results_df, self.audit_df)
        
        self.assertIsInstance(report, str)
        self.assertIn('SUMMARY REPORT', report)
        self.assertIn('Total Records Processed', report)
        self.assertIn('Successfully Matched', report)
        self.assertIn('Average Match Score', report)
    
    def test_generate_summary_report_statistics(self):
        """Test that summary report contains correct statistics."""
        report = ExcelOutputWriter.generate_summary_report(self.results_df, self.audit_df)
        
        # Should show 2 total records
        self.assertIn('2', report)
        # Should show match statistics
        self.assertIn('Matched', report)
    
    def test_generate_summary_report_with_no_matches(self):
        """Test summary report with no matches."""
        no_match_df = pd.DataFrame({
            'Description': ['Unknown item'],
            'Amount': [100.0],
            'Matched_Code': ['NO_MATCH'],
            'Match_Score': [45.0],
            'Match_Type': ['Poor Match']
        })
        
        no_match_audit = pd.DataFrame({
            'Source_Description': ['Unknown item'],
            'Source_Amount': [100.0],
            'Matched_Description': [''],
            'Matched_Code': ['NO_MATCH'],
            'Text_Match_Score': [45.0],
            'Numeric_Match': [False],
            'Final_Score': [45.0],
            'Match_Type': ['Poor Match'],
            'Explanation': ['No match found']
        })
        
        report = ExcelOutputWriter.generate_summary_report(no_match_df, no_match_audit)
        
        self.assertIn('No Match Found', report)
        self.assertIn('0', report)  # 0 matches
    
    def test_generate_summary_report_empty_dataframes(self):
        """Test summary report with empty DataFrames."""
        empty_df = pd.DataFrame(columns=['Description', 'Amount', 'Matched_Code', 'Match_Score', 'Match_Type'])
        empty_audit = pd.DataFrame(columns=['Source_Description', 'Numeric_Match', 'Final_Score'])
        
        report = ExcelOutputWriter.generate_summary_report(empty_df, empty_audit)
        
        self.assertIsInstance(report, str)
        self.assertIn('0', report)  # Should show 0 records


if __name__ == '__main__':
    unittest.main()

