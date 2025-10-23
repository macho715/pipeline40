# Stage 3: 종합 보고서 생성 상세 사용 가이드

## 📋 개요

Stage 3은 Stage 2의 파생 컬럼이 추가된 데이터를 기반으로 12개 시트로 구성된 종합 분석 보고서를 생성하는 단계입니다.

> 🔧 **2025-10-23 패치 / Patch:** `melt()` 호출 시 인덱스가 `id_vars`로 잘못 전달되어 발생하던 Stage 3 벡터화 모드의 KeyError를 제거했습니다. 이제 월별 과금 계산이 안정적으로 실행됩니다. / The vectorized Stage 3 workflow now keeps `id_vars` strictly to named columns, eliminating the KeyError triggered by passing index values into `melt()`.

### 주요 기능 (v3.0.1)
- **12개 시트 구성**: 다양한 관점에서 데이터 분석
- **날짜 범위 자동 확장**: 2023-02 ~ 현재 월까지 동적 계산 ✅
- **월별 분석**: 33개월 (2025-10 기준, 자동 확장)
- **KPI 대시보드**: 핵심 지표 시각화
- **데이터 품질 검증**: 데이터 무결성 및 품질 분석
- **트렌드 분석**: 시간별 변화 추이 분석
- **SQM 기반 관리**: 창고 면적 및 과금 분석
- **Toolkit 컬럼 정규화**: AAA Storage, site handling 동의어 자동 매핑 ✅
- **향상된 데이터 로딩**: Excel 로드 직후 정규화 적용 ✅

## 📁 입력 파일 요구사항

### 입력 파일
- **파일**: `data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx`
- **소스**: Stage 2 출력 파일
- **형식**: Excel (.xlsx)
- **필수 컬럼**: Stage 2의 13개 파생 컬럼 포함
- **컬럼 정규화**: v3.0.1에서 자동 적용 ✅

### 필수 파생 컬럼
Stage 2에서 생성된 다음 파생 컬럼들이 필요합니다:
- 시간 관련: Total_Days, DHL_Processing_Days, DSV_Processing_Days, Final_Processing_Days
- 지연 관련: DHL_Delay_Days, DSV_Delay_Days, Total_Delay_Days
- 효율성 관련: DHL_Efficiency, DSV_Efficiency, Overall_Efficiency
- 품질 관련: Data_Completeness, Consistency_Score, Quality_Grade

### v3.0.1 Toolkit 보강 패치
- **컬럼 정규화**: `AAA  Storage` → `AAA Storage` 자동 변환
- **동의어 매핑**: `site  handling` ↔ `site handling` 통합 처리
- **utils.py**: 공백 정규화 + 동의어 매핑 함수
- **column_definitions.py**: 컬럼 정의 상수

## 🚀 실행 방법

### 방법 1: 전체 파이프라인 실행 (권장)
```bash
cd hvdc_pipeline
python run_pipeline.py --all
```

### 방법 2: Stage 3만 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 3
```

### 방법 3: 직접 스크립트 실행
```bash
cd hvdc_pipeline
python scripts/stage3_report/report_generator.py \
  --input "data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --output "data/processed/reports/HVDC_종합리포트_$(date +%Y%m%d_%H%M%S).xlsx"
