# HVDC 파이프라인 실행 가이드

## 📋 개요

이 문서는 HVDC 프로젝트의 전체 데이터 처리 파이프라인을 단계별로 실행하는 방법을 상세히 설명합니다. 이 가이드를 따라하면 누구나 동일한 방식으로 파이프라인을 반복 실행할 수 있습니다.

### 프로젝트 정보
- **프로젝트명**: HVDC Invoice Audit System
- **목적**: 삼성물산/ADNOC 물류 데이터 동기화 및 분석
- **전체 실행 시간**: 약 1분 (v2.9.4 최적화)
- **처리 데이터량**: 5,552행, 57컬럼
- **문서 작성일**: 2025-10-20
- **현재 버전**: v3.0.1
- **주요 개선**: PyOD 앙상블 ML, toolkit 컬럼 정규화, 완전 자동화 달성

## 🔧 사전 요구사항

### 시스템 요구사항
- **Python**: 3.8 이상
- **운영체제**: Windows 10/11
- **메모리**: 최소 4GB RAM 권장
- **디스크 공간**: 최소 100MB 여유 공간

### 필수 Python 패키지
```bash
pandas>=1.3.0
openpyxl>=3.0.0
numpy>=1.21.0
xlsxwriter>=3.0.0
```

### 필수 입력 파일
```
data/raw/
├── CASE LIST.xlsx                    # Master 데이터 (NO. 컬럼 포함)
└── HVDC WAREHOUSE_HITACHI(HE).xlsx  # Warehouse 데이터
```

### v2.9.4 새로운 기능
- **유연한 컬럼 매칭**: "No"와 "No."를 동일하게 인식
- **Master NO. 순서 정렬**: Case List의 NO. 순서대로 자동 정렬
- **날짜 정규화**: 다양한 날짜 형식을 YYYY-MM-DD로 통일
- **출력 파일 버전 관리**: 파일명에 버전 정보 포함

## 🏗️ 파이프라인 아키텍처

### 전체 데이터 흐름 (v3.0.1 최적화)
```
Master (CASE LIST.xlsx)
    ↓
Stage 1: Data Synchronization + 색상 적용 (주황/노랑) ✅
    ↓
synced_v2.9.4.xlsx (색상 포함)
    ↓
Stage 2: Derived Columns (13개 파생 컬럼)
    ↓
Stage 3: Report Generation + Toolkit 컬럼 정규화 (2025-10까지) ✅
    ↓
종합리포트_YYYYMMDD_HHMMSS.xlsx
    ↓
Stage 4: PyOD 앙상블 ML + 색상 적용 (7,022건 이상치) ✅
    ├→ 자동 최신 파일 탐색 ✅
    └→ 이상치 시각화 + 백업 생성
```

### Stage별 상세 설명

#### Stage 1: Data Synchronization
- **목적**: Master와 Warehouse 데이터 동기화
- **핵심 로직**: "Master takes precedence" 원칙
- **새로운 기능**:
  - 유연한 컬럼 매칭 (No/No. 대소문자 무시)
  - Master NO. 순서 정렬
  - 날짜 정규화 (YYYY-MM-DD)
- **출력**: 동기화된 Excel 파일 (v2.9.4)

#### Stage 2: Derived Columns Generation
- **목적**: 비즈니스 로직에 필요한 파생 컬럼 추가
- **처리**: 13개 파생 컬럼 생성
- **출력**: 파생 컬럼이 추가된 Excel 파일

#### Stage 3: Report Generation + Toolkit 보강 패치
- **목적**: 종합 분석 보고서 생성
- **포함 시트**: 통합_원본데이터_Fixed 등
- **새로운 기능**:
  - 컬럼 정규화 강화 (AAA Storage, site handling)
  - 동의어 자동 매핑
  - utils.py, column_definitions.py 통합
- **출력**: Excel 종합 보고서

