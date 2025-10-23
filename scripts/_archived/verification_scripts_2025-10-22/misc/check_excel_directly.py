import pandas as pd

print("=" * 80)
print("엑셀 파일 직접 확인")
print("=" * 80)

# Stage 1 출력 파일 확인
print("\n1. Stage 1 출력 파일 (HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx):")
df = pd.read_excel(
    "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx"
)

print(f"   총 행 수: {len(df)}")
print(f"   총 컬럼 수: {len(df.columns)}")

# Source_Sheet 컬럼 확인
if "Source_Sheet" in df.columns:
    print(f"\n   Source_Sheet 컬럼 존재: 예")
    print(f"\n   Source_Sheet 값 분포:")
    print(df["Source_Sheet"].value_counts())

    print(f"\n   고유 Source_Sheet 값:")
    for val in df["Source_Sheet"].unique():
        print(f'     - "{val}"')

    # 각 Source_Sheet별 샘플 Case No. 확인
    print(f"\n   각 Source_Sheet별 샘플 Case No.:")
    for source_sheet in df["Source_Sheet"].unique():
        sheet_data = df[df["Source_Sheet"] == source_sheet]
        sample_cases = sheet_data["Case No."].dropna().head(5).tolist()
        print(f"     {source_sheet}: {len(sheet_data)}행")
        print(f"       샘플 Case No.: {sample_cases}")
else:
    print(f"\n   ❌ Source_Sheet 컬럼이 없습니다!")

# Master 파일의 시트별 Case 확인
print("\n" + "=" * 80)
print("2. CASE LIST (Master) 각 시트의 Case No.:")
print("=" * 80)

xl = pd.ExcelFile("data/raw/CASE LIST.xlsx")
for sheet_name in xl.sheet_names:
    df_sheet = pd.read_excel("data/raw/CASE LIST.xlsx", sheet_name=sheet_name)
    sample_cases = df_sheet["Case No."].dropna().head(10).tolist()
    print(f'\n   시트: "{sheet_name}"')
    print(f"     총 행: {len(df_sheet)}")
    print(f"     Case No. 개수: {df_sheet['Case No.'].notna().sum()}")
    print(f"     첫 10개 Case No.: {sample_cases}")

# Stage 1 출력에서 특정 Case 검색
print("\n" + "=" * 80)
print("3. Stage 1 출력에서 Master 시트의 Case 검색:")
print("=" * 80)

# "Case List, RIL" 시트의 첫 10개 Case가 Stage 1에 있는지
df_ril = pd.read_excel("data/raw/CASE LIST.xlsx", sheet_name="Case List, RIL")
ril_cases = df_ril["Case No."].dropna().head(10).tolist()

print(f"\n   'Case List, RIL' 시트의 첫 10개 Case:")
for case in ril_cases:
    case_in_stage1 = df[df["Case No."] == case]
    if not case_in_stage1.empty:
        source_sheet = case_in_stage1.iloc[0]["Source_Sheet"]
        print(f'     Case {case}: Stage 1에 존재, Source_Sheet="{source_sheet}"')
    else:
        print(f"     Case {case}: ❌ Stage 1에 없음")

# "HE-0214,0252 (Capacitor)" 시트의 첫 10개 Case
df_cap = pd.read_excel("data/raw/CASE LIST.xlsx", sheet_name="HE-0214,0252 (Capacitor)")
cap_cases = df_cap["Case No."].dropna().head(10).tolist()

print(f"\n   'HE-0214,0252 (Capacitor)' 시트의 첫 10개 Case:")
for case in cap_cases:
    case_in_stage1 = df[df["Case No."] == case]
    if not case_in_stage1.empty:
        source_sheet = case_in_stage1.iloc[0]["Source_Sheet"]
        print(f'     Case {case}: Stage 1에 존재, Source_Sheet="{source_sheet}"')
    else:
        print(f"     Case {case}: ❌ Stage 1에 없음")

print("\n" + "=" * 80)
