"""창고 월별 입출고 시트 테스트 / Warehouse monthly IO sheet tests."""

from datetime import datetime, timedelta
import pandas as pd
from scripts.stage3_report.report_generator import HVDCExcelReporterFinal

def test_monthly_sheet_counts_warehouse_transfers_once():
    """창고간 이동 출고를 한 번만 계산한다 / Count transfer outbounds only once."""
    
    reporter = HVDCExcelReporterFinal()
    current_month = datetime.now().strftime("%Y-%m")
    inbound_date = pd.Timestamp(f"{current_month}-01")
    transfer_date = inbound_date + timedelta(days=2)
    
    stats = {
        "inbound_result": {
            "inbound_items": [
                {
                    "Item_ID": 1,
                    "Warehouse": "DHL WH",
                    "Inbound_Date": inbound_date,
                    "Year_Month": current_month,
                    "Pkg_Quantity": 10,
                    "Inbound_Type": "external_arrival",
                }
            ],
            "warehouse_transfers": [
                {
                    "Row_ID": 1,
                    "from_warehouse": "DHL WH",
                    "to_warehouse": "DSV Indoor",
                    "transfer_date": transfer_date,
                    "pkg_quantity": 5,
                    "transfer_type": "warehouse_to_warehouse",
                    "Year_Month": current_month,
                }
            ],
        },
        "outbound_result": {
            "outbound_items": [
                {
                    "Item_ID": 1,
                    "From_Location": "DHL WH",
                    "To_Location": "DSV Indoor",
                    "Outbound_Date": transfer_date,
                    "Year_Month": current_month,
                    "Pkg_Quantity": 5,
                    "Outbound_Type": "warehouse_transfer",
                },
                {
                    "Item_ID": 2,
                    "From_Location": "DSV Indoor",
                    "To_Location": "AGI",
                    "Outbound_Date": transfer_date + timedelta(days=2),
                    "Year_Month": current_month,
                    "Pkg_Quantity": 4,
                    "Outbound_Type": "warehouse_to_site",
                },
            ]
        },
    }
    
    sheet = reporter.create_warehouse_monthly_sheet(stats)
    month_row = sheet.loc[sheet["입고월"] == current_month].iloc[0]
    
    assert month_row["입고_DHL WH"] == 10
    assert month_row["출고_DHL WH"] == 5  # ← Only counted once
    assert month_row["출고_DSV Indoor"] == 4
