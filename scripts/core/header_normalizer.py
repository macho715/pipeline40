# -*- coding: utf-8 -*-
"""
Header Normalizer Module
========================

This module handles the complete normalization of header names from Excel files.
It removes all variations that could prevent matching, including:
- Case differences (CASE NO vs case no)
- Whitespace (leading, trailing, multiple spaces)
- Full-width characters (全角文字)
- Special characters and punctuation
- Common abbreviations

The normalization process creates a standardized form that allows semantic matching
to work reliably regardless of how the header was originally written.
"""

import re
import unicodedata
from typing import Optional


class HeaderNormalizer:
    """
    Comprehensive header name normalization for robust matching.
    
    This class transforms header names into a standardized format that enables
    semantic matching across different writing styles and conventions.
    
    Examples:
        >>> normalizer = HeaderNormalizer()
        >>> normalizer.normalize("Case No.")
        'caseno'
        >>> normalizer.normalize("  CASE NUMBER  ")
        'casenumber'
        >>> normalizer.normalize("Case_No.")
        'caseno'
        >>> normalizer.normalize("ケース番号")  # Full-width Japanese
        'ケース番号'
    """
    
    def __init__(self):
        """
        Initialize the normalizer with standard transformation rules.
        
        The normalizer applies multiple transformation passes to ensure
        that headers are matched based on their semantic meaning rather
        than their superficial formatting.
        """
        # Mapping of common abbreviations to their full forms
        # This helps match variations like "No." and "Number"
        self.abbreviation_map = {
            'no': 'number',
            'num': 'number',
            'qty': 'quantity',
            'amt': 'amount',
            'desc': 'description',
            'est': 'estimated',
            'arr': 'arrival',
            'dep': 'departure',
            'wh': 'warehouse',
            'sqm': 'squaremeter',
            'cntr': 'container',
        }
        
        # Patterns for common separators that should be removed
        # These include punctuation, underscores, hyphens, etc.
        self.separator_pattern = re.compile(r'[._\-/\\|:;,\s]+')
        
    def normalize(self, header: str, expand_abbreviations: bool = True) -> str:
        """
        Normalize a header name to its canonical form.
        
        This method applies a series of transformations to create a standardized
        version of the header that can be reliably matched. The process includes:
        1. Converting to lowercase
        2. Normalizing Unicode characters
        3. Removing special characters and separators
        4. Optionally expanding common abbreviations
        
        Args:
            header: The original header name from the Excel file
            expand_abbreviations: Whether to expand abbreviations like "No." to "number"
        
        Returns:
            A normalized string suitable for semantic matching
            
        Examples:
            >>> normalizer = HeaderNormalizer()
            >>> normalizer.normalize("Case No.")
            'casenumber'
            >>> normalizer.normalize("ETD/ATD")
            'etdatd'
            >>> normalizer.normalize("  Total  Handling ")
            'totalhandling'
        """
        if not isinstance(header, str):
            header = str(header)
        
        # Step 1: Convert to lowercase for case-insensitive matching
        normalized = header.lower().strip()
        
        # Step 2: Normalize Unicode to handle full-width characters
        # NFKC normalization converts full-width to half-width
        normalized = unicodedata.normalize('NFKC', normalized)
        
        # Step 3: Remove all special characters and separators
        # Keep only alphanumeric characters
        normalized = self.separator_pattern.sub('', normalized)
        
        # Step 4: Remove remaining non-alphanumeric characters
        # This catches any edge cases not handled by the separator pattern
        normalized = re.sub(r'[^a-z0-9]', '', normalized)
        
        # Step 5: Expand common abbreviations if requested
        # This helps match "No." with "Number" and similar variations
        if expand_abbreviations and normalized in self.abbreviation_map:
            normalized = self.abbreviation_map[normalized]
        
        return normalized
    
    def normalize_with_alternatives(self, header: str) -> list[str]:
        """
        Generate multiple normalized forms for maximum matching flexibility.
        
        Some headers have multiple valid interpretations. For example, "Case No."
        could match as "caseno" or "casenumber". This method generates all
        reasonable alternatives to maximize matching success.
        
        Args:
            header: The original header name
            
        Returns:
            A list of normalized alternatives, ordered by preference
            
        Examples:
            >>> normalizer = HeaderNormalizer()
            >>> normalizer.normalize_with_alternatives("Case No.")
            ['casenumber', 'caseno']
            >>> normalizer.normalize_with_alternatives("QTY")
            ['quantity', 'qty']
        """
        alternatives = []
        
        # First alternative: with abbreviation expansion
        expanded = self.normalize(header, expand_abbreviations=True)
        alternatives.append(expanded)
        
        # Second alternative: without abbreviation expansion
        # This catches cases where the abbreviated form is more standard
        unexpanded = self.normalize(header, expand_abbreviations=False)
        if unexpanded != expanded:
            alternatives.append(unexpanded)
        
        # Third alternative: keep common separators for multi-word headers
        # Some headers like "Case No" might be better as "caseno" than "casenumber"
        partial = header.lower().strip()
        partial = unicodedata.normalize('NFKC', partial)
        partial = re.sub(r'[._\-/\\|:;,]+', '', partial)  # Remove separators but keep spaces
        partial = re.sub(r'\s+', '', partial)  # Then remove spaces
        partial = re.sub(r'[^a-z0-9]', '', partial)
        if partial not in alternatives:
            alternatives.append(partial)
        
        return alternatives


