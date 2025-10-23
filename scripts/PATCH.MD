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
index bcb2dd14e88d7463f80a1eaf845b46d7216b890e..fa3a20bff1b8871e7cd76fdb0706a71fb152846e 100644
--- a/scripts/stage3_report/report_generator.py
+++ b/scripts/stage3_report/report_generator.py
@@ -3244,50 +3244,55 @@ class HVDCExcelReporterFinal:

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
@@ -3308,65 +3313,50 @@ class HVDCExcelReporterFinal:
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
@@ -3434,91 +3424,117 @@ class HVDCExcelReporterFinal:
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
