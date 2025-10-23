# Stage 1 - 비정렬 버전 (No Sorting Version)

**Samsung C&T Logistics | ADNOC·DSV Partnership**

## 개요

이 폴더는 HVDC Pipeline Stage 1의 **비정렬 버전**을 포함합니다. 원본 Warehouse 파일 순서를 유지하여 빠른 처리를 제공합니다.

## 특징

- **원본 순서 유지**: Warehouse 파일의 원래 순서 그대로 출력
- **빠른 처리 속도**: 정렬 로직 없이 빠른 실행
- **처리 시간**: 약 30초
- **권장 용도**: 빠른 확인, 개발 테스트

## 파일 구성

```
stage1_sync_no_sorting/
├── __init__.py                              # 패키지 초기화
├── data_synchronizer_v29_no_sorting.py      # 비정렬 버전 동기화 스크립트
└── README.md                                # 이 파일
```

## 사용 방법

### 1. 파이프라인 통합 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 1 --no-sorting    # 비정렬 버전
python run_pipeline.py --all --no-sorting        # 전체 파이프라인 (비정렬)
```

### 2. 직접 스크립트 실행
```bash
python scripts/stage1_sync_no_sorting/data_synchronizer_v29_no_sorting.py \
  --master "data/raw/Case List.xlsx" \
  --warehouse "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --out "data/processed/synced/output_no_sorting.xlsx"
```

## 출력 파일

- **파일명**: `*.synced_v2.9.4_no_sorting.xlsx`
- **위치**: `data/processed/synced/`
- **특징**: 원본 Warehouse 순서 유지

## 색상 표시

- **🟠 주황색**: 날짜 변경사항
- **🟡 노란색**: 신규 추가된 케이스

## 기술적 세부사항

### 처리 로직
1. Master 파일 로드 (정렬 없음)
2. Warehouse 파일 로드 (원본 순서 유지)
3. 동기화 처리 (Master 우선 원칙)
4. 색상 적용

### 성능 특성
- 정렬 로직 제거로 빠른 실행
- 메모리 사용량 최소화
- 개발/테스트에 최적화

## 정렬 버전과의 차이점

| 항목 | 비정렬 버전 | 정렬 버전 |
|------|------------|----------|
| 처리 시간 | ~30초 | ~35초 |
| 출력 순서 | 원본 순서 | Master NO. 순 |
| 메모리 사용량 | 낮음 | 높음 |
| 권장 용도 | 빠른 확인, 테스트 | 보고서 작성 |

## 관련 문서

- [비정렬 버전 사용 가이드](../../docs/no_sorting_version/STAGE1_USER_GUIDE.md)
- [빠른 시작 가이드](../../docs/no_sorting_version/QUICK_START.md)
- [공통 가이드](../../docs/common/STAGE_BY_STAGE_GUIDE.md)

---

**버전**: v2.9.4
**최종 업데이트**: 2025-01-19
