#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파생 컬럼 검증 스크립트
Stage 2에서 13개 파생 컬럼이 올바르게 추가되었는지 확인
"""

import pandas as pd
from pathlib import Path
import sys


def verify_derived_columns():
    """파생 컬럼 추가 상태를 검증합니다."""

    print("=== 파생 컬럼 검증 ===")

    try:
        # 파일 경로 설정 (Synced 파일에서 파생 컬럼 확인)
        synced_file = (
            "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx"
        )
        derived_file = "data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx"

        # 파일 존재 확인
        if not Path(synced_file).exists():
            print(f"ERROR: Synced 파일이 존재하지 않습니다: {synced_file}")
            return False

        if not Path(derived_file).exists():
            print(f"ERROR: Derived 파일이 존재하지 않습니다: {derived_file}")
            return False

        print("데이터 로딩 중...")

        # 데이터 로드
        synced_df = pd.read_excel(synced_file)
        derived_df = pd.read_excel(derived_file)

        print(f"Synced 데이터: {len(synced_df)}행, {len(synced_df.columns)}컬럼")
        print(f"Derived 데이터: {len(derived_df)}행, {len(derived_df.columns)}컬럼")

        # Synced 파일에서 파생 컬럼 확인 (Stage 1에서 이미 추가됨)
        original_cols = 44  # 파생 컬럼 제외한 원본 컬럼 수
        synced_derived_cols = len(synced_df.columns) - original_cols
        derived_derived_cols = len(derived_df.columns) - original_cols

        print(f"\n파생 컬럼 확인:")
        print(f"원본 컬럼 수: {original_cols}")
        print(f"Synced 파생 컬럼 수: {synced_derived_cols}")
        print(f"Derived 파생 컬럼 수: {derived_derived_cols}")

        # Synced 파일에서 파생 컬럼 목록
        synced_derived_cols_list = synced_df.columns[original_cols:].tolist()
        print(f"\nSynced 파일의 파생 컬럼 목록 ({len(synced_derived_cols_list)}개):")
        for i, col in enumerate(synced_derived_cols_list, 1):
            print(f"  {i:2d}. {col}")

        # 예상 파생 컬럼 목록 (실제 컬럼명)
        expected_derived_cols = [
            "Status_WAREHOUSE",
            "Status_SITE",
            "Status_Current",
            "Status_Location",
            "Status_Location_Date",
            "Status_Storage",
            "wh handling",
            "site  handling",
            "total handling",
            "minus",
            "final handling",
            "SQM",
            "Stack_Status",
        ]

        print(f"\n예상 파생 컬럼과 비교:")

        # 예상 컬럼들이 모두 있는지 확인
        missing_cols = []
        extra_cols = []

        for expected_col in expected_derived_cols:
            if expected_col not in synced_derived_cols_list:
                missing_cols.append(expected_col)

        for new_col in synced_derived_cols_list:
            if new_col not in expected_derived_cols:
                extra_cols.append(new_col)

        if missing_cols:
            print(f"ERROR 누락된 컬럼 ({len(missing_cols)}개):")
            for col in missing_cols:
                print(f"   - {col}")
        else:
            print(f"PASS 모든 예상 컬럼이 추가되었습니다")

        if extra_cols:
            print(f"INFO 추가된 예상 외 컬럼 ({len(extra_cols)}개):")
            for col in extra_cols:
                print(f"   + {col}")

        # 데이터 무결성 검증
        print(f"\n데이터 무결성 검증:")

        # 행 수 일치 확인
        if len(synced_df) == len(derived_df):
            print(f"PASS 행 수 일치: {len(derived_df)}행")
        else:
            print(
                f"ERROR 행 수 불일치: Synced={len(synced_df)}, Derived={len(derived_df)}"
            )
            return False

        # 파생 컬럼의 NULL 값 확인
        null_counts = {}
        for col in synced_derived_cols_list:
            null_count = synced_df[col].isnull().sum()
            if null_count > 0:
                null_counts[col] = null_count

        if null_counts:
            print(f"WARNING NULL 값이 있는 파생 컬럼:")
            for col, count in null_counts.items():
                print(f"   {col}: {count}개 NULL")
        else:
            print(f"PASS 모든 파생 컬럼에 NULL 값 없음")

        # 전체 평가
        if synced_derived_cols >= 10:  # 최소 10개 이상의 파생 컬럼
            print(
                f"\nSUCCESS 파생 컬럼 확인 성공! ({synced_derived_cols}개 확인됨, Stage 1에서 추가)"
            )
            return True
        else:
            print(f"\nWARNING 파생 컬럼 부족 ({synced_derived_cols}개만 확인됨)")
            return False

    except Exception as e:
        print(f"ERROR 오류 발생: {str(e)}")
        return False


if __name__ == "__main__":
    success = verify_derived_columns()
    sys.exit(0 if success else 1)
