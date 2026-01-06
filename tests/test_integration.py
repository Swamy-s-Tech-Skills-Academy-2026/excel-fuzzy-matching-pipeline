#!/usr/bin/env python3
"""
Integration tests for the complete pipeline.
"""
import unittest
import sys
import tempfile
import os
import warnings
import logging
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Suppress openpyxl deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='openpyxl')

# Suppress logging during tests
logging.getLogger('src.fuzzy_matcher').setLevel(logging.CRITICAL)

from src.fuzzy_matcher import ExcelDataLoader, FuzzyMatcher, ExcelOutputWriter


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test Excel files
        self.source_file = os.path.join(self.temp_dir, "source.xlsx")
        self.reference_file = os.path.join(self.temp_dir, "reference.xlsx")
        self.output_file = os.path.join(self.temp_dir, "output.xlsx")
        self.audit_file = os.path.join(self.temp_dir, "audit.xlsx")
        
        # Create source data
        source_data = pd.DataFrame({
            'Description': [
                'Office supplies purchase 150.00',
                'Software license renewal',
                'Marketing campaign Q1 500',
                'Travel expenses',
                'Unknown transaction'
            ],
            'Amount': [150.0, 299.99, 500.0, 200.0, 100.0]
        })
        source_data.to_excel(self.source_file, index=False, engine='openpyxl')
        
        # Create reference data
        reference_data = pd.DataFrame({
            'Description': [
                'Office supplies and stationery 150',
                'Software licensing fees',
                'Marketing and advertising expenses 500',
                'Travel and accommodation',
                'Employee training'
            ],
            'Code': ['SUPP-001', 'SOFT-002', 'MRKT-004', 'TRAV-005', 'TRAIN-006']
        })
        reference_data.to_excel(self.reference_file, index=False, engine='openpyxl')
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_pipeline(self):
        """Test the complete pipeline from loading to output."""
        # Step 1: Load data
        source_df = ExcelDataLoader.load_source_data(
            self.source_file, 'Description', 'Amount'
        )
        reference_df = ExcelDataLoader.load_reference_data(
            self.reference_file, 'Description', 'Code'
        )
        
        self.assertGreater(len(source_df), 0)
        self.assertGreater(len(reference_df), 0)
        
        # Step 2: Perform matching
        matcher = FuzzyMatcher(threshold=70.0, amount_tolerance=5.0, exact_match_bonus=20.0)
        results_df = matcher.match_datasets(source_df, reference_df)
        
        self.assertEqual(len(results_df), len(source_df))
        self.assertIn('Matched_Code', results_df.columns)
        
        # Step 3: Get audit log
        audit_df = matcher.get_audit_log()
        self.assertEqual(len(audit_df), len(source_df))
        
        # Step 4: Save results
        ExcelOutputWriter.save_results(results_df, self.output_file)
        self.assertTrue(os.path.exists(self.output_file))
        
        # Step 5: Save audit log
        ExcelOutputWriter.save_audit_log(audit_df, self.audit_file)
        self.assertTrue(os.path.exists(self.audit_file))
        
        # Step 6: Generate summary
        summary = ExcelOutputWriter.generate_summary_report(results_df, audit_df)
        self.assertIsInstance(summary, str)
        self.assertIn('SUMMARY REPORT', summary)
    
    def test_pipeline_with_matches(self):
        """Test pipeline ensures some matches are found."""
        source_df = ExcelDataLoader.load_source_data(
            self.source_file, 'Description', 'Amount'
        )
        reference_df = ExcelDataLoader.load_reference_data(
            self.reference_file, 'Description', 'Code'
        )
        
        matcher = FuzzyMatcher(threshold=50.0)  # Low threshold to ensure matches
        results_df = matcher.match_datasets(source_df, reference_df)
        
        # Should have at least some matches
        matched_count = len(results_df[results_df['Matched_Code'] != 'NO_MATCH'])
        self.assertGreater(matched_count, 0, "Should have at least one match")
    
    def test_pipeline_audit_log_consistency(self):
        """Test that audit log matches results."""
        source_df = ExcelDataLoader.load_source_data(
            self.source_file, 'Description', 'Amount'
        )
        reference_df = ExcelDataLoader.load_reference_data(
            self.reference_file, 'Description', 'Code'
        )
        
        matcher = FuzzyMatcher(threshold=70.0)
        results_df = matcher.match_datasets(source_df, reference_df)
        audit_df = matcher.get_audit_log()
        
        # Audit log should have same number of records
        self.assertEqual(len(results_df), len(audit_df))
        
        # Codes should match
        for idx in range(len(results_df)):
            self.assertEqual(
                results_df.iloc[idx]['Matched_Code'],
                audit_df.iloc[idx]['Matched_Code']
            )


if __name__ == '__main__':
    unittest.main()

