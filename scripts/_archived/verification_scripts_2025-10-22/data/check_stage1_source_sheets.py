import pandas as pd

print("=" * 80)
print("Stage 1: Source_Sheet 분석")
print("=" * 80)

df = pd.read_excel(
    "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx"
)

print(f"\n총 행 수: {len(df)}")
print(f"총 컬럼 수: {len(df.columns)}")

print(f"\nSource_Sheet 컬럼 값 분포:")
print(df["Source_Sheet"].value_counts())

print(f"\nCASE LIST에서 온 데이터 확인:")
case_list_ril = df[df["Source_Sheet"] == "Case List, RIL"]
capacitor = df[df["Source_Sheet"] == "HE-0214,0252 (Capacitor)"]

print(f'  - "Case List, RIL" 시트: {len(case_list_ril)} 행')
if len(case_list_ril) > 0:
    print(f'    샘플 Case No.: {case_list_ril["Case No."].head(5).tolist()}')

print(f'  - "HE-0214,0252 (Capacitor)" 시트: {len(capacitor)} 행')
if len(capacitor) > 0:
    print(f'    샘플 Case No.: {capacitor["Case No."].head(5).tolist()}')

print(f"\nHVDC WAREHOUSE에서 온 데이터:")
case_list = df[df["Source_Sheet"] == "Case List"]
summary = df[df["Source_Sheet"] == "Summary"]
print(f'  - "Case List" 시트: {len(case_list)} 행')
print(f'  - "Summary" 시트: {len(summary)} 행')

print("\n" + "=" * 80)
print("분석 결과")
print("=" * 80)

total_master = len(case_list_ril) + len(capacitor)
print(f"\nCASE LIST(Master) 데이터: {total_master} 행")
print(f"HVDC WAREHOUSE 기존 데이터: {len(case_list) + len(summary)} 행")
print(f"총합: {len(df)} 행")

if total_master == 0:
    print("\n⚠️ 심각한 문제!")
    print("Stage 1에서 CASE LIST의 Source_Sheet 정보가 유실되었습니다!")
    print("\n원인:")
    print("  _apply_updates()에서 Master 데이터를 Warehouse에 업데이트할 때")
    print("  Source_Sheet 컬럼도 Warehouse 값으로 덮어씌워짐")
else:
    print("\n✅ Stage 1에서는 Source_Sheet 정보가 올바르게 유지됩니다.")
