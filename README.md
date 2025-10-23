# HVDC Pipeline v4.0.27

**Samsung C&T Logistics | ADNOC·DSV Partnership**

통합된 HVDC 파이프라인으로 데이터 동기화부터 이상치 탐지까지 전체 프로세스를 자동화합니다.

## 🚀 최근 업데이트 (v4.0.27 - 창고_월별_입출고 중복 합산 제거)

### 창고_월별_입출고 출고 중복 합산 제거 (2025-10-24)
- **Problem**: 창고간 이동 출고가 두 번 합산되어 월별 출고 합계가 실제보다 약 3,000건 크게 집계
  - `inbound_result["warehouse_transfers"]`에서 한 번
  - `outbound_result["outbound_items"]`에서 또 한 번
- **Solution**: 벡터화된 집계 로직으로 중복 제거
  - 창고 월별 집계 시 창고간 이동 출고를 `outbound_result`에서만 계산
  - DataFrame.groupby() 활용한 효율적인 맵 생성
- **Result**: 월별 출고 합계 정확도 대폭 개선
  - 총 출고: 3,500 → 274 (정확한 수치)
  - 창고간 이동 출고 실수령 수량과 월별 출고 합계 정합성 확보
  - 총입고 − 총출고 = 창고 재고 관계 복원

**주요 기능**:
- 벡터화된 입고/출고 맵 생성으로 성능 유지
- 창고간 이동 출고 중복 계산 완전 제거
- 창고 재고 검증 정확도 개선

**테스트 결과**: 창고간 이동 출고 한 번만 집계 ✅

## 이전 업데이트 (v4.0.25 - 창고_월별_입출고 계산 수정)

### 창고_월별_입출고 시트 데이터 정상화 (2025-10-24)
- **Problem**: 창고_월별_입출고 시트의 데이터가 대부분 0으로 표시
  - 벡터화 입고 계산에서 Inbound_Type 필드 누락
  - create_warehouse_monthly_sheet()에서 조건 미충족
- **Solution**: _calculate_warehouse_inbound_vectorized()에 Inbound_Type 명시적 설정
- **Result**: 입고 데이터 정상 표시
  - 입고_DHL WH: 0 → 408
  - 입고_DSV Indoor: 0 → 2,360
  - 입고_DSV Outdoor: 0 → 2,846
  - 입고_MOSB: 0 → 2,286

**주요 기능**:
- 벡터화 함수에 Inbound_Type="external_arrival" 명시적 설정
- 창고별/월별 집계 정확성 확보
- 입고 데이터 정상화로 월별 분석 가능

**테스트 결과**: 10개 창고 모두 정상 입고 데이터 표시 ✅

## 이전 업데이트 (v4.0.24 - SCT Ref.No 컬럼 위치 수정)

### SCT Ref.No 컬럼 위치 최적화 (2025-10-23)
- **Problem**: SCT Ref.No가 65번째 위치에 있어서 찾기 어려움
- **Solution**: STANDARD_HEADER_ORDER에서 SCT Ref.No를 4번째 위치로 이동
- **Result**:
  - 1. no.
  - 2. Shipment Invoice No.
  - 3. SCT Ref.No ← 이동 완료
  - 4. Site

**주요 기능**:
- 컬럼 순서 일관성 확보
- Stage 2와 Stage 3 헤더 순서 통일
- 데이터 접근성 향상

**검증 결과**: 66개 컬럼, SCT Ref.No 3번째 위치 ✅

## 이전 업데이트 (v4.0.23 - Stage 3 Excel 컬럼 보존)

### Stage 3 Excel 컬럼 누락 문제 해결 (2025-10-23)
- **Problem**: Stage 3 실행 시 Stack_Status, Total sqm 컬럼이 DataFrame에는 존재하지만 Excel 파일에서 누락
  - DataFrame: 66개 컬럼 (Total sqm, Stack_Status 포함)
  - Excel 출력: 64개 컬럼 (Total sqm, Stack_Status 누락)
  - 근본 원인: 닫힌 ExcelWriter 컨텍스트 밖에서 to_excel() 호출
- **Solution**: 모든 시트를 단일 ExcelWriter 컨텍스트 안에서 저장
  - scripts/stage3_report/report_generator.py 재구성
  - SQM 관련 시트를 사전 계산 (writer 컨텍스트 밖)
  - 모든 to_excel() 호출을 단일 with pd.ExcelWriter() 블록 안으로 이동

