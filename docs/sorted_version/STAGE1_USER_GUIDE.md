# Stage 1: 정렬 버전 데이터 동기화 가이드

## 📋 개요

이 가이드는 HVDC Pipeline Stage 1의 **정렬 버전**에 대한 상세한 사용법을 제공합니다. Master NO. 순서로 정렬된 데이터 동기화에 최적화되어 있습니다.

### 주요 특징
- **Warehouse 원본 순서 유지**: HVDC HITACHI 파일의 순서는 변경하지 않음
- **신규 케이스 하단 추가**: Master의 신규 항목만 제일 하단에 추가 ✅
- **데이터 동기화**: Master 데이터로 업데이트 (원본 위치 유지)
- **처리 시간**: 약 35초
- **권장 용도**: 원본 순서 보존이 필요한 경우

## 🚀 실행 방법

### 기본 실행 (정렬 버전)
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 1
```

### 전체 파이프라인 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --all
```

### 직접 스크립트 실행
```bash
cd hvdc_pipeline
python scripts/stage1_sync_sorted/data_synchronizer_v29.py \
  --master "data/raw/Case List.xlsx" \
  --warehouse "data/raw/HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --out "data/processed/synced/output.xlsx"
```

## 📊 정렬 처리 과정

### 1. Warehouse 원본 순서 유지
- **HVDC HITACHI 파일의 원본 순서는 변경하지 않음**
- 기존 케이스는 원래 위치에서 Master 데이터로 업데이트만 수행

### 2. Master 데이터 동기화
- Master에 있는 데이터로 Warehouse 업데이트
- **순서 변경 없음** - 원본 위치 유지

### 3. 신규 케이스 추가
- Master에만 있고 Warehouse에 없는 케이스
- **제일 하단에 추가** ✅
- 노란색으로 표시

## 📁 출력 파일

### 파일 위치
```
data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx
```

### 파일 특징
- **정렬 순서**: Master (NO, Case No.) 복합 키 순서대로 정렬
- **다중 시트 처리**: NO 중복을 안정적으로 처리
- **색상 표시**: 변경사항이 시각적으로 표시됨
- **데이터 완정성**: Master와 Warehouse 데이터 완전 동기화

## 🎨 색상 표시 규칙

### 주황색 (FFC000): 날짜 변경
- **조건**: 날짜 필드에서 실제 값이 변경된 경우
- **적용**: 해당 셀만 색칠
- **예외**: 빈 셀에는 색상 적용 안함

### 노란색 (FFFF00): 신규 행
- **조건**: Master에만 있고 Warehouse에 없는 Case
- **적용**: 전체 행의 데이터가 있는 셀만 색칠
- **위치**: **제일 하단에 배치** ✅
- **예외**: 빈 셀에는 색상 적용 안함

## 📈 성능 특성

### 처리 시간
- **정렬 버전**: 약 35초
- **정렬 처리**: Master (NO, Case No.) 복합 키 정렬 (약 5초 추가)

### 메모리 사용량
- 정렬 처리로 인한 메모리 사용량 증가
- 대용량 파일 처리 시 고려사항

### 최적화 팁
1. **메모리 정리**: 이전 실행 결과 삭제
2. **프로세스 종료**: 불필요한 프로그램 종료
3. **SSD 사용**: HDD 대신 SSD 사용 권장

## 🔧 고급 설정

### 설정 파일 수정
```yaml
# config/pipeline_config.yaml
stage1:
  sorting:
    enabled: true
    sort_by_master_no: true
    output_suffix: "_v2.9.4"
```

### 커스텀 실행 옵션
```bash
# 특정 출력 파일명 지정
python run_pipeline.py --stage 1 --output "custom_synced.xlsx"

# 로그 레벨 조정
python run_pipeline.py --stage 1 --log-level DEBUG
```

## ⚠️ 문제 해결

### 1. Master NO. 정렬 실패
**증상**: 출력 파일이 Master 순서와 다름

**해결방법**:
1. **NO. 컬럼 확인**:
```bash
python -c "
import pandas as pd
master = pd.read_excel('data/raw/Case List.xlsx')
print('Master 컬럼:', [c for c in master.columns if 'no' in c.lower()])
"
```

2. **수동 정렬**: Master 파일을 원하는 순서로 정렬 후 저장

### 2. 색상이 빈 셀에 적용됨
**해결방법**: 최신 버전의 data_synchronizer_v29.py 사용

### 3. 권한 오류
**해결방법**:
```bash
# Windows: Excel 프로세스 종료
taskkill /F /IM EXCEL.EXE
```

## 📞 추가 지원

### 관련 문서
- [빠른 시작 가이드](QUICK_START.md)
- [공통 Stage 가이드](../common/STAGE_BY_STAGE_GUIDE.md)
- [비정렬 버전 가이드](../no_sorting_version/STAGE1_USER_GUIDE.md)

### 로그 분석
```bash
# 상세 로그 확인
tail -f logs/pipeline.log

# Stage 1 관련 로그만 확인
grep "Stage 1" logs/pipeline.log
```

---

**📅 최종 업데이트**: 2025-01-19
**🔖 버전**: v2.9.4 (정렬 버전)
**👥 작성자**: HVDC 파이프라인 개발팀
