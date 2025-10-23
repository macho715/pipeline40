# -*- coding: utf-8 -*-
"""
Stage 3 Total sqm 계산 테스트

Test Coverage:
- Stack_Status 파싱 기본 테스트
- Total sqm 계산 기본 테스트
- 엣지 케이스 테스트
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(project_root))

from stage3_report.report_generator import (
    _calculate_stack_status,
    _calculate_total_sqm,
)


class TestCalculateStackStatus:
    """Stack_Status 파싱 테스트"""

    def test_basic_patterns(self):
        """기본 Stack_Status 파싱 테스트"""
        df = pd.DataFrame({
            "Stack": ["X2", "Stackable / 3", "Not stackable", None, ""]
        })
        result = _calculate_stack_status(df)
        
        assert result.iloc[0] == 2, "X2 should return 2"
        assert result.iloc[1] == 3, "Stackable / 3 should return 3"
        assert result.iloc[2] == 0, "Not stackable should return 0"
        assert pd.isna(result.iloc[3]), "None should return None"
        assert pd.isna(result.iloc[4]), "Empty string should return None"

    def test_various_numeric_patterns(self):
        """다양한 숫자 패턴 테스트"""
        df = pd.DataFrame({
            "Stack": [
                "X4",
                "2 pcs",
                "3 tier",
                "/ 2",
                "Stackable on top",
                "Stackable 600kg/m2",
            ]
        })
        result = _calculate_stack_status(df)
        
        assert result.iloc[0] == 4, "X4 should return 4"
        assert result.iloc[1] == 2, "2 pcs should return 2"
        assert result.iloc[2] == 3, "3 tier should return 3"
        assert result.iloc[3] == 2, "/ 2 should return 2"
        assert result.iloc[4] == 1, "on top should return 1"
        assert result.iloc[5] == 1, "600kg/m2 should be ignored, return 1"

    def test_missing_column(self):
        """Stack 컬럼이 없는 경우 테스트"""
        df = pd.DataFrame({
            "Other": ["value1", "value2"]
        })
        result = _calculate_stack_status(df, stack_col="Stack")
        
        # 컬럼이 없으면 모두 None
        assert all(pd.isna(result)), "All values should be None when column missing"


class TestCalculateTotalSqm:
    """Total sqm 계산 테스트"""

    def test_basic_calculation(self):
        """기본 Total sqm 계산 테스트"""
        df = pd.DataFrame({
            "Pkg": [10, 5, 2, None, 10],
            "SQM": [2.5, 3.0, 1.5, 2.0, None],
            "Stack_Status": [2, 3, 0, 1, 1]
        })
        result = _calculate_total_sqm(df)
        
        # PKG × SQM × Stack_Status
        assert result.iloc[0] == pytest.approx(50.0), "10 × 2.5 × 2 = 50.0"
        assert result.iloc[1] == pytest.approx(45.0), "5 × 3.0 × 3 = 45.0"
        assert pd.isna(result.iloc[2]), "Stack_Status=0 should return None"
        assert pd.isna(result.iloc[3]), "Pkg=None should return None"
        assert pd.isna(result.iloc[4]), "SQM=None should return None"

    def test_edge_cases(self):
        """Total sqm 엣지 케이스 테스트"""
        df = pd.DataFrame({
            "Pkg": [10, 0, -5, 10],
            "SQM": [2.5, 2.5, 2.5, 2.5],
            "Stack_Status": [2, 2, 2, None]
        })
        result = _calculate_total_sqm(df)
        
        assert result.iloc[0] == pytest.approx(50.0), "Valid calculation"
        assert pd.isna(result.iloc[1]), "Pkg = 0 should return None"
        assert pd.isna(result.iloc[2]), "Pkg < 0 should return None"
        assert pd.isna(result.iloc[3]), "Stack_Status None should return None"

    def test_missing_columns(self):
        """필수 컬럼이 없는 경우 테스트"""
        # Pkg만 있는 경우
        df = pd.DataFrame({
            "Pkg": [10, 20]
        })
        result = _calculate_total_sqm(df)
        
        # 모든 값이 None이어야 함
        assert all(pd.isna(result)), "All values should be None when required columns missing"

    def test_zero_and_negative_values(self):
        """0과 음수 값 처리 테스트"""
        df = pd.DataFrame({
            "Pkg": [10, 0, -5, 10, 10],
            "SQM": [2.5, 2.5, 2.5, 0, -1.5],
            "Stack_Status": [2, 2, 2, 2, 2]
        })
        result = _calculate_total_sqm(df)
        
        assert result.iloc[0] == pytest.approx(50.0), "Valid: 10 × 2.5 × 2"
        assert pd.isna(result.iloc[1]), "Pkg=0 invalid"
        assert pd.isna(result.iloc[2]), "Pkg<0 invalid"
        assert pd.isna(result.iloc[3]), "SQM=0 invalid"
        assert pd.isna(result.iloc[4]), "SQM<0 invalid"


class TestIntegration:
    """통합 테스트"""

    def test_full_workflow(self):
        """전체 워크플로우 테스트"""
        df = pd.DataFrame({
            "Pkg": [10, 5, 3],
            "Stack": ["X2", "Stackable / 3", "Not stackable"],
            "SQM": [2.5, 3.0, 1.5],
        })
        
        # Stack_Status 계산
        df["Stack_Status"] = _calculate_stack_status(df)
        
        # Total sqm 계산
        df["Total sqm"] = _calculate_total_sqm(df)
        
        # 검증
        assert df.iloc[0]["Stack_Status"] == 2
        assert df.iloc[0]["Total sqm"] == pytest.approx(50.0)  # 10 × 2.5 × 2
        
        assert df.iloc[1]["Stack_Status"] == 3
        assert df.iloc[1]["Total sqm"] == pytest.approx(45.0)  # 5 × 3.0 × 3
        
        assert df.iloc[2]["Stack_Status"] == 0
        assert pd.isna(df.iloc[2]["Total sqm"])  # Stack_Status=0 이므로 None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

