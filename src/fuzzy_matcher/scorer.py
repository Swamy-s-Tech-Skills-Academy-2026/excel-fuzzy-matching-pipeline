"""
Custom scoring logic for numeric-aware fuzzy matching.
"""
import re
import logging
from typing import Tuple, List
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


class NumericAwareScorer:
    """Handles custom scoring with numeric consistency enforcement."""
    
    def __init__(self, amount_tolerance_percent: float = 5.0, exact_match_bonus: float = 20.0):
        """
        Initialize the numeric-aware scorer.
        
        Args:
            amount_tolerance_percent: Percentage tolerance for numeric matching
            exact_match_bonus: Bonus points for exact numeric match
        """
        self.amount_tolerance_percent = amount_tolerance_percent
        self.exact_match_bonus = exact_match_bonus
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """
        Extract all numbers from a text string.
        
        Args:
            text: Input text
            
        Returns:
            List of numbers found in the text
        """
        # Pattern to match numbers (including decimals and negatives)
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        numbers = [float(m) for m in matches if m and m != '-']
        return numbers
    
    def check_numeric_consistency(self, source_amount: float, ref_description: str) -> Tuple[bool, float, str]:
        """
        Check if the source amount is consistent with numbers in reference description.
        
        Args:
            source_amount: Amount from source data
            ref_description: Description from reference data
            
        Returns:
            Tuple of (is_consistent, match_score, explanation)
        """
        # Extract numbers from reference description
        ref_numbers = self.extract_numbers(ref_description)
        
        if not ref_numbers:
            # No numbers in reference description - neutral match
            return True, 0.0, "No numbers in reference description"
        
        # Check if source amount matches any number in reference description
        tolerance = abs(source_amount * self.amount_tolerance_percent / 100)
        
        for ref_num in ref_numbers:
            diff = abs(source_amount - ref_num)
            
            # Exact match
            if diff == 0:
                return True, self.exact_match_bonus, f"Exact numeric match: {source_amount}"
            
            # Within tolerance
            if diff <= tolerance:
                match_score = self.exact_match_bonus * (1 - diff / tolerance) if tolerance > 0 else 0
                return True, match_score, f"Numeric match within {self.amount_tolerance_percent}% tolerance"
        
        # No matching numbers found
        return False, -50.0, f"Numeric mismatch: {source_amount} not found in {ref_numbers}"
    
    def calculate_text_similarity(self, source_desc: str, ref_desc: str) -> float:
        """
        Calculate text similarity score between two descriptions.
        
        Args:
            source_desc: Source description
            ref_desc: Reference description
            
        Returns:
            Similarity score (0-100)
        """
        # Use token_sort_ratio for better handling of word order variations
        score = fuzz.token_sort_ratio(source_desc, ref_desc)
        return float(score)
    
    def calculate_final_score(self, source_desc: str, source_amount: float, 
                             ref_desc: str) -> Tuple[float, dict]:
        """
        Calculate final matching score combining text similarity and numeric consistency.
        
        Args:
            source_desc: Source description
            source_amount: Source amount
            ref_desc: Reference description
            
        Returns:
            Tuple of (final_score, details_dict)
        """
        # Calculate text similarity
        text_score = self.calculate_text_similarity(source_desc, ref_desc)
        
        # Check numeric consistency
        is_consistent, numeric_score, explanation = self.check_numeric_consistency(
            source_amount, ref_desc
        )
        
        # Calculate final score
        # If numeric consistency fails, heavily penalize the score
        if not is_consistent:
            final_score = max(0, text_score + numeric_score)
        else:
            final_score = min(100, text_score + numeric_score)
        
        # Determine match type
        if final_score >= 90:
            match_type = "High Confidence"
        elif final_score >= 70:
            match_type = "Medium Confidence"
        elif final_score >= 50:
            match_type = "Low Confidence"
        else:
            match_type = "Poor Match"
        
        details = {
            'text_score': text_score,
            'numeric_consistent': is_consistent,
            'numeric_score': numeric_score,
            'final_score': final_score,
            'match_type': match_type,
            'explanation': explanation
        }
        
        return final_score, details
