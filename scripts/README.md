# HVDC Pipeline 스크립트 구조

**Samsung C&T Logistics | ADNOC·DSV Partnership**

HVDC Pipeline의 모든 스크립트에 대한 구조 설명입니다.

## 📁 스크립트 구조

### 🔄 Stage 1 - 정렬/비정렬 버전 분리

#### 정렬 버전 (Sorted Version)
```
scripts/stage1_sync_sorted/
├── __init__.py                    # 패키지 초기화
├── data_synchronizer_v29.py       # 정렬 버전 동기화 스크립트
└── README.md                      # 정렬 버전 설명
```

**특징**:
- Master NO. 순서로 정렬
- 보고서 작성 최적화
- 처리 시간: 약 35초

#### 비정렬 버전 (No Sorting Version)
```
scripts/stage1_sync_no_sorting/
├── __init__.py                              # 패키지 초기화
├── data_synchronizer_v29_no_sorting.py      # 비정렬 버전 동기화 스크립트
└── README.md                                # 비정렬 버전 설명
```

**특징**:
- 원본 Warehouse 순서 유지
- 빠른 처리 속도
- 처리 시간: 약 30초

### 📊 기타 Stage 스크립트

#### Stage 2: 파생 컬럼 처리
```
scripts/stage2_derived/
├── derived_columns_processor.py    # 13개 파생 컬럼 처리
└── ...
```

#### Stage 3: 종합 보고서 생성
```
scripts/stage3_report/
├── report_generator.py             # KPI 보고서 생성
└── ...
```

#### Stage 4: 이상치 탐지 (Balanced Boost Edition v4.0)
```
scripts/stage4_anomaly/
├── anomaly_detector_balanced.py    # v4 Balanced Boost 이상치 탐지
├── anomaly_visualizer.py            # 색상 시각화
├── analysis_reporter.py             # 분석 리포트 생성
└── ...
```


## 🚀 스크립트 사용법

### 파이프라인 통합 실행
```bash
# 정렬 버전 (기본)
python run_pipeline.py --all

# 비정렬 버전
python run_pipeline.py --all --no-sorting
```

### 개별 스크립트 실행

#### 정렬 버전 직접 실행
```bash
python scripts/stage1_sync_sorted/data_synchronizer_v29.py \
  --master "data/raw/Case List.xlsx" \
  --warehouse "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --out "output_sorted.xlsx"
```

#### 비정렬 버전 직접 실행
```bash
python scripts/stage1_sync_no_sorting/data_synchronizer_v29_no_sorting.py \
  --master "data/raw/Case List.xlsx" \
  --warehouse "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --out "output_no_sorting.xlsx"
```


## 📊 버전별 스크립트 비교

| 항목 | 정렬 버전 | 비정렬 버전 |
|------|----------|------------|
| 스크립트 위치 | `stage1_sync_sorted/` | `stage1_sync_no_sorting/` |
| 메인 클래스 | `DataSynchronizerV29` | `DataSynchronizerV29NoSorting` |
| 정렬 처리 | Master NO 기준 정렬 | 정렬 없음 |
| 처리 시간 | ~35초 | ~30초 |
| 메모리 사용량 | 높음 | 낮음 |

## 🔧 개발 및 확장

### 새로운 버전 추가
1. 새 폴더 생성 (예: `stage1_sync_custom/`)
2. `__init__.py` 파일 생성
3. 동기화 스크립트 작성
4. `README.md` 작성
5. `run_pipeline.py`에 import 경로 추가

### 스크립트 수정 시 주의사항
- 정렬 버전과 비정렬 버전은 독립적으로 수정 가능
- 공통 기능은 두 버전 모두에 적용 필요
- 각 버전의 README.md 업데이트 필요

## 📚 관련 문서

### 버전별 문서
- [정렬 버전 문서](../docs/sorted_version/)
- [비정렬 버전 문서](../docs/no_sorting_version/)
- [공통 문서](../docs/common/)