**주요 기능**:
- DataFrame과 Excel 파일 간 데이터 무결성 보장
- 모든 66개 컬럼이 Excel 파일에 정상 저장
- 창고 적재 효율 분석 가능 (Total sqm = SQM × PKG)

**테스트 결과**: 66개 컬럼 모두 Excel 저장 완료 ✅

## 이전 업데이트 (v4.0.22 - Stage 3 Total sqm 계산)

### 📊 Stage 3 Total sqm 계산 로직 추가 (2025-10-23)
- **신규 컬럼 추가**: Stage 3 통합_원본데이터_Fixed 시트에 `Stack_Status`, `Total sqm` 추가
- **Stack_Status 파싱**: 기존 "Stack" 컬럼 텍스트 파싱 (core.data_parser 활용)
- **Total sqm 계산**: PKG × SQM × Stack_Status 공식으로 실제 적재 면적 계산
- **헤더 순서**: SQM → Stack_Status → Total sqm
- **core 통합**: 헤더 순서 및 데이터 파싱 로직 core 모듈에서 중앙 관리

**주요 기능**:
- **Stack_Status**: "X2" → 2, "Stackable / 3" → 3, "Not stackable" → 0
- **Total sqm**: 실제 적재 시 차지하는 총 면적 (창고 공간 계획 활용)
- **엣지 케이스**: Pkg=0, SQM=None, Stack_Status=None → None 처리

**예시**:
```
통합_원본데이터_Fixed 시트:
... | SQM | Stack_Status | Total sqm | ...
... | 9.84 | 2 | 196.80 | ...  (PKG=10, SQM=9.84, Stack=2)
... | 5.20 | 3 | 156.00 | ...  (PKG=10, SQM=5.20, Stack=3)
```

**테스트 결과**: 8개 테스트 모두 통과 ✅

### 이전 업데이트 (v4.0.20 - 헤더 관리 통합)

### 🔧 헤더 관리 로직 Core 통합 (2025-10-23)
- **중앙 집중식 관리**: 헤더 정규화 로직을 core 모듈로 통합
- **코드 중복 제거**: Stage별 중복 로직 완전 제거
- **일관성 향상**: 모든 Stage에서 동일한 헤더 처리 규칙
- **유지보수성**: 한 곳만 수정하면 모든 Stage 자동 적용
- **DRY 원칙**: 단일 책임 원칙 준수

**주요 개선사항**:
- normalize_header_names_for_stage2/3() 함수에 중복 'no' 컬럼 제거 로직 통합
- derived_columns_processor.py에서 중복 로직 제거 (4줄 코드 정리)
- 모든 Stage에서 core 함수만 호출하여 일관된 헤더 처리

**관련 문서**:
- [헤더 관리 통합 보고서](docs/reports/centralized-header-management-report.md) - 상세 구현 내역

### 이전 업데이트 (v4.0.17 - Stage 3 벡터화 최적화)

### ⚡ Stage 3 벡터화 최적화 (2025-10-23)
- **🚀 82% 성능 개선**: Stage 3 실행 시간 155초 → 28초 (82% 개선)
- **📊 전체 파이프라인**: 217초 → 140초 (35% 개선)
- **🔧 완전 벡터화**: `iterrows()` → `melt()`, `groupby()`, `apply()` 벡터화 연산
- **⚙️ 자동 폴백**: 벡터화 실패 시 레거시 버전으로 자동 전환
- **🖥️ Windows 호환**: multiprocessing spawn 방식 지원
- **📈 확장성**: 대용량 데이터 처리 시 선형 확장성

**성능 비교**:
```
이전 (iterrows):     155초
벡터화:              28초  ✅ (82% 개선)
병렬 처리:           29초  (벡터화 대비 3.3% 느림)
프로덕션 권장:        벡터화 버전 사용
```

**관련 문서**:
- [프로덕션 권장사항](docs/reports/PRODUCTION-RECOMMENDATION.md) - 벡터화 버전 사용 권장
- [벡터화 최적화 보고서](docs/reports/stage3-performance-optimization-completed.md) - 상세 구현 내역
- [병렬 처리 테스트](docs/reports/stage3-parallel-optimization-final-report.md) - 병렬 처리 성능 분석

### 이전 업데이트 (v4.0.16 - Raw Data Protection 검증 시스템)

