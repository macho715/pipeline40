# -*- coding: utf-8 -*-
"""
Case ID 매칭 디버깅 스크립트
"""

import json, re
import pandas as pd
from pathlib import Path

def _norm_case(s):
    return re.sub(r'[^A-Z0-9]', '', str(s).strip().upper()) if s is not None else ""


def debug_case_matching():
    """Case ID 매칭 문제 디버깅"""

    # JSON 파일에서 이상치 로드
    with open("hvdc_anomaly_report_v2.json", "r", encoding="utf-8") as f:
        anomaly_data = json.load(f)

    print(f"📊 JSON에서 로드된 이상치: {len(anomaly_data)}건")

    # 처음 10개 이상치의 Case ID 확인
    print("\n🔍 처음 10개 이상치 Case ID:")
    for i, item in enumerate(anomaly_data[:10]):
        print(f"  {i+1}. {item['Case_ID']} ({item['Anomaly_Type']})")

    # Excel 파일에서 Case NO 컬럼 확인
    df = pd.read_excel("../HVDC WAREHOUSE_HITACHI(HE).xlsx", sheet_name="Case List")
    print(f"\n📋 Excel 데이터: {len(df)}행")
    print(f"📋 컬럼명: {list(df.columns)}")

    # Case NO 컬럼 찾기
    case_col = None
    for col in df.columns:
        if "case" in str(col).lower():
            case_col = col
            break

    if case_col:
        print(f"📋 Case NO 컬럼: '{case_col}'")

        # 처음 10개 Case NO 확인
        print(f"\n🔍 처음 10개 Case NO:")
        for i, case_no in enumerate(df[case_col].head(10)):
            print(f"  {i+1}. '{case_no}'")

        # Case NO 유니크 값 개수
        unique_cases = df[case_col].nunique()
        print(f"\n📊 유니크 Case NO: {unique_cases}개")

        # JSON의 Case ID와 Excel의 Case NO 매칭 확인 (정규화 적용)
        json_case_ids = set(_norm_case(item["Case_ID"]) for item in anomaly_data)
        excel_case_nos = set(_norm_case(case) for case in df[case_col].dropna())

        print(f"\n🔍 매칭 분석:")
        print(f"  - JSON Case ID 수: {len(json_case_ids)}")
        print(f"  - Excel Case NO 수: {len(excel_case_nos)}")

        # 교집합 확인
        matched = json_case_ids & excel_case_nos
        print(f"  - 매칭된 케이스: {len(matched)}개")

        if len(matched) < 10:
            print(f"\n❌ 매칭된 케이스가 적습니다!")
            print(f"  - JSON Case ID 샘플: {list(json_case_ids)[:5]}")
            print(f"  - Excel Case NO 샘플: {list(excel_case_nos)[:5]}")
            print(f"  - 매칭된 케이스: {list(matched)[:5]}")
        else:
            print(f"  - 매칭된 케이스 샘플: {list(matched)[:5]}")
    else:
        print("❌ Case NO 컬럼을 찾을 수 없습니다!")


if __name__ == "__main__":
    debug_case_matching()

Case ID 매칭 디버깅 스크립트
"""

import json, re
import pandas as pd
from pathlib import Path

def _norm_case(s):
    return re.sub(r'[^A-Z0-9]', '', str(s).strip().upper()) if s is not None else ""


def debug_case_matching():
    """Case ID 매칭 문제 디버깅"""

    # JSON 파일에서 이상치 로드
    with open("hvdc_anomaly_report_v2.json", "r", encoding="utf-8") as f:
        anomaly_data = json.load(f)

    print(f"📊 JSON에서 로드된 이상치: {len(anomaly_data)}건")

    # 처음 10개 이상치의 Case ID 확인
    print("\n🔍 처음 10개 이상치 Case ID:")
    for i, item in enumerate(anomaly_data[:10]):
        print(f"  {i+1}. {item['Case_ID']} ({item['Anomaly_Type']})")

    # Excel 파일에서 Case NO 컬럼 확인
    df = pd.read_excel("../HVDC WAREHOUSE_HITACHI(HE).xlsx", sheet_name="Case List")
    print(f"\n📋 Excel 데이터: {len(df)}행")
    print(f"📋 컬럼명: {list(df.columns)}")

    # Case NO 컬럼 찾기
    case_col = None
    for col in df.columns:
        if "case" in str(col).lower():
            case_col = col
            break

    if case_col:
        print(f"📋 Case NO 컬럼: '{case_col}'")

        # 처음 10개 Case NO 확인
        print(f"\n🔍 처음 10개 Case NO:")
        for i, case_no in enumerate(df[case_col].head(10)):
            print(f"  {i+1}. '{case_no}'")

        # Case NO 유니크 값 개수
        unique_cases = df[case_col].nunique()
        print(f"\n📊 유니크 Case NO: {unique_cases}개")

        # JSON의 Case ID와 Excel의 Case NO 매칭 확인 (정규화 적용)
        json_case_ids = set(_norm_case(item["Case_ID"]) for item in anomaly_data)
        excel_case_nos = set(_norm_case(case) for case in df[case_col].dropna())

        print(f"\n🔍 매칭 분석:")
        print(f"  - JSON Case ID 수: {len(json_case_ids)}")
        print(f"  - Excel Case NO 수: {len(excel_case_nos)}")

        # 교집합 확인
        matched = json_case_ids & excel_case_nos
        print(f"  - 매칭된 케이스: {len(matched)}개")

        if len(matched) < 10:
            print(f"\n❌ 매칭된 케이스가 적습니다!")
            print(f"  - JSON Case ID 샘플: {list(json_case_ids)[:5]}")
            print(f"  - Excel Case NO 샘플: {list(excel_case_nos)[:5]}")
            print(f"  - 매칭된 케이스: {list(matched)[:5]}")
        else:
            print(f"  - 매칭된 케이스 샘플: {list(matched)[:5]}")
    else:
        print("❌ Case NO 컬럼을 찾을 수 없습니다!")


if __name__ == "__main__":
    debug_case_matching()
