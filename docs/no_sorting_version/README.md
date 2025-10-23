# 비정렬 버전 (No Sorting Version) 문서

**Samsung C&T Logistics | ADNOC·DSV Partnership**

이 폴더는 HVDC Pipeline의 **비정렬 버전**에 대한 모든 문서를 포함합니다.

## 📋 문서 구성

### 📖 사용자 가이드
- **[빠른 시작 가이드](QUICK_START.md)** - 비정렬 버전 빠른 실행하기
- **[Stage 1 상세 가이드](STAGE1_USER_GUIDE.md)** - 비정렬 버전 데이터 동기화 상세 설명

## 🎯 비정렬 버전 특징

### 주요 특징
- **원본 순서 유지**: Warehouse 파일의 원래 순서 그대로 출력
- **빠른 처리 속도**: 정렬 로직 없이 빠른 실행
- **처리 시간**: 약 30초
- **권장 용도**: 빠른 확인, 개발 테스트

### 출력 파일
- **파일명**: `*.synced_v2.9.4_no_sorting.xlsx`
- **위치**: `data/processed/synced/`
- **특징**: 원본 Warehouse 순서 유지

## 🚀 빠른 실행

### 빠른 실행 (비정렬 버전)
```bash
cd hvdc_pipeline
python run_pipeline.py --all --no-sorting
```

### Stage 1만 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 1 --no-sorting
```

## 📊 성능 특성

| 항목 | 비정렬 버전 |
|------|------------|
| 처리 시간 | ~30초 |
| 출력 순서 | 원본 순서 |
| 권장 용도 | 빠른 확인, 개발 테스트 |
| 출력 파일명 | `*.synced_v2.9.4_no_sorting.xlsx` |
| 정렬 로직 | 정렬 없음 |

## 🎨 색상 표시

### Stage 1 색상 (데이터 동기화)
- **🟠 주황색**: Master 파일과 Warehouse 파일 간 날짜 변경사항
- **🟡 노란색**: 새로 추가된 케이스 전체 행

## 🔄 정렬 버전과의 비교

| 항목 | 비정렬 버전 | 정렬 버전 |
|------|------------|----------|
| 처리 시간 | ~30초 | ~35초 |
| 메모리 사용량 | 낮음 | 높음 |
| 출력 순서 | 원본 순서 | Master NO. 순 |
| 권장 용도 | 빠른 확인, 테스트 | 보고서 작성 |

## 📚 관련 문서

### 공통 문서
- [공통 Stage 가이드](../common/STAGE_BY_STAGE_GUIDE.md)
- [Stage 2 가이드](../common/STAGE2_USER_GUIDE.md)
- [Stage 3 가이드](../common/STAGE3_USER_GUIDE.md)
- [Stage 4 가이드](../common/STAGE4_USER_GUIDE.md)

### 기술 문서
- [Stage 1 상세 로직 가이드](../common/STAGE1_DETAILED_LOGIC_GUIDE.md)
- [파이프라인 실행 가이드](../common/PIPELINE_EXECUTION_GUIDE.md)

### 비교 문서
- [정렬 버전 문서](../sorted_version/README.md)

## 🔧 문제 해결

### 일반적인 문제
1. **Case NO 매칭 실패**: [Stage 1 상세 가이드](STAGE1_USER_GUIDE.md) 참조
2. **색상 표시 문제**: [공통 색상 문제 해결](../common/COLOR_FIX_SUMMARY.md) 참조
3. **권한 오류**: Excel 프로세스 종료 후 재실행

### 로그 확인
```bash
# 파이프라인 실행 로그
tail -f logs/pipeline.log

# 비정렬 버전 관련 로그
grep "no-sorting" logs/pipeline.log
```

## 🎯 언제 비정렬 버전을 사용할까?

### 비정렬 버전을 선택하는 경우
- **빠른 확인이 필요한 경우**
- **개발/테스트 환경**
- **메모리 사용량을 최소화해야 하는 경우**
- **원본 순서가 중요한 경우**

### 정렬 버전을 선택하는 경우
- **보고서 작성이 필요한 경우**
- **Master 파일 순서로 확인해야 하는 경우**
- **데이터 분석 작업**

## 📞 지원

### 문제 신고 절차
1. 실행 로그 확인 (`logs/pipeline.log`)
2. 오류 메시지 복사
3. 입력 파일 상태 확인
4. 문제 상황 상세 기록

---

**📅 최종 업데이트**: 2025-01-19
**🔖 버전**: v2.9.4 (비정렬 버전)
**👥 작성자**: HVDC 파이프라인 개발팀
