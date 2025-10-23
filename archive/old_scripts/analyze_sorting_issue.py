# -*- coding: utf-8 -*-
"""
Master NO. 정렬 실패 원인 분석 스크립트
"""

import pandas as pd

# 데이터 로드
master_df = pd.read_excel("data/raw/Case List.xlsx")
warehouse_df = pd.read_excel("data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx")
synced_df = pd.read_excel(
    "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx"
)

print("=== 786번째 위치 불일치 원인 분석 ===\n")

# Master Case No. 순서
master_cases = master_df["Case No."].dropna().tolist()
synced_cases = synced_df["Case No."].dropna().tolist()

# 786번째 주변 확인
print("1. 786번째 주변 Case No. 비교:")
for i in range(783, 790):
    if i < len(master_cases) and i < len(synced_cases):
        match = "MATCH" if master_cases[i] == synced_cases[i] else "MISMATCH"
        print(
            f"   위치 {i}: Master={master_cases[i]}, Synced={synced_cases[i]} [{match}]"
        )

# Master에서 Case 208614, 208613의 위치 확인
print("\n2. Master 파일에서 Case 208613, 208614 위치:")
if 208613 in master_cases:
    pos_613 = master_cases.index(208613)
    print(f"   Case 208613: {pos_613}번째")
else:
    print("   Case 208613: Master에 없음")

if 208614 in master_cases:
    pos_614 = master_cases.index(208614)
    print(f"   Case 208614: {pos_614}번째")
else:
    print("   Case 208614: Master에 없음")

# Synced에서 Case 208614, 208613의 위치 확인
print("\n3. Synced 파일에서 Case 208613, 208614 위치:")
if 208613 in synced_cases:
    pos_613_synced = synced_cases.index(208613)
    print(f"   Case 208613: {pos_613_synced}번째")
else:
    print("   Case 208613: Synced에 없음")

if 208614 in synced_cases:
    pos_614_synced = synced_cases.index(208614)
    print(f"   Case 208614: {pos_614_synced}번째")
else:
    print("   Case 208614: Synced에 없음")

# Master에 NO. 컬럼이 있는지 확인
print("\n4. Master 파일의 NO. 컬럼 확인:")
if "No." in master_df.columns:
    print("   NO. 컬럼 존재: Yes")
    # 785~790번째 행의 NO. 값 확인
    print("   785~790번째 행의 NO. 값:")
    for i in range(785, 790):
        if i < len(master_df):
            no_val = (
                master_df.iloc[i]["No."]
                if pd.notna(master_df.iloc[i]["No."])
                else "NaN"
            )
            case_val = (
                master_df.iloc[i]["Case No."]
                if pd.notna(master_df.iloc[i]["Case No."])
                else "NaN"
            )
            print(f"   행 {i}: NO.={no_val}, Case No.={case_val}")
else:
    print("   NO. 컬럼 존재: No")
    print("   가능한 NO. 컬럼명:")
    for col in master_df.columns:
        if "no" in col.lower() or "num" in col.lower():
            print(f"     - {col}")

# Warehouse와의 비교
print("\n5. Warehouse에서 Case 208613, 208614 확인:")
warehouse_cases = warehouse_df["Case No."].dropna().tolist()
if 208613 in warehouse_cases:
    wh_pos_613 = warehouse_cases.index(208613)
    print(f"   Case 208613: Warehouse에 존재 (위치: {wh_pos_613})")
else:
    print("   Case 208613: Warehouse에 없음")

if 208614 in warehouse_cases:
    wh_pos_614 = warehouse_cases.index(208614)
    print(f"   Case 208614: Warehouse에 존재 (위치: {wh_pos_614})")
else:
    print("   Case 208614: Warehouse에 없음")

# 중복 Case 확인
print("\n6. Master에서 Case No. 중복 확인:")
master_duplicates = master_df[master_df["Case No."].duplicated(keep=False)]
if len(master_duplicates) > 0:
    print(f"   중복된 Case No. 수: {len(master_duplicates)}")
    dup_cases = master_duplicates["Case No."].unique()
    print(f"   중복된 Case No.: {dup_cases[:10]}")  # 처음 10개만

    # 208613, 208614가 중복인지 확인
    if 208613 in dup_cases:
        print(f"   Case 208613은 중복됨")
    if 208614 in dup_cases:
        print(f"   Case 208614은 중복됨")
else:
    print("   중복된 Case No. 없음")

# 정렬 로직 분석
print("\n7. 정렬 로직 분석:")
print("   예상 정렬 순서: Master의 NO. 컬럼 순서")
print("   실제 Synced 순서: 786번째부터 불일치")
print("\n   가능한 원인:")
print("   1) Master NO. 컬럼이 없거나 올바르지 않음")
print("   2) Case No. 중복으로 인해 일부 행이 누락되거나 순서가 바뀜")
print("   3) _apply_updates 과정에서 행 순서가 재배치됨")
print("   4) _maintain_master_order가 제대로 실행되지 않음")
print("   5) Master와 Warehouse에서 동일 Case No.가 다른 위치에 있음")