#### Stage 4: PyOD 앙상블 ML + Visualization
- **목적**: 고급 이상치 탐지 및 시각화
- **ML 모델**: ECOD/COPOD/HBOS/IForest 앙상블
- **성능**: 1건 → 7,022건 (7,000배 향상)
- **시각화**: 통합_원본데이터_Fixed 시트에 색상 적용
- **출력**: 이상치 보고서 (Excel, JSON)

## 🚀 단계별 실행 가이드

### Stage 1: Data Synchronization

#### 실행 명령어
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 1
```

#### 입력 파일
- **Master**: `data/raw/CASE LIST.xlsx`
- **Warehouse**: `data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx`

#### 출력 파일
- **Synced**: `data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx`

#### 실행 시간
- **예상 시간**: 약 30초 (v2.9.4 최적화)

#### 통계 정보 해석 (v2.9.4)
```
동기화 통계:
- 업데이트: 1,564건 (Master 우선 업데이트)
- 날짜 업데이트: 1,564건 (날짜 변경 감지)
- 신규 행: 104건 (새로운 케이스)
- Master NO. 정렬: 적용됨
- 색상 표시: 주황(날짜 변경), 노랑(신규)
```

#### 결과물 2개 복사 (v2.9.4)
```bash
# 색상 작업용 복사
Copy-Item "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx" "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced_colored.xlsx"

# Stage 2 입력용 복사
Copy-Item "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx" "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced_for_stage2.xlsx"
```

### Stage 1.5: 색상 작업 (선택적)

#### 목적
- 날짜 변경 셀에 주황색 표시
- 새 케이스 행에 노란색 표시

#### 색상 코드
- **주황색 (FFC000)**: 날짜 변경 감지
- **노란색 (FFFF00)**: 새로운 케이스

#### 처리 파일
- **입력**: `synced_for_color.xlsx`
- **출력**: `HVDC WAREHOUSE_HITACHI(HE).synced_colored.xlsx`

### Stage 2: Derived Columns Generation

#### 실행 명령어
```bash
python run_pipeline.py --stage 2
```

#### 입력 파일
- **Source**: `data/processed/synced/synced_for_stage2.xlsx`

#### 출력 파일
- **Derived**: `data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx`

#### 실행 시간
- **예상 시간**: 약 9초

#### 파생 컬럼 목록 (13개)
1. **Warehouse 컬럼** (8개)
   - DHL Warehouse
   - DSV Indoor
   - DSV Al Markaz
   - Hauler Indoor
   - DSV Outdoor
   - DSV MZP
   - MOSB
   - AAA Storage

2. **Site 컬럼** (4개)
   - MIR
   - SHU
   - AGI
   - DAS

3. **기타 파생 컬럼** (1개)
   - Status_Location_YearMonth

### Stage 3: Report Generation

#### 실행 명령어
```bash
python run_pipeline.py --stage 3
```

#### 입력 파일
- **Derived**: `data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx`

#### 출력 파일
- **Report**: `data/processed/reports/HVDC_입고로직_종합리포트_[timestamp]_v3.0-corrected.xlsx`

#### 실행 시간
- **예상 시간**: 약 54초

#### 포함 시트 목록
- 통합_원본데이터_Fixed
- SQM 분석 결과
- KPI 대시보드
- Flow Code 분석
- 기타 분석 시트들

### Stage 4: Anomaly Detection & Visualization

#### 실행 명령어
```bash
python run_pipeline.py --stage 4
```

#### 입력 파일
- **Report**: 최신 종합 보고서

#### 출력 파일
- **Anomaly Excel**: `data/anomaly/HVDC_anomaly_report.xlsx`
- **Anomaly JSON**: `data/anomaly/HVDC_anomaly_report.json`

#### 실행 시간
- **예상 시간**: 1초 미만

#### 이상치 탐지 결과 (v3.0.1)
- **총 이상치**: 7,022건 (7,000배 향상)
- **ML 모델**: PyOD 앙상블 (ECOD/COPOD/HBOS/IForest)
- **위험도**: 0~1 ECDF 정규화
- **자동 폴백**: sklearn IsolationForest 지원

## 🔄 전체 파이프라인 자동화 스크립트

### Windows 배치 파일
```batch
@echo off
echo HVDC 파이프라인 실행 시작...

