# -*- coding: utf-8 -*-
"""창고_월별_입출고 데이터 디버깅"""
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

# 입고 결과 확인
logger.info("\n=== 입고 결과 (inbound_result) ===")
logger.info(f"총 입고: {stats['inbound_result'].get('total_inbound', 0)}")
logger.info(f"입고 항목 수: {len(stats['inbound_result'].get('inbound_items', []))}")
logger.info(f"창고간 이동 수: {len(stats['inbound_result'].get('warehouse_transfers', []))}")

# 입고 항목 샘플 확인
inbound_items = stats['inbound_result'].get('inbound_items', [])
if inbound_items:
    logger.info("\n입고 항목 샘플 (처음 5개):")
    for i, item in enumerate(inbound_items[:5], 1):
        logger.info(f"  {i}. Warehouse={item.get('Warehouse')}, Year_Month={item.get('Year_Month')}, "
                   f"Pkg_Quantity={item.get('Pkg_Quantity')}, Type={item.get('Inbound_Type')}")
else:
    logger.warning("⚠ inbound_items가 비어있습니다!")

# 창고별 입고 확인
by_warehouse = stats['inbound_result'].get('by_warehouse', {})
logger.info(f"\n창고별 입고:")
for warehouse, count in by_warehouse.items():
    logger.info(f"  {warehouse}: {count}")

# 월별 입고 확인
by_month = stats['inbound_result'].get('by_month', {})
logger.info(f"\n월별 입고 (처음 5개월):")
for i, (month, count) in enumerate(list(by_month.items())[:5], 1):
    logger.info(f"  {month}: {count}")

# 출고 결과 확인
logger.info("\n=== 출고 결과 (outbound_result) ===")
logger.info(f"총 출고: {stats['outbound_result'].get('total_outbound', 0)}")
logger.info(f"출고 항목 수: {len(stats['outbound_result'].get('outbound_items', []))}")

# 출고 항목 샘플
outbound_items = stats['outbound_result'].get('outbound_items', [])
if outbound_items:
    logger.info("\n출고 항목 샘플 (처음 5개):")
    for i, item in enumerate(outbound_items[:5], 1):
        logger.info(f"  {i}. From_Location={item.get('From_Location')}, Year_Month={item.get('Year_Month')}, "
                   f"Pkg_Quantity={item.get('Pkg_Quantity')}")
else:
    logger.warning("⚠ outbound_items가 비어있습니다!")

