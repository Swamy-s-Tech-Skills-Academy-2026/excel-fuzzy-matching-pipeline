"""
Fuzzy matching engine for finding best matches between source and reference data.
"""
import pandas as pd
import logging
from typing import Dict, List
from .scorer import NumericAwareScorer

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """Performs fuzzy matching between source and reference datasets."""
    
    def __init__(self, threshold: float = 70.0, amount_tolerance: float = 5.0, 
                 exact_match_bonus: float = 20.0):
        """
        Initialize the fuzzy matcher.
        
        Args:
            threshold: Minimum score threshold for accepting a match
            amount_tolerance: Percentage tolerance for numeric matching
            exact_match_bonus: Bonus points for exact numeric match
        """
        self.threshold = threshold
        self.scorer = NumericAwareScorer(amount_tolerance, exact_match_bonus)
        self.audit_records = []
    
    def find_best_match(self, source_desc: str, source_amount: float, 
                       reference_df: pd.DataFrame) -> Dict:
        """
        Find the best matching reference entry for a source entry.
        
        Args:
            source_desc: Source description
            source_amount: Source amount
            reference_df: DataFrame with reference descriptions and codes
            
        Returns:
            Dictionary with match results and details
        """
        best_score = 0
        best_match = None
        best_details = None
        
        # Iterate through all reference entries
        for idx, row in reference_df.iterrows():
            ref_desc = row['Description']
            ref_code = row['Code']
            
            # Calculate score with details
            score, details = self.scorer.calculate_final_score(
                source_desc, source_amount, ref_desc
            )
            
            # Track best match
            if score > best_score:
                best_score = score
                best_match = {
                    'Description': ref_desc,
                    'Code': ref_code
                }
                best_details = details
        
        # Return result only if above threshold
        if best_score >= self.threshold and best_match:
            return {
                'matched': True,
                'code': best_match['Code'],
                'matched_description': best_match['Description'],
                'score': best_score,
                'details': best_details
            }
        else:
            return {
                'matched': False,
                'code': 'NO_MATCH',
                'matched_description': '',
                'score': best_score,
                'details': best_details if best_details else {
                    'text_score': 0,
                    'numeric_consistent': False,
                    'numeric_score': 0,
                    'final_score': 0,
                    'match_type': 'No Match',
                    'explanation': 'No match found above threshold'
                }
            }
    
    def match_datasets(self, source_df: pd.DataFrame, 
                      reference_df: pd.DataFrame) -> pd.DataFrame:
        """
        Match all entries from source dataset to reference dataset.
        
        Args:
            source_df: DataFrame with source descriptions and amounts
            reference_df: DataFrame with reference descriptions and codes
            
        Returns:
            DataFrame with matched results
        """
        logger.info(f"Starting fuzzy matching for {len(source_df)} source entries "
                   f"against {len(reference_df)} reference entries")
        
        results = []
        self.audit_records = []
        
        for idx, source_row in source_df.iterrows():
            source_desc = source_row['Description']
            source_amount = source_row['Amount']
            
            # Find best match
            match_result = self.find_best_match(source_desc, source_amount, reference_df)
            
            # Prepare result record
            result = {
                'Description': source_desc,
                'Amount': source_amount,
                'Matched_Code': match_result['code'],
                'Match_Score': round(match_result['score'], 2),
                'Match_Type': match_result['details']['match_type']
            }
            results.append(result)
            
            # Prepare audit record
            audit_record = {
                'Source_Description': source_desc,
                'Source_Amount': source_amount,
                'Matched_Description': match_result['matched_description'],
                'Matched_Code': match_result['code'],
                'Text_Match_Score': round(match_result['details']['text_score'], 2),
                'Numeric_Match': match_result['details']['numeric_consistent'],
                'Final_Score': round(match_result['details']['final_score'], 2),
                'Match_Type': match_result['details']['match_type'],
                'Explanation': match_result['details']['explanation']
            }
            self.audit_records.append(audit_record)
            
            if (idx + 1) % 10 == 0:
                logger.info(f"Processed {idx + 1}/{len(source_df)} entries")
        
        logger.info(f"Matching complete. {len(results)} entries processed.")
        
        return pd.DataFrame(results)
    
    def get_audit_log(self) -> pd.DataFrame:
        """
        Get the audit log with detailed matching information.
        
        Returns:
            DataFrame with audit records
        """
        return pd.DataFrame(self.audit_records)
