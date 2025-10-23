# -*- coding: utf-8 -*-
"""
Test suite for core.data_parser module
=====================================

Tests for Stack_Status parsing logic with comprehensive edge cases.
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from core.data_parser import (
    parse_stack_status,
    calculate_sqm,
    convert_mm_to_cm,
    map_stack_status,
)


class TestParseStackStatus:
    """Test cases for parse_stack_status function"""

    def test_not_stackable_patterns(self):
        """Test various 'not stackable' patterns"""
        test_cases = [
            ("Not stackable", 0),
            ("not stackable", 0),
            ("NOT STACKABLE", 0),
            ("Non-stackable", 0),
            ("Non stackable", 0),
            ("No stack", 0),
            ("No stacking", 0),
            ("Not satckable", 0),  # 오타 케이스
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_on_top_only_patterns(self):
        """Test 'on top only' patterns"""
        test_cases = [
            ("Only on top", 1),
            ("On top only", 1),
            ("Stackable on top", 1),
            ("only on top", 1),
            ("ON TOP ONLY", 1),
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_x_patterns(self):
        """Test X patterns (X2, 2X, etc.)"""
        test_cases = [
            ("X2", 2),
            ("x3", 3),
            ("2X", 2),
            ("3x", 3),
            ("X 4", 4),
            ("5 X", 5),
            ("Stackable X2", 2),
            ("Stackable 2X", 2),
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_pcs_patterns(self):
        """Test pcs/pieces patterns"""
        test_cases = [
            ("2 pcs", 2),
            ("3 pc", 3),
            ("4 pieces", 4),
            ("5 piece", 5),
            ("Stackable 2 pcs", 2),
            ("Stackable 3 pieces", 3),
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_tier_patterns(self):
        """Test tier patterns"""
        test_cases = [
            ("2 tier", 2),
            ("3 tiers", 3),
            ("4 tier", 4),
            ("Stackable 2 tier", 2),
            ("Stackable 3 tiers", 3),
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_slash_patterns(self):
        """Test slash patterns (/ 2, / 3, etc.)"""
        test_cases = [
            ("Stackable / 2", 2),
            ("Stackable / 3 pcs", 3),
            ("Stackable / 4", 4),
            ("/ 5", 5),
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_weight_patterns_removal(self):
        """Test that weight patterns are properly removed"""
        test_cases = [
            ("Stackable 600kg/m2", 1),  # 하중 표기 제거 후 숫자 없음 → 1
            ("Stackable 500kg/㎡", 1),  # 하중 표기 제거 후 숫자 없음 → 1
            ("Stackable 400kg/m^2", 1), # 하중 표기 제거 후 숫자 없음 → 1
            ("Stackable 300kg", 1),     # 단독 kg 표기 제거 후 숫자 없음 → 1
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_complex_patterns(self):
        """Test complex patterns with multiple numbers"""
        test_cases = [
            ("Stackable 600kg/m2 / 2 pcs", 2),  # 하중 제거 후 / 2 → 2
            ("Stackable X3 500kg/m2", 3),       # 하중 제거 후 X3 → 3
            ("Stackable 2 tier 400kg/m2", 2),   # 하중 제거 후 2 tier → 2
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_max_number_selection(self):
        """Test that maximum number is selected when multiple numbers exist"""
        test_cases = [
            ("Stackable 2 pcs 3 tier", 3),  # 2, 3 중 최대값 3
            ("Stackable X2 4 pcs", 4),      # 2, 4 중 최대값 4
            ("Stackable 1 tier 5 pcs", 5),  # 1, 5 중 최대값 5
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_default_values(self):
        """Test default values for various cases"""
        test_cases = [
            ("Stackable", 1),           # 숫자 없음 → 1
            ("Stackability", 1),        # 숫자 없음 → 1
            ("Stackable text", 1),      # 숫자 없음 → 1
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_none_and_empty_values(self):
        """Test None and empty values"""
        test_cases = [
            (None, None),
            ("", None),
            ("   ", None),
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"

    def test_numeric_input(self):
        """Test numeric input"""
        test_cases = [
            (2, 2),      # 숫자 2 → 2
            (3, 3),      # 숫자 3 → 3
            (0, 0),      # 숫자 0 → 0
        ]
        
        for text, expected in test_cases:
            assert parse_stack_status(text) == expected, f"Failed for: '{text}'"


class TestCalculateSqm:
    """Test cases for calculate_sqm function"""

    def test_basic_calculation(self):
        """Test basic SQM calculation"""
        assert calculate_sqm(100, 50) == 0.5
        assert calculate_sqm(200, 150) == 3.0
        assert calculate_sqm(1000, 1000) == 100.0

    def test_decimal_values(self):
        """Test decimal values"""
        assert calculate_sqm(100.5, 50.5) == pytest.approx(0.507525, rel=1e-6)
        assert calculate_sqm(200.25, 150.75) == pytest.approx(3.01876875, rel=1e-6)


class TestConvertMmToCm:
    """Test cases for convert_mm_to_cm function"""

    def test_basic_conversion(self):
        """Test basic mm to cm conversion"""
        assert convert_mm_to_cm(1000) == 100.0
        assert convert_mm_to_cm(500) == 50.0
        assert convert_mm_to_cm(100) == 10.0

    def test_decimal_values(self):
        """Test decimal values"""
        assert convert_mm_to_cm(1000.5) == 100.05
        assert convert_mm_to_cm(500.25) == 50.025


class TestMapStackStatus:
    """Test cases for map_stack_status function"""

    def test_pandas_series(self):
        """Test with pandas Series"""
        import pandas as pd
        
        series = pd.Series(["Not stackable", "X2", "Stackable / 3", ""])
        result = map_stack_status(series)
        
        expected = pd.Series([0, 2, 3, None])
        pd.testing.assert_series_equal(result, expected)

    def test_list_input(self):
        """Test with list input (if supported)"""
        # map_stack_status는 pandas Series만 지원하므로 이 테스트는 스킵
        # 실제 사용 시에는 pandas Series를 사용해야 함
        import pandas as pd
        
        test_list = ["Not stackable", "X2", "Stackable / 3"]
        series = pd.Series(test_list)
        result = map_stack_status(series)
        
        # Should return a Series-like object
        assert hasattr(result, 'map')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