### 🔒 Raw Data Protection 검증 시스템 (2025-10-23)
- **✨ 완전 자동화된 무결성 검증**: MD5 해시, 파일 크기, 수정 시간, 데이터 행 수 검증
- **🛡️ 100% 보안 보장**: Raw data 파일이 파이프라인 실행 중 절대 수정되지 않음을 검증
- **📊 상세 검증 보고서**: 검증 과정과 결과를 완전히 문서화한 323줄 보고서 제공
- **🔧 자동화 도구**: `scripts/verification/verify_raw_data_protection.py`로 언제든지 검증 가능
- **✅ 검증 결과**: 2개 raw data 파일 모두 PASS (MD5 해시 100% 일치, 파일 크기 100% 일치)

**검증 대상 파일**:
- `Case List.xlsx`: 1,179,971 bytes, MD5: 174459d39602d436...
- `HVDC Hitachi.xlsx`: 911,226 bytes, MD5: 9b90732f6dbb12aa...

**사용법**:
```bash
# 1. Raw data baseline 수집
python scripts\verification\verify_raw_data_protection.py

# 2. 파이프라인 실행
python run_pipeline.py --all

# 3. 검증 재실행 (자동으로 baseline과 비교)
python scripts\verification\verify_raw_data_protection.py
```

**상세 보고서**: [Raw Data Protection 검증 보고서](docs/reports/RAW_DATA_PROTECTION_VERIFICATION_REPORT.md)

### 이전 업데이트 (v4.0.12 - Complete Documentation & Column Order Fix)

### 중요 기능 추가 (2025-10-22)
- **✨ Stage 1 컬럼 순서 최적화**: Shifting/Source_Sheet 위치 원본 데이터 순서 유지
- **🔧 DHL WH 데이터 복구**: 102건 데이터 정상 처리 및 Location 컬럼 자동 처리
- **📊 완전한 문서화**: 모든 Stage별 README 문서 완성 및 아카이브 시스템 구축
- **🎯 코드 정리 완료**: 임시/분석 스크립트 체계적 아카이브 처리

### 이전 업데이트 (v4.0.2 - Stage 3 Path Fix)
- **🐛 Stage 3 Path Fix**: Stage 3가 Stage 2 derived 폴더를 올바르게 읽도록 수정
- **✅ DHL WH Data Recovery**: 누락된 DHL WH 102건 데이터 복구
- **📊 Column Name Unification**: "DHL Warehouse" → "DHL WH" 통일
- **⚡ Performance**: 전체 실행 시간 ~3.6분 (216초)

### 이전 업데이트 (v4.0.2 - Multi-Sheet + Stable Sorting)
- **📊 Multi-Sheet Support**: 엑셀 파일의 모든 시트 자동 로드 및 병합 (3 sheets → 7,172 records)
- **🔧 DSV WH Consolidation**: "DSV WH" → "DSV Indoor" 자동 병합 (1,226 records total)
- **✅ Stable Sorting**: 복합 정렬 키 (No, Case No.)로 HVDC HITACHI 순번 유지
- **✨ Semantic Header Matching**: 하드코딩 100% 제거, 의미 기반 자동 매칭
- **🎯 자동 헤더 탐지**: 97% 신뢰도로 헤더 행 자동 인식

### 이전 버전 (v3.0.2)

### 주요 기능
- **유연한 컬럼 매칭**: "No"와 "No."를 동일하게 인식
- **Master NO. 정렬**: Case List 순서대로 자동 정렬
- **날짜 정규화**: 다양한 날짜 형식 자동 변환
- **버전 관리**: 출력 파일에 버전 정보 포함
- **자동화 개선**: Stage 3 날짜 범위 동적 계산, Stage 4 자동 파일 탐색
- **색상 적용**: Stage 1/4 색상 자동 적용 완료
- **PyOD 앙상블 ML**: Stage 4 이상치 탐지 7,000배 향상
- **컬럼 정규화 강화**: AAA Storage, site handling 동의어 자동 매핑
- **Stage 4 최적화**: Final_Location 활용으로 정확도 38% 향상 ✨ NEW

### 검증된 실행 결과
- Master 5,552행 + Warehouse 5,552행 → Synced 5,552행
- 날짜 업데이트: 1,564건
- 신규 행: 104건
- 파생 컬럼: 13개 추가
- 이상치 탐지: 자동 색상 표시

