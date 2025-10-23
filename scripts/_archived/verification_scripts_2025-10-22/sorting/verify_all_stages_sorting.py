"""Verify sorting is maintained across all pipeline stages"""
import pandas as pd
from pathlib import Path

def check_sorting(file_path, stage_name):
    """Check if file is sorted by (No, Case No.)"""
    if not Path(file_path).exists():
        print(f"\n❌ {stage_name}: File not found - {file_path}")
        return False
    
    try:
        df = pd.read_excel(file_path)
        
        if 'No' not in df.columns or 'Case No.' not in df.columns:
            print(f"\n❌ {stage_name}: Missing columns")
            print(f"   Available columns: {df.columns.tolist()[:10]}...")
            return False
        
        # Check compound sort
        sorted_df = df.sort_values(['No', 'Case No.'])
        is_sorted = df[['No', 'Case No.']].equals(sorted_df[['No', 'Case No.']])
        
        print(f"\n{'='*70}")
        print(f"{stage_name}")
        print(f"{'='*70}")
        print(f"File: {Path(file_path).name}")
        print(f"Total rows: {len(df)}")
        print(f"Sorted by (No, Case No.): {is_sorted}")
        
        if is_sorted:
            print("✅ PASS: Properly sorted")
        else:
            print("❌ FAIL: NOT properly sorted")
            # Find first mismatch
            for i in range(min(20, len(df))):
                if df.iloc[i]['No'] != sorted_df.iloc[i]['No'] or \
                   df.iloc[i]['Case No.'] != sorted_df.iloc[i]['Case No.']:
                    print(f"\nFirst mismatch at row {i+1}:")
                    print(f"  Current: No={df.iloc[i]['No']}, Case={df.iloc[i]['Case No.']}")
                    print(f"  Expected: No={sorted_df.iloc[i]['No']}, Case={sorted_df.iloc[i]['Case No.']}")
                    break
        
        # Show first 10 records
        print("\nFirst 10 records:")
        for i in range(min(10, len(df))):
            print(f"  Row {i+1}: No={df.iloc[i]['No']}, Case={df.iloc[i]['Case No.']}")
        
        return is_sorted
        
    except Exception as e:
        print(f"\n❌ {stage_name}: Error reading file - {e}")
        return False

# Check all stages
print("="*70)
print("HVDC Pipeline Sorting Verification - All Stages")
print("="*70)

results = {}

# Stage 1
results['Stage 1'] = check_sorting(
    'data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx',
    'Stage 1: Data Synchronization'
)

# Stage 2
results['Stage 2'] = check_sorting(
    'data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx',
    'Stage 2: Derived Columns'
)

# Stage 3 - Check the latest report
import glob
reports = glob.glob('data/processed/reports/HVDC_입고로직_종합리포트_*.xlsx')
if reports:
    latest_report = max(reports)
    print(f"\n{'='*70}")
    print(f"Stage 3: Report Generation")
    print(f"{'='*70}")
    print(f"Checking sheet: 통합_원본데이터_Fixed")
    
    try:
        df = pd.read_excel(latest_report, sheet_name='통합_원본데이터_Fixed')
        
        if 'No' in df.columns and 'Case No.' in df.columns:
            sorted_df = df.sort_values(['No', 'Case No.'])
            is_sorted = df[['No', 'Case No.']].equals(sorted_df[['No', 'Case No.']])
            
            print(f"File: {Path(latest_report).name}")
            print(f"Total rows: {len(df)}")
            print(f"Sorted by (No, Case No.): {is_sorted}")
            
            if is_sorted:
                print("✅ PASS: Properly sorted")
            else:
                print("❌ FAIL: NOT properly sorted")
            
            # Show first 10 records
            print("\nFirst 10 records:")
            for i in range(min(10, len(df))):
                print(f"  Row {i+1}: No={df.iloc[i]['No']}, Case={df.iloc[i]['Case No.']}")
            
            results['Stage 3'] = is_sorted
        else:
            print("❌ Missing columns in Stage 3 sheet")
            results['Stage 3'] = False
            
    except Exception as e:
        print(f"❌ Error reading Stage 3 sheet: {e}")
        results['Stage 3'] = False
else:
    print("\n❌ Stage 3: No report found")
    results['Stage 3'] = False

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

all_passed = True
for stage, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{stage}: {status}")
    if not passed:
        all_passed = False

print(f"\n{'='*70}")
if all_passed:
    print("✅ ALL STAGES: Sorting maintained throughout pipeline")
else:
    print("❌ FAILURE: Some stages have incorrect sorting")
    print("\n⚠️ REQUIRED FIX: Ensure all stages preserve (No, Case No.) sort order")
print(f"{'='*70}")

