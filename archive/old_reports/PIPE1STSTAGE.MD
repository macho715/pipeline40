# 전체 파이프라인 처음부터 재실행

## 실행 전략

패치가 적용된 상태에서 전체 파이프라인을 클린하게 재실행합니다.

## 실행 단계

### Stage 0: 기존 결과물 정리 (선택)

기존 출력 파일들을 백업 또는 삭제:

- `hvdc_pipeline/data/processed/synced/*.xlsx`
- `hvdc_pipeline/data/processed/derived/*.xlsx`

### Stage 1: 데이터 동기화 (Master + Warehouse)

**입력**:

- Master: `hvdc_pipeline/data/raw/Case List.xlsx`
- Warehouse: `hvdc_pipeline/data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx`

**실행**:

```bash
python hvdc_pipeline/run_pipeline.py --stage 1
```

**출력**:

- `hvdc_pipeline/data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced.xlsx`
- 예상: ~7,161행, 57컬럼
- 색상: 🟠 날짜 변경 (주황), 🟡 신규 케이스 (노랑)

**패치 효과**:

- ✅ PROJECT_ROOT 안전화
- ✅ 권한 오류 방지 (워하우스 파일 위치 기준)
- ✅ 유령 키 'NAN' 방지

### Stage 1.5: SYNC 결과 2개로 복사

**복사 1: 색상 작업용**

```bash
Copy-Item "hvdc_pipeline/data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced.xlsx" `
          "hvdc_pipeline/data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_for_color.xlsx"
```

**복사 2: 컬럼 작업용**

```bash
Copy-Item "hvdc_pipeline/data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced.xlsx" `
          "hvdc_pipeline/data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_for_derived.xlsx"
```

### Stage 2A: 색상 작업 (파일 1)

**대상**: `HVDC WAREHOUSE_HITACHI(HE).synced_for_color.xlsx`

**확인 사항**:

- Stage 1 동기화 과정에서 이미 색상이 적용되어 있는지 확인
- 색상이 없다면 별도 색상 적용 스크립트 실행 필요

**검증**:

- 🟠 주황색: 날짜 변경 셀
- 🟡 노란색: 신규 케이스 전체 행

### Stage 2B: 파생 컬럼 처리 (파일 2)

**입력**: `HVDC WAREHOUSE_HITACHI(HE).synced_for_derived.xlsx`

**처리**:

- Stage 2 파생 컬럼 프로세서 실행
- 입력 파일 경로를 명시적으로 지정

**출력**: `hvdc_pipeline/data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx`

**예상 결과**:

- 7,161행, 70컬럼 (57 + 13 파생)
- 파생 컬럼 13개:
  - Status_WAREHOUSE, Status_SITE, Status_Current
  - Status_Location, Status_Location_Date, Status_Storage
  - wh handling, site handling, total handling
  - minus, final handling, SQM, Stack_Status

### Stage 3: 종합 검증

**검증 항목**:

1. ✅ Stage 1 출력 파일 존재 및 크기
2. ✅ 2개 복사본 생성 확인
3. ✅ 색상 작업 파일 색상 확인
4. ✅ 파생 컬럼 파일 13개 컬럼 확인
5. ✅ 데이터 무결성 (행 수 일치)

## 예상 산출물

```
hvdc_pipeline/
└── data/
    └── processed/
        ├── synced/
        │   ├── HVDC WAREHOUSE_HITACHI(HE).synced.xlsx (원본)
        │   ├── HVDC WAREHOUSE_HITACHI(HE).synced_for_color.xlsx (색상용)
        │   └── HVDC WAREHOUSE_HITACHI(HE).synced_for_derived.xlsx (컬럼용)
        └── derived/
            └── HVDC WAREHOUSE_HITACHI(HE).xlsx (파생 컬럼 추가)
```

## 실행 시간 예상

- Stage 1: ~100초
- 파일 복사: ~5초
- Stage 2: ~11초
- **총 예상 시간**: ~2분

## 주의사항

- 기존 파일이 열려있으면 덮어쓰기 실패할 수 있음
- 권한 오류는 패치로 해결됨
- Stage 2는 색상을 보존하지 않음 (설계된 동작)
