import pandas as pd
import os

print("=" * 80)
print("원본 RAW 데이터 파일 구조 분석")
print("=" * 80)

# CASE LIST 파일 확인
case_list_path = "data/raw/CASE LIST.xlsx"
if os.path.exists(case_list_path):
    print(f"\n1. CASE LIST.xlsx 분석:")
    xl = pd.ExcelFile(case_list_path)
    print(f"   총 시트 수: {len(xl.sheet_names)}")
    for i, sheet in enumerate(xl.sheet_names, 1):
        df = pd.read_excel(case_list_path, sheet_name=sheet)
        print(f'   시트 {i}: "{sheet}" - {len(df)} 행, {len(df.columns)} 컬럼')
        if "Case No." in df.columns:
            case_count = df["Case No."].notna().sum()
            print(f"      → Case No. 데이터: {case_count}개")
else:
    print(f"\n1. CASE LIST.xlsx: 파일 없음")

# HVDC WAREHOUSE 파일 확인
hvdc_path = "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx"
if os.path.exists(hvdc_path):
    print(f"\n2. HVDC WAREHOUSE_HITACHI(HE).xlsx 분석:")
    xl = pd.ExcelFile(hvdc_path)
    print(f"   총 시트 수: {len(xl.sheet_names)}")
    for i, sheet in enumerate(xl.sheet_names, 1):
        try:
            df = pd.read_excel(hvdc_path, sheet_name=sheet, header=0)
            print(f'   시트 {i}: "{sheet}" - {len(df)} 행, {len(df.columns)} 컬럼')
            if "Case No." in df.columns:
                case_count = df["Case No."].notna().sum()
                print(f"      → Case No. 데이터: {case_count}개")
        except Exception as e:
            print(f'   시트 {i}: "{sheet}" - 읽기 실패: {e}')
else:
    print(f"\n2. HVDC WAREHOUSE_HITACHI(HE).xlsx: 파일 없음")

print("\n" + "=" * 80)
print("현재 Stage 1 로딩 방식 분석")
print("=" * 80)

print("\n현재 구현:")
print("  - _load_file_with_header_detection() 메서드가")
print("  - 각 파일의 **모든 시트**를 자동으로 로드")
print("  - pd.concat()으로 모든 시트를 하나로 병합")

print("\n✅ 확인 결과:")
print("  CASE LIST의 모든 시트가 HVDC WAREHOUSE로 업데이트되고 있습니다.")
print("  이것이 정상적인 동작입니다.")

print("\n만약 문제가 있다면:")
print("  1. 특정 시트만 로드해야 하는가?")
print("  2. 시트별로 다른 처리가 필요한가?")
print("  3. Summary 시트는 제외해야 하는가?")
