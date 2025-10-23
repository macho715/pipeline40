# -*- coding: utf-8 -*-
"""
Stack and SQM Processing Module
===============================

STACK.MD 기반 치수 기반 SQM 계산 및 Stack_Status 파싱 로직을 구현합니다.

주요 기능:
- 치수 기반 SQM 계산: L(cm) × W(cm) / 10,000
- Stack 텍스트 파싱: "Not stackable" → 0, "X2" → 2 등
- mm 단위 자동 변환 (÷10)
- 폴백 전략: 치수 없으면 기존 추정 로직 사용

작성자: AI Development Team
버전: v1.0
작성일: 2025-10-23
"""

from __future__ import annotations

import math
import re
from typing import Optional, Union

import pandas as pd

# 정규식 패턴 사전 컴파일 (성능 최적화)
NOT_STACK_PATTERNS = [
    re.compile(r"\bnot\s*stackable\b", re.IGNORECASE),
    re.compile(r"\bnon[-\s]*stackable\b", re.IGNORECASE),
    re.compile(r"\bno\s*stack(ing)?\b", re.IGNORECASE),
]

TOP_ONLY_PATTERNS = [
    re.compile(r"only\s+on\s+top", re.IGNORECASE),
    re.compile(r"on\s+top\s+only", re.IGNORECASE),
    re.compile(r"stackable\s+on\s+top", re.IGNORECASE),
]

# 숫자 추출 패턴들
NUMBER_PAT = re.compile(r"\b(\d+)\b")
XNUM_PAT = re.compile(r"[xX]\s*(\d+)")
PCS_PAT = re.compile(r"(\d+)\s*(pcs?)", re.IGNORECASE)
TIER_PAT = re.compile(r"(\d+)\s*(tier|tiers?)", re.IGNORECASE)


def _to_float(value: Union[str, float, int, None]) -> Optional[float]:
    """
    안전한 float 변환 함수

    Args:
        value: 변환할 값

    Returns:
        float 값 또는 None (변환 실패 시)
    """
    try:
        if pd.isna(value) or value is None:
            return None

        # 문자열인 경우 처리
        if isinstance(value, str):
            # 공백 제거 및 쉼표 제거
            cleaned = value.strip().replace(",", "")
            if not cleaned:
                return None
            return float(cleaned)

        return float(value)
    except (ValueError, TypeError):
        return None


def compute_sqm_from_dims(
    row: pd.Series, l_col: Optional[str] = None, w_col: Optional[str] = None
) -> Optional[float]:
    """
    치수 기반 SQM 계산: L(cm) × W(cm) / 10,000

    Args:
        row: 데이터 행
        l_col: 길이 컬럼명 (None이면 자동 탐지)
        w_col: 너비 컬럼명 (None이면 자동 탐지)

    Returns:
        계산된 SQM 값 또는 None (계산 불가 시)
    """
    # 컬럼명 자동 탐지
    if not l_col:
        for col in ["L(CM)", "Length (cm)", "L CM", "Length", "L(mm)", "L(MM)"]:
            if col in row.index:
                l_col = col
                break

    if not w_col:
        for col in ["W(CM)", "Width (cm)", "W CM", "Width", "W(mm)", "W(MM)"]:
            if col in row.index:
                w_col = col
                break

    if not l_col or not w_col:
        return None

    # 값 추출 및 변환
    L = _to_float(row.get(l_col))
    W = _to_float(row.get(w_col))

    if L is None or W is None or L <= 0 or W <= 0:
        return None

    # mm 단위인 경우 cm으로 변환
    if "mm" in l_col.lower() or "MM" in l_col:
        L = L / 10.0
    if "mm" in w_col.lower() or "MM" in w_col:
        W = W / 10.0

    # SQM 계산: L(cm) × W(cm) / 10,000
    sqm = (L * W) / 10000.0
    return round(sqm, 2)


def parse_stack_status(text: Union[str, None]) -> Optional[int]:
    """
    Stack 텍스트에서 tier 수 파싱

    규칙:
    - 'not stackable'류 → 0
    - 숫자 표현: X2, x3, '2 pcs', '3 tier' 등 → 해당 숫자
    - 'on top only'류 → 1
    - 숫자 전혀 없으면 → 1
    - '600kg/m2' 등 하중 표기는 단수 지정 근거가 없으므로 1로 간주

    Args:
        text: 파싱할 텍스트

    Returns:
        파싱된 tier 수 또는 None (파싱 실패 시)
    """
    if text is None or (isinstance(text, float) and math.isnan(text)):
        return None

    s = str(text).lower().strip()
    if not s:
        return None

    # 명시적 비적재 (더 포괄적인 패턴)
    not_stackable_patterns = [
        r"\bnot\s*stackable\b",
        r"\bnon[-\s]*stackable\b",
        r"\bno\s*stack(ing)?\b",
        r"\bnot\s*satckable\b",  # 오타 포함
    ]

    for pattern_str in not_stackable_patterns:
        if re.search(pattern_str, s, re.IGNORECASE):
            return 0

    # on top only 류
    for pattern in TOP_ONLY_PATTERNS:
        if pattern.search(s):
            return 1

    # 숫자 후보들 추출
    nums = []

    # X2, x3 형태 (우선순위 높음)
    for match in XNUM_PAT.finditer(s):
        try:
            nums.append(int(match.group(1)))
        except (ValueError, IndexError):
            pass

    # 2 pcs, 3 pcs 형태
    for match in PCS_PAT.finditer(s):
        try:
            nums.append(int(match.group(1)))
        except (ValueError, IndexError):
            pass

    # 2 tier, 3 tiers 형태
    for match in TIER_PAT.finditer(s):
        try:
            nums.append(int(match.group(1)))
        except (ValueError, IndexError):
            pass

    # 2X, 3X 형태 (추가 패턴)
    x_suffix_pattern = re.compile(r"(\d+)\s*[xX]\b", re.IGNORECASE)
    for match in x_suffix_pattern.finditer(s):
        try:
            nums.append(int(match.group(1)))
        except (ValueError, IndexError):
            pass

    # 일반 숫자 (마지막)
    for match in NUMBER_PAT.finditer(s):
        try:
            nums.append(int(match.group(1)))
        except (ValueError, IndexError):
            pass

    if nums:
        return max(nums)  # 가장 큰 숫자 반환

    # 'Stackable', 'Stackability', '600kg/m2' 등 → 숫자 부재시 1단
    return 1


