#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import glob

def main():
    # 최신 리포트 파일 찾기 (20251024_012115)
    latest_file = 'data/processed/reports/HVDC_입고로직_종합리포트_20251024_012115_v3.0-corrected.xlsx'
    
    print(f'최신 파일: {latest_file}')
    
    # 창고_월별_입출고 시트 읽기
    df = pd.read_excel(latest_file, sheet_name='창고_월별_입출고')
    print(f'시트 크기: {df.shape}')
    
    # Total 행 확인
    total_row = df[df['입고월'] == 'Total']
    if not total_row.empty:
        inbound_total = total_row['누계_입고'].iloc[0]
        outbound_total = total_row['누계_출고'].iloc[0]
        inventory = inbound_total - outbound_total
        
        print(f'\n=== 창고 월별 입출고 결과 ===')
        print(f'누계_입고: {inbound_total:,}')
        print(f'누계_출고: {outbound_total:,}')
        print(f'창고 재고 (입고-출고): {inventory:,}')
        
        # 목표 범위 확인
        print(f'\n=== 목표 범위 확인 ===')
        inbound_ok = "OK" if 5000 <= inbound_total <= 6000 else "FAIL"
        outbound_ok = "OK" if 3000 <= outbound_total <= 4000 else "FAIL"
        inventory_ok = "OK" if 2800 <= inventory <= 3200 else "FAIL"
        
        print(f'입고 목표: 5,000~6,000 | 실제: {inbound_total:,} | {inbound_ok}')
        print(f'출고 목표: 3,000~4,000 | 실제: {outbound_total:,} | {outbound_ok}')
        print(f'재고 목표: 2,800~3,200 | 실제: {inventory:,} | {inventory_ok}')
        
        # 창고별 상세 출고
        print(f'\n=== 창고별 출고 상세 ===')
        outbound_cols = [col for col in df.columns if col.startswith('출고_')]
        for col in outbound_cols:
            warehouse = col.replace('출고_', '')
            count = total_row[col].iloc[0]
            print(f'  {warehouse}: {count:,}')
    else:
        print('Total 행을 찾을 수 없습니다.')

if __name__ == '__main__':
    main()
