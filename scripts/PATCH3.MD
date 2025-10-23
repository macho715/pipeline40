diff --git a/CHANGELOG.md b/CHANGELOG.md
index c7e9f46811c91e3d3e1003a3b33e1c58c729b51e..d8e112c88226e7833d83aa256df97408db658853 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -1,32 +1,43 @@
 # Changelog

 All notable changes to the HVDC Pipeline project will be documented in this file.

 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

+## [4.0.27] - 2025-10-24
+
+### 🐛 Fixed
+
+#### 창고_월별_입출고 출고 중복 합산 제거
+- **Problem**: 창고_월별_입출고 시트에서 창고간 이동 출고가 두 번 합산되어 월별 출고 합계가 실제보다 약 3,000건 크게 집계됨
+- **Solution**: 창고 월별 집계 시 창고간 이동 출고를 `outbound_result` 집계 결과로만 계산하여 중복 제거
+- **Result**:
+  - 창고간 이동 출고 실수령 수량과 월별 출고 합계 정합성 확보
+  - 총입고 − 총출고 = 창고 재고 관계가 복원되어 재고 검증 정확도 개선
+
 ## [4.0.26] - 2025-10-24

 ### 🐛 Fixed

 #### 창고 출고 계산 로직 개선
 - **Problem**: 벡터화 출고 계산에서 창고→현장 이동 감지가 매우 낮음 (6개)
   - 기존 로직이 "다음 날 이동만 출고로 인정"하여 너무 엄격한 조건
   - 창고간 이동 제외 로직이 너무 광범위하게 적용됨
 - **Solution**:
   - 날짜 조건을 `site_date.date() > wh_date.date()`로 완화
   - 창고간 이동 제외 로직 제거
 - **Result**:
   - 창고→현장 이동 감지: 6개 → 588개 (98배 개선)
   - 창고_월별_입출고 시트의 출고 데이터 정확도 향상
   - 벡터화 출고 계산 성능 유지

 ## [4.0.25] - 2025-10-24

 ### 🐛 Fixed

 #### 창고_월별_입출고 계산 수정
 - **Problem**: 창고_월별_입출고 시트의 데이터가 대부분 0으로 표시
   - 벡터화 입고 계산에서 Inbound_Type 필드 누락
   - create_warehouse_monthly_sheet()에서 조건 미충족
 - **Solution**: _calculate_warehouse_inbound_vectorized()에 Inbound_Type 명시적 설정
diff --git a/scripts/stage3_report/report_generator.py b/scripts/stage3_report/report_generator.py
index 407ba1d8f8d013fab18ac2b4d3650d6ec7fbf78d..3acfa1d32c06fe2cff20bff38db81b2d6d10f724 100644
--- a/scripts/stage3_report/report_generator.py
+++ b/scripts/stage3_report/report_generator.py
@@ -2776,109 +2776,152 @@ class HVDCExcelReporterFinal:
             "outbound_result": outbound_result,
             "inventory_result": inventory_result,
             "direct_result": direct_result,
             "inbound_pivot": inbound_pivot,
             "processed_data": df,
             #  NEW: SQM 관련 결과 추가
             "sqm_inbound": sqm_inbound,
             "sqm_outbound": sqm_outbound,
             "sqm_cumulative_inventory": sqm_cumulative,
             "sqm_invoice_charges": sqm_charges,
             "sqm_data_quality": sqm_quality,
         }

     def create_warehouse_monthly_sheet(self, stats: Dict) -> pd.DataFrame:
         """창고_월별_입출고 시트 생성 (동일 날짜 창고간 이동 반영)"""
         logger.info(" 창고_월별_입출고 시트 생성 (창고간 이동 반영)")

         # 월별 기간 생성 (2023-02 ~ 현재 월까지 동적 계산)
         end_month = datetime.now().strftime("%Y-%m")
         months = pd.date_range("2023-02", end_month, freq="MS")
         month_strings = [month.strftime("%Y-%m") for month in months]

         # 결과 DataFrame 초기화
         results = []

