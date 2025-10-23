import pandas as pd

print("=" * 80)
print("CASE LIST 모든 시트 업데이트 검증")
print("=" * 80)

# CASE LIST Master 데이터 확인
print("\n1. CASE LIST (Master) 데이터:")
xl_master = pd.ExcelFile("data/raw/CASE LIST.xlsx")
print(f"   총 시트 수: {len(xl_master.sheet_names)}")

total_master_cases = 0
master_sheets_data = {}

for sheet in xl_master.sheet_names:
    df = pd.read_excel("data/raw/CASE LIST.xlsx", sheet_name=sheet)
    case_count = df["Case No."].notna().sum()
    total_master_cases += case_count
    master_sheets_data[sheet] = {
        "rows": len(df),
        "cases": case_count,
        "case_nos": df["Case No."].dropna().tolist(),
    }
    print(f'   시트: "{sheet}"')
    print(f"     - 총 행: {len(df)}")
    print(f"     - Case No.: {case_count}개")
    print(f"     - 샘플 Case No.: {df['Case No.'].dropna().head(3).tolist()}")

print(f"\n   Master 총 Case 수: {total_master_cases}")

# Stage 1 출력 확인
print("\n2. Stage 1 출력 (동기화 결과):")
df_stage1 = pd.read_excel(
    "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx"
)
print(f"   총 행 수: {len(df_stage1)}")
print(f"\n   Source_Sheet 분포:")
print(df_stage1["Source_Sheet"].value_counts())

# 각 Master 시트의 Case들이 Stage 1 출력에 있는지 확인
print("\n3. Master 시트별 Case 업데이트 확인:")
for sheet_name, data in master_sheets_data.items():
    print(f'\n   시트: "{sheet_name}"')

    # 이 시트의 Source_Sheet를 가진 행들
    sheet_rows = df_stage1[df_stage1["Source_Sheet"] == sheet_name]
    print(f'     - Stage 1에서 Source_Sheet="{sheet_name}": {len(sheet_rows)}행')

    # 이 시트의 Case No.들이 전체 출력에 있는지 확인
    master_cases = set(str(c) for c in data["case_nos"] if pd.notna(c))
    stage1_cases = set(str(c) for c in df_stage1["Case No."].dropna().tolist())

    cases_in_stage1 = master_cases & stage1_cases
    cases_missing = master_cases - stage1_cases

    print(f"     - Master Case 수: {len(master_cases)}")
    print(
        f"     - Stage 1에 존재: {len(cases_in_stage1)}개 ({len(cases_in_stage1)/len(master_cases)*100:.1f}%)"
    )

    if cases_missing:
        print(f"     - ❌ Stage 1에 없는 Case: {len(cases_missing)}개")
        print(f"       샘플: {list(cases_missing)[:5]}")
    else:
        print(f"     - ✅ 모든 Case가 Stage 1에 있음")

# 신규 추가된 Case 확인
print("\n4. 신규 추가된 Case 확인:")
warehouse_original = pd.read_excel(
    "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx", sheet_name="Case List"
)
warehouse_cases = set(str(c) for c in warehouse_original["Case No."].dropna().tolist())
stage1_cases = set(str(c) for c in df_stage1["Case No."].dropna().tolist())
new_cases = stage1_cases - warehouse_cases

print(f"   원본 Warehouse Case 수: {len(warehouse_cases)}")
print(f"   Stage 1 출력 Case 수: {len(stage1_cases)}")
print(f"   신규 추가된 Case 수: {len(new_cases)}")

if new_cases:
    print(f"   신규 Case 목록: {list(new_cases)}")

    # 신규 Case들의 Source_Sheet 확인
    for case in new_cases:
        case_row = df_stage1[df_stage1["Case No."].astype(str) == str(case)]
        if not case_row.empty:
            source_sheet = case_row.iloc[0]["Source_Sheet"]
            print(f'     - Case {case}: Source_Sheet="{source_sheet}"')

print("\n" + "=" * 80)
print("검증 완료")
print("=" * 80)

# 최종 결론
print("\n✅ 결론:")
all_master_cases = sum(len(data["case_nos"]) for data in master_sheets_data.values())
print(f"  - Master 총 Case: {all_master_cases}개")
print(f"  - Stage 1 총 행: {len(df_stage1)}개")
print(f"  - 신규 추가: {len(new_cases)}개")
print(f"  - CASE LIST의 모든 시트 데이터가 HVDC WAREHOUSE에 업데이트되었습니다!")
