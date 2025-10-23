# HVDC Pipeline 문서 인덱스

**Samsung C&T Logistics | ADNOC·DSV Partnership**

HVDC Pipeline의 모든 문서에 대한 중앙 인덱스입니다.

## 📁 문서 구조

### 🔄 정렬/비정렬 버전별 문서

#### 정렬 버전 (Sorted Version)
- **[빠른 시작 가이드](sorted_version/QUICK_START.md)** - 정렬 버전 5분 빠른 시작
- **[Stage 1 사용 가이드](sorted_version/STAGE1_USER_GUIDE.md)** - 정렬 버전 상세 가이드
- **[README](sorted_version/README.md)** - 정렬 버전 개요

#### 비정렬 버전 (No Sorting Version)
- **[빠른 시작 가이드](no_sorting_version/QUICK_START.md)** - 비정렬 버전 빠른 시작
- **[Stage 1 사용 가이드](no_sorting_version/STAGE1_USER_GUIDE.md)** - 비정렬 버전 상세 가이드
- **[README](no_sorting_version/README.md)** - 비정렬 버전 개요

### 📚 공통 문서 (Common)

#### Stage별 가이드
- **[Stage별 상세 가이드](common/STAGE_BY_STAGE_GUIDE.md)** - 전체 파이프라인 통합 가이드
- **[Stage 2 사용 가이드](common/STAGE2_USER_GUIDE.md)** - 파생 컬럼 처리 가이드
- **[Stage 3 사용 가이드](common/STAGE3_USER_GUIDE.md)** - 종합 보고서 생성 가이드
- **[Stage 4 사용 가이드](common/STAGE4_USER_GUIDE.md)** - 이상치 탐지 가이드

#### 기술 문서
- **[파이프라인 실행 가이드](common/PIPELINE_EXECUTION_GUIDE.md)** - 상세한 실행 방법
- **[색상 문제 해결](common/COLOR_FIX_SUMMARY.md)** - 빈 셀 색상 문제 해결 완료 보고서
- **[Stage 1 상세 로직 가이드](common/STAGE1_DETAILED_LOGIC_GUIDE.md)** - Stage 1 기술적 세부사항

#### 보고서 및 분석
- **[날짜 로직 검증 보고서](common/DATE_LOGIC_VERIFICATION_REPORT.md)** - 날짜 처리 로직 검증
- **[Stage 4 색상 적용 보고서](common/STAGE4_COLOR_APPLICATION_REPORT.md)** - 이상치 색상 적용 결과
- **[Stage 4 이상치 가이드](common/STAGE4_ANOMALY_GUIDE.md)** - 이상치 탐지 상세 가이드

## 🚀 빠른 시작

### 정렬 버전 (권장 - 보고서 작성용)
```bash
cd hvdc_pipeline
python run_pipeline.py --all
```
- **특징**: Master NO. 순서로 정렬
- **처리 시간**: 약 35초
- **권장 용도**: 보고서 작성, 데이터 분석

### 비정렬 버전 (빠른 실행)
```bash
cd hvdc_pipeline
python run_pipeline.py --all --no-sorting
```
- **특징**: 원본 순서 유지
- **처리 시간**: 약 30초
- **권장 용도**: 빠른 확인, 개발 테스트

## 📊 버전 비교

| 항목 | 정렬 버전 | 비정렬 버전 |
|------|----------|------------|
| 처리 시간 | ~35초 | ~30초 |
| 출력 순서 | Master NO. 순 | Warehouse 원본 순 |
| 권장 용도 | 보고서 작성, 데이터 비교 | 빠른 확인, 개발 테스트 |
| 출력 파일명 | `*.synced_v2.9.4.xlsx` | `*.synced_v2.9.4_no_sorting.xlsx` |

## 🎯 사용 목적별 가이드

### 보고서 작성이 목적인 경우
1. [정렬 버전 빠른 시작](sorted_version/QUICK_START.md) 읽기
2. [정렬 버전 Stage 1 가이드](sorted_version/STAGE1_USER_GUIDE.md) 참조
3. `python run_pipeline.py --all` 실행

