diff --git a/CHANGELOG.md b/CHANGELOG.md
index b38f5228d51fbf68cd88f7b19903df44e55ebabb..f2849bb765a79b6c44143918c683096fc614106e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -41,50 +41,58 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0

 - **Files Created**:
   - `tests/test_stage3_total_sqm.py`: 포괄적 테스트 스위트 (8개 테스트, 모두 통과)

 - **Benefits**:
   - **적재 효율 분석**: 실제 적재 가능한 총 면적 계산
   - **재사용성**: core.data_parser 활용으로 코드 중복 제거
   - **정확도**: 개선된 Stack_Status 파싱 로직 사용
   - **창고 공간 계획**: Total sqm 기반 실제 사용 공간 추적
   - **중앙 관리**: core 모듈에서 헤더 순서 및 파싱 로직 일괄 관리

 - **Test Results**:
   - Stack_Status 파싱: "X2" → 2, "Stackable / 3" → 3, "Not stackable" → 0
   - Total sqm 계산: SQM=2.5, PKG=10 → 25.0
   - 엣지 케이스: Pkg=0, SQM=None → None
   - 모든 테스트 통과 (8/8)

 - **Example Usage**:
   ```python
   # Stage 3 통합_원본데이터_Fixed 시트
   # ... | SQM | Stack_Status | Total sqm | ...
   # ... | 9.84 | 2 | 98.40 | ...  (SQM=9.84, PKG=10)
   # ... | 5.20 | 3 | 52.00 | ...  (SQM=5.20, PKG=10)
   ```

+### 🐛 Fixed
+
+- Stage 3 Excel 저장 시 `Stack_Status`, `Total sqm` 컬럼이 누락되던 문제를 해결했습니다.
+  - `scripts/stage3_report/report_generator.py`에서 모든 시트를 단일 `ExcelWriter`
+    컨텍스트 안에서 기록하도록 재구성했습니다.
+  - 기존에는 DataFrame에 신규 컬럼이 존재했으나, 닫힌 writer 재사용으로 저장 단계에서
+    컬럼이 빠지는 현상이 발생했습니다.
+
 ## [4.0.21] - 2025-10-23

 ### ✨ Added

 #### Core 모듈에 데이터 파싱 유틸리티 추가
 - **Problem**: Stack_Status 파싱 로직이 Stage 2에만 존재하여 재사용 불가
   - Stage별 중복 코드 발생 위험
   - 개선된 파싱 로직이 일부 Stage에만 적용
   - 유지보수 어려움: 각 Stage별로 별도 구현 필요

 - **Solution**: Core 모듈에 data_parser.py 추가
   - **중앙 집중식 관리**: 모든 Stage에서 `from core.data_parser import parse_stack_status` 사용
   - **개선된 파싱 로직**: 하중 표기 제거, 슬래시 패턴, 양방향 X 패턴 지원
   - **하위 호환성**: 기존 stack_and_sqm.py는 core 모듈로 위임하여 유지

 - **Implementation Details**:
   - `scripts/core/data_parser.py`: 새로운 데이터 파싱 모듈 생성
   - `_strip_weights()`: 하중 표기(600kg/m2, kg/㎡ 등) 제거 함수
   - `parse_stack_status()`: 개선된 Stack_Status 파싱 로직
   - `calculate_sqm()`, `convert_mm_to_cm()`: 향후 확장을 위한 유틸리티 함수
   - `scripts/core/__init__.py`: data_parser 모듈 export 추가

 - **Files Created**:
   - `scripts/core/data_parser.py`: 데이터 파싱 유틸리티 (약 200줄)
   - `tests/test_data_parser.py`: 포괄적 테스트 스위트 (약 150줄)
diff --git a/scripts/stage3_report/report_generator.py b/scripts/stage3_report/report_generator.py
index bcb2dd14e88d7463f80a1eaf845b46d7216b890e..609933fba313b4d2bbefe0151fcd6d824544b6e5 100644
--- a/scripts/stage3_report/report_generator.py
+++ b/scripts/stage3_report/report_generator.py
@@ -860,82 +860,148 @@ class CorrectedWarehouseIOCalculator:
                     except Exception as e:
                         logger.warning(f"입고 계산 오류 (Row {idx}, Warehouse {warehouse}): {e}")
                         continue

         #  1. warehouse_transfers에 Year_Month 키 주입
         for transfer in warehouse_transfers:
             transfer["Year_Month"] = transfer["transfer_date"].strftime("%Y-%m")

         logger.info(
             f" 수정된 창고 입고 계산 완료: {total_inbound}건 (창고간 이동 {len(warehouse_transfers)}건 별도)"
         )

         return {
             "total_inbound": total_inbound,
             "by_warehouse": by_warehouse,
             "by_month": by_month,
             "inbound_items": inbound_items,
             "warehouse_transfers": warehouse_transfers,
         }

     def _calculate_warehouse_inbound_vectorized(self, df: pd.DataFrame) -> Dict:
         """벡터화된 창고 입고 계산 (PATCH.MD 전략)"""
         logger.info(" Vectorized 창고 입고 계산 시작")

         # 1. 창고 컬럼을 melt하여 벡터화 처리