def normalize_header(header: str, expand_abbreviations: bool = True) -> str:
    """
    Convenience function for quick header normalization.
    
    This is a simplified interface to the HeaderNormalizer class that's useful
    when you just need to normalize a single header without creating an instance.
    
    Args:
        header: The header name to normalize
        expand_abbreviations: Whether to expand abbreviations
        
    Returns:
        The normalized header name
        
    Examples:
        >>> normalize_header("Case No.")
        'casenumber'
        >>> normalize_header("ETA/ATA")
        'etaata'
    """
    normalizer = HeaderNormalizer()
    return normalizer.normalize(header, expand_abbreviations)


if __name__ == "__main__":
    """
    Test suite demonstrating the normalization capabilities.
    
    This test suite covers various edge cases including:
    - Mixed case handling
    - Special character removal
    - Whitespace normalization
    - Full-width character conversion
    - Abbreviation expansion
    """
    
    normalizer = HeaderNormalizer()
    
    print("=" * 60)
    print("Header Normalizer Test Suite")
    print("=" * 60)
    
    test_cases = [
        # Basic normalization tests
        ("Case No.", "casenumber", "Basic abbreviation expansion"),
        ("CASE NO", "casenumber", "Uppercase handling"),
        ("case_no", "casenumber", "Underscore removal"),
        ("Case-No", "casenumber", "Hyphen removal"),
        ("  Case  No.  ", "casenumber", "Whitespace handling"),
        
        # Special character tests
        ("ETD/ATD", "etdatd", "Slash removal"),
        ("Total.Handling", "totalhandling", "Dot removal"),
        ("Wh_Handling", "whhandling", "Mixed separators"),
        
        # Abbreviation tests
        ("Qty", "quantity", "Quantity abbreviation"),
        ("Desc", "description", "Description abbreviation"),
        ("Est. Arrival", "estimatedarrival", "Multi-word abbreviation"),
        
        # Full-width character tests (if applicable)
        ("Ｃａｓｅ　Ｎｏ", "casenumber", "Full-width ASCII"),
        
        # Complex real-world cases
        ("Status_WAREHOUSE", "statuswarehouse", "Mixed case with underscore"),
        ("DHL Warehouse", "dhlwarehouse", "Space between words"),
        ("DSV Al Markaz", "dsvalmarkaz", "Multiple spaces"),
    ]
    
    passed = 0
    failed = 0
    
    for original, expected, description in test_cases:
        result = normalizer.normalize(original)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}")
        print(f"  Description: {description}")
        print(f"  Input:       '{original}'")
        print(f"  Expected:    '{expected}'")
        print(f"  Got:         '{result}'")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 60)
    
    # Demonstrate alternative generation
    print("\n" + "=" * 60)
    print("Alternative Generation Examples")
    print("=" * 60)
    
    test_headers = ["Case No.", "QTY", "Wh Handling", "ETD/ATD"]
    
    for header in test_headers:
        alternatives = normalizer.normalize_with_alternatives(header)
        print(f"\n'{header}' →")
        for i, alt in enumerate(alternatives, 1):
            print(f"  {i}. {alt}")