+        #  Stage-1 정규화 순서 기반 창고 목록 사용
+        warehouses = list(self.calculator.warehouse_columns)
+        warehouse_display_names = list(self.calculator.warehouse_columns)
+
+        # 벡터화된 입고/출고 맵 생성
+        inbound_items = stats["inbound_result"].get("inbound_items", [])
+        inbound_df = pd.DataFrame(inbound_items)
+
+        if not inbound_df.empty:
+            inbound_df = inbound_df.copy()
+            if "Inbound_Type" in inbound_df.columns:
+                inbound_df = inbound_df[
+                    inbound_df["Inbound_Type"].astype(str).str.lower()
+                    == "external_arrival"
+                ]
+            if "Year_Month" not in inbound_df.columns:
+                inbound_df["Inbound_Date"] = pd.to_datetime(
+                    inbound_df.get("Inbound_Date"), errors="coerce"
+                )
+                inbound_df["Year_Month"] = inbound_df["Inbound_Date"].dt.strftime("%Y-%m")
+            inbound_df["Year_Month"] = inbound_df["Year_Month"].astype(str)
+            inbound_df["Warehouse"] = inbound_df["Warehouse"].astype(str)
+            inbound_df["Pkg_Quantity"] = pd.to_numeric(
+                inbound_df.get("Pkg_Quantity", inbound_df.get("pkg_quantity", 0)),
+                errors="coerce",
+            ).fillna(0).astype(int)
+            external_inbound_map = (
+                inbound_df.groupby(["Year_Month", "Warehouse"])["Pkg_Quantity"]
+                .sum()
+                .to_dict()
+            )
+        else:
+            external_inbound_map = {}
+
+        transfer_items = stats["inbound_result"].get("warehouse_transfers", [])
+        transfer_df = pd.DataFrame(transfer_items)
+
+        if not transfer_df.empty:
+            transfer_df = transfer_df.copy()
+            if "Year_Month" not in transfer_df.columns:
+                transfer_df["transfer_date"] = pd.to_datetime(
+                    transfer_df.get("transfer_date"), errors="coerce"
+                )
+                transfer_df["Year_Month"] = transfer_df["transfer_date"].dt.strftime("%Y-%m")
+            transfer_df["Year_Month"] = transfer_df["Year_Month"].astype(str)
+            transfer_df["to_warehouse"] = transfer_df["to_warehouse"].astype(str)
+            transfer_df["Transfer_Quantity"] = pd.to_numeric(
+                transfer_df.get("pkg_quantity", transfer_df.get("Pkg_Quantity", 0)),
+                errors="coerce",
+            ).fillna(0).astype(int)
+            transfer_inbound_map = (
+                transfer_df.groupby(["Year_Month", "to_warehouse"])["Transfer_Quantity"]
+                .sum()
+                .to_dict()
+            )
+        else:
+            transfer_inbound_map = {}
+
+        outbound_items = stats["outbound_result"].get("outbound_items", [])
+        outbound_df = pd.DataFrame(outbound_items)
+
+        if not outbound_df.empty:
+            outbound_df = outbound_df.copy()
+            if "Year_Month" not in outbound_df.columns:
+                outbound_df["Outbound_Date"] = pd.to_datetime(
+                    outbound_df.get("Outbound_Date"), errors="coerce"
+                )
+                outbound_df["Year_Month"] = outbound_df["Outbound_Date"].dt.strftime("%Y-%m")
+            outbound_df["Year_Month"] = outbound_df["Year_Month"].astype(str)
+            outbound_df["From_Location"] = outbound_df["From_Location"].astype(str)
+            outbound_df["Pkg_Quantity"] = pd.to_numeric(
+                outbound_df.get("Pkg_Quantity", outbound_df.get("pkg_quantity", 0)),
+                errors="coerce",
+            ).fillna(0).astype(int)
+            outbound_map = (
+                outbound_df.groupby(["Year_Month", "From_Location"])["Pkg_Quantity"]
+                .sum()
+                .to_dict()
+            )
+        else:
+            outbound_map = {}
+
         for month_str in month_strings:
             row = [month_str]  # 첫 번째 컬럼: 입고월

-            #  Stage-1 정규화 순서 기반 창고 목록 사용
-            warehouses = list(self.calculator.warehouse_columns)
-            warehouse_display_names = list(self.calculator.warehouse_columns)
-
             inbound_values = []

-            # 입고 계산 (순수 입고 + 창고간 이동 입고)
-            for i, warehouse in enumerate(warehouses):
-                inbound_count = 0
-
-                # 1. 순수 입고 (external_arrival)
-                for item in stats["inbound_result"].get("inbound_items", []):
-                    if (
-                        item.get("Warehouse") == warehouse
-                        and item.get("Year_Month") == month_str
-                        and item.get("Inbound_Type") == "external_arrival"
-                    ):
-                        inbound_count += item.get("Pkg_Quantity", 1)
-
-                # 2. 창고간 이동 입고 (키 이름 폴백)
-                for transfer in stats["inbound_result"].get("warehouse_transfers", []):
-                    if (
-                        transfer.get("to_warehouse") == warehouse
-                        and transfer.get("Year_Month") == month_str
-                    ):
-                        pkg_qty = transfer.get("pkg_quantity") or transfer.get("Pkg_Quantity", 1)
-                        inbound_count += pkg_qty
-
-                inbound_values.append(inbound_count)
-                row.append(inbound_count)
-
-            # 출고 계산 (창고간 이동 출고 + 현장 이동 출고)
+            for warehouse in warehouses:
+                key = (month_str, warehouse)
+                inbound_count = external_inbound_map.get(key, 0)
+                inbound_count += transfer_inbound_map.get(key, 0)
+
+                inbound_values.append(int(inbound_count))
+                row.append(int(inbound_count))
+
             outbound_values = []