```

## 📊 5개 시트 상세 구성

### 시트 1: HITACHI_입고로직_종합리포트_Fixed
**목적**: 원본 데이터와 파생 컬럼을 포함한 종합 데이터

**포함 내용**:
- 원본 컬럼 (Case No., ETD/ATD, ETA/ATA 등)
- 파생 컬럼 (13개)
- Stage 1 색상 정보 (주황: 날짜변경, 노랑: 신규)
- 데이터 정렬 (Master NO. 순서)

**특징**:
- 가장 상세한 데이터 시트
- 모든 분석의 기초 데이터
- 색상으로 변경사항 구분

### 시트 2: KPI_대시보드
**목적**: 핵심 성과 지표(KPI) 시각화

**포함 내용**:
- **처리량 지표**:
  - 총 처리 건수
  - 일평균 처리량
  - 월별 처리량 트렌드
- **시간 지표**:
  - 평균 총 소요일수
  - DHL 평균 처리일수
  - DSV 평균 처리일수
- **효율성 지표**:
  - 전체 효율성 평균
  - DHL 효율성 평균
  - DSV 효율성 평균
- **지연 지표**:
  - 지연 발생률
  - 평균 지연일수
  - 지연 원인별 분석

**시각화 요소**:
- 막대 그래프
- 선 그래프
- 원형 차트
- 게이지 차트

### 시트 3: 데이터_품질_검증
**목적**: 데이터 품질 및 무결성 검증 결과

**포함 내용**:
- **완성도 분석**:
  - 필수 컬럼별 완성도
  - 전체 데이터 완성도
  - 누락 데이터 패턴
- **일관성 검증**:
  - 날짜 순서 일관성
  - 논리적 일관성 검사
  - 이상값 탐지 결과
- **품질 등급 분포**:
  - A등급 비율
  - B등급 비율
  - C등급 비율
  - D등급 비율
- **개선 권장사항**:
  - 데이터 수집 개선점
  - 입력 프로세스 개선점
  - 검증 규칙 강화 방안

### 시트 4: 트렌드_분석
**목적**: 시간별 변화 추이 및 패턴 분석

**포함 내용**:
- **월별 트렌드**:
  - 처리량 변화
  - 평균 소요일수 변화
  - 효율성 변화
- **요일별 패턴**:
  - 요일별 처리량
  - 요일별 효율성
  - 주말 영향 분석
- **계절별 분석**:
  - 계절별 처리 패턴
  - 휴일 영향 분석
  - 특수 이벤트 영향
- **예측 분석**:
  - 다음 달 예상 처리량
  - 효율성 개선 예상치
  - 리스크 요소 분석

### 시트 5: 요약_및_권장사항
**목적**: 전체 분석 결과 요약 및 실행 가능한 권장사항

**포함 내용**:
- **실행 요약**:
  - 주요 발견사항
  - 핵심 지표 요약
  - 개선 영역 식별
- **성과 분석**:
  - 목표 대비 성과
  - 전년 동기 대비 성과
  - 벤치마크 비교
- **권장사항**:
  - 단기 개선 방안 (1-3개월)
  - 중기 개선 방안 (3-6개월)
  - 장기 개선 방안 (6-12개월)
- **리스크 관리**:
  - 주요 리스크 요소
  - 대응 방안
  - 모니터링 지표

## 🔄 처리 과정

### 1. 입력 데이터 검증
```python
# 파생 컬럼 존재 확인
required_derived_columns = [
    'Total_Days', 'DHL_Processing_Days', 'DSV_Processing_Days',
    'DHL_Efficiency', 'DSV_Efficiency', 'Overall_Efficiency',
    'Data_Completeness', 'Consistency_Score', 'Quality_Grade'
]
missing_columns = [col for col in required_derived_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"필수 파생 컬럼 누락: {missing_columns}")
```

### 2. 데이터 전처리
```python
# 날짜 컬럼 정규화
date_columns = ['ETD/ATD', 'ETA/ATA', 'DHL Warehouse', 'DSV Indoor']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# 파생 컬럼 데이터 타입 최적화
numeric_columns = ['Total_Days', 'DHL_Processing_Days', 'DSV_Processing_Days']
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')
```

### 3. KPI 계산
```python
# 기본 통계 계산
kpi_stats = {
    'total_cases': len(df),
    'avg_total_days': df['Total_Days'].mean(),
    'avg_dhl_days': df['DHL_Processing_Days'].mean(),
    'avg_dsv_days': df['DSV_Processing_Days'].mean(),
    'avg_efficiency': df['Overall_Efficiency'].mean(),
    'delay_rate': (df['Total_Delay_Days'] > 0).mean() * 100
}
```

### 4. 시각화 생성
```python
# matplotlib을 사용한 차트 생성
import matplotlib.pyplot as plt
import seaborn as sns

