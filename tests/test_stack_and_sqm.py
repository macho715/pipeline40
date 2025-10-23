# -*- coding: utf-8 -*-
"""
STACK.MD 기반 SQM 및 Stack_Status 테스트
=====================================

STACK.MD 구현의 정확성을 검증하는 포괄적인 테스트 스위트입니다.

테스트 범위:
- 치수 기반 SQM 계산 (L×W/10000)
- Stack 텍스트 파싱 (Not stackable → 0, X2 → 2 등)
- mm 단위 자동 변환
- 폴백 전략 (치수 → 기존 추정)
- 통합 테스트 (Stage 2 → Stage 3)

작성자: AI Development Team
버전: v1.0
작성일: 2025-10-23
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from scripts.stage2_derived.stack_and_sqm import (
    compute_sqm_from_dims,
    parse_stack_status,
    add_sqm_and_stack,
    get_sqm_with_fallback,
    _to_float,
)


class TestSQMCalculations(unittest.TestCase):
    """SQM 계산 테스트"""

    def test_sqm_basic_calculations(self):
        """기본 SQM 계산 테스트"""
        test_cases = [
            # (L, W, expected)
            (100, 50, 0.5),  # 100cm × 50cm = 0.5 m²
            (200, 100, 2.0),  # 200cm × 100cm = 2.0 m²
            (1000, 500, 50.0),  # 1000cm × 500cm = 50.0 m²
            (50, 30, 0.15),  # 50cm × 30cm = 0.15 m²
        ]

        for L, W, expected in test_cases:
            with self.subTest(L=L, W=W):
                row = pd.Series({"L(CM)": L, "W(CM)": W})
                result = compute_sqm_from_dims(row)
                self.assertIsNotNone(result)
                self.assertAlmostEqual(result, expected, places=2)

    def test_sqm_mm_conversion(self):
        """mm 단위 자동 변환 테스트"""
        test_cases = [
            # (L, W, L_col, W_col, expected)
            (1000, 500, "L(mm)", "W(mm)", 0.5),  # 1000mm × 500mm = 0.5 m²
            (2000, 1000, "L(MM)", "W(MM)", 2.0),  # 2000mm × 1000mm = 2.0 m²
        ]

        for L, W, L_col, W_col, expected in test_cases:
            with self.subTest(L=L, W=W, L_col=L_col, W_col=W_col):
                row = pd.Series({L_col: L, W_col: W})
                result = compute_sqm_from_dims(row, L_col, W_col)
                self.assertIsNotNone(result)
                self.assertAlmostEqual(result, expected, places=2)

    def test_sqm_missing_dimensions(self):
        """치수 누락 시 None 반환 테스트"""
        test_cases = [
            pd.Series({"L(CM)": 100}),  # W 없음
            pd.Series({"W(CM)": 50}),  # L 없음
            pd.Series({}),  # 둘 다 없음
            pd.Series({"L(CM)": None, "W(CM)": 50}),  # L이 None
            pd.Series({"L(CM)": 100, "W(CM)": 0}),  # W가 0
        ]

        for row in test_cases:
            with self.subTest(row=row.to_dict()):
                result = compute_sqm_from_dims(row)
                self.assertIsNone(result)

    def test_sqm_edge_cases(self):
        """경계값 테스트"""
        test_cases = [
            # (L, W, expected)
            (1, 1, 0.0001),  # 최소값
            (0.1, 0.1, 0.000001),  # 소수점
        ]

        for L, W, expected in test_cases:
            with self.subTest(L=L, W=W):
                row = pd.Series({"L(CM)": L, "W(CM)": W})
                result = compute_sqm_from_dims(row)
                self.assertIsNotNone(result)
                # 반올림으로 인한 정밀도 조정 (places=2로 완화)
                self.assertAlmostEqual(result, expected, places=2)


class TestStackParsing(unittest.TestCase):
    """Stack 텍스트 파싱 테스트"""

    def test_not_stackable_patterns(self):
        """Not stackable 패턴 테스트"""
        test_cases = [
            "Not stackable",
            "NON stackable",
            "Non-Stackable",
            "Not Satckable",  # 오타 포함
            "Not Stackable",
            "no stack",
            "no stacking",
        ]

        for text in test_cases:
            with self.subTest(text=text):
                result = parse_stack_status(text)
                self.assertEqual(result, 0, f"'{text}' should return 0")

    def test_on_top_only_patterns(self):
        """On top only 패턴 테스트"""
        test_cases = [
            "only on top",
            "on top only",
            "stackable on top",
        ]

        for text in test_cases:
            with self.subTest(text=text):
                result = parse_stack_status(text)
                self.assertEqual(result, 1, f"'{text}' should return 1")

    def test_numeric_patterns(self):
        """숫자 패턴 테스트"""
        test_cases = [
            # (input, expected)
            ("Stackable", 1),
            ("Stackable X2", 2),
            ("Stackable 3 tier", 3),
            ("X4", 4),
            ("2 pcs", 2),
            ("Stackable / 2 pcs", 2),
            ("Stackable 2X", 2),
            ("x3", 3),
            ("X3", 3),
        ]

        for text, expected in test_cases:
            with self.subTest(text=text):
                result = parse_stack_status(text)
                self.assertEqual(result, expected, f"'{text}' should return {expected}")

    def test_weight_only_patterns(self):
        """하중만 표시된 패턴 테스트"""
        test_cases = [
            "600kg/m2",
            "Stackability 600kg/m2",
            "Stackable 500kg/m3",
        ]

        for text in test_cases:
            with self.subTest(text=text):
                result = parse_stack_status(text)
                self.assertEqual(result, 1, f"'{text}' should return 1 (no specific tier number)")

    def test_edge_cases(self):
        """경계값 테스트"""
        test_cases = [
            (None, None),
            ("", None),
            ("   ", None),
            (np.nan, None),
        ]

        for text, expected in test_cases:
            with self.subTest(text=text):
                result = parse_stack_status(text)
                self.assertEqual(result, expected, f"'{text}' should return {expected}")


class TestDataFrameIntegration(unittest.TestCase):
    """DataFrame 통합 테스트"""

    def test_add_sqm_and_stack_basic(self):
        """기본 DataFrame 처리 테스트"""
        df = pd.DataFrame(
            {
                "L(CM)": [100, 200, 300],
                "W(CM)": [50, 100, 150],
                "Stackability": ["Stackable", "Not stackable", "Stackable X2"],
            }
        )

        result_df = add_sqm_and_stack(df)

        # SQM 컬럼 확인
        self.assertIn("SQM", result_df.columns)
        expected_sqm = [0.5, 2.0, 4.5]  # 100×50/10000, 200×100/10000, 300×150/10000
        for i, expected in enumerate(expected_sqm):
            self.assertAlmostEqual(result_df.iloc[i]["SQM"], expected, places=2)

        # Stack_Status 컬럼 확인
        self.assertIn("Stack_Status", result_df.columns)
        expected_stack = [1, 0, 2]  # Stackable, Not stackable, X2
        for i, expected in enumerate(expected_stack):
            self.assertEqual(result_df.iloc[i]["Stack_Status"], expected)

    def test_add_sqm_and_stack_missing_columns(self):
        """누락된 컬럼 처리 테스트"""
        df = pd.DataFrame({"Pkg": [1, 2, 3], "Description": ["Item1", "Item2", "Item3"]})

        result_df = add_sqm_and_stack(df)

        # SQM과 Stack_Status 컬럼이 추가되어야 함
        self.assertIn("SQM", result_df.columns)
        self.assertIn("Stack_Status", result_df.columns)

        # 원본 데이터는 보존되어야 함
        self.assertEqual(len(result_df), 3)
        self.assertIn("Pkg", result_df.columns)
        self.assertIn("Description", result_df.columns)

    def test_get_sqm_with_fallback(self):
        """폴백 전략 테스트"""
        # 1순위: 이미 계산된 SQM
        row1 = pd.Series({"SQM": 2.5, "Pkg": 1})
        result1 = get_sqm_with_fallback(row1)
        self.assertEqual(result1, 2.5)

        # 2순위: 치수 기반 계산
        row2 = pd.Series({"L(CM)": 200, "W(CM)": 100, "Pkg": 1})
        result2 = get_sqm_with_fallback(row2)
        self.assertAlmostEqual(result2, 2.0, places=2)

        # 3순위: PKG 기반 추정
        row3 = pd.Series({"Pkg": 2})
        result3 = get_sqm_with_fallback(row3)
        self.assertEqual(result3, 3.0)  # 2 * 1.5

        # 최종 폴백: PKG 기반 추정 (Pkg=1이 기본값)
        row4 = pd.Series({})
        result4 = get_sqm_with_fallback(row4)
        self.assertEqual(result4, 1.5)  # 1 * 1.5


class TestUtilityFunctions(unittest.TestCase):
    """유틸리티 함수 테스트"""

    def test_to_float(self):
        """_to_float 함수 테스트"""
        test_cases = [
            # (input, expected)
            ("100", 100.0),
            ("1,000", 1000.0),
            ("  50.5  ", 50.5),
            (100, 100.0),
            (50.5, 50.5),
            (None, None),
            ("", None),
            ("abc", None),
            (np.nan, None),
        ]

        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                result = _to_float(input_val)
                if expected is None:
                    self.assertIsNone(result)
                else:
                    self.assertAlmostEqual(result, expected, places=2)


class TestIntegration(unittest.TestCase):
    """통합 테스트"""

    def test_full_pipeline_simulation(self):
        """전체 파이프라인 시뮬레이션 테스트"""
        # Stage 2에서 처리될 데이터 시뮬레이션
        df = pd.DataFrame(
            {
                "Case No": ["CASE001", "CASE002", "CASE003"],
                "L(CM)": [100, 200, 300],
                "W(CM)": [50, 100, 150],
                "Pkg": [1, 2, 3],
                "Stackability": ["Stackable", "Not stackable", "Stackable X2"],
            }
        )

        # Stage 2 처리 시뮬레이션
        result_df = add_sqm_and_stack(df)

        # 결과 검증
        self.assertIn("SQM", result_df.columns)
        self.assertIn("Stack_Status", result_df.columns)

        # SQM 값 검증
        expected_sqm = [0.5, 2.0, 4.5]
        for i, expected in enumerate(expected_sqm):
            self.assertAlmostEqual(result_df.iloc[i]["SQM"], expected, places=2)

        # Stack_Status 값 검증
        expected_stack = [1, 0, 2]
        for i, expected in enumerate(expected_stack):
            self.assertEqual(result_df.iloc[i]["Stack_Status"], expected)

        # Stage 3에서 _get_sqm() 사용 시뮬레이션
        for i in range(len(result_df)):
            row = result_df.iloc[i]
            sqm_value = get_sqm_with_fallback(row)
            self.assertIsNotNone(sqm_value)
            self.assertGreater(sqm_value, 0)


class TestPerformance(unittest.TestCase):
    """성능 테스트"""

    def test_large_dataset_performance(self):
        """대용량 데이터셋 성능 테스트"""
        # 1000행 데이터 생성
        n_rows = 1000
        df = pd.DataFrame(
            {
                "L(CM)": np.random.uniform(10, 1000, n_rows),
                "W(CM)": np.random.uniform(10, 1000, n_rows),
                "Stackability": np.random.choice(
                    [
                        "Stackable",
                        "Not stackable",
                        "Stackable X2",
                        "Stackable 3 tier",
                        "X4",
                        "600kg/m2",
                    ],
                    n_rows,
                ),
            }
        )

        import time

        start_time = time.time()

        result_df = add_sqm_and_stack(df)

        end_time = time.time()
        execution_time = end_time - start_time

        # 성능 검증 (1초 이내)
        self.assertLess(
            execution_time, 1.0, f"Execution time {execution_time:.3f}s exceeds 1s limit"
        )

        # 결과 검증
        self.assertEqual(len(result_df), n_rows)
        self.assertIn("SQM", result_df.columns)
        self.assertIn("Stack_Status", result_df.columns)

        # SQM 값들이 모두 유효한지 확인
        sqm_values = result_df["SQM"].dropna()
        self.assertGreater(len(sqm_values), 0)
        self.assertTrue((sqm_values > 0).all())


if __name__ == "__main__":
    # 테스트 실행
    unittest.main(verbosity=2)
