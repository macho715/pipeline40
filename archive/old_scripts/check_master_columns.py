# -*- coding: utf-8 -*-
import pandas as pd

master = pd.read_excel("data/raw/Case List.xlsx")
print("Master 컬럼 목록:")
for i, col in enumerate(master.columns):
    print(f"{i+1}. {col}")

print(f"\n총 {len(master.columns)}개 컬럼")

# No 컬럼 확인
if "No" in master.columns:
    print('\n"No" 컬럼 존재')
    print(f'첫 10개 값: {master["No"].head(10).tolist()}')
elif "No." in master.columns:
    print('\n"No." 컬럼 존재')
    print(f'첫 10개 값: {master["No."].head(10).tolist()}')
else:
    print("\nNO 컬럼이 없음")
