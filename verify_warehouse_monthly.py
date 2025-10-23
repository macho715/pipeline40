#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import glob

def main():
    # 최신 리포트 파일 찾기
    files = glob.glob('data/processed/reports/HVDC_*_v3.0-corrected.xlsx')
    latest_file = max(files, key=lambda x: x.split('_')[-2])
    
    print(f'최신 파일: {latest_file}')
    
    # 창고_월별_입출고 시트 읽기
    df = pd.read_excel(latest_file, sheet_name='창고_월별_입출고')
    print(f'시트 크기: {df.shape}')
    
    # Total 행 확인
    total_row = df[df['입고월'] == 'Total']
    if not total_row.empty:
        print('Total 행:')
        print(f'  누계_입고: {total_row["누계_입고"].iloc[0]}')
        print(f'  누계_출고: {total_row["누계_출고"].iloc[0]}')
        
        # 창고별 출고 합계
        outbound_cols = [col for col in df.columns if col.startswith('출고_')]
        total_outbound = sum(total_row[col].iloc[0] for col in outbound_cols)
        print(f'  창고별 출고 합계: {total_outbound}')
        
        # 창고별 상세 출고
        print('\n창고별 출고 상세:')
        for col in outbound_cols:
            warehouse = col.replace('출고_', '')
            count = total_row[col].iloc[0]
            print(f'  {warehouse}: {count}')
    else:
        print('Total 행을 찾을 수 없습니다.')

if __name__ == '__main__':
    main()