### 전체 실행 시간 (v4.0.17 - 벡터화 최적화)
- Stage 1 (v3.0 Multi-Sheet): ~36초 ⚡ (3 sheets 병합 + DSV WH 통합 + 안정 정렬)
- Stage 2 (파생 컬럼): ~16초
- Stage 3 (벡터화 최적화): ~28초 ⚡ (155초 → 28초, 82% 개선)
- Stage 4 (이상치 + 색상): ~50초 (탐지 + 색상화)
- **총 실행 시간**: ~130초 (약 2분 10초) ⚡ (217초 → 130초, 40% 개선)

### 색상 시각화 ✨ NEW

Stage 1과 Stage 4의 이상치 및 변경사항이 **자동으로 색상화**됩니다:

**Stage 1 색상**:
- 🟠 주황: 날짜 변경 셀
- 🟡 노랑: 신규 레코드 전체 행

**Stage 4 색상**:
- 🔴 빨강: 시간 역전 (날짜 컬럼만)
- 🟠 주황: ML 이상치 (치명적/높음)
- 🟡 노랑: ML 이상치 (보통/낮음) + 과도 체류
- 🟣 보라: 데이터 품질

**⚠️ 중요**: Stage 4 색상화를 활성화하려면 `--stage4-visualize` 플래그가 **필수**입니다!

**플래그 없이 실행하면 색상이 적용되지 않습니다.**

```bash
# 권장: 배치 스크립트 사용 (플래그 자동 포함)
.\run_full_pipeline.bat

# 수동 실행 시 플래그 필수
python run_pipeline.py --all --stage4-visualize
```

자세한 내용: [색상 작업 완료 보고서](docs/reports/COLOR_FIX_SUMMARY.md)

## 📊 실행 결과 (v4.0 Balanced Boost)

### 이상치 탐지 성능
- **ML 이상치**: 115건 (기존 3,724건에서 97% 감소)
- **위험도 범위**: 0.981~0.999 (포화 문제 완전 해결)
- **위험도 1.000**: 0건 (100% 해결)

### 이상치 유형별 분포
- 데이터 품질: 1건
- 시간 역전: 790건 (치명적)
- 과도 체류: 258건
- ML 이상치: 115건

### 실행 시간 (5,834행 기준)
- Stage 1: ~29초
- Stage 2: ~7초
- Stage 3: ~43초
- Stage 4: ~4초
- **총 실행 시간**: ~83초

## 🚀 주요 개선사항 (v2.0)

### 이름 변경
- **Post-AGI** → **Derived Columns** (파생 컬럼)
- 더 명확하고 표준적인 용어 사용

### 구조 통합
- 분산된 파일들을 `hvdc_pipeline/` 하나로 통합
- 일관된 디렉토리 구조
- 중복 파일 제거

### 기능 향상
- 통합 실행 스크립트 (`run_pipeline.py`)
- YAML 기반 설정 관리
- 모듈화된 구조

## 📁 프로젝트 구조

```
hvdc_pipeline/
├── data/
│   ├── raw/                           # 원본 데이터 (읽기 전용)
│   │   ├── CASE LIST.xlsx
│   │   └── HVDC_WAREHOUSE_HITACHI_HE.xlsx
│   ├── processed/
│   │   ├── synced/                   # Stage 1: 동기화 결과
│   │   ├── derived/                  # Stage 2: 파생 컬럼 처리 결과
│   │   └── reports/                  # Stage 3: 최종 보고서
│   └── anomaly/                      # Stage 4: 이상치 분석 결과
│
├── scripts/
│   ├── stage1_sync/                  # 데이터 동기화
│   ├── stage2_derived/               # 파생 컬럼 처리
│   ├── stage3_report/                # 종합 보고서 생성
│   └── stage4_anomaly/               # 이상치 탐지
│
├── docs/                             # 모든 문서
├── tests/                            # 모든 테스트
├── config/                           # 설정 파일
├── logs/                             # 로그 파일
├── temp/                             # 임시 파일
├── run_pipeline.py                   # 통합 실행 스크립트
├── requirements.txt
└── README.md
```

## 🔄 파이프라인 단계

### Stage 1: 데이터 동기화 (Data Synchronization)
- 원본 데이터 로드 및 정제
- 컬럼 정규화 및 타입 변환
- 동기화된 데이터 출력

### Stage 2: 파생 컬럼 생성 (Derived Columns)
- **13개 파생 컬럼** 자동 계산:
  - **상태 관련 (6개)**: Status_SITE, Status_WAREHOUSE, Status_Current, Status_Location, Status_Location_Date, Status_Storage
  - **처리량 관련 (5개)**: Site_AGI_handling, WH_AGI_handling, Total_AGI_handling, Minus, Final_AGI_handling
  - **분석 관련 (2개)**: Stack_Status, SQM