### 빠른 확인이 목적인 경우
1. [비정렬 버전 빠른 시작](no_sorting_version/QUICK_START.md) 읽기
2. [비정렬 버전 Stage 1 가이드](no_sorting_version/STAGE1_USER_GUIDE.md) 참조
3. `python run_pipeline.py --all --no-sorting` 실행

### 개발/테스트 환경인 경우
1. [비정렬 버전 가이드](no_sorting_version/) 전체 검토
2. [공통 기술 문서](common/) 참조
3. 비정렬 버전으로 개발 및 테스트

## 🔧 문제 해결

### 일반적인 문제
- [파이프라인 실행 가이드](common/PIPELINE_EXECUTION_GUIDE.md) - 실행 관련 문제
- [색상 문제 해결](common/COLOR_FIX_SUMMARY.md) - 색상 표시 문제
- [날짜 로직 검증](common/DATE_LOGIC_VERIFICATION_REPORT.md) - 날짜 처리 문제

### Stage별 문제
- **Stage 1**: 각 버전의 Stage 1 가이드 참조
- **Stage 2**: [Stage 2 사용 가이드](common/STAGE2_USER_GUIDE.md)
- **Stage 3**: [Stage 3 사용 가이드](common/STAGE3_USER_GUIDE.md)
- **Stage 4**: [Stage 4 사용 가이드](common/STAGE4_USER_GUIDE.md)

## 📞 지원 및 문의

### 로그 확인
```bash
# 파이프라인 실행 로그 확인
tail -f logs/pipeline.log

# 특정 Stage 로그만 확인
grep "Stage 1" logs/pipeline.log
```

### 문제 신고 절차
1. 실행 로그 확인 (`logs/pipeline.log`)
2. 오류 메시지 복사
3. 입력 파일 상태 확인
4. 문제 상황 상세 기록

---

**📅 최종 업데이트**: 2025-10-20
**🔖 버전**: v3.0.1
**👥 작성자**: HVDC 파이프라인 개발팀

## 🆕 v3.0.1 주요 개선사항

### Stage 3 Toolkit 보강 패치 통합
- ✅ **컬럼 정규화 강화**: AAA Storage, site handling 동의어 자동 매핑
- ✅ **utils.py 추가**: 공백 정규화 + 동의어 매핑 함수
- ✅ **column_definitions.py 추가**: 컬럼 정의 상수
- ✅ **IndentationError 수정**: toolkit 통합 완료

### Stage 4 PyOD 앙상블 ML + 색상 자동화 (v4.0.15)
- ✅ **이상치 탐지**: 1건 → 7,022건 (7,000배 향상)
- ✅ **ML 앙상블**: ECOD/COPOD/HBOS/IForest 4개 알고리즘
- ✅ **자동 폴백**: sklearn IsolationForest 지원
- ✅ **위험도 정규화**: 0~1 ECDF 캘리브레이션
- ✅ **자동 색상 적용**: 이상치 유형별 색상 마킹 (기본 활성화)
  - 🔴 빨강: 시간 역전 (치명적 오류)
  - 🟠 주황: ML 이상치 치명적/높음
  - 🟡 노랑: ML 이상치 보통/낮음 + 과도 체류
  - 🟣 보라: 데이터 품질 문제

### 완전 자동화 달성 (v2.9.4-hotfix-4)
- ✅ **Stage 3 날짜 범위 자동 확장**: 2025-10까지 (현재 월까지 동적 계산)
- ✅ **Stage 4 자동 파일 탐색**: 최신 보고서 자동 선택 (config 업데이트 불필요)
- ✅ **색상 적용 완전 자동화**: Stage 1/4 색상 자동 적용
- ✅ **불필요한 파일 복사 제거**: synced_for_color.xlsx 복사 제거
- ✅ **실행 스크립트 개선**: 명확한 메시지 및 자동화
