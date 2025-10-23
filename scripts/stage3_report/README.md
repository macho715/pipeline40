# Stage 3 - 종합 보고서 생성 (Report Generation)

**Samsung C&T Logistics | ADNOC·DSV Partnership**

## 개요

Stage 3는 Stage 2의 파생 컬럼 데이터를 기반으로 **5개 시트**로 구성된 종합 분석 보고서를 생성합니다.

## 파일 구성

```
stage3_report/
├── __init__.py                              # 패키지 초기화
├── column_definitions.py                    # 컬럼 정의
├── hvdc_excel_reporter_final_sqm_rev.py     # 보고서 생성 메인 로직
├── report_generator.py                      # 보고서 생성기
└── utils.py                                 # 유틸리티 함수
```

## 보고서 구성 (5개 시트)

1. **통합_원본데이터_Fixed**: 전체 원본 데이터 + 입고일자
2. **HITACHI_원본데이터_Fixed**: HITACHI 데이터
3. **SIEMENSE_원본데이터_Fixed**: SIEMENSE 데이터
4. **창고_월별_입출고**: 창고별 월별 입출고 현황
5. **HITACHI_입고로직_종합리포트_Fixed**: KPI 종합 분석

## 주요 기능

- **입고일자 자동 계산**: 모든 창고 컬럼의 최소 날짜
- **창고별 집계**: 10개 창고 (DHL WH 포함)
- **사이트별 집계**: 4개 사이트 (MIR, SHU, AGI, DAS)
- **월별 분석**: 입출고 추세 분석

## 사용 방법

### 파이프라인 통합 실행
```bash
python run_pipeline.py --stage 3
```

### 입력/출력
- **입력**: `data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx`
- **출력**: `data/processed/reports/HVDC_입고로직_종합리포트_[TIMESTAMP].xlsx`

## 기술적 세부사항

- **처리 시간**: 약 115초
- **컬럼 순서 보존**: Stage 1의 컬럼 순서 완벽 유지
- **10개 창고 지원**: DHL WH, DSV Indoor, DSV Al Markaz, Hauler Indoor, DSV Outdoor, DSV MZP, HAULER, JDN MZD, MOSB, AAA Storage

## 색상 시각화 연계

Stage 3 보고서는 Stage 4 이상치 탐지의 입력 파일로 사용됩니다. Stage 4 실행 시 이상치가 색상으로 표시됩니다.

### Stage 1 색상 (이미 적용됨)
- **🟠 주황색**: 날짜 변경 셀 (Master와 Warehouse 간 차이)
- **🟡 노란색**: 신규 추가 케이스 전체 행

### Stage 4 색상 (자동 적용)
Stage 4 실행 시 보고서에 추가되는 색상:
- **🔴 빨간색**: 시간 역전 이상치 (날짜 컬럼만)
- **🟠 주황색**: ML 이상치 - 높음/치명적 (전체 행)
- **🟡 노란색**: ML 이상치 - 보통/낮음 (전체 행)
- **🟣 보라색**: 데이터 품질 이상 (전체 행)

**중요**: Stage 4 색상을 적용하려면 `--stage4-visualize` 플래그가 필요합니다.

```bash
# 올바른 실행 방법
python run_pipeline.py --stage 4 --stage4-visualize
```

자세한 내용: [COLOR_FIX_SUMMARY.md](../../COLOR_FIX_SUMMARY.md)

---

**버전**: v4.0.12
**최종 업데이트**: 2025-10-22
