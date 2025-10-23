# HVDC 파이프라인 Stage별 상세 사용 가이드

## 📋 개요

HVDC 파이프라인은 4단계의 데이터 처리 과정을 통해 물류 데이터를 동기화, 분석, 보고하는 통합 시스템입니다.

### 파이프라인 구조 (v3.0.1)
```
RAW 데이터 → Stage 1 (색상✅) → Stage 2 → Stage 3 (동적날짜✅) → Stage 4 (자동탐색+색상✅)
           동기화+주황/노랑   파생컬럼   종합보고서(2025-10)   이상치탐지+빨강/주황/노랑/보라
```

## 🚀 빠른 시작

### 실행 옵션 선택

#### 옵션 A: Master NO. 순서 정렬 (권장)
```bash
cd hvdc_pipeline
python run_pipeline.py --all
```
- **특징**: 출력 파일이 Case List.xlsx의 NO. 순서대로 정렬됨
- **장점**: Master 파일과 동일한 순서로 데이터 확인 가능
- **처리 시간**: 약 35초
- **권장 용도**: 보고서 작성, 데이터 분석

#### 옵션 B: 정렬 없이 빠른 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --all --no-sorting
```
- **특징**: 원본 Warehouse 파일 순서 유지
- **장점**: 빠른 처리 속도
- **처리 시간**: 약 30초
- **권장 용도**: 빠른 확인, 개발 테스트

### 비교표
| 항목 | 정렬 버전 | 비정렬 버전 |
|------|----------|------------|
| 처리 시간 | ~35초 | ~30초 |
| 출력 순서 | Master NO. 순 | Warehouse 원본 순 |
| 권장 용도 | 보고서 작성, 데이터 비교 | 빠른 확인, 개발 테스트 |
| 출력 파일명 | `*.synced_v2.9.4.xlsx` | `*.synced_v2.9.4_no_sorting.xlsx` |
| 정렬 로직 | Master NO. 기준 정렬 | 원본 순서 유지 |

### 개별 Stage 실행
```bash
# Stage 1만 실행
python run_pipeline.py --stage 1

# Stage 2만 실행
python run_pipeline.py --stage 2

# Stage 3만 실행
python run_pipeline.py --stage 3

# Stage 4만 실행
python run_pipeline.py --stage 4
```

## 📁 입력 파일 요구사항

### 필수 입력 파일
- **Master 파일**: `data/raw/Case List.xlsx`
- **Warehouse 파일**: `data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx`

### 파일 위치 확인
```bash
# 입력 파일 존재 확인
ls data/raw/
# 출력: Case List.xlsx, HVDC WAREHOUSE_HITACHI(HE).xlsx
```

## 🔄 Stage별 상세 가이드

### Stage 1: 데이터 동기화
**목적**: Master와 Warehouse 데이터를 동기화하고 색상으로 변경사항 표시

**실행 시간**: 약 2-3분

**주요 기능**:
- Master 우선 원칙으로 데이터 동기화
- 날짜 필드 자동 정규화
- 변경사항 색상 표시 (주황: 날짜변경, 노랑: 신규행)
- Master NO. 순서로 정렬 (선택 가능)

**실행 옵션**:
```bash
# 정렬 버전 (기본 - 권장)
python run_pipeline.py --stage 1

# 비정렬 버전 (빠른 실행)
python run_pipeline.py --stage 1 --no-sorting
```

**출력 파일**:
- 정렬 버전: `data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx`
- 비정렬 버전: `data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4_no_sorting.xlsx`

**상세 가이드**: [STAGE1_USER_GUIDE.md](STAGE1_USER_GUIDE.md)

### Stage 2: 파생 컬럼 처리
**목적**: 13개의 파생 컬럼을 추가하여 데이터 분석 기능 강화

**실행 시간**: 약 1-2분

**주요 기능**:
- 13개 파생 컬럼 자동 계산
- Stage 1 색상 정보 보존
- 데이터 검증 및 품질 확인

**출력 파일**:
- `data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx`

**상세 가이드**: [STAGE2_USER_GUIDE.md](STAGE2_USER_GUIDE.md)

### Stage 3: 종합 보고서 생성
**목적**: KPI 분석과 시각화가 포함된 종합 보고서 생성

**실행 시간**: 약 3-5분

**주요 기능**:
- 5개 시트로 구성된 종합 보고서
- KPI 대시보드 및 트렌드 분석
- 데이터 품질 검증 결과
- 시각적 차트 및 그래프

**출력 파일**:
- `data/processed/reports/HVDC_종합리포트_YYYYMMDD_HHMMSS.xlsx`

**상세 가이드**: [STAGE3_USER_GUIDE.md](STAGE3_USER_GUIDE.md)

### Stage 4: 이상치 탐지
**목적**: 데이터에서 이상치를 자동 탐지하고 색상으로 표시

**실행 시간**: 약 2-3분

**주요 기능**:
- 5가지 이상치 유형 자동 탐지
- 이상치 색상 표시 (빨강, 주황, 노랑 등)
- 이상치 상세 분석 보고서
- 데이터 품질 개선 제안

**출력 파일**:
- `data/anomaly/HVDC_anomaly_report.xlsx`
- `data/anomaly/HVDC_anomaly_report.json`

**상세 가이드**: [STAGE4_USER_GUIDE.md](STAGE4_USER_GUIDE.md)

## 📊 실행 결과 확인

### 전체 파이프라인 실행 후 확인사항
```bash
# 1. Stage 1 결과 확인
ls -la data/processed/synced/
# HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx 파일 확인

