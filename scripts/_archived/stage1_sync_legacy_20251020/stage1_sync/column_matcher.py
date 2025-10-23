# -*- coding: utf-8 -*-
"""
컬럼명 유연한 매칭을 위한 유틸리티 모듈
"""

import re
from typing import List, Optional
import pandas as pd


def normalize_column_name(col_name: str) -> str:
    """
    컬럼명을 정규화하여 비교 가능한 형태로 변환

    변환 규칙:
    - 소문자로 변환
    - 점(.), 공백, 특수문자 제거
    - 연속된 공백을 단일 공백으로

    예시:
    "No." -> "no"
    "No" -> "no"
    " NO. " -> "no"
    "Case No." -> "caseno"
    "CASE_NO" -> "caseno"
    """
    # 소문자 변환
    normalized = str(col_name).lower()
    # 특수문자 및 공백 제거 (알파벳과 숫자만 남김)
    normalized = re.sub(r"[^a-z0-9]", "", normalized)

    # 특정 패턴 정규화
    if normalized == "casenumber":
        normalized = "caseno"
    elif normalized == "estimatedarrival":
        normalized = "eta"
    elif normalized == "estimateddeparture":
        normalized = "etd"
    return normalized


def find_column_flexible(df: pd.DataFrame, target_names: List[str]) -> Optional[str]:
    """
    DataFrame에서 target_names 중 하나와 일치하는 컬럼명을 찾음

    Args:
        df: DataFrame
        target_names: 찾고자 하는 컬럼명 리스트 (예: ['no', 'number', 'num'])

    Returns:
        일치하는 실제 컬럼명 또는 None
    """
    # 타겟 컬럼명 정규화
    normalized_targets = [normalize_column_name(name) for name in target_names]

    # DataFrame의 모든 컬럼명 정규화 및 매핑
    column_map = {normalize_column_name(col): col for col in df.columns}

    # 일치하는 컬럼 찾기
    for target in normalized_targets:
        if target in column_map:
            return column_map[target]

    return None


# 주요 컬럼명 매핑 테이블
COLUMN_ALIASES = {
    "no": ["no", "num", "number", "index", "id"],
    "caseno": ["caseno", "case", "casenumber", "casenum"],
    "eta": ["eta", "estimatedarrival", "expectedarrival"],
    "etd": ["etd", "estimateddeparture", "expecteddeparture"],
    "date": ["date", "datetime", "time"],
    "qty": ["qty", "quantity", "amount", "count"],
    "description": ["description", "desc", "detail", "name"],
}


def find_column_by_meaning(df: pd.DataFrame, meaning: str) -> Optional[str]:
    """
    의미를 기반으로 컬럼 찾기

    Args:
        df: DataFrame
        meaning: 컬럼의 의미 (예: 'no', 'caseno', 'eta')

    Returns:
        일치하는 실제 컬럼명 또는 None
    """
    if meaning in COLUMN_ALIASES:
        return find_column_flexible(df, COLUMN_ALIASES[meaning])
    return find_column_flexible(df, [meaning])


def test_column_matcher():
    """
    컬럼 매처 함수들의 테스트
    """
    print("=== 컬럼명 정규화 테스트 ===")

    # 테스트할 컬럼명 변형들
    test_cases = [
        ("No", "no"),
        ("No.", "no"),
        ("NO.", "no"),
        (" No ", "no"),
        ("no", "no"),
        ("Case No.", "caseno"),
        ("CASE_NO", "caseno"),
        ("case-no", "caseno"),
        ("Case Number", "caseno"),
    ]

    for input_col, expected_normalized in test_cases:
        result = normalize_column_name(input_col)
        status = "PASS" if result == expected_normalized else "FAIL"
        print(f"  {input_col} -> {result} (expected: {expected_normalized}) [{status}]")

    print("\n=== 컬럼 검색 테스트 ===")

    # 테스트 DataFrame 생성
    test_df = pd.DataFrame(
        {
            "No": [1, 2, 3],
            "Case No.": ["A001", "A002", "A003"],
            "Description": ["Item 1", "Item 2", "Item 3"],
            "ETA": ["2024-01-01", "2024-01-02", "2024-01-03"],
        }
    )

    # NO 컬럼 찾기 테스트
    no_col = find_column_flexible(test_df, ["no", "number", "num", "index"])
    print(f"NO 컬럼 찾기: {no_col}")

    # Case No. 컬럼 찾기 테스트
    case_col = find_column_by_meaning(test_df, "caseno")
    print(f"Case No. 컬럼 찾기: {case_col}")

    # ETA 컬럼 찾기 테스트
    eta_col = find_column_by_meaning(test_df, "eta")
    print(f"ETA 컬럼 찾기: {eta_col}")


if __name__ == "__main__":
    test_column_matcher()
