# -*- coding: utf-8 -*-
import pandas as pd

excel_file = "data/processed/reports/HVDC_입고로직_종합리포트_20251023_235452_v3.0-corrected.xlsx"
df = pd.read_excel(excel_file, sheet_name="통합_원본데이터_Fixed")

print(f"총 컬럼 수: {len(df.columns)}")
print(f"\n첫 10개 컬럼:")
for i, col in enumerate(df.columns[:10], 1):
    print(f"{i:2d}. {col}")

# 주요 컬럼 위치 확인
key_columns = [
    "no.",
    "Shipment Invoice No.",
    "HVDC CODE",
    "SCT Ref.No",
    "Site",
    "SQM",
    "Stack_Status",
    "Total sqm",
]
print(f"\n주요 컬럼 위치:")
for col in key_columns:
    if col in df.columns:
        position = list(df.columns).index(col) + 1
        print(f"  {col:25s}: {position:2d}번째")
    else:
        print(f"  {col:25s}: 없음")