-        wh_df = df.melt(
-            id_vars=["Pkg"],
+        df_with_index = df.reset_index().rename(columns={"index": "Row_ID"})
+        wh_df = df_with_index.melt(
+            id_vars=["Row_ID", "Pkg"],
             value_vars=self.warehouse_columns,
             var_name="Warehouse",
             value_name="Inbound_Date",
         )
-        wh_df = wh_df[wh_df["Inbound_Date"].notna()]
+        wh_df = wh_df[wh_df["Inbound_Date"].notna()].copy()
+        wh_df["Row_ID"] = wh_df["Row_ID"].apply(
+            lambda value: int(value)
+            if isinstance(value, (int, np.integer))
+            else value
+        )
         wh_df["Inbound_Date"] = pd.to_datetime(wh_df["Inbound_Date"])
         wh_df["Year_Month"] = wh_df["Inbound_Date"].dt.strftime("%Y-%m")
         wh_df["Pkg_Quantity"] = wh_df["Pkg"].fillna(1).clip(lower=1).astype(int)

         # 2. 창고간 이동 감지 (벡터화)
-        df["transfers"] = df.apply(self._detect_warehouse_transfers, axis=1)
-        transfers_flat = pd.DataFrame([t for transfers in df["transfers"] for t in transfers])
+        df_with_transfers = df.copy()
+        df_with_transfers["transfers"] = df_with_transfers.apply(
+            self._detect_warehouse_transfers, axis=1
+        )
+        transfers_flat = pd.DataFrame(
+            [t for transfers in df_with_transfers["transfers"] for t in transfers]
+        )

         if not transfers_flat.empty:
-            transfers_flat["Year_Month"] = transfers_flat["transfer_date"].dt.strftime("%Y-%m")
-            # 창고간 이동 목적지 제외
-            transfer_dest = transfers_flat["to_warehouse"].unique()
-            wh_df = wh_df[~wh_df["Warehouse"].isin(transfer_dest)]
+            if "Row_ID" in transfers_flat.columns:
+                transfers_flat["Row_ID"] = transfers_flat["Row_ID"].apply(
+                    lambda value: int(value)
+                    if isinstance(value, (int, np.integer))
+                    else value
+                )
+            transfers_flat["transfer_date"] = pd.to_datetime(
+                transfers_flat["transfer_date"]
+            )
+            transfers_flat["Year_Month"] = transfers_flat["transfer_date"].dt.strftime(
+                "%Y-%m"
+            )

-        # 3. 집계 (벡터화)
-        by_month_wh = (
-            wh_df.groupby(["Year_Month", "Warehouse"])["Pkg_Quantity"].sum().unstack(fill_value=0)
+            transfer_destinations = transfers_flat.rename(
+                columns={
+                    "to_warehouse": "Warehouse",
+                    "transfer_date": "Inbound_Date",
+                    "pkg_quantity": "Transfer_Quantity",
+                }
+            )
+            transfer_destinations = transfer_destinations[
+                ["Row_ID", "Warehouse", "Inbound_Date", "Transfer_Quantity"]
+            ]
+
+            wh_df = wh_df.merge(
+                transfer_destinations,
+                on=["Row_ID", "Warehouse", "Inbound_Date"],
+                how="left",
+            )
+            wh_df["Transfer_Quantity"] = (
+                wh_df["Transfer_Quantity"].fillna(0).astype(int)
+            )
+        else:
+            wh_df["Transfer_Quantity"] = 0
+
+        # 창고간 이동 목적지 수량 제외
+        wh_df["External_Quantity"] = (
+            wh_df["Pkg_Quantity"] - wh_df["Transfer_Quantity"]
+        ).clip(lower=0)
+        external_wh_df = wh_df[wh_df["External_Quantity"] > 0].copy()
+        external_wh_df["Pkg_Quantity"] = (
+            external_wh_df["External_Quantity"].astype(int)
         )
+        external_wh_df.drop(columns=["Transfer_Quantity", "External_Quantity", "Pkg"], inplace=True)
+
+        # 3. 집계 (벡터화)
+        if external_wh_df.empty:
+            by_month_wh = pd.DataFrame(columns=self.warehouse_columns)
+        else:
+            by_month_wh = (
+                external_wh_df.groupby(["Year_Month", "Warehouse"])["Pkg_Quantity"].sum()
+                .unstack(fill_value=0)
+            )
         by_warehouse = by_month_wh.sum(axis=0).to_dict()
         by_month = by_month_wh.sum(axis=1).to_dict()
-        total_inbound = wh_df["Pkg_Quantity"].sum()
+        total_inbound = int(external_wh_df["Pkg_Quantity"].sum())

         # 4. 결과 구성
-        inbound_items = wh_df.to_dict("records")
-        warehouse_transfers = transfers_flat.to_dict("records") if not transfers_flat.empty else []
+        if external_wh_df.empty:
+            inbound_items: List[Dict] = []
+        else:
+            inbound_items = external_wh_df.rename(columns={"Row_ID": "Item_ID"}).to_dict("records")
+
+        for item in inbound_items:
+            if isinstance(item.get("Item_ID"), (int, np.integer)):
+                item["Item_ID"] = int(item["Item_ID"])
+            item["Inbound_Type"] = "external_arrival"
+
+        warehouse_transfers = (
+            transfers_flat.to_dict("records") if not transfers_flat.empty else []
+        )

         logger.info(f" Vectorized 창고 입고 계산 완료: {total_inbound}건")

         return {
             "total_inbound": total_inbound,
             "by_warehouse": by_warehouse,
             "by_month": by_month,
             "inbound_items": inbound_items,
             "warehouse_transfers": warehouse_transfers,
         }

     def _calculate_warehouse_inbound_parallel(self, df: pd.DataFrame) -> Dict:
         """병렬 처리된 창고 입고 계산"""
         logger.info(" Parallel 창고 입고 계산 시작")

         try:
             from multiprocessing import Pool, cpu_count
             import numpy as np

             n_cores = min(cpu_count(), 4)  # 최대 4코어로 제한
             chunks = np.array_split(df, n_cores)

             with Pool(n_cores) as pool:
                 results = pool.starmap(
                     self._process_chunk_inbound,
@@ -1468,126 +1534,137 @@ class CorrectedWarehouseIOCalculator:
         transfers = []

         # 주요 창고간 이동 패턴들
         warehouse_pairs = [
             ("DSV Indoor", "DSV Al Markaz"),
             ("DSV Indoor", "DSV Outdoor"),
             ("DSV Al Markaz", "DSV Outdoor"),
             ("AAA Storage", "DSV Al Markaz"),
             ("AAA Storage", "DSV Indoor"),
             ("DSV Indoor", "MOSB"),
             ("DSV Al Markaz", "MOSB"),
         ]

         for from_wh, to_wh in warehouse_pairs:
             from_date = pd.to_datetime(row.get(from_wh), errors="coerce")
             to_date = pd.to_datetime(row.get(to_wh), errors="coerce")

             if (
                 pd.notna(from_date) and pd.notna(to_date) and from_date.date() == to_date.date()
             ):  # 동일 날짜 이동

                 #  추가: 논리적 검증
                 if self._validate_transfer_logic(from_wh, to_wh, from_date, to_date):
                     transfers.append(
                         {
+                            "Row_ID": int(row.name)
+                            if isinstance(row.name, (int, np.integer))
+                            else row.name,
                             "from_warehouse": from_wh,
                             "to_warehouse": to_wh,
                             "transfer_date": from_date,
                             "pkg_quantity": self._get_pkg_quantity(row),
                             "transfer_type": "warehouse_to_warehouse",
                             "Year_Month": from_date.strftime("%Y-%m"),  #  Year_Month 키 추가
                         }
                     )

         return transfers

     def _vectorized_detect_warehouse_transfers_batch(self, df: pd.DataFrame) -> pd.DataFrame:
         """완전 벡터화된 창고간 이동 감지 (v4.1 전략)"""
         logger.info(" Vectorized 창고간 이동 감지 시작")

         transfers_list = []
         warehouse_pairs = [
             ("DSV Indoor", "DSV Al Markaz"),
             ("DSV Indoor", "DSV Outdoor"),
             ("DSV Al Markaz", "DSV Outdoor"),
             ("AAA Storage", "DSV Al Markaz"),
             ("AAA Storage", "DSV Indoor"),
             ("DSV Indoor", "MOSB"),
             ("DSV Al Markaz", "MOSB"),
         ]

         for from_wh, to_wh in warehouse_pairs:
             if from_wh in df.columns and to_wh in df.columns:
                 # 벡터화된 날짜 변환
                 from_date = pd.to_datetime(df[from_wh], errors="coerce")
                 to_date = pd.to_datetime(df[to_wh], errors="coerce")

                 # 동일 날짜 이동 마스크
                 same_date_mask = (
                     from_date.notna() & to_date.notna() & (from_date.dt.date == to_date.dt.date)
                 )

                 if same_date_mask.any():
                     # 유효한 이동만 필터링
                     valid_mask = same_date_mask & self._validate_transfer_logic_vectorized(
                         from_wh, to_wh, from_date, to_date, df
                     )

                     if valid_mask.any():
                         # 이동 데이터 생성
                         transfer_df = df[valid_mask].copy()
+                        transfer_df["Row_ID"] = transfer_df.index
                         transfer_df["from_warehouse"] = from_wh
                         transfer_df["to_warehouse"] = to_wh
                         transfer_df["transfer_date"] = from_date[valid_mask]
                         transfer_df["pkg_quantity"] = self._get_pkg_quantity_vectorized(transfer_df)
                         transfer_df["transfer_type"] = "warehouse_to_warehouse"
                         transfer_df["Year_Month"] = transfer_df["transfer_date"].dt.strftime(
                             "%Y-%m"
                         )

                         transfers_list.append(
                             transfer_df[
                                 [
+                                    "Row_ID",
                                     "from_warehouse",
                                     "to_warehouse",
                                     "transfer_date",
                                     "pkg_quantity",
                                     "transfer_type",
                                     "Year_Month",
                                 ]
                             ]
                         )

         if transfers_list:
             result = pd.concat(transfers_list, ignore_index=True)
             logger.info(f" Vectorized 창고간 이동 감지 완료: {len(result)}건")
+            result["Row_ID"] = result["Row_ID"].apply(
+                lambda value: int(value)
+                if isinstance(value, (int, np.integer))
+                else value
+            )
             return result
         else:
             logger.info(" Vectorized 창고간 이동 감지 완료: 0건")
             return pd.DataFrame(
                 columns=[
+                    "Row_ID",
                     "from_warehouse",
                     "to_warehouse",
                     "transfer_date",
                     "pkg_quantity",
                     "transfer_type",
                     "Year_Month",
                 ]
             )

     def _validate_transfer_logic_vectorized(self, from_wh, to_wh, from_date, to_date, df):
         """벡터화된 이동 로직 검증"""
         # 우선순위 기반 검증
         from_priority = pd.Series(self.location_priority.get(from_wh, 99), index=df.index)
         to_priority = pd.Series(self.location_priority.get(to_wh, 99), index=df.index)

         # 우선순위가 높은 경우만 허용 (낮은 숫자 = 높은 우선순위)
         priority_valid = from_priority > to_priority

         # 특별 허용 쌍들
         special_pairs = [
             ("DSV Indoor", "DSV Al Markaz"),
             ("AAA Storage", "DSV Al Markaz"),
             ("DSV Outdoor", "MOSB"),
         ]
         special_valid = pd.Series(False, index=df.index)
@@ -3244,50 +3321,55 @@ class HVDCExcelReporterFinal:

         # 시트 1: 창고_월별_입출고 (Multi-Level Header, 17열 - 누계 포함)
         warehouse_monthly = self.create_warehouse_monthly_sheet(stats)
         warehouse_monthly_with_headers = self.create_multi_level_headers(
             warehouse_monthly, "warehouse"
         )

         # 시트 2: 현장_월별_입고재고 (Multi-Level Header, 9열)
         site_monthly = self.create_site_monthly_sheet(stats)
         site_monthly_with_headers = self.create_multi_level_headers(site_monthly, "site")

         # 시트 3: Flow_Code_분석
         flow_analysis = self.create_flow_analysis_sheet(stats)

         # 시트 4: 전체_트랜잭션_요약
         transaction_summary = self.create_transaction_summary_sheet(stats)

         # 시트 5: KPI_검증_결과 (수정 버전)
         kpi_validation_df = pd.DataFrame.from_dict(kpi_validation, orient="index")
         kpi_validation_df.reset_index(inplace=True)
         kpi_validation_df.columns = ["KPI", "Status", "Value", "Threshold"]

         # 시트 6: 원본_데이터_샘플 (처음 1000건)
         sample_data = stats["processed_data"].head(1000)

+        # Stage 3 SQM 관련 시트 사전 계산
+        sqm_cumulative_sheet = self.create_sqm_cumulative_sheet(stats)
+        sqm_invoice_sheet = self.create_sqm_invoice_sheet(stats)
+        sqm_pivot_sheet = self.create_sqm_pivot_sheet(stats)
+
         #  FIX: 원본 데이터 시트들 (컬럼 보존)
         hitachi_original = stats["processed_data"][
             stats["processed_data"]["Vendor"] == "HITACHI"
         ].copy()
         siemens_original = stats["processed_data"][
             stats["processed_data"]["Vendor"] == "SIMENSE"
         ].copy()
         combined_original = stats["processed_data"].copy()

         #  검증: AAA Storage 컬럼 존재 확인
         print(f"\n 최종 데이터 컬럼 검증:")
         for data_name, data_df in [
             ("HITACHI", hitachi_original),
             ("SIEMENS", siemens_original),
             ("통합", combined_original),
         ]:
             if "AAA Storage" in data_df.columns:
                 aaa_count = data_df["AAA Storage"].notna().sum()
                 print(f"    {data_name} - AAA Storage: {aaa_count}건")
             else:
                 print(f"    {data_name} - AAA Storage: 컬럼 없음")

         #  검증: Status_Location_YearMonth 컬럼 확인
         if "Status_Location_YearMonth" in combined_original.columns:
             print(f"    Status_Location_YearMonth 컬럼 포함")
@@ -3308,65 +3390,50 @@ class HVDCExcelReporterFinal:
             else:
                 print(f"    {col}: 컬럼 없음")

         #  FIX: 전체 데이터는 CSV로도 저장 (백업용)
         hitachi_original.to_csv(
             self.report_output_dir / "HITACHI_원본데이터_FULL_fixed.csv",
             index=False,
             encoding="utf-8-sig",
         )
         siemens_original.to_csv(
             self.report_output_dir / "SIEMENS_원본데이터_FULL_fixed.csv",
             index=False,
             encoding="utf-8-sig",
         )
         combined_original.to_csv(
             self.report_output_dir / "통합_원본데이터_FULL_fixed.csv",
             index=False,
             encoding="utf-8-sig",
         )

         # Excel 파일 생성 (수정 버전)
         excel_filename = (
             self.report_output_dir
             / f"HVDC_입고로직_종합리포트_{self.timestamp}_v3.0-corrected.xlsx"
         )
-        with pd.ExcelWriter(excel_filename, engine="xlsxwriter") as writer:
-            warehouse_monthly_with_headers.to_excel(
-                writer, sheet_name="창고_월별_입출고", index=True
-            )
-            site_monthly_with_headers.to_excel(writer, sheet_name="현장_월별_입고재고", index=True)
-            flow_analysis.to_excel(writer, sheet_name="Flow_Code_분석", index=False)
-            transaction_summary.to_excel(writer, sheet_name="전체_트랜잭션_요약", index=False)
-            kpi_validation_df.to_excel(writer, sheet_name="KPI_검증_결과", index=False)
-            sqm_cumulative_sheet = self.create_sqm_cumulative_sheet(stats)
-            sqm_cumulative_sheet.to_excel(writer, sheet_name="SQM_누적재고", index=False)
-            sqm_invoice_sheet = self.create_sqm_invoice_sheet(stats)
-            sqm_invoice_sheet.to_excel(writer, sheet_name="SQM_Invoice과금", index=False)
-            sqm_pivot_sheet = self.create_sqm_pivot_sheet(stats)
-            sqm_pivot_sheet.to_excel(writer, sheet_name="SQM_피벗테이블", index=False)
-            sample_data.to_excel(writer, sheet_name="원본_데이터_샘플", index=False)
         # ✅ Stage 3 헤더명 정규화 및 표준 순서 적용
         logger.info(" 통합_원본데이터_Fixed 시트 생성 - 유연한 헤더 검색 및 표준 순서 적용")

         # HITACHI 데이터 처리
         hitachi_normalized = normalize_header_names_for_stage3(hitachi_original)
         hitachi_reordered = reorder_dataframe_columns(
             hitachi_normalized, is_stage2=False, use_semantic_matching=True
         )

         # SIEMENS 데이터 처리
         siemens_normalized = normalize_header_names_for_stage3(siemens_original)
         siemens_reordered = reorder_dataframe_columns(
             siemens_normalized, is_stage2=False, use_semantic_matching=True
         )

         # 통합 데이터 처리
         combined_normalized = normalize_header_names_for_stage3(combined_original)

         # ✅ Stage 3 신규 컬럼 추가 (통합 데이터에만)
         logger.info("\n[INFO] Stage 3 신규 컬럼 계산 중...")

         # Stack_Status 계산
         combined_normalized["Stack_Status"] = _calculate_stack_status(combined_normalized, "Stack")
         stack_parsed = combined_normalized["Stack_Status"].notna().sum()
         logger.info(f"  - Stack_Status 파싱 완료: {stack_parsed}개")
@@ -3434,91 +3501,117 @@ class HVDCExcelReporterFinal:
             logger.info(f"  - Total sqm 유효값 개수: {total_sqm_count}")
         if "Stack_Status" in combined_reordered.columns:
             stack_status_count = combined_reordered["Stack_Status"].notna().sum()
             logger.info(f"  - Stack_Status 유효값 개수: {stack_status_count}")

         # 🔍 디버그: Excel 저장 직전 최종 검증
         logger.info(f"\n[DEBUG] Excel 저장 직전 최종 검증:")
         logger.info(f"  - combined_reordered 컬럼 수: {len(combined_reordered.columns)}")
         logger.info(f"  - 마지막 5개 컬럼: {list(combined_reordered.columns[-5:])}")

         # 🔍 디버그: Excel 저장 전 컬럼명 검증
         logger.info(f"\n[DEBUG] Excel 저장 전 컬럼명 검증:")
         logger.info(f"  - Total sqm 컬럼명: {repr('Total sqm')}")
         logger.info(f"  - Stack_Status 컬럼명: {repr('Stack_Status')}")
         logger.info(f"  - Total sqm in columns: {'Total sqm' in combined_reordered.columns}")
         logger.info(f"  - Stack_Status in columns: {'Stack_Status' in combined_reordered.columns}")

         # 🔍 디버그: 문제가 될 수 있는 컬럼명 확인
         problem_cols = []
         for col in combined_reordered.columns:
             if any(char in col for char in ["\n", "\r", "\t", "\x00"]):
                 problem_cols.append(f"'{col}' (contains special chars)")
         if problem_cols:
             logger.warning(f"[WARN] 문제가 될 수 있는 컬럼명: {problem_cols}")

-        #  FIX: 수정된 원본 데이터 시트들 (표준 헤더 순서 적용)
-        hitachi_reordered.to_excel(writer, sheet_name="HITACHI_원본데이터_Fixed", index=False)
-        siemens_reordered.to_excel(writer, sheet_name="SIEMENS_원본데이터_Fixed", index=False)
+        with pd.ExcelWriter(excel_filename, engine="xlsxwriter") as writer:
+            warehouse_monthly_with_headers.to_excel(
+                writer, sheet_name="창고_월별_입출고", index=True
+            )
+            site_monthly_with_headers.to_excel(
+                writer, sheet_name="현장_월별_입고재고", index=True
+            )
+            flow_analysis.to_excel(writer, sheet_name="Flow_Code_분석", index=False)
+            transaction_summary.to_excel(writer, sheet_name="전체_트랜잭션_요약", index=False)
+            kpi_validation_df.to_excel(writer, sheet_name="KPI_검증_결과", index=False)
+            sqm_cumulative_sheet.to_excel(writer, sheet_name="SQM_누적재고", index=False)
+            sqm_invoice_sheet.to_excel(writer, sheet_name="SQM_Invoice과금", index=False)
+            sqm_pivot_sheet.to_excel(writer, sheet_name="SQM_피벗테이블", index=False)
+            sample_data.to_excel(writer, sheet_name="원본_데이터_샘플", index=False)

-        # 🔍 디버그: combined_reordered 저장 전 최종 확인
-        logger.info(f"\n[DEBUG] combined_reordered Excel 저장 직전:")
-        logger.info(f"  - 컬럼 수: {len(combined_reordered.columns)}")
-        logger.info(
-            f"  - Total sqm 위치: {list(combined_reordered.columns).index('Total sqm') if 'Total sqm' in combined_reordered.columns else 'NOT FOUND'}"
-        )
-        logger.info(
-            f"  - Stack_Status 위치: {list(combined_reordered.columns).index('Stack_Status') if 'Stack_Status' in combined_reordered.columns else 'NOT FOUND'}"
-        )
+            #  FIX: 수정된 원본 데이터 시트들 (표준 헤더 순서 적용)
+            hitachi_reordered.to_excel(
+                writer, sheet_name="HITACHI_원본데이터_Fixed", index=False
+            )
+            siemens_reordered.to_excel(
+                writer, sheet_name="SIEMENS_원본데이터_Fixed", index=False
+            )

-        # 🔍 디버그: Excel 저장 전 최종 컬럼 검증
-        logger.info(f"\n[DEBUG] Excel 저장 전 최종 컬럼 검증:")
-        logger.info(f"  - combined_reordered 컬럼 수: {len(combined_reordered.columns)}")
-        logger.info(f"  - Total sqm 존재: {'Total sqm' in combined_reordered.columns}")
-        logger.info(f"  - Stack_Status 존재: {'Stack_Status' in combined_reordered.columns}")
-        logger.info(
-            f"  - Total sqm 위치: {list(combined_reordered.columns).index('Total sqm') if 'Total sqm' in combined_reordered.columns else 'NOT FOUND'}"
-        )
-        logger.info(
-            f"  - Stack_Status 위치: {list(combined_reordered.columns).index('Stack_Status') if 'Stack_Status' in combined_reordered.columns else 'NOT FOUND'}"
-        )
+            # 🔍 디버그: combined_reordered 저장 전 최종 확인
+            logger.info(f"\n[DEBUG] combined_reordered Excel 저장 직전:")
+            logger.info(f"  - 컬럼 수: {len(combined_reordered.columns)}")
+            logger.info(
+                f"  - Total sqm 위치: {list(combined_reordered.columns).index('Total sqm') if 'Total sqm' in combined_reordered.columns else 'NOT FOUND'}"
+            )
+            logger.info(
+                f"  - Stack_Status 위치: {list(combined_reordered.columns).index('Stack_Status') if 'Stack_Status' in combined_reordered.columns else 'NOT FOUND'}"
+            )

-        # 🔍 디버그: Excel 저장 시도
-        try:
-            # Excel 저장 시 컬럼 제한 확인
-            logger.info(f"[DEBUG] Excel 저장 시도: {len(combined_reordered.columns)}개 컬럼")
-            combined_reordered.to_excel(writer, sheet_name="통합_원본데이터_Fixed", index=False)
-            logger.info("[SUCCESS] Excel 저장 완료")
-        except Exception as e:
-            logger.error(f"[ERROR] Excel 저장 실패: {e}")
-            # 컬럼명 문제일 수 있으므로 컬럼명을 안전하게 변경
-            safe_df = combined_reordered.copy()
-            safe_df.columns = [
-                str(col).replace(" ", "_").replace(".", "_") for col in safe_df.columns
-            ]
-            safe_df.to_excel(writer, sheet_name="통합_원본데이터_Fixed", index=False)
-            logger.info("[FALLBACK] 안전한 컬럼명으로 Excel 저장 완료")
+            # 🔍 디버그: Excel 저장 전 최종 컬럼 검증
+            logger.info(f"\n[DEBUG] Excel 저장 전 최종 컬럼 검증:")
+            logger.info(f"  - combined_reordered 컬럼 수: {len(combined_reordered.columns)}")
+            logger.info(f"  - Total sqm 존재: {'Total sqm' in combined_reordered.columns}")
+            logger.info(f"  - Stack_Status 존재: {'Stack_Status' in combined_reordered.columns}")
+            logger.info(
+                f"  - Total sqm 위치: {list(combined_reordered.columns).index('Total sqm') if 'Total sqm' in combined_reordered.columns else 'NOT FOUND'}"
+            )
+            logger.info(
+                f"  - Stack_Status 위치: {list(combined_reordered.columns).index('Stack_Status') if 'Stack_Status' in combined_reordered.columns else 'NOT FOUND'}"
+            )
+
+            # 🔍 디버그: Excel 저장 시도
+            try:
+                # Excel 저장 시 컬럼 제한 확인
+                logger.info(
+                    f"[DEBUG] Excel 저장 시도: {len(combined_reordered.columns)}개 컬럼"
+                )
+                combined_reordered.to_excel(
+                    writer, sheet_name="통합_원본데이터_Fixed", index=False
+                )
+                logger.info("[SUCCESS] Excel 저장 완료")
+            except Exception as e:
+                logger.error(f"[ERROR] Excel 저장 실패: {e}")
+                # 컬럼명 문제일 수 있으므로 컬럼명을 안전하게 변경
+                safe_df = combined_reordered.copy()
+                safe_df.columns = [
+                    str(col).replace(" ", "_").replace(".", "_")
+                    for col in safe_df.columns
+                ]
+                safe_df.to_excel(
+                    writer, sheet_name="통합_원본데이터_Fixed", index=False
+                )
+                logger.info("[FALLBACK] 안전한 컬럼명으로 Excel 저장 완료")

         # 🔍 디버그: Excel 저장 후 검증
         logger.info(f"\n[DEBUG] Excel 저장 후 검증:")
         logger.info(f"  - combined_reordered 컬럼 수: {len(combined_reordered.columns)}")
         logger.info(f"  - 'Total sqm' 존재: {'Total sqm' in combined_reordered.columns}")
         logger.info(f"  - 'Stack_Status' 존재: {'Stack_Status' in combined_reordered.columns}")

         logger.info(f" 표준 헤더 순서 적용 완료: {len(combined_reordered.columns)}개 컬럼")

         # 저장 후 검증
         try:
             _ = pd.read_excel(excel_filename, sheet_name=0)
         except Exception as e:
             print(f" [경고] 엑셀 파일 저장 후 열기 실패: {e}")

         logger.info(f" 최종 Excel 리포트 생성 완료: {excel_filename}")
         logger.info(
             " 원본 전체 데이터는 %s 경로의 CSV로도 저장됨",
             self.report_output_dir,
         )

         #  FIX: 수정사항 요약 출력
         print(f"\n v3.0-corrected 수정사항 요약:")
         print(f"    1. 창고 vs 현장 입고 분리")
         print(f"    2. 출고 타이밍 정확성 개선")
diff --git a/tests/stage3/test_vectorized_inbound.py b/tests/stage3/test_vectorized_inbound.py
new file mode 100644
index 0000000000000000000000000000000000000000..071501a026ab9777ab9a05608d87a72872dc333e
--- /dev/null
+++ b/tests/stage3/test_vectorized_inbound.py
@@ -0,0 +1,46 @@
+import pandas as pd
+
+from scripts.stage3_report.report_generator import CorrectedWarehouseIOCalculator
+
+
+def test_vectorized_inbound_retains_external_arrivals_for_transfer_destinations():
+    calculator = CorrectedWarehouseIOCalculator(use_vectorized=True)
+
+    warehouse_data = {column: [None, None] for column in calculator.warehouse_columns}
+    warehouse_data["DSV Indoor"][0] = "2023-02-10"
+    warehouse_data["DSV Al Markaz"][0] = "2023-02-10"
+    warehouse_data["DSV Al Markaz"][1] = "2023-02-12"
+
+    data = {"Pkg": [10, 5]}
+    data.update(warehouse_data)
+
+    df = pd.DataFrame(data)
+
+    inbound_result = calculator._calculate_warehouse_inbound_vectorized(df)
+
+    assert inbound_result["total_inbound"] == 15
+    assert inbound_result["by_warehouse"]["DSV Indoor"] == 10
+    assert inbound_result["by_warehouse"]["DSV Al Markaz"] == 5
+
+    inbound_items = pd.DataFrame(inbound_result["inbound_items"])
+    assert not inbound_items.empty
+    assert (
+        inbound_items[
+            (inbound_items["Warehouse"] == "DSV Al Markaz")
+            & (inbound_items["Inbound_Date"] == pd.Timestamp("2023-02-10"))
+        ]
+        .empty
+    )
+
+    al_markaz_external = inbound_items[
+        (inbound_items["Warehouse"] == "DSV Al Markaz")
+        & (inbound_items["Inbound_Date"] == pd.Timestamp("2023-02-12"))
+    ]
+    assert not al_markaz_external.empty
+    assert al_markaz_external.iloc[0]["Pkg_Quantity"] == 5
+
+    warehouse_transfers = inbound_result["warehouse_transfers"]
+    assert any(
+        transfer["to_warehouse"] == "DSV Al Markaz" and transfer.get("Row_ID") == 0
+        for transfer in warehouse_transfers
+    )
