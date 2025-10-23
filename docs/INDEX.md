# HVDC Pipeline Documentation Index

## 📚 문서 구조

### 📖 필수 문서 (프로젝트 루트)
- [README.md](../README.md) - 프로젝트 개요 및 빠른 시작
- [CHANGELOG.md](../CHANGELOG.md) - 버전별 변경 이력 (v4.0.12)

---

## 📂 문서 카테고리

### 🔧 기술 보고서 (`/docs/reports/`)
주요 기능 개발 및 버그 수정에 대한 상세 보고서

**색상 작업**:
- [COLOR_FIX_SUMMARY.md](reports/COLOR_FIX_SUMMARY.md) - 색상 작업 완료 요약 ⭐
- [COLOR_VERIFICATION_REPORT_20251022.md](reports/COLOR_VERIFICATION_REPORT_20251022.md) - 색상 검증 상세

**Core 모듈**:
- [CORE_MODULE_INTEGRATION_REPORT.md](reports/CORE_MODULE_INTEGRATION_REPORT.md) - Semantic Matching v3.0

**Stage별 수정**:
- [STAGE1_MISSING_COLUMNS_FIX_REPORT.md](reports/STAGE1_MISSING_COLUMNS_FIX_REPORT.md) - Location 컬럼 자동 생성
- [STAGE3_PATH_FIX_REPORT.md](reports/STAGE3_PATH_FIX_REPORT.md) - Stage 3 경로 수정
- [STAGE4_BALANCED_BOOST_UPGRADE_REPORT.md](reports/STAGE4_BALANCED_BOOST_UPGRADE_REPORT.md) - Balanced Boost v4.0

**데이터 처리**:
- [DSV_WH_FIX_FINAL_REPORT.md](reports/DSV_WH_FIX_FINAL_REPORT.md) - DSV WH 통합
- [MULTI_SHEET_SUPPORT_REPORT.md](reports/MULTI_SHEET_SUPPORT_REPORT.md) - 다중 시트 지원
- [FINAL_INTEGRATION_SUMMARY.md](reports/FINAL_INTEGRATION_SUMMARY.md) - 최종 통합 요약

**정렬 기능**:
- [SORTING_FIX_FINAL_REPORT.md](reports/SORTING_FIX_FINAL_REPORT.md) - 정렬 수정
- [SORTING_OPTIONS_FINAL_REPORT.md](reports/SORTING_OPTIONS_FINAL_REPORT.md) - 정렬 옵션
- [SORTING_OPTIONS_IMPLEMENTATION_REPORT.md](reports/SORTING_OPTIONS_IMPLEMENTATION_REPORT.md) - 정렬 구현

---

### ⚙️ 설정 가이드 (`/docs/setup/`)
프로젝트 및 개발 환경 설정

- [Cursor_Project_AutoSetup_Guide.md](setup/Cursor_Project_AutoSetup_Guide.md) - 자동 설정 가이드 (권장) ⭐
- [Cursor_Project_Setup_v1.3.md](setup/Cursor_Project_Setup_v1.3.md) - 프로젝트 설정 v1.3
- [Cursor_Config_Patch_v1_Guide.md](setup/Cursor_Config_Patch_v1_Guide.md) - Cursor 설정 패치

---

### 📝 작업 세션 (`/docs/sessions/`)
개발 작업 세션 기록 및 단계별 패치 히스토리

- [CLEANUP_COMPLETION_REPORT.md](sessions/CLEANUP_COMPLETION_REPORT.md) - 코드 정리 작업 완료
- [PHASE_BY_PHASE_PATCH_REPORT.md](sessions/PHASE_BY_PHASE_PATCH_REPORT.md) - 단계별 패치 (45.9KB)
- [WORK_SESSION_REPORT_20251022.md](sessions/WORK_SESSION_REPORT_20251022.md) - 2025-10-22 작업 보고서
- [WORK_SESSION_SUMMARY_20251022.md](sessions/WORK_SESSION_SUMMARY_20251022.md) - 2025-10-22 작업 요약
- [WORK_SESSION_20251022_STAGE1_FIX.md](sessions/WORK_SESSION_20251022_STAGE1_FIX.md) - Stage 1 수정 작업

