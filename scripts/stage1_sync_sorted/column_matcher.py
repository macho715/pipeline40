"""Stage 1 컬럼 매칭 헬퍼로 Core 헤더 매니저를 래핑합니다. / Stage 1 column matching helpers backed by the core header manager."""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from scripts.core import HEADER_MANAGER, HeaderManager


_MEANING_TO_SEMANTIC = {
    "no": "item_number",
    "caseno": "case_number",
    "eta": "eta_ata",
    "etd": "etd_atd",
    "qty": "quantity",
    "description": "description",
}

# 유지: 레거시 의미 매핑 (핫픽스 호환). / Legacy alias groups kept for backward compatibility.
COLUMN_ALIASES = {
    "no": ["no", "num", "number", "index", "id"],
    "caseno": ["caseno", "case", "casenumber", "casenum"],
    "eta": ["eta", "estimatedarrival", "expectedarrival"],
    "etd": ["etd", "estimateddeparture", "expecteddeparture"],
    "date": ["date", "datetime", "time"],
    "qty": ["qty", "quantity", "amount", "count"],
    "description": ["description", "desc", "detail", "name"],
}


def _manager() -> HeaderManager:
    """공유 헤더 매니저를 반환합니다. / Return the shared header manager."""

    return HEADER_MANAGER


def normalize_column_name(col_name: str) -> str:
    """컬럼명을 매칭 토큰으로 정규화합니다. / Normalize a column label into a matching token."""

    return _manager().normalize_token(col_name)


def find_column_flexible(df: pd.DataFrame, target_names: Iterable[str]) -> Optional[str]:
    """여러 후보명을 대상으로 컬럼을 찾습니다. / Find a column among multiple alias candidates."""

    manager = _manager()
    cleaned_columns = manager.clean_columns(df.columns)
    column_map = {
        manager.normalize_token(cleaned): original
        for cleaned, original in zip(cleaned_columns, df.columns)
    }

    for candidate in target_names:
        normalized_candidate = manager.normalize_token(candidate)
        if normalized_candidate in column_map:
            return column_map[normalized_candidate]
    return None


def find_column_by_meaning(df: pd.DataFrame, meaning: str) -> Optional[str]:
    """의미 기반으로 컬럼을 탐색합니다. / Locate a column based on its semantic meaning."""

    manager = _manager()
    semantic_key = _MEANING_TO_SEMANTIC.get(meaning)

    if semantic_key:
        matched = manager.find_column(df, semantic_key)
        if matched:
            return matched

    if meaning in COLUMN_ALIASES:
        return find_column_flexible(df, COLUMN_ALIASES[meaning])

    return find_column_flexible(df, [meaning])


def test_column_matcher():
    """단위 테스트를 수행합니다. / Execute ad-hoc unit tests."""

    print("=== 컬럼명 정규화 테스트 ===")

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

    test_df = pd.DataFrame(
        {
            "No": [1, 2, 3],
            "Case No.": ["A001", "A002", "A003"],
            "Description": ["Item 1", "Item 2", "Item 3"],
            "ETA": ["2024-01-01", "2024-01-02", "2024-01-03"],
        }
    )

    no_col = find_column_flexible(test_df, ["no", "number", "num", "index"])
    print(f"NO 컬럼 찾기: {no_col}")

    case_col = find_column_by_meaning(test_df, "caseno")
    print(f"Case No. 컬럼 찾기: {case_col}")

    eta_col = find_column_by_meaning(test_df, "eta")
    print(f"ETA 컬럼 찾기: {eta_col}")


if __name__ == "__main__":
    test_column_matcher()
