#!/usr/bin/env python3
"""
Simple test script to validate the fuzzy matching pipeline components.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fuzzy_matcher import NumericAwareScorer


def test_numeric_extraction():
    """Test number extraction from text."""
    print("Testing numeric extraction...")
    scorer = NumericAwareScorer()
    
    test_cases = [
        ("Office supplies 150.00", [150.0]),
        ("Marketing campaign Q1 500", [1.0, 500.0]),
        ("No numbers here", []),
        ("Multiple 10 numbers 20.5 here 30", [10.0, 20.5, 30.0]),
    ]
    
    for text, expected in test_cases:
        result = scorer.extract_numbers(text)
        assert result == expected, f"Failed for '{text}': expected {expected}, got {result}"
        print(f"  ✓ '{text}' -> {result}")
    
    print("✅ All numeric extraction tests passed!\n")


def test_numeric_consistency():
    """Test numeric consistency checking."""
    print("Testing numeric consistency...")
    scorer = NumericAwareScorer(amount_tolerance_percent=5.0, exact_match_bonus=20.0)
    
    # Test exact match
    is_consistent, score, explanation = scorer.check_numeric_consistency(
        150.0, "Office supplies 150"
    )
    assert is_consistent == True
    assert score == 20.0
    print(f"  ✓ Exact match: {explanation} (score: {score})")
    
    # Test within tolerance
    is_consistent, score, explanation = scorer.check_numeric_consistency(
        152.0, "Office supplies 150"
    )
    assert is_consistent == True
    print(f"  ✓ Within tolerance: {explanation} (score: {score:.2f})")
    
    # Test numeric mismatch
    is_consistent, score, explanation = scorer.check_numeric_consistency(
        200.0, "Office supplies 150"
    )
    assert is_consistent == False
    assert score == -50.0
    print(f"  ✓ Mismatch: {explanation} (score: {score})")
    
    # Test no numbers
    is_consistent, score, explanation = scorer.check_numeric_consistency(
        100.0, "Office supplies only"
    )
    assert is_consistent == True
    assert score == 0.0
    print(f"  ✓ No numbers: {explanation} (score: {score})")
    
    print("✅ All numeric consistency tests passed!\n")


def test_text_similarity():
    """Test text similarity calculation."""
    print("Testing text similarity...")
    scorer = NumericAwareScorer()
    
    # Similar texts
    score = scorer.calculate_text_similarity(
        "Office supplies purchase",
        "Office supplies and stationery"
    )
    assert score > 60, f"Expected high similarity, got {score}"
    print(f"  ✓ Similar texts: score = {score:.2f}")
    
    # Different texts
    score = scorer.calculate_text_similarity(
        "Office supplies",
        "Travel expenses"
    )
    assert score < 50, f"Expected low similarity, got {score}"
    print(f"  ✓ Different texts: score = {score:.2f}")
    
    print("✅ All text similarity tests passed!\n")


def test_final_score():
    """Test final score calculation."""
    print("Testing final score calculation...")
    scorer = NumericAwareScorer(amount_tolerance_percent=5.0, exact_match_bonus=20.0)
    
    # Good match with numeric consistency
    final_score, details = scorer.calculate_final_score(
        "Office supplies purchase 150.00",
        150.0,
        "Office supplies and stationery 150"
    )
    assert final_score >= 80, f"Expected high score, got {final_score}"
    assert details['numeric_consistent'] == True
    assert details['match_type'] in ['High Confidence', 'Medium Confidence']
    print(f"  ✓ Good match: score = {final_score:.2f}, type = {details['match_type']}")
    
    # Poor match due to numeric mismatch
    final_score, details = scorer.calculate_final_score(
        "Office supplies 200",
        200.0,
        "Office supplies 150"
    )
    assert details['numeric_consistent'] == False
    print(f"  ✓ Numeric mismatch: score = {final_score:.2f}, type = {details['match_type']}")
    
    print("✅ All final score tests passed!\n")


def main():
    """Run all tests."""
    print("="*70)
    print("FUZZY MATCHING PIPELINE - TEST SUITE")
    print("="*70)
    print()
    
    try:
        test_numeric_extraction()
        test_numeric_consistency()
        test_text_similarity()
        test_final_score()
        
        print("="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
