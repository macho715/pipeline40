# 검증 스크립트 아카이브 (2025-10-22)

프로젝트 루트에서 이동된 검증 및 디버그 스크립트들입니다.

## 아카이브 날짜
2025-10-22

## 아카이브 사유
프로젝트 루트 정리 - 필수 실행 파일만 유지

## 원본 위치
모든 파일은 프로젝트 루트 (`/`)에 있었습니다.

## 디렉토리 구조

```
verification_scripts_2025-10-22/
├── README.md (이 파일)
├── colors/          # 색상 검증 (3개)
│   ├── verify_all_colors.py
│   ├── verify_anomaly_colors.py
│   └── debug_color_matching.py
├── data/            # 데이터 검증 (5개)
│   ├── check_raw_data_all_sheets.py
│   ├── check_raw_data_structure.py
│   ├── check_stage1_source_sheets.py
│   ├── check_stage2_source_sheets.py
│   └── verify_all_sheets_updated.py
├── sorting/         # 정렬 검증 (2개)
│   ├── debug_sorting_issue.py
│   └── verify_all_stages_sorting.py
├── columns/         # 컬럼 검증 (1개)
│   └── detailed_column_check.py
└── misc/            # 기타 검증 (3개)
    ├── check_anomaly_types.py
    ├── check_excel_directly.py
    └── check_master_source_sheet.py
```

## 복원 방법

필요한 스크립트를 프로젝트 루트로 복사:

```bash
# 예: 색상 검증 스크립트 복원
cp scripts/_archived/verification_scripts_2025-10-22/colors/verify_all_colors.py .

# 예: 전체 복원
cp -r scripts/_archived/verification_scripts_2025-10-22/* .
```

## 스크립트 용도

### 색상 검증
- **verify_all_colors.py**: Stage 1/4 전체 색상 작업 검증
- **verify_anomaly_colors.py**: Stage 4 이상치 색상 상세 검증
- **debug_color_matching.py**: 색상 매칭 로직 디버그

### 데이터 검증
- **check_raw_data_all_sheets.py**: 원본 데이터 전체 시트 확인
- **check_raw_data_structure.py**: 원본 데이터 구조 분석
- **check_stage1_source_sheets.py**: Stage 1 Source_Sheet 분포
- **check_stage2_source_sheets.py**: Stage 2 Source_Sheet 분포
- **verify_all_sheets_updated.py**: 전체 시트 업데이트 검증

### 정렬 검증
- **debug_sorting_issue.py**: 정렬 문제 디버그
- **verify_all_stages_sorting.py**: 전체 Stage 정렬 상태 검증

### 컬럼 검증
- **detailed_column_check.py**: Stage별 컬럼 순서/구조 확인

### 기타 검증
- **check_anomaly_types.py**: 이상치 타입 분류/통계
- **check_excel_directly.py**: Excel 파일 직접 확인
- **check_master_source_sheet.py**: Master Source_Sheet 분포

## 참고
이 스크립트들은 개발 과정에서 사용되었으며, 현재 파이프라인은 정상 작동합니다.
문제 발생 시 디버깅 용도로 활용할 수 있습니다.
