import pandas as pd

print("=" * 80)
print("Master DataFrame Source_Sheet 확인")
print("=" * 80)

# Master 파일을 직접 로딩하여 Source_Sheet 확인
xl = pd.ExcelFile("data/raw/CASE LIST.xlsx")
all_dfs = []

for sheet_name in xl.sheet_names:
    df = pd.read_excel("data/raw/CASE LIST.xlsx", sheet_name=sheet_name)
    df["Source_Sheet"] = sheet_name
    all_dfs.append(df)
    print(f"시트: '{sheet_name}'")
    print(f"  - 행 수: {len(df)}")
    print(f"  - Source_Sheet 설정: '{sheet_name}'")

# Master DataFrame 병합
master_df = pd.concat(all_dfs, ignore_index=True, sort=False)
print(f"\n병합된 Master DataFrame:")
print(f"  - 총 행 수: {len(master_df)}")
print(f"  - Source_Sheet 분포:")
print(master_df["Source_Sheet"].value_counts())

# 각 시트별 Case No. 샘플 확인
print(f"\n각 시트별 Case No. 샘플:")
for sheet_name in master_df["Source_Sheet"].unique():
    sheet_data = master_df[master_df["Source_Sheet"] == sheet_name]
    sample_cases = sheet_data["Case No."].dropna().head(5).tolist()
    print(f"  {sheet_name}: {len(sheet_data)}행")
    print(f"    샘플 Case No.: {sample_cases}")

print("\n" + "=" * 80)
