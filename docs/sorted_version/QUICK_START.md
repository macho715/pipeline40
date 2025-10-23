# HVDC Pipeline 정렬 버전 빠른 시작 가이드

**Samsung C&T Logistics | ADNOC·DSV Partnership**

정렬 버전을 사용하여 5분 안에 전체 파이프라인을 실행하는 빠른 가이드입니다.

## 🚀 정렬 버전 실행

### 기본 실행 (Master NO. 순서 정렬)
```bash
cd hvdc_pipeline
python run_pipeline.py --all
```

### Stage 1만 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 1
```

## 📊 정렬 버전 특징

| 항목 | 정렬 버전 |
|------|----------|
| 처리 시간 | ~35초 |
| 출력 순서 | Master NO. 순 |
| 권장 용도 | 보고서 작성, 데이터 분석 |
| 출력 파일명 | `*.synced_v2.9.4.xlsx` |
| 정렬 로직 | Master NO. 기준 정렬 |

## 🎯 정렬 버전을 선택하는 경우

- **보고서 작성이 필요한 경우**
- **Master 파일과 동일한 순서로 데이터 확인해야 하는 경우**
- **데이터 분석 작업**
- **최종 결과물 제출**

## 📁 출력 파일 구조

### Stage 1: 데이터 동기화
```
data/processed/synced/
└── HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx  # 정렬 버전
```

### Stage 2: 파생 컬럼 처리
```
data/processed/derived/
└── HVDC WAREHOUSE_HITACHI(HE).xlsx
```

### Stage 3: 종합 보고서
```
data/processed/reports/
└── HVDC_입고로직_종합리포트_YYYYMMDD_HHMMSS_v3.0-corrected.xlsx
```

### Stage 4: 이상치 탐지
```
data/anomaly/
├── HVDC_anomaly_report.xlsx
└── HVDC_anomaly_report.json
```

## 🎨 색상 시각화

### Stage 1 색상 (데이터 동기화)
- **🟠 주황색**: Master 파일과 Warehouse 파일 간 날짜 변경사항
- **🟡 노란색**: 새로 추가된 케이스 전체 행

### Stage 4 색상 (이상치 탐지)
- **🔴 빨간색**: 시간 역전 이상치
- **🟠 주황색**: ML 이상치 - 높음/치명적 심각도
- **🟡 노란색**: ML 이상치 - 보통/낮음 심각도
- **🟣 보라색**: 데이터 품질 이상

## ⚡ 개별 Stage 실행

### Stage 1만 실행 (데이터 동기화)
```bash
python run_pipeline.py --stage 1
```

### Stage 2만 실행 (파생 컬럼)
```bash
python run_pipeline.py --stage 2
```

### Stage 3만 실행 (종합 보고서)
```bash
python run_pipeline.py --stage 3
```

### Stage 4만 실행 (이상치 탐지 + 색상 적용) ✅
```bash
python run_pipeline.py --stage 4 --stage4-visualize
```
**특징:**
- 자동으로 최신 보고서 파일 탐색
- 이상치 탐지 후 색상 자동 적용

## 📊 예상 실행 시간

| Stage | 정렬 버전 | 설명 |
|-------|----------|------|
| Stage 1 | ~35초 | 데이터 동기화 (정렬 포함) |
| Stage 2 | ~15초 | 파생 컬럼 생성 |
| Stage 3 | ~10초 | 종합 보고서 생성 |
| Stage 4 | ~5초 | 이상치 탐지 |
| **총합** | **~1분** | **전체 파이프라인** |

## 🔧 고급 사용법

### 특정 Stage 조합 실행
```bash
# Stage 1, 2만 실행
python run_pipeline.py --stage 1,2

# Stage 2, 3만 실행
python run_pipeline.py --stage 2,3
```

### 설정 파일 수정
```bash
# 파이프라인 설정 수정
vim config/pipeline_config.yaml
```

## ⚠️ 문제 해결

### 1. 파일을 찾을 수 없음
```bash
# 입력 파일 위치 확인
ls data/raw/
# Case List.xlsx와 HVDC WAREHOUSE_HITACHI(HE).xlsx가 있는지 확인
```

### 2. 권한 오류
```bash
# Excel 파일이 열려있는지 확인하고 닫기
# Windows: 작업 관리자에서 EXCEL.EXE 종료
taskkill /F /IM EXCEL.EXE
```

### 3. 로그 확인
```bash
# 실행 로그 확인
tail -f logs/pipeline.log
```

## 📞 추가 지원

### 상세 가이드
- [Stage 1 상세 가이드](STAGE1_USER_GUIDE.md)
- [공통 Stage 가이드](../common/STAGE_BY_STAGE_GUIDE.md)
- [비정렬 버전 가이드](../no_sorting_version/QUICK_START.md)

### 문제 신고
1. 실행 로그 확인 (`logs/pipeline.log`)
2. 오류 메시지 복사
3. 입력 파일 상태 확인
4. 문제 상황 상세 기록

---

**📅 최종 업데이트**: 2025-10-20
**🔖 버전**: v3.0.1 (정렬 버전)
**👥 작성자**: HVDC 파이프라인 개발팀

## 🆕 v3.0.1 개선사항
- ✅ Stage 3 날짜 범위: 2025-10까지 자동 확장
- ✅ Stage 4 자동 파일 탐색: config 업데이트 불필요
- ✅ 색상 적용 완전 자동화: Stage 1/4 자동 실행