cd hvdc_pipeline

echo Stage 1: Data Synchronization...
python run_pipeline.py --stage 1

echo 파일 복사 중...
copy "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced.xlsx" "data\processed\synced\synced_for_color.xlsx"
copy "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced.xlsx" "data\processed\synced\synced_for_stage2.xlsx"

echo Stage 2-3: Derived Columns & Report Generation...
python run_pipeline.py --stage 2,3

echo Stage 4: Anomaly Detection...
python run_pipeline.py --stage 4

echo 파이프라인 실행 완료!
pause
```

### PowerShell 스크립트
```powershell
Write-Host "HVDC 파이프라인 실행 시작..." -ForegroundColor Green

Set-Location "hvdc_pipeline"

Write-Host "Stage 1: Data Synchronization..." -ForegroundColor Yellow
python run_pipeline.py --stage 1

Write-Host "파일 복사 중..." -ForegroundColor Yellow
Copy-Item "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced.xlsx" "data\processed\synced\synced_for_color.xlsx"
Copy-Item "data\processed\synced\HVDC WAREHOUSE_HITACHI(HE).synced.xlsx" "data\processed\synced\synced_for_stage2.xlsx"

Write-Host "Stage 2-3: Derived Columns & Report Generation..." -ForegroundColor Yellow
python run_pipeline.py --stage 2,3

Write-Host "Stage 4: Anomaly Detection..." -ForegroundColor Yellow
python run_pipeline.py --stage 4

Write-Host "파이프라인 실행 완료!" -ForegroundColor Green
```

## ✅ 결과물 확인 체크리스트

### Stage 1 확인사항
- [ ] `HVDC WAREHOUSE_HITACHI(HE).synced.xlsx` 생성 확인
- [ ] 파일 크기: 약 1.43MB
- [ ] 동기화 통계 로그 확인
- [ ] `synced_for_color.xlsx` 복사본 생성 확인
- [ ] `synced_for_stage2.xlsx` 복사본 생성 확인

### Stage 2 확인사항
- [ ] `data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx` 생성 확인
- [ ] 파생 컬럼 13개 추가 확인
- [ ] 처리 로그: "SUCCESS: 파생 컬럼 13개 생성 완료"

### Stage 3 확인사항
- [ ] `data/processed/reports/HVDC_입고로직_종합리포트_[timestamp].xlsx` 생성 확인
- [ ] 파일 크기: 약 2.85MB
- [ ] `통합_원본데이터_Fixed` 시트 존재 확인
- [ ] SQM 분석 결과 시트 확인

### Stage 4 확인사항
- [ ] `data/anomaly/HVDC_anomaly_report.xlsx` 생성 확인
- [ ] `data/anomaly/HVDC_anomaly_report.json` 생성 확인
- [ ] 이상치 탐지 로그 확인

## 📊 성능 지표

### 실행 시간
- **Stage 1**: 135초 (2분 15초)
- **Stage 2**: 9초
- **Stage 3**: 54초
- **Stage 4**: 1초 미만
- **총 실행 시간**: 약 3분 20초

### 처리 데이터량
- **총 행수**: 7,161행
- **총 컬럼수**: 59컬럼 (원본 46 + 파생 13)
- **동기화 건수**: 46,539건 업데이트
- **파생 컬럼**: 13개

### 파일 크기
- **Synced 파일**: 1.43MB
- **종합 보고서**: 2.85MB
- **이상치 보고서**: 6.97KB

## 🔧 트러블슈팅

### 일반적인 오류 및 해결 방법

#### 1. 파일 경로 오류
```
오류: FileNotFoundError: [Errno 2] No such file or directory
해결: 현재 디렉토리가 hvdc_pipeline인지 확인
```

#### 2. 인코딩 오류
```
오류: UnicodeDecodeError
해결: 모든 Python 파일에 # -*- coding: utf-8 -*- 추가
```

#### 3. 권한 오류
```
오류: PermissionError: [Errno 13] Permission denied
해결: Excel 파일이 다른 프로그램에서 열려있지 않은지 확인
```

#### 4. 메모리 부족
```
오류: MemoryError
해결: 다른 프로그램 종료 후 재시도
```

### 로그 확인 방법
```bash
# 상세 로그 확인
python run_pipeline.py --stage 1 --verbose