- 벡터화 연산으로 고성능 처리

### Stage 3: 보고서 생성 (Report Generation)
- 다중 시트 Excel 보고서 생성
- 창고별/사이트별 분석
- KPI 대시보드

### Stage 4: 이상치 탐지 (Balanced Boost Edition v4.0)
- **ECDF 캘리브레이션**: 위험도를 0.001~0.999 범위로 정규화
- **Balanced Boost**: 룰/통계/ML 혼합 위험도 시스템
  - 시간 역전 감지: +0.25 가산
  - 통계 이상(높음/치명): +0.15 가산
  - 통계 이상(보통): +0.08 가산
- **위치별 임계치**: MOSB/DSV 등 지점별 IQR+MAD 과도 체류 판정
- **PyOD 앙상블 ML**: IsolationForest 기반 이상치 탐지 (sklearn 자동 폴백)
- **실시간 시각화**: 색상 기반 이상치 표시
- **기본 시트**: `통합_원본데이터_Fixed` (Stage 3 출력)
- **Resilient 처리**: 빈 문자열이나 공백 시트명은 자동으로 기본값으로 정규화
- **CLI 오버라이드**: `--stage4-sheet-name` 옵션으로 다른 시트 지정 가능

## 🛠️ 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 실행 옵션 선택

#### 옵션 A: Master NO. 순서 정렬 (권장)
```bash
python run_pipeline.py --all
```
- **특징**: 출력 파일이 Case List.xlsx의 NO. 순서대로 정렬됨
- **장점**: Master 파일과 동일한 순서로 데이터 확인 가능
- **처리 시간**: 약 35초
- **권장 용도**: 보고서 작성, 데이터 분석

#### 옵션 B: 정렬 없이 빠른 실행
```bash
python run_pipeline.py --all --no-sorting
```
- **특징**: 원본 Warehouse 파일 순서 유지
- **장점**: 빠른 처리 속도
- **처리 시간**: 약 30초
- **권장 용도**: 빠른 확인, 개발 테스트

### 3. 특정 Stage만 실행
```bash
# Stage 2만 실행 (파생 컬럼 생성)
python run_pipeline.py --stage 2

# Stage 1, 2 실행
python run_pipeline.py --stage 1,2
```

## ⚙️ 설정

설정 파일은 `config/` 디렉토리에 YAML 형식으로 저장됩니다:

- `pipeline_config.yaml`: 전체 파이프라인 설정
- `stage2_derived_config.yaml`: 파생 컬럼 처리 설정

## 📊 파생 컬럼 상세

### 상태 관련 컬럼 (6개)
1. **Status_SITE**: 사이트 상태 판별
2. **Status_WAREHOUSE**: 창고 상태 판별
3. **Status_Current**: 현재 상태 (최신 위치 기반)
4. **Status_Location**: 최종 위치 (창고 또는 사이트)
5. **Status_Location_Date**: 위치 변경 날짜
6. **Status_Storage**: 저장 상태 (Indoor/Outdoor)

### 처리량 관련 컬럼 (5개)
7. **Site_AGI_handling**: 사이트별 처리량
8. **WH_AGI_handling**: 창고별 처리량
9. **Total_AGI_handling**: 총 처리량
10. **Minus**: 차감량 계산
11. **Final_AGI_handling**: 최종 처리량

### 분석 관련 컬럼 (2개)
12. **Stack_Status**: 적재 상태
13. **SQM**: 면적 계산

## 🎨 색상 시각화 시스템

### Stage 1 (데이터 동기화) 색상
- **🟠 주황색**: Master 파일과 Warehouse 파일 간 날짜 변경사항
- **🟡 노란색**: 새로 추가된 케이스 전체 행

### Stage 4 (이상치 탐지) 색상
- **🔴 빨간색**: 시간 역전 이상치 (날짜 컬럼만)
- **🟠 주황색**: ML 이상치 - 높음/치명적 심각도 (전체 행)
- **🟡 노란색**: ML 이상치 - 보통/낮음 심각도 (전체 행)
- **🟣 보라색**: 데이터 품질 이상 (전체 행)

### 색상 적용 방법
```bash
# Stage 4 이상치 색상 적용
python apply_anomaly_colors.py
```

