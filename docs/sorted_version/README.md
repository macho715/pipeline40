# 정렬 버전 (Sorted Version) 문서

**Samsung C&T Logistics | ADNOC·DSV Partnership**

이 폴더는 HVDC Pipeline의 **정렬 버전**에 대한 모든 문서를 포함합니다.

## 📋 문서 구성

### 📖 사용자 가이드
- **[빠른 시작 가이드](QUICK_START.md)** - 5분 안에 정렬 버전 실행하기
- **[Stage 1 상세 가이드](STAGE1_USER_GUIDE.md)** - 정렬 버전 데이터 동기화 상세 설명

## 🎯 정렬 버전 특징

### 주요 특징
- **Warehouse 원본 순서 유지**: HVDC HITACHI 파일의 순서는 변경하지 않음
- **신규 케이스 하단 추가**: Master의 신규 항목만 제일 하단에 추가 ✅
- **데이터 동기화**: Master 데이터로 업데이트 (원본 위치 유지)
- **처리 시간**: 약 35초
- **권장 용도**: 원본 순서 보존이 필요한 경우

### 출력 파일
- **파일명**: `*.synced_v3.6.xlsx`
- **위치**: `data/processed/synced/`
- **특징**: Warehouse 원본 순서 유지 + 신규 케이스 하단 추가

## 🚀 빠른 실행

### 기본 실행 (정렬 버전)
```bash
cd hvdc_pipeline
python run_pipeline.py --all
```

### Stage 1만 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 1
```

## 📊 성능 특성

| 항목 | 정렬 버전 |
|------|----------|
| 처리 시간 | ~35초 |
| 출력 순서 | Master NO. 순 |
| 권장 용도 | 보고서 작성, 데이터 분석 |
| 출력 파일명 | `*.synced_v2.9.4.xlsx` |
| 정렬 로직 | Master NO. 기준 정렬 |

## 🎨 색상 표시

### Stage 1 색상 (데이터 동기화)
- **🟠 주황색**: Master 파일과 Warehouse 파일 간 날짜 변경사항
- **🟡 노란색**: 새로 추가된 케이스 전체 행

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
- [비정렬 버전 문서](../no_sorting_version/README.md)

## 🔧 문제 해결

### 일반적인 문제
1. **Master NO. 정렬 실패**: [Stage 1 상세 가이드](STAGE1_USER_GUIDE.md) 참조
2. **색상 표시 문제**: [공통 색상 문제 해결](../common/COLOR_FIX_SUMMARY.md) 참조
3. **권한 오류**: Excel 프로세스 종료 후 재실행

### 로그 확인
```bash
# 파이프라인 실행 로그
tail -f logs/pipeline.log

# 정렬 버전 관련 로그
grep "sorted" logs/pipeline.log
```

## 📞 지원

### 문제 신고 절차
1. 실행 로그 확인 (`logs/pipeline.log`)
2. 오류 메시지 복사
3. 입력 파일 상태 확인
4. 문제 상황 상세 기록

---

**📅 최종 업데이트**: 2025-01-19
**🔖 버전**: v2.9.4 (정렬 버전)
**👥 작성자**: HVDC 파이프라인 개발팀