# 처리량 트렌드 차트
plt.figure(figsize=(12, 6))
df.groupby(df['ETD/ATD'].dt.to_period('M')).size().plot(kind='line')
plt.title('월별 처리량 트렌드')
plt.savefig('temp_charts/monthly_trend.png')
```

### 5. Excel 보고서 생성
```python
# openpyxl을 사용한 Excel 파일 생성
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart

wb = Workbook()

# 시트 1: 원본 데이터
ws1 = wb.active
ws1.title = "HITACHI_입고로직_종합리포트_Fixed"
# 데이터 및 색상 정보 추가

# 시트 2: KPI 대시보드
ws2 = wb.create_sheet("KPI_대시보드")
# KPI 데이터 및 차트 추가

# ... 기타 시트들
```

## 📈 실행 결과 확인

### 성공적인 실행 확인
```bash
# 1. 출력 파일 존재 확인
ls -la data/processed/reports/
# HVDC_종합리포트_YYYYMMDD_HHMMSS.xlsx 파일 확인

# 2. 파일 크기 확인 (일반적으로 5-10MB)
ls -lh data/processed/reports/HVDC_종합리포트_*.xlsx

# 3. 시트 수 확인 (5개 시트)
python -c "
import openpyxl
wb = openpyxl.load_workbook('data/processed/reports/HVDC_종합리포트_*.xlsx')
print(f'시트 수: {len(wb.sheetnames)}')
print(f'시트 목록: {wb.sheetnames}')
"
```

### 예상 출력 로그
```
[INFO] Stage 3: 종합 보고서 생성 시작
[INFO] 입력 파일 로드: HVDC WAREHOUSE_HITACHI(HE).xlsx
[INFO] 데이터 검증: 5,552행, 38개 컬럼 (13개 파생 컬럼 포함)
[INFO] 시트 1 생성: HITACHI_입고로직_종합리포트_Fixed
[INFO] 시트 2 생성: KPI_대시보드
[INFO] KPI 계산 완료: 15개 핵심 지표
[INFO] 시각화 생성: 8개 차트
[INFO] 시트 3 생성: 데이터_품질_검증
[INFO] 품질 분석 완료: 완성도 95.2%, 일관성 92.1%
[INFO] 시트 4 생성: 트렌드_분석
[INFO] 트렌드 분석 완료: 월별/요일별/계절별 패턴
[INFO] 시트 5 생성: 요약_및_권장사항
[INFO] 권장사항 생성: 12개 개선 방안
[INFO] Excel 파일 저장: HVDC_종합리포트_20250119_143022.xlsx
[SUCCESS] Stage 3 완료: 5개 시트, 8개 차트, 15개 KPI
```

## ⚠️ 문제 해결

### 1. 입력 파일 없음
**증상**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'HVDC WAREHOUSE_HITACHI(HE).xlsx'
```

**원인**: Stage 2가 실행되지 않았거나 출력 파일이 없음

**해결방법**:
```bash
# Stage 2 먼저 실행
python run_pipeline.py --stage 2

# 또는 전체 파이프라인 실행
python run_pipeline.py --all
```

### 2. 파생 컬럼 누락
**증상**:
```
ValueError: 필수 파생 컬럼 누락: ['Total_Days', 'DHL_Processing_Days']
```

**원인**: Stage 2에서 파생 컬럼이 제대로 생성되지 않음

**해결방법**:
1. **Stage 2 출력 확인**:
```bash
python -c "
import pandas as pd
df = pd.read_excel('data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx')
derived_cols = [col for col in df.columns if col.startswith(('Total_', 'DHL_', 'DSV_', 'Data_', 'Consistency_', 'Quality_'))]
print(f'파생 컬럼 수: {len(derived_cols)}')
print(f'파생 컬럼 목록: {derived_cols}')
"
```

2. **Stage 2 재실행**:
```bash
python run_pipeline.py --stage 2
```

### 3. 메모리 부족
**증상**:
```
MemoryError: Unable to allocate array
```

**원인**: 대용량 데이터 처리 시 메모리 부족