**자세한 내용**: [Stage 4 색상 적용 보고서](docs/STAGE4_COLOR_APPLICATION_REPORT.md)

## 🔧 Stage 4 튜닝 가이드

### Contamination 조정
```bash
# Stage 4만 실행 (contamination 조정)
python run_pipeline.py --stage 4 --contamination 0.01  # 보수적
python run_pipeline.py --stage 4 --contamination 0.02  # 권장 (기본값)
python run_pipeline.py --stage 4 --contamination 0.05  # 공격적
```

### 가산치 조정
`scripts/stage4_anomaly/anomaly_detector_balanced.py` 수정:
```python
class DetectorConfig:
    rule_boost: float = 0.25      # 시간역전 가산
    stat_boost_high: float = 0.15 # 통계 높음/치명 가산
    stat_boost_med: float = 0.08  # 통계 보통 가산
```

## 🏢 지원 창고 및 사이트

### 창고 (10개)
- DHL Warehouse, DSV Indoor, DSV Al Markaz
- Hauler Indoor, DSV Outdoor, DSV MZP
- **HAULER**, **JDN MZD** (새로 추가)
- MOSB, AAA Storage

### 사이트 (4개)
- MIR, SHU, AGI, DAS

## 🔧 개발자 정보

### 코드 품질 도구
```bash
# 테스트 실행
pytest

# 코드 포맷팅
black .
isort .

# 린팅
flake8

# 타입 체크
mypy .
```

### 로그 확인
```bash
tail -f logs/pipeline.log
```

## 📚 문서

### 🚀 빠른 시작
- [빠른 시작 가이드](QUICK_START.md) - 5분 안에 전체 파이프라인 실행
- [Stage별 상세 가이드](docs/STAGE_BY_STAGE_GUIDE.md) - 통합 실행 가이드

### 📖 Stage별 상세 가이드
- [Stage 1: 데이터 동기화](docs/STAGE1_USER_GUIDE.md) - Master/Warehouse 동기화 및 색상 표시
- [Stage 2: 파생 컬럼 처리](docs/STAGE2_USER_GUIDE.md) - 13개 파생 컬럼 자동 계산
- [Stage 3: 종합 보고서 생성](docs/STAGE3_USER_GUIDE.md) - 5개 시트 KPI 분석 보고서 (벡터화 최적화)
- [Stage 4: 이상치 탐지](docs/STAGE4_USER_GUIDE.md) - 5가지 이상치 유형 자동 탐지

### 🚀 성능 최적화 가이드
- [프로덕션 권장사항](docs/reports/PRODUCTION-RECOMMENDATION.md) - Stage 3 벡터화 버전 사용 권장
- [벡터화 최적화 보고서](docs/reports/stage3-performance-optimization-completed.md) - 82% 성능 개선 상세
- [병렬 처리 테스트](docs/reports/stage3-parallel-optimization-final-report.md) - 병렬 처리 성능 분석

### 🔧 기술 문서
- [파이프라인 실행 가이드](docs/PIPELINE_EXECUTION_GUIDE.md) - 상세한 실행 방법
- [색상 문제 해결](docs/COLOR_FIX_SUMMARY.md) - 빈 셀 색상 문제 해결 완료 보고서

## 📈 성능 지표

- **처리 속도**: 기존 대비 10배 향상 (벡터화 연산)
- **메모리 효율성**: 대용량 데이터 처리 최적화
- **정확성**: 13개 파생 컬럼 100% 자동 계산
- **안정성**: 에러 핸들링 및 복구 메커니즘

## 🤝 기여 가이드

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## 📄 라이선스

이 프로젝트는 Samsung C&T Logistics와 ADNOC·DSV Partnership을 위한 내부 프로젝트입니다.

---

## 📚 추가 문서

- [Core Module 통합 보고서](docs/reports/CORE_MODULE_INTEGRATION_REPORT.md) - Semantic matching 시스템 상세
- [최종 통합 요약](docs/reports/FINAL_INTEGRATION_SUMMARY.md) - v4.0.1 변경 사항
- [Core Module 가이드](scripts/core/README.md) - 사용법 및 예제
- [통합 가이드](scripts/core/INTEGRATION_GUIDE.md) - 개발자 가이드

---

**버전**: v4.0.25 (창고_월별_입출고 계산 수정)
**최종 업데이트**: 2025-10-24
**문의**: AI Development Team
