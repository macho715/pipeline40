# -*- coding: utf-8 -*-
"""창고_월별_입출고 시트 검증"""
import pandas as pd

excel_file = "data/processed/reports/HVDC_입고로직_종합리포트_20251023_235452_v3.0-corrected.xlsx"

# 모든 시트 이름 확인
xl = pd.ExcelFile(excel_file)
print("사용 가능한 시트 목록:")
for i, sheet in enumerate(xl.sheet_names, 1):
    print(f"  {i:2d}. {sheet}")

# 창고_월별_입출고 시트 확인
target_sheet = "창고_월별_입출고"
if target_sheet in xl.sheet_names:
    print(f"\n'{target_sheet}' 시트 발견!")
    df = pd.read_excel(excel_file, sheet_name=target_sheet)
    print(f"  - 행 수: {len(df)}")
    print(f"  - 컬럼 수: {len(df.columns)}")
    print(f"\n  - 첫 5개 컬럼:")
    for col in df.columns[:5]:
        print(f"    - {col}")

    print(f"\n  - 첫 3행 데이터:")
    print(df.head(3).to_string())

    # 데이터 값 확인
    print(f"\n  - 데이터 요약:")
    print(f"    - 총 행 수: {len(df)}")
    print(f"    - 입고월 범위: {df.iloc[:, 0].min()} ~ {df.iloc[:, 0].max()}")

    # 입고 컬럼 값 확인 (예: DHL WH)
    if len(df.columns) > 1:
        col_name = df.columns[1]
        total = df.iloc[:, 1].sum()
        print(f"    - {col_name} 입고 총합: {total}")

    # 모든 창고 컬럼의 총합 확인
    print(f"\n  - 창고별 입고 총합:")
    for i, col in enumerate(df.columns[1:], 1):
        if i <= 10:  # 처음 10개만 출력
            total = df.iloc[:, i].sum()
            print(f"    - {col}: {total}")
else:
    print(f"\n❌ '{target_sheet}' 시트를 찾을 수 없습니다!")
