# -*- coding: utf-8 -*-
"""
Semantic Matcher Module
========================

This is the core matching engine that brings together normalization,
detection, and registry lookup to find headers in Excel files based
on their semantic meaning rather than exact string matching.

The semantic matcher works in several stages:

1. NORMALIZE: Convert all header names to a standard form
2. MATCH: Compare normalized names against semantic aliases
3. RANK: Score matches by confidence
4. SELECT: Choose the best match for each semantic key

This approach allows the pipeline to handle Excel files with different
header naming conventions without any code changes. You simply add new
aliases to the registry and the matcher will find them automatically.

Key Features:
- Zero hardcoding of column names
- Fuzzy matching with confidence scores
- Multiple matching strategies (exact, partial, phonetic)
- Fallback mechanisms when no exact match exists
- Detailed matching reports for debugging
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field

from .header_normalizer import HeaderNormalizer
from .header_registry import HVDC_HEADER_REGISTRY, HeaderDefinition


@dataclass
class MatchResult:
    """
    Result of attempting to match a semantic key to an actual column.
    
    This dataclass contains all the information about how a semantic key
    was matched (or not matched) to a column in the DataFrame. It includes
    confidence scores and the actual column name found.
    
    Attributes:
        semantic_key: The semantic key we were trying to find
        matched: Whether a match was found
        column_name: The actual column name in the DataFrame (if matched)
        confidence: Confidence score (0-1) for the match
        match_type: How the match was found (exact, partial, fallback)
        alternatives: Other columns that partially matched
    """
    semantic_key: str
    matched: bool = False
    column_name: Optional[str] = None
    confidence: float = 0.0
    match_type: str = "none"  # none, exact, partial, fallback
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    
    def __str__(self) -> str:
        """String representation for debugging."""
        if self.matched:
            return (f"✓ {self.semantic_key} → '{self.column_name}' "
                   f"({self.match_type}, {self.confidence:.0%})")
        else:
            return f"✗ {self.semantic_key} - No match found"


@dataclass
class MatchReport:
    """
    Complete report of all matching attempts for a DataFrame.
    
    This report provides a comprehensive view of how semantic keys were
    matched to actual columns. It's useful for debugging and understanding
    why certain columns were or weren't found.
    
    Attributes:
        total_semantic_keys: Total number of semantic keys attempted
        successful_matches: Number of successful matches
        failed_matches: Number of failed matches
        average_confidence: Average confidence across all successful matches
        results: Individual match results for each semantic key
        unmatched_columns: Columns in DataFrame that weren't matched
    """
    total_semantic_keys: int = 0
    successful_matches: int = 0
    failed_matches: int = 0
    average_confidence: float = 0.0
    results: List[MatchResult] = field(default_factory=list)
    unmatched_columns: List[str] = field(default_factory=list)
    
    def get_match(self, semantic_key: str) -> Optional[MatchResult]:
        """Get the match result for a specific semantic key."""
        for result in self.results:
            if result.semantic_key == semantic_key:
                return result
        return None
    
    def get_column_name(self, semantic_key: str) -> Optional[str]:
        """Get the actual column name for a semantic key (if matched)."""
        result = self.get_match(semantic_key)
        return result.column_name if result and result.matched else None
    
    def print_summary(self):
        """Print a human-readable summary of the matching results."""
        print("\n" + "=" * 70)
        print("SEMANTIC MATCHING REPORT")
        print("=" * 70)
        
        print(f"\nOverall Statistics:")
        print(f"  Total semantic keys:     {self.total_semantic_keys}")
        print(f"  Successful matches:      {self.successful_matches}")
        print(f"  Failed matches:          {self.failed_matches}")
        print(f"  Success rate:            {self.successful_matches/max(1,self.total_semantic_keys):.1%}")
        print(f"  Average confidence:      {self.average_confidence:.1%}")
        
        # Group results by match type
        by_type = {}
        for result in self.results:
            if result.matched:
                match_type = result.match_type
                if match_type not in by_type:
                    by_type[match_type] = []
                by_type[match_type].append(result)
        
        if by_type:
            print(f"\nMatches by Type:")
            for match_type, results in sorted(by_type.items()):
                print(f"  {match_type:12s}: {len(results):3d}")
        
        # Show successful matches
        successful = [r for r in self.results if r.matched]
        if successful:
            print(f"\n{'Successful Matches:':70s}")
            print(f"  {'Semantic Key':<25s} {'→':<3s} {'Column Name':<30s} {'Conf':<6s}")
            print("  " + "-" * 64)
            for result in sorted(successful, key=lambda x: x.confidence, reverse=True):
                print(f"  {result.semantic_key:<25s} {'→':<3s} "
                      f"'{result.column_name}':<30s {result.confidence:5.1%}")
        
        # Show failed matches
        failed = [r for r in self.results if not r.matched]
        if failed:
            print(f"\nFailed Matches:")
            for result in failed:
                print(f"  ✗ {result.semantic_key}")
                if result.alternatives:
                    print(f"    Alternatives: {', '.join(col for col, _ in result.alternatives[:3])}")
        
        # Show unmatched columns
        if self.unmatched_columns:
            print(f"\nUnmatched Columns in DataFrame:")
            for col in self.unmatched_columns[:10]:
                print(f"  • {col}")
            if len(self.unmatched_columns) > 10:
                print(f"  ... and {len(self.unmatched_columns)-10} more")
        
        print("\n" + "=" * 70)


class SemanticMatcher:
    """
    Engine for matching semantic keys to actual DataFrame columns.
    
    This class implements sophisticated matching logic that goes beyond
    simple string comparison. It uses normalization, alias matching, and
    confidence scoring to reliably find columns even when they're named
    differently than expected.
    
    The matcher supports multiple strategies:
    - Exact matching: Normalized name exactly matches an alias
    - Partial matching: Normalized name contains or is contained in an alias
    - Phonetic matching: Names sound similar (future enhancement)
    - Fuzzy matching: Levenshtein distance within threshold (future enhancement)
    
    Examples:
        >>> matcher = SemanticMatcher()
        >>> report = matcher.match_dataframe(df, ["case_number", "eta_ata"])
        >>> case_col = report.get_column_name("case_number")
        >>> print(f"Case column is: {case_col}")
        Case column is: Case No.
    """
    
    def __init__(
        self,
        registry=None,
        normalizer=None,
        min_confidence: float = 0.7,
        allow_partial: bool = True
    ):
        """
        Initialize the semantic matcher.
        
        Args:
            registry: Header registry to use (defaults to HVDC_HEADER_REGISTRY)
            normalizer: Header normalizer to use (defaults to new instance)
            min_confidence: Minimum confidence score to accept a match (0-1)
            allow_partial: Whether to allow partial matching as fallback
        """
        self.registry = registry or HVDC_HEADER_REGISTRY
        self.normalizer = normalizer or HeaderNormalizer()
        self.min_confidence = min_confidence
        self.allow_partial = allow_partial
    
    def match_dataframe(
        self,
        df: pd.DataFrame,
        semantic_keys: Optional[List[str]] = None,
        required_only: bool = False
    ) -> MatchReport:
        """
        Match semantic keys to actual columns in a DataFrame.
        
        This is the main entry point for semantic matching. It attempts to
        find each requested semantic key in the DataFrame's columns.
        
        Args:
            df: The DataFrame to match against
            semantic_keys: List of semantic keys to find. If None, tries all registered keys.
            required_only: If True, only tries to match required headers
            
        Returns:
            A MatchReport containing all matching results
            
        Examples:
            >>> matcher = SemanticMatcher()
            >>> # Match specific headers
            >>> report = matcher.match_dataframe(df, ["case_number", "eta_ata"])
            >>> 
            >>> # Match all required headers
            >>> report = matcher.match_dataframe(df, required_only=True)
            >>> 
            >>> # Try to match everything in the registry
            >>> report = matcher.match_dataframe(df)
        """
        # Determine which semantic keys to try matching
        if semantic_keys is None:
            if required_only:
                semantic_keys = self.registry.get_required_headers()
            else:
                semantic_keys = self.registry.get_all_semantic_keys()
        
        # Normalize all DataFrame column names once for efficiency
        normalized_columns = self._normalize_dataframe_columns(df)
        
        # Attempt to match each semantic key
        results = []
        matched_columns = set()
        
        for key in semantic_keys:
            try:
                result = self._match_single_key(
                    key, 
                    df.columns.tolist(),
                    normalized_columns,
                    matched_columns
                )
                results.append(result)
                
                if result.matched and result.column_name:
                    matched_columns.add(result.column_name)
                    
            except KeyError:
                # Semantic key not in registry - skip it
                continue
        
        # Find unmatched columns
        unmatched = [col for col in df.columns if col not in matched_columns]
        
        # Build the report
        report = MatchReport(
            total_semantic_keys=len(results),
            successful_matches=sum(1 for r in results if r.matched),
            failed_matches=sum(1 for r in results if not r.matched),
            results=results,
            unmatched_columns=unmatched
        )
        
        # Calculate average confidence
        if report.successful_matches > 0:
            report.average_confidence = np.mean([
                r.confidence for r in results if r.matched
            ])
        
        return report
    
    def find_column(
        self,
        df: pd.DataFrame,
        semantic_key: str,
        required: bool = False
    ) -> Optional[str]:
        """
        Find a single column by semantic key.
        
        This is a convenience method for when you just need to find one
        column without generating a full report.
        
        Args:
            df: The DataFrame to search
            semantic_key: The semantic key to find
            required: If True, raises ValueError when not found
            
        Returns:
            The actual column name, or None if not found
            
        Raises:
            ValueError: If required=True and column not found
            
        Examples:
            >>> matcher = SemanticMatcher()
            >>> case_col = matcher.find_column(df, "case_number", required=True)
            >>> eta_col = matcher.find_column(df, "eta_ata")
        """
        report = self.match_dataframe(df, [semantic_key])
        result = report.get_match(semantic_key)
        
        if result and result.matched:
            return result.column_name
        elif required:
            raise ValueError(
                f"Required column '{semantic_key}' not found in DataFrame. "
                f"Columns available: {df.columns.tolist()}"
            )
        else:
            return None
    
    def _normalize_dataframe_columns(
        self,
        df: pd.DataFrame
    ) -> Dict[str, str]:
        """
        Create a mapping of normalized column names to original names.
        
        Args:
            df: The DataFrame
            
        Returns:
            Dict mapping normalized names to original column names
        """
        mapping = {}
        for col in df.columns:
            # Get all normalized alternatives for this column
            alternatives = self.normalizer.normalize_with_alternatives(str(col))
            
            # Map each alternative to the original column name
            for alt in alternatives:
                if alt not in mapping:  # Keep first occurrence
                    mapping[alt] = col
        
        return mapping
    
    def _match_single_key(
        self,
        semantic_key: str,
        actual_columns: List[str],
        normalized_columns: Dict[str, str],
        already_matched: Set[str]
    ) -> MatchResult:
        """
        Attempt to match a single semantic key to a column.
        
        This method tries multiple matching strategies in order of confidence:
        1. Exact match: Normalized column name exactly matches an alias
        2. Partial match: Normalized names have significant overlap
        3. Fallback: Best guess based on partial similarity
        
        Args:
            semantic_key: The semantic key to match
            actual_columns: List of actual column names in the DataFrame
            normalized_columns: Mapping of normalized to original names
            already_matched: Set of columns already matched (to avoid duplicates)
            
        Returns:
            A MatchResult describing what was found
        """
        result = MatchResult(semantic_key=semantic_key)
        
        # Get the definition for this semantic key
        definition = self.registry.get_definition(semantic_key)
        
        # Normalize all aliases for this semantic key
        normalized_aliases = []
        for alias in definition.aliases:
            alternatives = self.normalizer.normalize_with_alternatives(alias)
            normalized_aliases.extend(alternatives)
        
        # Remove duplicates while preserving order
        normalized_aliases = list(dict.fromkeys(normalized_aliases))
        
        # Strategy 1: Try exact matching
        for norm_alias in normalized_aliases:
            if norm_alias in normalized_columns:
                original_col = normalized_columns[norm_alias]
                
                # Skip if this column was already matched to another semantic key
                if original_col in already_matched:
                    continue
                
                result.matched = True
                result.column_name = original_col
                result.confidence = 1.0
                result.match_type = "exact"
                return result
        
        # Strategy 2: Try partial matching (if enabled)
        if self.allow_partial:
            partial_matches = self._find_partial_matches(
                normalized_aliases,
                normalized_columns,
                already_matched
            )
            
            if partial_matches:
                # Take the best partial match
                norm_col, score = partial_matches[0]
                original_col = normalized_columns[norm_col]
                
                if score >= self.min_confidence:
                    result.matched = True
                    result.column_name = original_col
                    result.confidence = score
                    result.match_type = "partial"
                    result.alternatives = [
                        (normalized_columns[nc], s) 
                        for nc, s in partial_matches[1:3]
                    ]
                    return result
                else:
                    # Score too low, but record alternatives
                    result.alternatives = [
                        (normalized_columns[nc], s)
                        for nc, s in partial_matches[:3]
                    ]
        
        return result
    
    def _find_partial_matches(
        self,
        normalized_aliases: List[str],
        normalized_columns: Dict[str, str],
        already_matched: Set[str]
    ) -> List[Tuple[str, float]]:
        """
        Find columns that partially match the aliases.
        
        Partial matching uses substring containment to find columns that
        might be variations of the expected names. For example, "casenumber"
        would partially match "casenumberid" or "caseno".
        
        Args:
            normalized_aliases: List of normalized alias variations
            normalized_columns: Mapping of normalized to original names
            already_matched: Columns to exclude
            
        Returns:
            List of (normalized_column, score) tuples, sorted by score descending
        """
        matches = []
        
        for norm_col, original_col in normalized_columns.items():
            # Skip already matched columns
            if original_col in already_matched:
                continue
            
            # Calculate best match score against all aliases
            best_score = 0.0
            
            for alias in normalized_aliases:
                score = self._calculate_similarity_score(alias, norm_col)
                best_score = max(best_score, score)
            
            if best_score > 0:
                matches.append((norm_col, best_score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def _calculate_similarity_score(self, alias: str, column: str) -> float:
        """
        Calculate similarity score between an alias and a column name.
        
        Uses substring containment to determine similarity:
        - If one string contains the other: high score
        - If they share a significant prefix: medium score
        - Otherwise: low or zero score
        
        Args:
            alias: Normalized alias from the registry
            column: Normalized column name from the DataFrame
            
        Returns:
            Similarity score between 0 and 1
        """
        if not alias or not column:
            return 0.0
        
        # Exact match would have been caught earlier, but check anyway
        if alias == column:
            return 1.0
        
        # Check if one contains the other
        if alias in column:
            # Column name contains the alias
            # Score based on how much of the column the alias represents
            return len(alias) / len(column) * 0.9
        
        if column in alias:
            # Alias contains the column name
            return len(column) / len(alias) * 0.85
        
        # Check for common prefix
        common_prefix_len = 0
        for i, (a, c) in enumerate(zip(alias, column)):
            if a == c:
                common_prefix_len += 1
            else:
                break
        
        if common_prefix_len >= 3:  # At least 3 characters in common
            max_len = max(len(alias), len(column))
            return (common_prefix_len / max_len) * 0.7
        
        return 0.0


def find_header_by_meaning(
    df: pd.DataFrame,
    semantic_key: str,
    required: bool = False,
    registry=None
) -> Optional[str]:
    """
    Convenience function to find a single header by semantic meaning.
    
    This is the simplest interface for semantic matching. Use this when
    you just need to find one column and don't need detailed match reports.
    
    Args:
        df: The DataFrame to search
        semantic_key: The semantic key to find (e.g., "case_number")
        required: If True, raises ValueError when not found
        registry: Custom registry (defaults to HVDC_HEADER_REGISTRY)
        
    Returns:
        The actual column name, or None if not found
        
    Raises:
        ValueError: If required=True and column not found
        
    Examples:
        >>> # Find the case number column
        >>> case_col = find_header_by_meaning(df, "case_number")
        >>> 
        >>> # Find a required column (raises error if missing)
        >>> case_col = find_header_by_meaning(df, "case_number", required=True)
    """
    matcher = SemanticMatcher(registry=registry)
    return matcher.find_column(df, semantic_key, required=required)


if __name__ == "__main__":
    """
    Test suite and demonstration of semantic matching capabilities.
    """
    
    print("=" * 70)
    print("Semantic Matcher Test Suite")
    print("=" * 70)
    
    # Create test DataFrames with various column naming styles
    test_cases = [
        {
            'name': 'Standard Format',
            'df': pd.DataFrame({
                'Case No.': ['A001', 'A002'],
                'Description': ['Item 1', 'Item 2'],
                'ETA/ATA': ['2024-01-01', '2024-01-02'],
                'DHL Warehouse': ['2024-01-05', '2024-01-06'],
            }),
            'expected_matches': {'case_number', 'description', 'eta_ata', 'dhl_warehouse'}
        },
        {
            'name': 'Uppercase with Underscores',
            'df': pd.DataFrame({
                'CASE_NUMBER': ['B001', 'B002'],
                'DESC': ['Item 1', 'Item 2'],
                'ESTIMATED_ARRIVAL': ['2024-01-01', '2024-01-02'],
            }),
            'expected_matches': {'case_number', 'description', 'eta_ata'}
        },
        {
            'name': 'Mixed Separators',
            'df': pd.DataFrame({
                'Case-No': ['C001', 'C002'],
                'Item Description': ['Item 1', 'Item 2'],
                'ETA / ATA': ['2024-01-01', '2024-01-02'],
                'Status_Current': ['Active', 'Pending'],
            }),
            'expected_matches': {'case_number', 'description', 'eta_ata', 'status_current'}
        },
    ]
    
    matcher = SemanticMatcher()
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}: {test['name']}")
        print(f"{'='*70}")
        
        df = test['df']
        print(f"\nOriginal columns: {df.columns.tolist()}")
        
        # Try to match expected semantic keys
        semantic_keys = list(test['expected_matches'])
        report = matcher.match_dataframe(df, semantic_keys)
        
        # Print summary
        print(f"\nMatching Results:")
        print(f"  Expected: {len(test['expected_matches'])} matches")
        print(f"  Found:    {report.successful_matches} matches")
        print(f"  Success rate: {report.successful_matches/len(test['expected_matches']):.0%}")
        
        # Show individual matches
        print(f"\nMatched Columns:")
        for result in report.results:
            if result.matched:
                print(f"  ✓ {result.semantic_key:20s} → '{result.column_name}' ({result.confidence:.0%})")
            else:
                print(f"  ✗ {result.semantic_key:20s} - NOT FOUND")
    
    print(f"\n{'='*70}")
    print("Test Suite Complete")
    print(f"{'='*70}")
