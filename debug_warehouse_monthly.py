# -*- coding: utf-8 -*-
"""창고_월별_입출고 계산 디버깅 (상세)"""
import sys
import logging
from scripts.stage3_report.report_generator import HVDCExcelReporterFinal

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 리포터 초기화
reporter = HVDCExcelReporterFinal()

# 통계 계산
logger.info("통계 계산 중...")
stats = reporter.calculate_warehouse_statistics()

# 창고_월별_입출고 시트 생성
logger.info("\n=== 창고_월별_입출고 시트 생성 ===")
warehouse_monthly = reporter.create_warehouse_monthly_sheet(stats)

logger.info(f"시트 크기: {warehouse_monthly.shape}")
logger.info(f"컬럼: {list(warehouse_monthly.columns)}")

# 첫 5행 확인
logger.info(f"\n첫 5행 데이터:")
print(warehouse_monthly.head().to_string())

# 입고 데이터 확인
logger.info(f"\n입고 컬럼별 총합:")
for col in warehouse_monthly.columns:
    if col.startswith("입고_"):
        total = warehouse_monthly[col].sum()
        logger.info(f"  {col}: {total}")

# 특정 월의 데이터 확인 (2024-11월)
nov_2024 = warehouse_monthly[warehouse_monthly["입고월"] == "2024-11"]
if not nov_2024.empty:
    logger.info(f"\n2024-11월 데이터:")
    print(nov_2024.to_string())
else:
    logger.info(f"\n2024-11월 데이터 없음")

# inbound_items 상세 확인
inbound_items = stats["inbound_result"].get("inbound_items", [])
logger.info(f"\n=== inbound_items 상세 분석 ===")
logger.info(f"총 개수: {len(inbound_items)}")

# 월별/창고별 그룹화
from collections import defaultdict
monthly_warehouse = defaultdict(lambda: defaultdict(int))

for item in inbound_items:
    warehouse = item.get("Warehouse")
    year_month = item.get("Year_Month")
    pkg_qty = item.get("Pkg_Quantity", 1)
    inbound_type = item.get("Inbound_Type")
    
    monthly_warehouse[year_month][warehouse] += pkg_qty

logger.info(f"\n월별/창고별 집계 (처음 5개월):")
for i, (month, warehouses) in enumerate(list(monthly_warehouse.items())[:5], 1):
    logger.info(f"  {month}:")
    for warehouse, count in warehouses.items():
        logger.info(f"    {warehouse}: {count}")

# 2024-11월 특정 확인
nov_data = monthly_warehouse.get("2024-11", {})
logger.info(f"\n2024-11월 창고별 데이터:")
for warehouse, count in nov_data.items():
    logger.info(f"  {warehouse}: {count}")