# 특정 Stage만 실행
python run_pipeline.py --stage 2

# 모든 Stage 실행
python run_pipeline.py --all
```

## 📁 파일 구조 참조

```
hvdc_pipeline/
├── data/
│   ├── raw/                                    # 원본 데이터
│   │   ├── CASE LIST.xlsx                     # Master 데이터
│   │   └── HVDC WAREHOUSE_HITACHI(HE).xlsx   # Warehouse 데이터
│   ├── processed/
│   │   ├── synced/                            # Stage 1 출력
│   │   │   ├── HVDC WAREHOUSE_HITACHI(HE).synced.xlsx
│   │   │   ├── synced_for_color.xlsx
│   │   │   └── synced_for_stage2.xlsx
│   │   ├── derived/                           # Stage 2 출력
│   │   │   └── HVDC WAREHOUSE_HITACHI(HE).xlsx
│   │   └── reports/                           # Stage 3 출력
│   │       └── HVDC_입고로직_종합리포트_[timestamp].xlsx
│   └── anomaly/                               # Stage 4 출력
│       ├── HVDC_anomaly_report.xlsx
│       └── HVDC_anomaly_report.json
├── scripts/
│   ├── stage1_sync/                          # Stage 1 스크립트
│   │   └── data_synchronizer_v29.py
│   ├── stage2_derived/                       # Stage 2 스크립트
│   │   ├── derived_columns_processor.py
│   │   └── column_definitions.py
│   ├── stage3_report/                        # Stage 3 스크립트
│   │   ├── report_generator.py
│   │   └── hvdc_excel_reporter_final_sqm_rev.py
│   └── stage4_anomaly/                       # Stage 4 스크립트
│       ├── anomaly_detector.py
│       └── anomaly_visualizer.py
├── config/
│   └── pipeline_config.yaml                  # 파이프라인 설정
├── docs/
│   └── PIPELINE_EXECUTION_GUIDE.md          # 이 문서
└── run_pipeline.py                          # 메인 실행 스크립트
```

## 📝 버전 정보

- **Data Synchronizer**: v2.9.4
- **보고서 생성기**: v3.0-corrected + Toolkit 보강 패치
- **이상치 탐지**: PyOD v3.0 앙상블 ML
- **문서 버전**: v3.0.1
- **문서 작성일**: 2025-10-20
- **최종 검증일**: 2025-10-20
- **Python 버전**: 3.8+

## 📞 지원 및 문의

### 문제 발생 시 확인사항
1. Python 버전 확인: `python --version`
2. 필수 패키지 설치 확인: `pip list`
3. 입력 파일 존재 확인
4. 디렉토리 권한 확인
5. 로그 파일 확인

### 추가 도움말
- 상세 로그는 `logs/` 디렉토리에서 확인 가능
- 설정 변경은 `config/pipeline_config.yaml` 수정
- 스크립트 수정은 `scripts/` 디렉토리에서 진행

---

**이 가이드를 따라하면 HVDC 파이프라인을 성공적으로 실행할 수 있습니다. 문제가 발생하면 트러블슈팅 섹션을 참조하세요.**
