import pandas as pd

print("=" * 80)
print("Master DataFrame 정렬 후 Source_Sheet 확인")
print("=" * 80)

# 1. Master 파일 로딩 및 병합 (Stage 1과 동일한 방식)
xl = pd.ExcelFile("data/raw/CASE LIST.xlsx")
all_dfs = []

for sheet_name in xl.sheet_names:
    df = pd.read_excel("data/raw/CASE LIST.xlsx", sheet_name=sheet_name)
    df["Source_Sheet"] = sheet_name
    all_dfs.append(df)
    print(f"\n로딩: '{sheet_name}' - {len(df)}행")
    print(f"  Source_Sheet 설정: '{sheet_name}'")
    print(f"  샘플 Case No.: {df['Case No.'].dropna().head(3).tolist()}")

# 2. 병합
master_df = pd.concat(all_dfs, ignore_index=True, sort=False)
print(f"\n병합 후:")
print(f"  총 행 수: {len(master_df)}")
print(f"  Source_Sheet 분포:")
print(master_df["Source_Sheet"].value_counts())

# 3. 정렬 (Stage 1과 동일한 방식 - NO, Case No.로 정렬)
print(f"\n정렬 수행: (NO, Case No.)...")
sorted_master = master_df.sort_values(
    ["NO", "Case No."], na_position="last"
).reset_index(drop=True)

print(f"\n정렬 후 Source_Sheet 분포:")
print(sorted_master["Source_Sheet"].value_counts())

# 4. 정렬 후 각 시트의 Case들 확인
print(f"\n정렬 후 각 시트별 Case No. 샘플:")
for sheet_name in sorted_master["Source_Sheet"].unique():
    sheet_data = sorted_master[sorted_master["Source_Sheet"] == sheet_name]
    sample_cases = sheet_data["Case No."].dropna().head(5).tolist()
    print(f"  {sheet_name}: {len(sheet_data)}행")
    print(f"    샘플 Case No.: {sample_cases}")

# 5. 정렬 후 첫 20개 행의 Source_Sheet 확인
print(f"\n정렬 후 첫 20개 행:")
print(sorted_master[["NO", "Case No.", "Source_Sheet"]].head(20))

# 6. HE-0214,0252 (Capacitor) 시트의 Case들이 어디에 있는지 확인
capacitor_cases = sorted_master[
    sorted_master["Source_Sheet"] == "HE-0214,0252 (Capacitor)"
]
print(f"\n'HE-0214,0252 (Capacitor)' 시트 데이터:")
print(f"  총 행 수: {len(capacitor_cases)}")
print(f"  첫 10개 Case No.:")
print(capacitor_cases[["NO", "Case No.", "Source_Sheet"]].head(10))

print("\n" + "=" * 80)
