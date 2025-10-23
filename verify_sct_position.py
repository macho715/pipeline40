# -*- coding: utf-8 -*-
import pandas as pd

excel_file = "data/processed/reports/HVDC_입고로직_종합리포트_20251023_234735_v3.0-corrected.xlsx"
df = pd.read_excel(excel_file, sheet_name="통합_원본데이터_Fixed")

print(f"총 컬럼 수: {len(df.columns)}")
print(f"\n첫 10개 컬럼:")
for i, col in enumerate(df.columns[:10], 1):
    print(f"{i:2d}. {col}")

print(f"\nSCT Ref.No 위치 확인:")
if "SCT Ref.No" in df.columns:
    sct_position = list(df.columns).index("SCT Ref.No") + 1
    print(f"✅ SCT Ref.No: {sct_position}번째 위치")
else:
    print("❌ SCT Ref.No 없음")

print(f"\nShipment Invoice No. 위치 확인:")
if "Shipment Invoice No." in df.columns:
    invoice_position = list(df.columns).index("Shipment Invoice No.") + 1
    print(f"✅ Shipment Invoice No.: {invoice_position}번째 위치")
else:
    print("❌ Shipment Invoice No. 없음")

print(f"\nHVDC CODE 위치 확인:")
if "HVDC CODE" in df.columns:
    hvdccode_position = list(df.columns).index("HVDC CODE") + 1
    print(f"✅ HVDC CODE: {hvdccode_position}번째 위치")
else:
    print("❌ HVDC CODE 없음")
