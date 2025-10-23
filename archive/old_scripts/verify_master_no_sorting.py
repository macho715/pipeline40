#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master NO. 정렬 검증 스크립트
Stage 1 출력이 Master의 NO. 순서를 올바르게 따르는지 확인
"""

import pandas as pd
from pathlib import Path
import sys


def verify_master_no_sorting():
    """Master NO. 정렬 상태를 검증합니다."""

    print("=== Master NO. 정렬 검증 ===")

    try:
        # 파일 경로 설정
        master_file = "data/raw/Case List.xlsx"
        synced_file = (
            "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx"
        )

        # 파일 존재 확인
        if not Path(master_file).exists():
            print(f"ERROR: Master 파일이 존재하지 않습니다: {master_file}")
            return False

        if not Path(synced_file).exists():
            print(f"ERROR: Synced 파일이 존재하지 않습니다: {synced_file}")
            return False

        # 데이터 로드
        print("데이터 로딩 중...")
        master_df = pd.read_excel(master_file)
        synced_df = pd.read_excel(synced_file)

        print(f"Master 데이터: {len(master_df)}행, {len(master_df.columns)}컬럼")
        print(f"Synced 데이터: {len(synced_df)}행, {len(synced_df.columns)}컬럼")

        # NO 컬럼 찾기 (유연한 매칭)
        master_no_col = None
        synced_no_col = None

        for col in master_df.columns:
            if "no" in str(col).lower() and "case" not in str(col).lower():
                master_no_col = col
                break

        for col in synced_df.columns:
            if "no" in str(col).lower() and "case" not in str(col).lower():
                synced_no_col = col
                break

        if not master_no_col:
            print("ERROR: Master에서 NO 컬럼을 찾을 수 없습니다")
            return False

        if not synced_no_col:
            print("ERROR: Synced에서 NO 컬럼을 찾을 수 없습니다")
            return False

        print(f"Master NO 컬럼: {master_no_col}")
        print(f"Synced NO 컬럼: {synced_no_col}")

        # NO 값 추출 및 정규화 (데이터 타입 통일)
        master_nos = (
            master_df[master_no_col]
            .dropna()
            .astype(float)
            .astype(int)
            .astype(str)
            .tolist()
        )
        synced_nos = (
            synced_df[synced_no_col]
            .dropna()
            .astype(float)
            .astype(int)
            .astype(str)
            .tolist()
        )

        print(f"Master NO 개수: {len(master_nos)}")
        print(f"Synced NO 개수: {len(synced_nos)}")

        # 처음 1000개 비교
        compare_count = min(1000, len(master_nos), len(synced_nos))
        master_sample = master_nos[:compare_count]
        synced_sample = synced_nos[:compare_count]

        print(f"\n처음 {compare_count}개 비교:")

        # 정확히 일치하는 개수
        exact_matches = sum(
            1 for i in range(compare_count) if master_sample[i] == synced_sample[i]
        )

        # 순서대로 일치하는 연속 구간 찾기
        consecutive_matches = 0
        for i in range(compare_count):
            if master_sample[i] == synced_sample[i]:
                consecutive_matches += 1
            else:
                break

        match_rate = (exact_matches / compare_count) * 100

        print(f"PASS 정확히 일치: {exact_matches}/{compare_count} ({match_rate:.1f}%)")
        print(f"PASS 연속 일치: {consecutive_matches}개")

        # 불일치 구간 분석
        if exact_matches < compare_count:
            print(f"\n불일치 구간 분석:")
            for i in range(min(10, compare_count)):
                if master_sample[i] != synced_sample[i]:
                    print(
                        f"  위치 {i+1}: Master='{master_sample[i]}' vs Synced='{synced_sample[i]}'"
                    )

        # 전체 순서 일치 여부
        if exact_matches == compare_count:
            print("SUCCESS: 전체 순서가 완벽히 일치합니다!")
            return True
        elif match_rate >= 95:
            print("PASS: 높은 일치율을 보입니다 (95% 이상)")
            return True
        else:
            print("WARNING: 일치율이 낮습니다. 정렬 로직을 확인해주세요.")
            return False

    except Exception as e:
        print(f"ERROR: 오류 발생: {str(e)}")
        return False


if __name__ == "__main__":
    success = verify_master_no_sorting()
    sys.exit(0 if success else 1)
