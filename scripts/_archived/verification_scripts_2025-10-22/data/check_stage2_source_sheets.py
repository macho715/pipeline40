import pandas as pd

print("=" * 80)
print("Stage 2: Source_Sheet 분석")
print("=" * 80)

df = pd.read_excel("data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx")

print(f"\n총 행 수: {len(df)}")
print(f"총 컬럼 수: {len(df.columns)}")

print(f"\nSource_Sheet 컬럼 값 분포:")
print(df["Source_Sheet"].value_counts())

print(f"\nCASE LIST에서 온 데이터 확인:")
case_list_ril = df[df["Source_Sheet"] == "Case List, RIL"]
capacitor = df[df["Source_Sheet"] == "HE-0214,0252 (Capacitor)"]

print(f'  - "Case List, RIL" 시트: {len(case_list_ril)} 행')
print(f'  - "HE-0214,0252 (Capacitor)" 시트: {len(capacitor)} 행')

print(f"\nHVDC WAREHOUSE에서 온 데이터:")
case_list = df[df["Source_Sheet"] == "Case List"]
summary = df[df["Source_Sheet"] == "Summary"]
print(f'  - "Case List" 시트: {len(case_list)} 행')
print(f'  - "Summary" 시트: {len(summary)} 행')

print("\n" + "=" * 80)
print("분석 결과")
print("=" * 80)

if len(case_list_ril) == 0 and len(capacitor) == 0:
    print("\n⚠️ 문제 발견!")
    print("Stage 2 결과에 CASE LIST의 원본 시트 정보가 없습니다.")
    print('모든 데이터가 HVDC WAREHOUSE의 "Case List" 시트로만 표시됩니다.')
    print("\n예상 원인:")
    print("  Stage 1에서 Master(CASE LIST) 데이터를 Warehouse로 업데이트할 때")
    print("  Source_Sheet 정보가 Warehouse의 기존 값으로 덮어씌워졌을 가능성")
else:
    print("\n✅ 정상!")
    print("CASE LIST의 모든 시트 데이터가 포함되어 있습니다.")

print(f"\n샘플 데이터 확인 (처음 20행):")
print(df[["no.", "Case No.", "Source_Sheet"]].head(20))
