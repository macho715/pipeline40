# -*- coding: utf-8 -*-
import pandas as pd

excel_file = "data/processed/reports/HVDC_입고로직_종합리포트_20251023_233328_v3.0-corrected.xlsx"
df = pd.read_excel(excel_file, sheet_name="통합_원본데이터_Fixed")

print(f"총 컬럼 수: {len(df.columns)}")
print(f'SCT Ref.No 존재: {"SCT Ref.No" in df.columns}')

# SCT 관련 컬럼 찾기
sct_cols = [col for col in df.columns if "sct" in col.lower() or "ref" in col.lower()]
print(f"\nSCT/Ref 관련 컬럼: {sct_cols}")

print(f"\n전체 컬럼 목록:")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")
