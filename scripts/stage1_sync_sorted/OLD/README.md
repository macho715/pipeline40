# Stage 1 - 정렬 버전 (Sorted Version)

**Samsung C&T Logistics | ADNOC·DSV Partnership**

## 개요

이 폴더는 HVDC Pipeline Stage 1의 **정렬 버전**을 포함합니다. Master NO. 순서로 데이터를 정렬하여 출력합니다.

## 특징

- **Master NO. 정렬**: Case List.xlsx의 NO. 순서대로 정렬
- **보고서 작성 최적화**: Master 파일과 동일한 순서로 데이터 확인 가능
- **처리 시간**: 약 35초
- **권장 용도**: 보고서 작성, 데이터 분석

## 파일 구성

```
stage1_sync_sorted/
├── __init__.py                    # 패키지 초기화
├── data_synchronizer_v29.py       # 정렬 버전 동기화 스크립트
└── README.md                      # 이 파일
```

## 사용 방법

### 1. 파이프라인 통합 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 1          # 정렬 버전 (기본)
python run_pipeline.py --all              # 전체 파이프라인 (정렬)
```

### 2. 직접 스크립트 실행
```bash
python scripts/stage1_sync_sorted/data_synchronizer_v29.py \
  --master "data/raw/Case List.xlsx" \
  --warehouse "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --out "data/processed/synced/output.xlsx"
```

## 출력 파일

- **파일명**: `*.synced_v2.9.4.xlsx`
- **위치**: `data/processed/synced/`
- **특징**: Master NO. 순서로 정렬된 데이터

## 색상 표시

- **🟠 주황색**: 날짜 변경사항
- **🟡 노란색**: 신규 추가된 케이스

## 기술적 세부사항

### 정렬 로직
1. Master 파일을 NO. 컬럼 기준으로 정렬
2. Master Case NO 순서에 따라 Warehouse 데이터 정렬
3. 동기화 처리 후 색상 적용

### 성능 특성
- 정렬 처리로 약간의 시간 추가 (5초)
- 메모리 사용량 증가
- 보고서 작성에 최적화된 순서

## 관련 문서

- [정렬 버전 사용 가이드](../../docs/sorted_version/STAGE1_USER_GUIDE.md)
- [빠른 시작 가이드](../../docs/sorted_version/QUICK_START.md)
- [공통 가이드](../../docs/common/STAGE_BY_STAGE_GUIDE.md)

---

**버전**: v2.9.4
**최종 업데이트**: 2025-01-19
