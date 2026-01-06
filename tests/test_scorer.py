#!/usr/bin/env python3
"""
Unit tests for NumericAwareScorer module.
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fuzzy_matcher import NumericAwareScorer


class TestNumericAwareScorer(unittest.TestCase):
    """Test cases for NumericAwareScorer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scorer = NumericAwareScorer(amount_tolerance_percent=5.0, exact_match_bonus=20.0)
    
    def test_extract_numbers_basic(self):
        """Test basic number extraction."""
        result = self.scorer.extract_numbers("Office supplies 150.00")
        self.assertEqual(result, [150.0])
    
    def test_extract_numbers_multiple(self):
        """Test extraction of multiple numbers."""
        result = self.scorer.extract_numbers("Marketing campaign Q1 500")
        self.assertIn(1.0, result)
        self.assertIn(500.0, result)
    
    def test_extract_numbers_none(self):
        """Test extraction when no numbers present."""
        result = self.scorer.extract_numbers("No numbers here")
        self.assertEqual(result, [])
    
    def test_extract_numbers_mixed(self):
        """Test extraction of mixed numbers."""
        result = self.scorer.extract_numbers("Multiple 10 numbers 20.5 here 30")
        expected = [10.0, 20.5, 30.0]
        self.assertEqual(result, expected)
    
    def test_check_numeric_consistency_exact_match(self):
        """Test numeric consistency with exact match."""
        is_consistent, score, explanation = self.scorer.check_numeric_consistency(
            150.0, "Office supplies 150"
        )
        self.assertTrue(is_consistent)
        self.assertEqual(score, 20.0)
        self.assertIn("Exact", explanation)
    
    def test_check_numeric_consistency_within_tolerance(self):
        """Test numeric consistency within tolerance."""
        is_consistent, score, explanation = self.scorer.check_numeric_consistency(
            152.0, "Office supplies 150"
        )
        self.assertTrue(is_consistent)
        self.assertGreater(score, 0)
        self.assertLess(score, 20.0)  # Partial bonus
    
    def test_check_numeric_consistency_mismatch(self):
        """Test numeric consistency with mismatch."""
        is_consistent, score, explanation = self.scorer.check_numeric_consistency(
            200.0, "Office supplies 150"
        )
        self.assertFalse(is_consistent)
        self.assertEqual(score, -50.0)
        self.assertIn("mismatch", explanation.lower())
    
    def test_check_numeric_consistency_no_numbers(self):
        """Test numeric consistency when no numbers in reference."""
        is_consistent, score, explanation = self.scorer.check_numeric_consistency(
            100.0, "Office supplies only"
        )
        self.assertTrue(is_consistent)  # Neutral - no numbers to compare
        self.assertEqual(score, 0.0)
    
    def test_calculate_text_similarity_high(self):
        """Test text similarity calculation for similar texts."""
        score = self.scorer.calculate_text_similarity(
            "Office supplies purchase",
            "Office supplies and stationery"
        )
        self.assertGreater(score, 60)
        self.assertLessEqual(score, 100)
    
    def test_calculate_text_similarity_low(self):
        """Test text similarity calculation for different texts."""
        score = self.scorer.calculate_text_similarity(
            "Office supplies",
            "Travel expenses"
        )
        self.assertLess(score, 50)
        self.assertGreaterEqual(score, 0)
    
    def test_calculate_final_score_good_match(self):
        """Test final score calculation for good match."""
        final_score, details = self.scorer.calculate_final_score(
            "Office supplies purchase 150.00",
            150.0,
            "Office supplies and stationery 150"
        )
        self.assertGreaterEqual(final_score, 80)
        self.assertTrue(details['numeric_consistent'])
        self.assertIn(details['match_type'], ['High Confidence', 'Medium Confidence'])
    
    def test_calculate_final_score_numeric_mismatch(self):
        """Test final score with numeric mismatch."""
        final_score, details = self.scorer.calculate_final_score(
            "Office supplies 200",
            200.0,
            "Office supplies 150"
        )
        self.assertFalse(details['numeric_consistent'])
        self.assertIn('explanation', details)
        self.assertIn('match_type', details)
    
    def test_calculate_final_score_details_structure(self):
        """Test that final score returns correct details structure."""
        final_score, details = self.scorer.calculate_final_score(
            "Test description",
            100.0,
            "Test reference"
        )
        
        required_keys = ['text_score', 'numeric_consistent', 'numeric_score', 
                        'final_score', 'match_type', 'explanation']
        for key in required_keys:
            self.assertIn(key, details)


if __name__ == '__main__':
    unittest.main()