### 스크립트별 상세 가이드
- [Stage 1 정렬 버전](../docs/sorted_version/STAGE1_USER_GUIDE.md)
- [Stage 1 비정렬 버전](../docs/no_sorting_version/STAGE1_USER_GUIDE.md)
- [Stage 2 가이드](../docs/common/STAGE2_USER_GUIDE.md)
- [Stage 3 가이드](../docs/common/STAGE3_USER_GUIDE.md)
- [Stage 4 가이드](../docs/common/STAGE4_USER_GUIDE.md)

## 🔍 디버깅 및 로그

### 로그 확인
```bash
# 파이프라인 실행 로그
tail -f logs/pipeline.log

# 특정 스크립트 로그
grep "data_synchronizer" logs/pipeline.log
```

### 스크립트별 디버깅
```bash
# 정렬 버전 디버깅
python -m pdb scripts/stage1_sync_sorted/data_synchronizer_v29.py \
  --master "data/raw/Case List.xlsx" \
  --warehouse "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx"

# 비정렬 버전 디버깅
python -m pdb scripts/stage1_sync_no_sorting/data_synchronizer_v29_no_sorting.py \
  --master "data/raw/Case List.xlsx" \
  --warehouse "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx"
```

---

### v4.0.12 주요 개선사항 (2025-10-22)

#### Stage 1 컬럼 순서 최적화
- **Shifting 위치 수정**: 원본 데이터 순서 유지 (창고 컬럼 뒤)
- **Source_Sheet 분리**: 메타데이터로 분류, 컬럼 순서 로직에서 제외
- **DHL WH 데이터 복구**: 102건 데이터 정상 처리
- **전체 파이프라인**: 5,553행 정상 처리

#### 코드 정리 완료
- 임시/분석 스크립트 아카이브 처리
- `_archived/cleanup_2025-10-22/` 디렉토리로 이동
- 캐시 디렉토리 정리 완료

## 🆕 v4.0.0 주요 개선사항 (2025-10-22)

### Stage 4 Balanced Boost Edition
- **ECDF 캘리브레이션**: 위험도 포화 문제 완전 해결 (0.981~0.999 범위)
- **Balanced Boost 혼합 위험도**: 룰/통계 근거 기반 ML 위험도 가산 시스템
- **위치별 체류 임계치**: IQR+MAD 기반 과도 체류 정밀 판정
- **헤더 정규화 강화**: 공백 변형 자동 흡수
- **ML 이상치 97% 감소**: 3,724건 → 115건
- **위험도 1.000 포화 100% 해결**: 0건

### v3.0.1 주요 개선사항

### Stage 3 Toolkit 보강 패치 통합
- **컬럼 정규화 강화**:
  - `utils.py`: 공백 정규화 + 동의어 매핑 함수
  - `AAA  Storage` → `AAA Storage` 자동 변환
  - `site  handling` ↔ `site handling` 통합 처리
- **향상된 데이터 로딩**:
  - Excel 로드 직후 정규화 적용
  - 데이터 결합 후 재정규화
  - 컬럼 누락 방지
- **파일 구조**:
  - `scripts/stage3_report/utils.py` 추가
  - `scripts/stage3_report/column_definitions.py` 추가
  - toolkit 패키지 구조 통합

### Stage 4 PyOD 앙상블 ML (v3.0.0)
- **이상치 탐지**: 1건 → 7,022건 (7,000배 향상)
- **ML 모델**: ECOD/COPOD/HBOS/IForest 앙상블
- **자동 폴백**: sklearn IsolationForest
- **위험도**: 0~1 ECDF 정규화

### 완전 자동화 달성
- **날짜 범위**: 2025-10까지 자동 확장 (33개월)
- **파일 탐색**: 최신 파일 자동 선택
- **색상 적용**: Stage 1/4 완전 자동
- **백업 시스템**: 안전한 롤백 가능

---

**📅 최종 업데이트**: 2025-10-22
**🔖 버전**: v4.0.0
**👥 작성자**: HVDC 파이프라인 개발팀