---

### 💻 개발 문서 (`/docs/development/`)
개발 프로세스 및 테스트 계획

- [plan.md](development/plan.md) - TDD 테스트 계획

---

### 📚 Stage별 가이드 (`/docs/common/`)
기존 공통 문서 (13개)

- [STAGE_BY_STAGE_GUIDE.md](common/STAGE_BY_STAGE_GUIDE.md) - 전체 파이프라인 가이드 ⭐
- [PIPELINE_EXECUTION_GUIDE.md](common/PIPELINE_EXECUTION_GUIDE.md) - 실행 가이드
- [STAGE1_SYNC_GUIDE.md](common/STAGE1_SYNC_GUIDE.md) - Stage 1 상세
- [STAGE2_DERIVED_GUIDE.md](common/STAGE2_DERIVED_GUIDE.md) - Stage 2 상세
- [STAGE3_USER_GUIDE.md](common/STAGE3_USER_GUIDE.md) - Stage 3 상세
- [STAGE4_USER_GUIDE.md](common/STAGE4_USER_GUIDE.md) - Stage 4 상세
- [STAGE4_COLOR_APPLICATION_REPORT.md](common/STAGE4_COLOR_APPLICATION_REPORT.md) - 색상 적용
- [DATE_LOGIC_VERIFICATION_REPORT.md](common/DATE_LOGIC_VERIFICATION_REPORT.md) - 날짜 로직 검증
- [PIPELINE_OVERVIEW.md](common/PIPELINE_OVERVIEW.md) - 파이프라인 개요
- [STAGE1_DETAILED_LOGIC_GUIDE.md](common/STAGE1_DETAILED_LOGIC_GUIDE.md) - Stage 1 상세 로직
- [STAGE2_USER_GUIDE.md](common/STAGE2_USER_GUIDE.md) - Stage 2 사용자 가이드
- [STAGE3_USER_GUIDE.md](common/STAGE3_USER_GUIDE.md) - Stage 3 사용자 가이드
- [STAGE4_ANOMALY_GUIDE.md](common/STAGE4_ANOMALY_GUIDE.md) - Stage 4 이상치 가이드

---

### 🔀 버전별 문서
- `/docs/sorted_version/` - 정렬 버전 문서
- `/docs/no_sorting_version/` - 비정렬 버전 문서

---

### 📜 스크립트 문서 (`/scripts/`)
각 Stage별 README 및 기술 문서

- [scripts/README.md](../scripts/README.md) - 스크립트 개요
- [scripts/core/README.md](../scripts/core/README.md) - Core 모듈 (Semantic Matching v3.0)
- [scripts/stage1_sync_sorted/README.md](../scripts/stage1_sync_sorted/README.md) - Stage 1 정렬 버전
- [scripts/stage2_derived/README.md](../scripts/stage2_derived/README.md) - Stage 2 파생 컬럼
- [scripts/stage3_report/README.md](../scripts/stage3_report/README.md) - Stage 3 보고서
- [scripts/stage4_anomaly/README.md](../scripts/stage4_anomaly/README.md) - Stage 4 이상치 탐지

---

## 🎯 빠른 시작

1. **프로젝트 개요**: [README.md](../README.md) 읽기
2. **설정**: [Cursor_Project_AutoSetup_Guide.md](setup/Cursor_Project_AutoSetup_Guide.md)
3. **실행**: [PIPELINE_EXECUTION_GUIDE.md](common/PIPELINE_EXECUTION_GUIDE.md)
4. **Stage별 상세**: [STAGE_BY_STAGE_GUIDE.md](common/STAGE_BY_STAGE_GUIDE.md)

---

**버전**: v4.0.12
**최종 업데이트**: 2025-10-22