**해결방법**:
1. **메모리 사용량 확인**:
```bash
# Windows
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE

# Linux/macOS
ps aux | grep python
```

2. **메모리 최적화**:
```bash
# 다른 프로그램 종료
# 가상 메모리 증가
# 청크 단위 처리 활성화
```

### 4. 차트 생성 오류
**증상**:
```
AttributeError: 'NoneType' object has no attribute 'add_data'
```

**원인**: matplotlib 또는 openpyxl 차트 생성 오류

**해결방법**:
1. **의존성 확인**:
```bash
pip install matplotlib seaborn openpyxl
```

2. **차트 생성 비활성화** (임시):
```bash
python run_pipeline.py --stage 3 --no-charts
```

### 5. Excel 파일 저장 오류
**증상**:
```
PermissionError: [Errno 13] Permission denied
```

**원인**: Excel 파일이 다른 프로그램에서 열려있음

**해결방법**:
```bash
# Windows: Excel 프로세스 종료
taskkill /F /IM EXCEL.EXE

# 파일 잠금 확인
lsof "data/processed/reports/HVDC_종합리포트_*.xlsx"
```

## 🔧 고급 설정

### 설정 파일 수정
```yaml
# config/pipeline_config.yaml
stage3:
  report_settings:
    include_charts: true
    chart_quality: "high"  # high, medium, low
    max_chart_size: 1000   # 최대 데이터 포인트 수
  kpi_settings:
    target_efficiency: 85.0
    max_delay_days: 7
    min_completeness: 90.0
  sheet_settings:
    max_rows_per_sheet: 1000000
    auto_fit_columns: true
    freeze_panes: true
```

### 커스텀 KPI 추가
```python
# scripts/stage3_report/custom_kpi.py
def calculate_custom_kpi(df):
    """사용자 정의 KPI 계산"""
    custom_kpi = {
        'peak_processing_day': df.groupby(df['ETD/ATD'].dt.date).size().idxmax(),
        'avg_weekend_efficiency': df[df['ETD/ATD'].dt.weekday >= 5]['Overall_Efficiency'].mean(),
        'quality_trend': df.groupby(df['ETD/ATD'].dt.to_period('M'))['Quality_Grade'].apply(lambda x: (x == 'A').mean()).iloc[-1]
    }
    return custom_kpi
```

### 보고서 템플릿 커스터마이징
```python
# scripts/stage3_report/report_templates.py
def apply_custom_formatting(ws, sheet_type):
    """시트별 커스텀 포맷팅 적용"""
    if sheet_type == "KPI_대시보드":
        # KPI 대시보드 전용 포맷팅
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 15
    elif sheet_type == "데이터_품질_검증":
        # 품질 검증 시트 전용 포맷팅
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 12
```

## 📊 성능 최적화

### 메모리 사용량 최적화
```python
# 청크 단위 처리
chunk_size = 1000
for chunk in pd.read_excel(input_file, chunksize=chunk_size):
    # 청크별 처리
    process_chunk(chunk)
```

### 차트 생성 최적화
```python
# 차트 데이터 샘플링
if len(data) > 1000:
    data = data.sample(n=1000, random_state=42)
```

### Excel 파일 최적화
```python
# 불필요한 스타일 제거
from openpyxl.styles import PatternFill
# 기본 색상만 사용하여 파일 크기 최적화
```

## 📞 추가 지원

### 관련 문서
- [Stage별 상세 가이드](STAGE_BY_STAGE_GUIDE.md)
- [Stage 2 상세 가이드](STAGE2_USER_GUIDE.md)
- [Stage 4 상세 가이드](STAGE4_USER_GUIDE.md)

### 보고서 검증
```bash
# 보고서 내용 검증
python -c "
import openpyxl
wb = openpyxl.load_workbook('data/processed/reports/HVDC_종합리포트_*.xlsx')
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    print(f'{sheet_name}: {ws.max_row}행 x {ws.max_column}열')
"
```

---

**📅 최종 업데이트**: 2025-01-19
**🔖 버전**: v2.9.4
**👥 작성자**: HVDC 파이프라인 개발팀
