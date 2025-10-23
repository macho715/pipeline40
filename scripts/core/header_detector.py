# -*- coding: utf-8 -*-
"""
Header Detector Module
======================

This module automatically detects where header rows start in Excel files.
Excel files often have various structures:
- Title rows at the top
- Multiple blank rows before headers
- Headers that don't start in row 1
- Merged cells in title sections

The HeaderDetector analyzes the file structure and intelligently identifies
the row that contains the actual column headers.

Detection Strategy:
1. Look for rows with high text density (headers are usually all text)
2. Check for rows with many unique non-null values
3. Detect common header keywords (No, Name, Date, etc.)
4. Verify that subsequent rows contain data matching the header types
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List
from pathlib import Path
import re


class HeaderDetector:
    """
    Automatically detects the header row in Excel files.
    
    This class uses multiple heuristics to identify where the actual column
    headers are located, even when there are title rows, blank rows, or
    other non-data content at the top of the file.
    
    The detector works by analyzing:
    - Row density (headers have many non-null values)
    - Text patterns (headers contain descriptive text)
    - Value uniqueness (headers are unique, data may repeat)
    - Common keywords (headers often contain standard terms)
    
    Examples:
        >>> detector = HeaderDetector()
        >>> header_row, confidence = detector.detect_from_file("data.xlsx")
        >>> print(f"Headers found at row {header_row} with {confidence:.0%} confidence")
        Headers found at row 3 with 95% confidence
    """
    
    def __init__(self, max_search_rows: int = 20, min_confidence: float = 0.7):
        """
        Initialize the header detector with search parameters.
        
        Args:
            max_search_rows: Maximum number of rows to search for headers.
                Most Excel files have headers within the first 20 rows.
            min_confidence: Minimum confidence threshold (0-1) for header detection.
                Lower values may result in false positives.
        """
        self.max_search_rows = max_search_rows
        self.min_confidence = min_confidence
        
        # Common keywords found in headers
        # These words frequently appear in column headers across various domains
        self.header_keywords = [
            'no', 'number', 'name', 'date', 'time', 'status', 'type',
            'description', 'quantity', 'amount', 'total', 'case', 'id',
            'eta', 'etd', 'location', 'warehouse', 'site', 'handling',
            'storage', 'arrival', 'departure', 'current', 'container',
        ]
        
    def detect_from_file(
        self, 
        file_path: str, 
        sheet_name: Optional[str] = None
    ) -> Tuple[int, float]:
        """
        Detect the header row from an Excel file.
        
        This method reads the Excel file and analyzes its structure to determine
        where the column headers are located. It returns both the row number
        and a confidence score.
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Name of the sheet to analyze. If None, uses the first sheet.
            
        Returns:
            A tuple of (header_row_index, confidence_score)
            - header_row_index: 0-based row index where headers are found
            - confidence_score: Float between 0 and 1 indicating detection confidence
            
        Examples:
            >>> detector = HeaderDetector()
            >>> row, conf = detector.detect_from_file("invoices.xlsx")
            >>> print(f"Headers at row {row}, confidence: {conf:.2%}")
            Headers at row 2, confidence: 92%
        """
        # Read the first N rows of the file for analysis
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name or 0,
                header=None,  # Don't assume any row is the header yet
                nrows=self.max_search_rows
            )
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {e}")
        
        return self.detect_from_dataframe(df)
    
    def detect_from_dataframe(self, df: pd.DataFrame) -> Tuple[int, float]:
        """
        Detect the header row from a DataFrame.
        
        This is the core detection algorithm. It analyzes each row and assigns
        a score based on how likely that row is to be a header row.
        
        Args:
            df: DataFrame with header=None (raw data from Excel)
            
        Returns:
            A tuple of (header_row_index, confidence_score)
            
        Algorithm:
            For each potential header row, calculate:
            1. Density score: Percentage of non-null values
            2. Text score: Percentage of values that are text
            3. Uniqueness score: Percentage of unique values
            4. Keyword score: Presence of common header keywords
            5. Data validation score: Whether following rows look like data
            
            The row with the highest combined score is selected as the header.
        """
        if df.empty or len(df) == 0:
            return 0, 0.0
        
        scores = []
        
        for idx in range(min(len(df), self.max_search_rows)):
            row = df.iloc[idx]
            
            # Calculate multiple scoring factors
            density = self._calculate_density_score(row)
            text_ratio = self._calculate_text_score(row)
            uniqueness = self._calculate_uniqueness_score(row)
            keywords = self._calculate_keyword_score(row)
            
            # Validate that subsequent rows look like data
            data_validation = self._validate_data_rows(df, idx)
            
            # Combined weighted score
            # Density and text ratio are most important
            combined_score = (
                density * 0.30 +          # Headers have many filled cells
                text_ratio * 0.25 +       # Headers are usually text
                uniqueness * 0.20 +       # Headers are unique values
                keywords * 0.15 +         # Headers contain common keywords
                data_validation * 0.10    # Following rows should be data
            )
            
            scores.append((idx, combined_score))
        
        # Find the row with the highest score
        if not scores:
            return 0, 0.0
        
        best_row, best_score = max(scores, key=lambda x: x[1])
        
        return best_row, best_score
    
    def _calculate_density_score(self, row: pd.Series) -> float:
        """
        Calculate what percentage of the row has non-null values.
        
        Headers typically have a high density because every column should
        have a header name. Data rows might have missing values.
        
        Args:
            row: A single row from the DataFrame
            
        Returns:
            Score between 0 and 1
        """
        non_null_count = row.notna().sum()
        total_count = len(row)
        
        if total_count == 0:
            return 0.0
        
        return non_null_count / total_count
    
    def _calculate_text_score(self, row: pd.Series) -> float:
        """
        Calculate what percentage of non-null values are text.
        
        Headers are almost always text strings. Data rows often contain
        numbers, dates, or other data types.
        
        Args:
            row: A single row from the DataFrame
            
        Returns:
            Score between 0 and 1
        """
        non_null_values = row.dropna()
        
        if len(non_null_values) == 0:
            return 0.0
        
        # Count how many values are strings (not numbers or dates)
        text_count = sum(1 for val in non_null_values if isinstance(val, str))
        
        return text_count / len(non_null_values)
    
    def _calculate_uniqueness_score(self, row: pd.Series) -> float:
        """
        Calculate what percentage of values are unique.
        
        Header values should all be unique (each column has a different name).
        Data rows often have repeated values.
        
        Args:
            row: A single row from the DataFrame
            
        Returns:
            Score between 0 and 1
        """
        non_null_values = row.dropna()
        
        if len(non_null_values) == 0:
            return 0.0
        
        unique_count = len(non_null_values.unique())
        total_count = len(non_null_values)
        
        return unique_count / total_count
    
    def _calculate_keyword_score(self, row: pd.Series) -> float:
        """
        Check how many common header keywords appear in the row.
        
        Headers often contain standard terms like "No", "Name", "Date", etc.
        This checks for the presence of these common patterns.
        
        Args:
            row: A single row from the DataFrame
            
        Returns:
            Score between 0 and 1
        """
        # Convert all values to lowercase strings for comparison
        row_text = ' '.join(str(val).lower() for val in row.dropna())
        
        # Count how many keywords are found
        keyword_matches = sum(1 for keyword in self.header_keywords 
                            if keyword in row_text)
        
        # Normalize by the number of non-null values
        # A row with 10 columns needs more keywords than a row with 3 columns
        non_null_count = row.notna().sum()
        
        if non_null_count == 0:
            return 0.0
        
        # Score is higher when we find multiple keywords relative to row length
        expected_keywords = max(1, non_null_count // 5)  # Expect 1 keyword per 5 columns
        
        return min(1.0, keyword_matches / expected_keywords)
    
    def _validate_data_rows(self, df: pd.DataFrame, header_idx: int) -> float:
        """
        Validate that rows after the potential header look like data.
        
        After we identify a potential header row, we should verify that the
        following rows contain actual data. This helps distinguish headers
        from title rows or other non-data content.
        
        Args:
            df: The full DataFrame
            header_idx: Index of the potential header row
            
        Returns:
            Score between 0 and 1 indicating how data-like the following rows are
        """
        # Need at least one data row to validate
        if header_idx >= len(df) - 1:
            return 0.0
        
        # Look at the next 3 rows (or however many are available)
        data_rows_to_check = min(3, len(df) - header_idx - 1)
        validation_score = 0.0
        
        for i in range(1, data_rows_to_check + 1):
            data_row = df.iloc[header_idx + i]
            
            # Data rows should have:
            # 1. Some non-null values (but not necessarily all)
            # 2. Mix of data types (not all text like headers)
            # 3. Some repeated values (unlike unique headers)
            
            density = data_row.notna().sum() / len(data_row)
            text_ratio = sum(1 for val in data_row.dropna() 
                           if isinstance(val, str)) / max(1, data_row.notna().sum())
            
            # Good data row: moderate density, not all text
            row_score = density * 0.5 + (1 - text_ratio) * 0.5
            validation_score += row_score
        
        return validation_score / data_rows_to_check
    
    def detect_with_column_names(
        self, 
        df: pd.DataFrame, 
        expected_columns: List[str]
    ) -> Tuple[int, float]:
        """
        Detect header row with validation against expected column names.
        
        If you know what columns should exist in the file, this method provides
        additional validation by checking if the detected header row actually
        contains those column names (after normalization).
        
        Args:
            df: DataFrame with header=None
            expected_columns: List of column names that should exist
            
        Returns:
            A tuple of (header_row_index, confidence_score)
            
        Examples:
            >>> detector = HeaderDetector()
            >>> expected = ["Case No", "Description", "ETA"]
            >>> row, conf = detector.detect_with_column_names(df, expected)
        """
        # First, do normal detection
        header_row, base_confidence = self.detect_from_dataframe(df)
        
        # Then validate against expected columns
        if header_row >= len(df):
            return header_row, base_confidence
        
        detected_headers = df.iloc[header_row].tolist()
        
        # Normalize both expected and detected headers for comparison
        from .header_normalizer import normalize_header
        
        normalized_expected = [normalize_header(col) for col in expected_columns]
        normalized_detected = [normalize_header(str(col)) for col in detected_headers 
                              if pd.notna(col)]
        
        # Calculate match ratio
        matches = sum(1 for exp in normalized_expected 
                     if any(exp in det or det in exp for det in normalized_detected))
        
        match_ratio = matches / len(normalized_expected) if normalized_expected else 0.0
        
        # Adjust confidence based on column name matching
        adjusted_confidence = (base_confidence * 0.7) + (match_ratio * 0.3)
        
        return header_row, adjusted_confidence


def detect_header_row(
    file_path: str, 
    sheet_name: Optional[str] = None,
    expected_columns: Optional[List[str]] = None
) -> Tuple[int, float]:
    """
    Convenience function for quick header detection.
    
    This is a simplified interface to the HeaderDetector class for when you
    just need to quickly find where headers are in a file.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Sheet name to analyze (None = first sheet)
        expected_columns: Optional list of expected column names for validation
        
    Returns:
        A tuple of (header_row_index, confidence_score)
        
    Examples:
        >>> row, confidence = detect_header_row("data.xlsx")
        >>> print(f"Headers at row {row}")
        Headers at row 2
    """
    detector = HeaderDetector()
    
    # Read the file
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name or 0,
        header=None,
        nrows=detector.max_search_rows
    )
    
    # Use validation if expected columns provided
    if expected_columns:
        return detector.detect_with_column_names(df, expected_columns)
    else:
        return detector.detect_from_dataframe(df)


if __name__ == "__main__":
    """
    Test suite and demonstration of header detection capabilities.
    """
    
    print("=" * 60)
    print("Header Detector Test Suite")
    print("=" * 60)
    
    # Create test scenarios
    test_scenarios = [
        {
            'name': 'Headers in Row 1 (Standard)',
            'data': pd.DataFrame([
                ['No', 'Name', 'Date', 'Amount'],
                [1, 'Item A', '2024-01-01', 100],
                [2, 'Item B', '2024-01-02', 200],
            ]),
            'expected_row': 0
        },
        {
            'name': 'Headers in Row 3 (With Title)',
            'data': pd.DataFrame([
                ['Company Report 2024', None, None, None],
                [None, None, None, None],
                ['No', 'Name', 'Date', 'Amount'],
                [1, 'Item A', '2024-01-01', 100],
                [2, 'Item B', '2024-01-02', 200],
            ]),
            'expected_row': 2
        },
        {
            'name': 'Headers in Row 5 (Multiple Blank Lines)',
            'data': pd.DataFrame([
                [None, None, None, None],
                [None, None, None, None],
                [None, None, None, None],
                [None, None, None, None],
                ['Case No', 'Description', 'ETA', 'Status'],
                ['A001', 'Equipment', '2024-01-15', 'Active'],
                ['A002', 'Container', '2024-01-16', 'Active'],
            ]),
            'expected_row': 4
        },
    ]
    
    detector = HeaderDetector()
    
    for scenario in test_scenarios:
        print(f"\n{'=' * 60}")
        print(f"Scenario: {scenario['name']}")
        print(f"{'=' * 60}")
        
        df = scenario['data']
        expected = scenario['expected_row']
        
        detected_row, confidence = detector.detect_from_dataframe(df)
        
        print(f"Expected header row: {expected}")
        print(f"Detected header row: {detected_row}")
        print(f"Confidence: {confidence:.1%}")
        print(f"Status: {'✓ PASS' if detected_row == expected else '✗ FAIL'}")
        
        # Show the detected header
        if detected_row < len(df):
            headers = df.iloc[detected_row].tolist()
            print(f"Detected headers: {headers}")
    
    print(f"\n{'=' * 60}")
    print("Test Suite Complete")
    print(f"{'=' * 60}")
