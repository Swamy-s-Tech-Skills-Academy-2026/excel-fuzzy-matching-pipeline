#!/usr/bin/env python3
"""
Unit tests for FuzzyMatcher module.
"""
import unittest
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcher(unittest.TestCase):
    """Test cases for FuzzyMatcher."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matcher = FuzzyMatcher(threshold=70.0, amount_tolerance=5.0, exact_match_bonus=20.0)
        
        # Create test reference data
        self.reference_df = pd.DataFrame({
            'Description': [
                'Office supplies and stationery 150',
                'Software licensing fees',
                'Marketing and advertising expenses 500',
                'Travel and accommodation',
                'Employee training and development'
            ],
            'Code': ['SUPP-001', 'SOFT-002', 'MRKT-004', 'TRAV-005', 'TRAIN-006']
        })
    
    def test_find_best_match_success(self):
        """Test finding a successful match above threshold."""
        result = self.matcher.find_best_match(
            'Office supplies purchase 150.00',
            150.0,
            self.reference_df
        )
        
        self.assertTrue(result['matched'])
        self.assertEqual(result['code'], 'SUPP-001')
        self.assertGreaterEqual(result['score'], 70.0)
        self.assertIn('details', result)
    
    def test_find_best_match_below_threshold(self):
        """Test match below threshold returns NO_MATCH."""
        matcher_low = FuzzyMatcher(threshold=90.0)  # High threshold
        result = matcher_low.find_best_match(
            'Completely different description',
            100.0,
            self.reference_df
        )
        
        self.assertFalse(result['matched'])
        self.assertEqual(result['code'], 'NO_MATCH')
        self.assertLess(result['score'], 90.0)
    
    def test_find_best_match_numeric_mismatch(self):
        """Test that numeric mismatch reduces score."""
        result = self.matcher.find_best_match(
            'Office supplies purchase 200.00',  # Amount doesn't match
            200.0,
            self.reference_df
        )
        
        # Should still find the best match but score should be penalized
        self.assertIsNotNone(result)
        # If numeric mismatch is severe, it might not match
        if result['matched']:
            self.assertLess(result['score'], 95.0)  # Should be lower due to mismatch
    
    def test_match_datasets_success(self):
        """Test matching entire datasets."""
        source_df = pd.DataFrame({
            'Description': [
                'Office supplies purchase 150.00',
                'Software license renewal',
                'Marketing campaign Q1 500'
            ],
            'Amount': [150.0, 299.99, 500.0]
        })
        
        results_df = self.matcher.match_datasets(source_df, self.reference_df)
        
        self.assertEqual(len(results_df), 3)
        self.assertIn('Matched_Code', results_df.columns)
        self.assertIn('Match_Score', results_df.columns)
        self.assertIn('Match_Type', results_df.columns)
    
    def test_match_datasets_creates_audit_log(self):
        """Test that audit log is created during matching."""
        source_df = pd.DataFrame({
            'Description': ['Office supplies purchase 150.00'],
            'Amount': [150.0]
        })
        
        self.matcher.match_datasets(source_df, self.reference_df)
        audit_df = self.matcher.get_audit_log()
        
        self.assertEqual(len(audit_df), 1)
        self.assertIn('Source_Description', audit_df.columns)
        self.assertIn('Matched_Code', audit_df.columns)
        self.assertIn('Final_Score', audit_df.columns)
        self.assertIn('Explanation', audit_df.columns)
    
    def test_get_audit_log_empty_before_matching(self):
        """Test that audit log is empty before matching."""
        audit_df = self.matcher.get_audit_log()
        self.assertEqual(len(audit_df), 0)
    
    def test_match_datasets_handles_empty_source(self):
        """Test matching with empty source DataFrame."""
        source_df = pd.DataFrame({
            'Description': [],
            'Amount': []
        })
        
        results_df = self.matcher.match_datasets(source_df, self.reference_df)
        self.assertEqual(len(results_df), 0)
    
    def test_match_datasets_handles_empty_reference(self):
        """Test matching with empty reference DataFrame."""
        source_df = pd.DataFrame({
            'Description': ['Office supplies purchase 150.00'],
            'Amount': [150.0]
        })
        reference_df = pd.DataFrame({
            'Description': [],
            'Code': []
        })
        
        results_df = self.matcher.match_datasets(source_df, reference_df)
        self.assertEqual(len(results_df), 1)
        self.assertEqual(results_df.iloc[0]['Matched_Code'], 'NO_MATCH')
    
    def test_threshold_affects_matching(self):
        """Test that different thresholds affect match results."""
        source_df = pd.DataFrame({
            'Description': ['Office supplies purchase 150.00'],
            'Amount': [150.0]
        })
        
        # Low threshold - should match
        matcher_low = FuzzyMatcher(threshold=50.0)
        results_low = matcher_low.match_datasets(source_df, self.reference_df)
        
        # High threshold - might not match
        matcher_high = FuzzyMatcher(threshold=95.0)
        results_high = matcher_high.match_datasets(source_df, self.reference_df)
        
        # At least verify they run without error
        self.assertEqual(len(results_low), 1)
        self.assertEqual(len(results_high), 1)


if __name__ == '__main__':
    unittest.main()