def add_sqm_and_stack(
    df: pd.DataFrame,
    l_col: Optional[str] = None,
    w_col: Optional[str] = None,
    stack_col: Optional[str] = None,
) -> pd.DataFrame:
    """
    DataFrame에 SQM 및 Stack_Status 컬럼 추가

    Args:
        df: 처리할 DataFrame
        l_col: 길이 컬럼명 (None이면 자동 탐지)
        w_col: 너비 컬럼명 (None이면 자동 탐지)
        stack_col: Stack 텍스트 컬럼명 (None이면 자동 탐지)

    Returns:
        SQM, Stack_Status 컬럼이 추가된 DataFrame
    """
    result_df = df.copy()

    # SQM 계산
    if l_col or w_col or any(col in df.columns for col in ["L(CM)", "W(CM)", "Length", "Width"]):
        result_df["SQM"] = result_df.apply(
            lambda row: compute_sqm_from_dims(row, l_col, w_col), axis=1
        )
    else:
        # 치수 컬럼이 없어도 기본값으로 SQM 컬럼 추가
        result_df["SQM"] = None

    # Stack_Status 계산
    if stack_col or any(col in df.columns for col in ["Stackability", "Stackable", "Stack"]):
        if stack_col and stack_col in df.columns:
            result_df["Stack_Status"] = df[stack_col].apply(parse_stack_status)
        else:
            # 자동 탐지
            for col in ["Stackability", "Stackable", "Stack", "Stack ability"]:
                if col in df.columns:
                    result_df["Stack_Status"] = df[col].apply(parse_stack_status)
                    break
            else:
                # Stack 컬럼이 없으면 기본값으로 Stack_Status 컬럼 추가
                result_df["Stack_Status"] = None
    else:
        # Stack 컬럼이 없어도 기본값으로 Stack_Status 컬럼 추가
        result_df["Stack_Status"] = None

    return result_df


def get_sqm_with_fallback(
    row: pd.Series, l_col: Optional[str] = None, w_col: Optional[str] = None
) -> float:
    """
    폴백 전략이 포함된 SQM 계산

    우선순위:
    1. 이미 계산된 SQM 컬럼
    2. 치수 기반 계산
    3. 기존 추정 로직 (PKG 기반)

    Args:
        row: 데이터 행
        l_col: 길이 컬럼명
        w_col: 너비 컬럼명

    Returns:
        계산된 SQM 값
    """
    # 1순위: 이미 계산된 SQM
    if "SQM" in row.index and pd.notna(row["SQM"]):
        return float(row["SQM"])

    # 2순위: 치수 기반 계산
    sqm = compute_sqm_from_dims(row, l_col, w_col)
    if sqm is not None:
        return sqm

    # 3순위: 기존 추정 로직 (PKG 기반)
    try:
        pkg = _to_float(row.get("Pkg", 1))
        if pkg is not None and pkg > 0:
            return float(pkg) * 1.5  # 기존 추정 로직
    except (ValueError, TypeError):
        pass

    # 최종 폴백: PKG 기반 추정 또는 1.0
    try:
        pkg = _to_float(row.get("Pkg", 1))
        if pkg is not None and pkg > 0:
            return float(pkg) * 1.5  # 기존 추정 로직
    except (ValueError, TypeError):
        pass

    return 1.0


# 테스트 함수들
def test_sqm_calculations():
    """SQM 계산 테스트"""
    test_cases = [
        # (L, W, expected)
        (100, 50, 0.5),  # 100cm × 50cm = 0.5 m²
        (200, 100, 2.0),  # 200cm × 100cm = 2.0 m²
        (1000, 500, 50.0),  # 1000cm × 500cm = 50.0 m²
    ]

    for L, W, expected in test_cases:
        row = pd.Series({"L(CM)": L, "W(CM)": W})
        result = compute_sqm_from_dims(row)
        assert abs(result - expected) < 0.01, f"Expected {expected}, got {result}"


def test_stack_parsing():
    """Stack 파싱 테스트"""
    test_cases = [
        # (input, expected)
        ("Not stackable", 0),
        ("Stackable", 1),
        ("Stackable X2", 2),
        ("Stackable 3 tier", 3),
        ("600kg/m2", 1),
        ("Stackable on top", 1),
        ("X4", 4),
        ("2 pcs", 2),
    ]

    for text, expected in test_cases:
        result = parse_stack_status(text)
        assert result == expected, f"Input '{text}': Expected {expected}, got {result}"


if __name__ == "__main__":
    """테스트 실행"""
    print("Testing SQM calculations...")
    test_sqm_calculations()
    print("✅ SQM calculations passed")

    print("Testing Stack parsing...")
    test_stack_parsing()
    print("✅ Stack parsing passed")

    print("All tests passed! 🎉")
