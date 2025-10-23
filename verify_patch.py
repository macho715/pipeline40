# -*- coding: utf-8 -*-
import pandas as pd

excel_file = 'data/processed/reports/HVDC_입고로직_종합리포트_20251023_233328_v3.0-corrected.xlsx'
df = pd.read_excel(excel_file, sheet_name='통합_원본데이터_Fixed')

print(f'Excel 파일 컬럼 수: {len(df.columns)}')
print(f'Total sqm 존재: {"Total sqm" in df.columns}')
print(f'Stack_Status 존재: {"Stack_Status" in df.columns}')
print(f'SQM 존재: {"SQM" in df.columns}')
print(f'\n컬럼 50-56: {list(df.columns[50:56])}')
print(f'\nTotal sqm 샘플 데이터 (상위 5개):')
print(df[['SQM', 'Stack_Status', 'Total sqm', 'PKG']].head())