# 2. Stage 2 결과 확인
ls -la data/processed/derived/
# HVDC WAREHOUSE_HITACHI(HE).xlsx 파일 확인

# 3. Stage 3 결과 확인
ls -la data/processed/reports/
# HVDC_종합리포트_*.xlsx 파일 확인

# 4. Stage 4 결과 확인
ls -la data/anomaly/
# HVDC_anomaly_report.xlsx 파일 확인
```

### 성공적인 실행 확인
- 모든 Stage에서 "SUCCESS" 메시지 출력
- 각 단계별 출력 파일 생성
- 오류 메시지 없음

## ⚠️ 문제 해결

### 일반적인 문제들

#### 1. 파일을 찾을 수 없음
```bash
# 해결방법: 입력 파일 위치 확인
ls data/raw/
# Case List.xlsx와 HVDC WAREHOUSE_HITACHI(HE).xlsx가 있는지 확인
```

#### 2. 권한 오류 (Permission Error)
```bash
# 해결방법: Excel 파일이 열려있는지 확인하고 닫기
# Windows: 작업 관리자에서 EXCEL.EXE 종료
taskkill /F /IM EXCEL.EXE
```

#### 3. 색상이 빈 셀에 적용됨
- **원인**: Stage 1의 색상 적용 로직 문제
- **해결**: 최신 버전의 data_synchronizer_v29.py 사용
- **상세**: [COLOR_FIX_SUMMARY.md](COLOR_FIX_SUMMARY.md) 참조

#### 4. Case NO 매칭 실패
- **원인**: 컬럼명 차이 또는 데이터 형식 불일치
- **해결**: 유연한 컬럼 매칭 로직 적용됨
- **확인**: Stage 1 실행 로그에서 매칭률 확인

### 로그 확인
```bash
# 파이프라인 실행 로그 확인
tail -f logs/pipeline.log
```

## 📈 성능 최적화

### 실행 시간 단축 팁
1. **개별 Stage 실행**: 전체 파이프라인 대신 필요한 Stage만 실행
2. **파일 정리**: 이전 실행 결과 파일 삭제 후 실행
3. **메모리 관리**: 대용량 파일 처리 시 다른 프로그램 종료

### 권장 하드웨어 사양
- **RAM**: 최소 8GB (16GB 권장)
- **CPU**: 4코어 이상
- **디스크**: 여유 공간 2GB 이상

## 🔧 고급 사용법

### 설정 파일 수정
```bash
# 파이프라인 설정 수정
vim config/pipeline_config.yaml

# Stage 2 설정 수정
vim config/stage2_derived_config.yaml
```

### 커스텀 실행
```bash
# 특정 입력 파일로 실행
python run_pipeline.py --all --master "custom_master.xlsx" --warehouse "custom_warehouse.xlsx"

# 출력 디렉토리 지정
python run_pipeline.py --all --output-dir "custom_output"
```

## 📞 지원 및 문의

### 문서 참조
- [빠른 시작 가이드](QUICK_START.md)
- [Stage별 상세 가이드](STAGE1_USER_GUIDE.md)
- [색상 문제 해결](COLOR_FIX_SUMMARY.md)

### 문제 신고
1. 실행 로그 확인 (`logs/pipeline.log`)
2. 오류 메시지 복사
3. 입력 파일 상태 확인
4. 문제 상황 상세 기록

---

**최종 업데이트**: 2025-01-19
**버전**: v2.9.4
**작성자**: HVDC 파이프라인 개발팀
