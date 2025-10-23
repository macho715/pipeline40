# Stage 1: 비정렬 버전 데이터 동기화 가이드

## 📋 개요

이 가이드는 HVDC Pipeline Stage 1의 **비정렬 버전**에 대한 상세한 사용법을 제공합니다. 원본 Warehouse 순서를 유지하여 빠른 처리를 제공합니다.

### 주요 특징
- **원본 순서 유지**: Warehouse 파일의 원래 순서 그대로 출력
- **빠른 처리 속도**: 정렬 로직 없이 빠른 실행
- **처리 시간**: 약 30초
- **권장 용도**: 빠른 확인, 개발 테스트

## 🚀 실행 방법

### 빠른 실행 (비정렬 버전)
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 1 --no-sorting
```

### 전체 파이프라인 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --all --no-sorting
```

### 직접 스크립트 실행
```bash
cd hvdc_pipeline
python scripts/stage1_sync_no_sorting/data_synchronizer_v29_no_sorting.py \
  --master "data/raw/Case List.xlsx" \
  --warehouse "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --out "data/processed/synced/output_no_sorting.xlsx"
```

## 📊 처리 과정

### 1. 파일 로드
- Master 파일과 Warehouse 파일을 순서대로 로드
- 정렬 처리 없이 원본 순서 유지

### 2. 동기화 처리
- Master 우선 원칙으로 데이터 동기화
- Case NO 기준으로 매칭 및 업데이트

### 3. 색상 적용
- 변경사항을 색상으로 표시
- 신규 Case는 끝에 추가

## 📁 출력 파일

### 파일 위치
```
data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4_no_sorting.xlsx
```

### 파일 특징
- **정렬 순서**: 원본 Warehouse 순서 유지
- **색상 표시**: 변경사항이 시각적으로 표시됨
- **데이터 완정성**: Master와 Warehouse 데이터 완전 동기화

## 🎨 색상 표시 규칙

### 주황색 (FFC000): 날짜 변경
- **조건**: 날짜 필드에서 실제 값이 변경된 경우
- **적용**: 해당 셀만 색칠

### 노란색 (FFFF00): 신규 행
- **조건**: Master에만 있고 Warehouse에 없는 Case
- **적용**: 전체 행의 데이터가 있는 셀만 색칠

## 📈 성능 특성

### 처리 시간
- **비정렬 버전**: 약 30초
- **정렬 처리 없음**: 빠른 실행

### 메모리 사용량
- 정렬 로직 제거로 메모리 사용량 최소화
- 대용량 파일 처리에 최적화

### 성능 비교
| 항목 | 비정렬 버전 | 정렬 버전 |
|------|------------|----------|
| 처리 시간 | ~30초 | ~35초 |
| 메모리 사용량 | 낮음 | 높음 |
| 출력 순서 | 원본 순서 | Master NO. 순 |

## 🔧 고급 설정

### 설정 파일 수정
```yaml
# config/pipeline_config.yaml
stage1:
  sorting:
    enabled: false
    no_sorting_suffix: "_no_sorting"
```

### 커스텀 실행 옵션
```bash
# 특정 출력 파일명 지정
python run_pipeline.py --stage 1 --no-sorting --output "custom_no_sorting.xlsx"

# 로그 레벨 조정
python run_pipeline.py --stage 1 --no-sorting --log-level DEBUG
```

## ⚠️ 문제 해결

### 1. Case NO 매칭 실패
**증상**:
```
[WARNING] Case NO 매칭률 낮음: 10%
```

**해결방법**:
1. **컬럼명 확인**:
```bash
python -c "
import pandas as pd
master = pd.read_excel('data/raw/Case List.xlsx')
warehouse = pd.read_excel('data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx')
print('Master 컬럼:', master.columns.tolist())
print('Warehouse 컬럼:', warehouse.columns.tolist())
"
```

2. **유연한 매칭**: 대소문자/특수문자 차이 자동 처리

### 2. 날짜 형식 오류
**원인**: 다양한 날짜 형식이 혼재

**해결방법**: 자동 정규화 적용됨
- `2024-10-03 190000` → `2024-10-03`
- `10/03/2024 7:00:00 PM` → `2024-10-03`

### 3. 권한 오류
**해결방법**:
```bash
# Windows: Excel 프로세스 종료
taskkill /F /IM EXCEL.EXE
```

## 🔄 정렬 버전과의 선택 가이드

### 비정렬 버전을 선택하는 경우
- **빠른 확인이 필요한 경우**
- **개발/테스트 환경**
- **메모리 사용량을 최소화해야 하는 경우**
- **원본 순서가 중요한 경우**

### 정렬 버전을 선택하는 경우
- **보고서 작성이 필요한 경우**
- **Master 파일 순서로 확인해야 하는 경우**
- **데이터 분석 작업**

## 📞 추가 지원

### 관련 문서
- [빠른 시작 가이드](QUICK_START.md)
- [공통 Stage 가이드](../common/STAGE_BY_STAGE_GUIDE.md)
- [정렬 버전 가이드](../sorted_version/STAGE1_USER_GUIDE.md)

### 로그 분석
```bash
# 상세 로그 확인
tail -f logs/pipeline.log

# 비정렬 버전 관련 로그
grep "no-sorting" logs/pipeline.log
```

---

**📅 최종 업데이트**: 2025-01-19
**🔖 버전**: v2.9.4 (비정렬 버전)
**👥 작성자**: HVDC 파이프라인 개발팀