-            for i, warehouse in enumerate(warehouses):
-                outbound_count = 0
-
-                # 창고간 이동 출고 (키 이름 폴백)
-                for transfer in stats["inbound_result"].get("warehouse_transfers", []):
-                    if (
-                        transfer.get("from_warehouse") == warehouse
-                        and transfer.get("Year_Month") == month_str
-                    ):
-                        pkg_qty = transfer.get("pkg_quantity") or transfer.get("Pkg_Quantity", 1)
-                        outbound_count += pkg_qty
-
-                # 창고→현장 출고 (키 이름 폴백)
-                for item in stats["outbound_result"].get("outbound_items", []):
-                    if (
-                        item.get("From_Location") == warehouse
-                        and item.get("Year_Month") == month_str
-                    ):
-                        pkg_qty = item.get("Pkg_Quantity") or item.get("pkg_quantity", 1)
-                        outbound_count += pkg_qty
-
-                outbound_values.append(outbound_count)
-                row.append(outbound_count)
+            for warehouse in warehouses:
+                key = (month_str, warehouse)
+                outbound_count = outbound_map.get(key, 0)
+
+                outbound_values.append(int(outbound_count))
+                row.append(int(outbound_count))

             # 누계 열 추가
             row.append(sum(inbound_values))  # 누계_입고
             row.append(sum(outbound_values))  # 누계_출고

             results.append(row)

         # 컬럼 생성 (19열)
         columns = ["입고월"]

         # 입고 8개 창고
         for warehouse in warehouse_display_names:
             columns.append(f"입고_{warehouse}")

         # 출고 8개 창고
         for warehouse in warehouse_display_names:
             columns.append(f"출고_{warehouse}")

         # 누계 열
         columns.append("누계_입고")
         columns.append("누계_출고")

         # DataFrame 생성
         warehouse_monthly = pd.DataFrame(results, columns=columns)

diff --git a/tests/stage3/test_warehouse_monthly_sheet.py b/tests/stage3/test_warehouse_monthly_sheet.py
new file mode 100644
index 0000000000000000000000000000000000000000..c1be873b913425d80f7d96c9a12dae339bda2a7f
--- /dev/null
+++ b/tests/stage3/test_warehouse_monthly_sheet.py
@@ -0,0 +1,71 @@
+"""창고 월별 입출고 시트 테스트 / Warehouse monthly IO sheet tests."""
+
+from datetime import datetime, timedelta
+
+import pandas as pd
+
+from scripts.stage3_report.report_generator import HVDCExcelReporterFinal
+
+
+def test_monthly_sheet_counts_warehouse_transfers_once():
+    """창고간 이동 출고를 한 번만 계산한다 / Count transfer outbounds only once."""
+
+    reporter = HVDCExcelReporterFinal()
+    current_month = datetime.now().strftime("%Y-%m")
+    inbound_date = pd.Timestamp(f"{current_month}-01")
+    transfer_date = inbound_date + timedelta(days=2)
+
+    stats = {
+        "inbound_result": {
+            "inbound_items": [
+                {
+                    "Item_ID": 1,
+                    "Warehouse": "DHL WH",
+                    "Inbound_Date": inbound_date,
+                    "Year_Month": current_month,
+                    "Pkg_Quantity": 10,
+                    "Inbound_Type": "external_arrival",
+                }
+            ],
+            "warehouse_transfers": [
+                {
+                    "Row_ID": 1,
+                    "from_warehouse": "DHL WH",
+                    "to_warehouse": "DSV Indoor",
+                    "transfer_date": transfer_date,
+                    "pkg_quantity": 5,
+                    "transfer_type": "warehouse_to_warehouse",
+                    "Year_Month": current_month,
+                }
+            ],
+        },
+        "outbound_result": {
+            "outbound_items": [
+                {
+                    "Item_ID": 1,
+                    "From_Location": "DHL WH",
+                    "To_Location": "DSV Indoor",
+                    "Outbound_Date": transfer_date,
+                    "Year_Month": current_month,
+                    "Pkg_Quantity": 5,
+                    "Outbound_Type": "warehouse_transfer",
+                },
+                {
+                    "Item_ID": 2,
+                    "From_Location": "DSV Indoor",
+                    "To_Location": "AGI",
+                    "Outbound_Date": transfer_date + timedelta(days=2),
+                    "Year_Month": current_month,
+                    "Pkg_Quantity": 4,
+                    "Outbound_Type": "warehouse_to_site",
+                },
+            ]
+        },
+    }
+
+    sheet = reporter.create_warehouse_monthly_sheet(stats)
+    month_row = sheet.loc[sheet["입고월"] == current_month].iloc[0]
+
+    assert month_row["입고_DHL WH"] == 10
+    assert month_row["출고_DHL WH"] == 5
+    assert month_row["출고_DSV Indoor"] == 4
