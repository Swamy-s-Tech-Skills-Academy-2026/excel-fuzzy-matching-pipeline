"""
Output writer module for saving results to Excel files.
"""
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ExcelOutputWriter:
    """Handles writing results to Excel files."""
    
    @staticmethod
    def ensure_output_directory(filepath: str) -> None:
        """
        Ensure the output directory exists.
        
        Args:
            filepath: Path to the output file
        """
        output_dir = Path(filepath).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ensured: {output_dir}")
    
    @staticmethod
    def save_results(df: pd.DataFrame, filepath: str) -> None:
        """
        Save matched results to Excel file.
        
        Args:
            df: DataFrame with matched results
            filepath: Path to save the Excel file
        """
        try:
            ExcelOutputWriter.ensure_output_directory(filepath)
            
            # Save to Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            logger.info(f"Results saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving results to {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def save_audit_log(df: pd.DataFrame, filepath: str) -> None:
        """
        Save audit log with detailed matching information to Excel file.
        
        Args:
            df: DataFrame with audit records
            filepath: Path to save the Excel file
        """
        try:
            ExcelOutputWriter.ensure_output_directory(filepath)
            
            # Create Excel writer with formatting
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Audit Log', index=False)
                
                # Get the worksheet
                worksheet = writer.sheets['Audit Log']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except (AttributeError, TypeError):
                            # Skip cells with None or non-string values
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Audit log saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving audit log to {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def generate_summary_report(results_df: pd.DataFrame, audit_df: pd.DataFrame) -> str:
        """
        Generate a text summary report of the matching results.
        
        Args:
            results_df: DataFrame with matched results
            audit_df: DataFrame with audit records
            
        Returns:
            String containing the summary report
        """
        total_records = len(results_df)
        matched_records = len(results_df[results_df['Matched_Code'] != 'NO_MATCH'])
        no_match_records = total_records - matched_records
        
        # Handle division by zero for empty DataFrames
        if total_records == 0:
            matched_pct = 0.0
            no_match_pct = 0.0
        else:
            matched_pct = matched_records/total_records*100
            no_match_pct = no_match_records/total_records*100
        
        # Match type breakdown
        match_type_counts = results_df['Match_Type'].value_counts() if total_records > 0 else {}
        
        # Average score for matched records
        matched_df = results_df[results_df['Matched_Code'] != 'NO_MATCH']
        avg_score = matched_df['Match_Score'].mean() if len(matched_df) > 0 else 0
        
        # Numeric consistency stats
        numeric_match_count = audit_df['Numeric_Match'].sum() if len(audit_df) > 0 else 0
        numeric_match_pct = numeric_match_count/total_records*100 if total_records > 0 else 0.0
        
        report = f"""
======================================================================
         EXCEL FUZZY MATCHING PIPELINE - SUMMARY REPORT          
======================================================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

MATCHING STATISTICS
----------------------------------------------------------------------
Total Records Processed:       {total_records:>6}
Successfully Matched:          {matched_records:>6} ({matched_pct:.1f}%)
No Match Found:                {no_match_records:>6} ({no_match_pct:.1f}%)

MATCH QUALITY BREAKDOWN
----------------------------------------------------------------------
"""
        for match_type, count in match_type_counts.items():
            match_pct = count/total_records*100 if total_records > 0 else 0.0
            report += f"{match_type:.<30} {count:>6} ({match_pct:.1f}%)\n"
        
        report += f"""
SCORING METRICS
----------------------------------------------------------------------
Average Match Score:           {avg_score:>6.2f}
Numeric Consistency Matches:   {numeric_match_count:>6} ({numeric_match_pct:.1f}%)

OUTPUT FILES
----------------------------------------------------------------------
[OK] Matched results saved
[OK] Audit log with detailed explanations saved

======================================================================
"""
        
        return report
