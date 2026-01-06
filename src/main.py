#!/usr/bin/env python3
"""
Excel Fuzzy Matching Pipeline
Main entry point for the deterministic, numeric-aware fuzzy matching system.
"""
import sys
import logging
from pathlib import Path

# Add parent directory to path to access config and src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fuzzy_matcher import ExcelDataLoader, FuzzyMatcher, ExcelOutputWriter
from src.config import constants as config


def setup_logging():
    """Configure logging for the pipeline."""
    # Ensure log directory exists
    log_dir = Path(__file__).parent.parent / 'data' / 'output'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'pipeline.log'
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(str(log_file))
        ]
    )


def main():
    """Main pipeline execution."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("="*70)
        logger.info("Excel Fuzzy Matching Pipeline - Starting")
        logger.info("="*70)
        
        # Step 1: Load source data (Description + Amount)
        logger.info("\n[Step 1/5] Loading source data...")
        source_df = ExcelDataLoader.load_source_data(
            config.INPUT_FILE_1,
            config.SOURCE_DESC_COL,
            config.SOURCE_AMOUNT_COL
        )
        logger.info(f"[OK] Loaded {len(source_df)} source records")
        
        # Step 2: Load reference data (Description + Code)
        logger.info("\n[Step 2/5] Loading reference data...")
        reference_df = ExcelDataLoader.load_reference_data(
            config.INPUT_FILE_2,
            config.REF_DESC_COL,
            config.REF_CODE_COL
        )
        logger.info(f"[OK] Loaded {len(reference_df)} reference records")
        
        # Step 3: Perform fuzzy matching
        logger.info("\n[Step 3/5] Performing fuzzy matching...")
        matcher = FuzzyMatcher(
            threshold=config.FUZZY_THRESHOLD,
            amount_tolerance=config.AMOUNT_TOLERANCE_PERCENT,
            exact_match_bonus=config.EXACT_MATCH_BONUS
        )
        results_df = matcher.match_datasets(source_df, reference_df)
        logger.info(f"[OK] Matched {len(results_df)} records")
        
        # Step 4: Save results
        logger.info("\n[Step 4/5] Saving results...")
        ExcelOutputWriter.save_results(results_df, config.OUTPUT_FILE)
        logger.info(f"[OK] Results saved to: {config.OUTPUT_FILE}")
        
        # Step 5: Generate audit log
        logger.info("\n[Step 5/5] Generating audit log...")
        audit_df = matcher.get_audit_log()
        ExcelOutputWriter.save_audit_log(audit_df, config.AUDIT_LOG_FILE)
        logger.info(f"[OK] Audit log saved to: {config.AUDIT_LOG_FILE}")
        
        # Generate and display summary report
        logger.info("\n" + "="*70)
        logger.info("GENERATING SUMMARY REPORT")
        logger.info("="*70)
        summary = ExcelOutputWriter.generate_summary_report(results_df, audit_df)
        print(summary)
        logger.info(summary)
        
        logger.info("\n" + "="*70)
        logger.info("Pipeline completed successfully!")
        logger.info("="*70)
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"\n[ERROR] File not found: {str(e)}")
        logger.error("Please ensure input files exist in the correct location.")
        return 1
        
    except Exception as e:
        logger.error(f"\n[ERROR] Pipeline failed with error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    setup_logging()
    sys.exit(main())
