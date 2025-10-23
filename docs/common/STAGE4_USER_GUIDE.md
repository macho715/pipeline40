# Stage 4: 이상치 탐지 상세 사용 가이드

## 📋 개요

Stage 4는 Stage 3의 종합 보고서 데이터에서 이상치를 자동으로 탐지하고, 색상으로 구분하여 표시하는 고급 분석 단계입니다.

### 주요 기능 (v3.0.1)
- **5가지 이상치 유형 탐지**: 다양한 패턴의 이상치 자동 식별
- **색상 구분 표시**: 이상치 유형별로 다른 색상 적용
- **자동 파일 탐색**: 최신 보고서를 자동으로 찾아서 분석 ✅
- **색상 적용 자동화**: `--stage4-visualize` 플래그로 간편 실행 ✅
- **상세 분석 보고서**: 이상치 원인 및 영향도 분석
- **데이터 품질 개선 제안**: 이상치 해결 방안 제시

## 📁 입력 파일 요구사항

### 입력 파일 (자동 탐색)
- **파일 패턴**: `HVDC_입고로직_종합리포트_*_v3.0-corrected.xlsx`
- **자동 선택**: 가장 최신 파일 자동 탐색 ✅
- **소스**: Stage 3 출력 파일
- **형식**: Excel (.xlsx)
- **필수 시트**: 첫 번째 시트 (통합_원본데이터_Fixed)

### 필수 컬럼
Stage 3 보고서의 첫 번째 시트에 다음 컬럼들이 필요합니다:
- Case No.
- ETD/ATD, ETA/ATA
- DHL Warehouse, DSV Indoor
- 파생 컬럼 (Total_Days, DHL_Processing_Days, DSV_Processing_Days 등)

## 🚀 실행 방법

### 방법 1: 전체 파이프라인 실행 (권장) - 색상 포함
```bash
cd hvdc_pipeline
.\run_full_pipeline.bat
# 또는
python run_pipeline.py --all
```

### 방법 2: Stage 4만 실행 - 색상 적용 포함 ✅
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 4 --stage4-visualize
```
**특징:**
- 자동으로 최신 보고서 파일 탐색
- 이상치 탐지 후 색상 자동 적용
- 원본 파일 자동 백업

### 방법 3: 색상 없이 탐지만 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 4
```
**특징:**
- 이상치 탐지만 수행 (JSON/Excel 보고서 생성)
- 색상 적용 제외

### 방법 4: 직접 스크립트 실행
```bash
cd hvdc_pipeline
python scripts/stage4_anomaly/anomaly_detector.py \
  --input "data/processed/reports/HVDC_입고로직_종합리포트_*.xlsx" \
  --excel-out "data/anomaly/HVDC_anomaly_report.xlsx" \
  --visualize  # 색상 적용 옵션
```

## 🔍 5가지 이상치 유형 상세

### 1. 시간 이상치 (Time Anomalies) - 빨간색
**탐지 대상**:
- 총 소요일수가 비정상적으로 긴 경우
- DHL 또는 DSV 처리일수가 극단적으로 긴 경우
- 날짜 순서가 논리적으로 맞지 않는 경우

**탐지 규칙**:
```python
# 총 소요일수 이상치 (99.5% 분위수 초과)
time_anomalies = df['Total_Days'] > df['Total_Days'].quantile(0.995)

# DHL 처리일수 이상치 (99% 분위수 초과)
dhl_anomalies = df['DHL_Processing_Days'] > df['DHL_Processing_Days'].quantile(0.99)

# 날짜 순서 이상치 (ETA < ETD)
date_order_anomalies = df['ETA/ATA'] < df['ETD/ATD']
```

**비즈니스 영향**:
- 고객 만족도 저하
- 비용 증가
- 프로세스 비효율성

### 2. 효율성 이상치 (Efficiency Anomalies) - 주황색
**탐지 대상**:
- 전체 효율성이 비정상적으로 낮은 경우
- DHL 또는 DSV 효율성이 극단적으로 낮은 경우
- 효율성 지표 간 불일치가 큰 경우

**탐지 규칙**:
```python
# 전체 효율성 이상치 (5% 분위수 미만)
efficiency_anomalies = df['Overall_Efficiency'] < df['Overall_Efficiency'].quantile(0.05)

# DHL 효율성 이상치 (1% 분위수 미만)
dhl_efficiency_anomalies = df['DHL_Efficiency'] < df['DHL_Efficiency'].quantile(0.01)

# 효율성 불일치 이상치 (표준편차 3배 초과)
efficiency_std = df['Overall_Efficiency'].std()
efficiency_mean = df['Overall_Efficiency'].mean()
efficiency_inconsistency = abs(df['Overall_Efficiency'] - efficiency_mean) > 3 * efficiency_std
```

**비즈니스 영향**:
- 운영 비효율성
- 리소스 낭비
- 서비스 품질 저하

### 3. 지연 이상치 (Delay Anomalies) - 노란색
**탐지 대상**:
- 총 지연일수가 비정상적으로 긴 경우
- DHL 또는 DSV 지연이 극단적인 경우
- 지연 패턴이 비정상적인 경우

**탐지 규칙**:
```python
# 총 지연일수 이상치 (95% 분위수 초과)
delay_anomalies = df['Total_Delay_Days'] > df['Total_Delay_Days'].quantile(0.95)

# DHL 지연 이상치 (90% 분위수 초과)
dhl_delay_anomalies = df['DHL_Delay_Days'] > df['DHL_Delay_Days'].quantile(0.90)

# 지연 패턴 이상치 (연속 지연)
consecutive_delays = df['Total_Delay_Days'].rolling(window=5).sum() > 20
```

**비즈니스 영향**:
- 고객 불만
- 비용 증가
- 신뢰도 하락

### 4. 데이터 품질 이상치 (Data Quality Anomalies) - 보라색
**탐지 대상**:
- 데이터 완성도가 극단적으로 낮은 경우
- 일관성 점수가 비정상적으로 낮은 경우
- 품질 등급이 D등급인 경우

**탐지 규칙**:
```python
# 데이터 완성도 이상치 (50% 미만)
completeness_anomalies = df['Data_Completeness'] < 50

# 일관성 점수 이상치 (30% 미만)
consistency_anomalies = df['Consistency_Score'] < 30

# 품질 등급 이상치 (D등급)
quality_anomalies = df['Quality_Grade'] == 'D'
```

**비즈니스 영향**:
- 의사결정 오류
- 분석 신뢰도 하락
- 프로세스 개선 어려움

### 5. 패턴 이상치 (Pattern Anomalies) - 파란색
**탐지 대상**:
- 특정 패턴에서 벗어나는 경우
- 계절성이나 트렌드와 맞지 않는 경우
- 그룹별 평균에서 크게 벗어나는 경우

**탐지 규칙**:
```python
# 계절성 이상치 (계절별 평균에서 2표준편차 초과)
seasonal_anomalies = detect_seasonal_anomalies(df, 'Total_Days')

# 그룹별 이상치 (창고별 평균에서 3표준편차 초과)
group_anomalies = detect_group_anomalies(df, 'Warehouse', 'Total_Days')

# 트렌드 이상치 (이동평균에서 크게 벗어남)
trend_anomalies = detect_trend_anomalies(df, 'ETD/ATD', 'Total_Days')
```

**비즈니스 영향**:
- 예측 정확도 하락
- 계획 수립 어려움
- 리스크 관리 실패

## 🎨 색상 표시 시스템

### 색상 코드
```python
ANOMALY_COLORS = {
    'time_anomaly': 'FF0000',      # 빨간색 - 시간 이상치
    'efficiency_anomaly': 'FFA500', # 주황색 - 효율성 이상치
    'delay_anomaly': 'FFFF00',     # 노란색 - 지연 이상치
    'quality_anomaly': '800080',   # 보라색 - 데이터 품질 이상치
    'pattern_anomaly': '0000FF'    # 파란색 - 패턴 이상치
}
```

### 색상 적용 규칙
1. **우선순위**: 시간 > 효율성 > 지연 > 품질 > 패턴
2. **중복 처리**: 여러 유형에 해당하는 경우 우선순위 높은 색상 적용
3. **셀 단위**: 이상치가 있는 셀만 색상 적용
4. **빈 셀 제외**: 데이터가 없는 빈 셀에는 색상 적용 안함

## 📊 출력 파일

### 1. 이상치 보고서 (Excel)
**파일 위치**: `data/anomaly/HVDC_anomaly_report.xlsx`

**시트 구성**:
- **시트 1**: 이상치가 색상으로 표시된 원본 데이터
- **시트 2**: 이상치 유형별 요약 통계
- **시트 3**: 이상치 상세 분석
- **시트 4**: 개선 권장사항

### 2. 이상치 데이터 (JSON)
**파일 위치**: `data/anomaly/HVDC_anomaly_report.json`

**포함 내용**:
```json
{
  "anomaly_summary": {
    "total_anomalies": 156,
    "time_anomalies": 23,
    "efficiency_anomalies": 45,
    "delay_anomalies": 34,
    "quality_anomalies": 28,
    "pattern_anomalies": 26
  },
  "anomaly_details": [
    {
      "case_no": "208221",
      "anomaly_type": "time_anomaly",
      "severity": "high",
      "description": "총 소요일수 45일 (정상 범위 초과)",
      "recommendation": "DHL 처리 과정 검토 필요"
    }
  ]
}
```

## 🔄 처리 과정

### 1. 입력 데이터 검증
```python
# Stage 3 출력 파일 존재 확인
input_files = glob.glob("data/processed/reports/HVDC_종합리포트_*.xlsx")
if not input_files:
    raise FileNotFoundError("Stage 3 출력 파일을 찾을 수 없습니다")

# 최신 파일 선택
latest_file = max(input_files, key=os.path.getctime)
```

### 2. 이상치 탐지 알고리즘 실행
```python
# 각 이상치 유형별 탐지
anomaly_detectors = {
    'time': TimeAnomalyDetector(),
    'efficiency': EfficiencyAnomalyDetector(),
    'delay': DelayAnomalyDetector(),
    'quality': QualityAnomalyDetector(),
    'pattern': PatternAnomalyDetector()
}

anomaly_results = {}
for anomaly_type, detector in anomaly_detectors.items():
    anomaly_results[anomaly_type] = detector.detect(df)
```

### 3. 색상 적용
```python
# openpyxl을 사용한 색상 적용
from openpyxl.styles import PatternFill

for anomaly_type, anomalies in anomaly_results.items():
    color = ANOMALY_COLORS[anomaly_type]
    fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

    for idx in anomalies:
        # 해당 행의 데이터가 있는 셀만 색칠
        for cell in ws[idx + 2]:  # +2 for header row
            if cell.value is not None and str(cell.value).strip() != "":
                cell.fill = fill
```

### 4. 보고서 생성
```python
# 이상치 요약 통계 계산
summary_stats = calculate_anomaly_summary(anomaly_results)

# 상세 분석 수행
detailed_analysis = perform_detailed_analysis(df, anomaly_results)

# 개선 권장사항 생성
recommendations = generate_recommendations(anomaly_results, detailed_analysis)
```

## 📈 실행 결과 확인

### 성공적인 실행 확인
```bash
# 1. 출력 파일 존재 확인
ls -la data/anomaly/
# HVDC_anomaly_report.xlsx, HVDC_anomaly_report.json 파일 확인

# 2. 이상치 수 확인
python -c "
import json
with open('data/anomaly/HVDC_anomaly_report.json', 'r') as f:
    data = json.load(f)
print(f'총 이상치 수: {data[\"anomaly_summary\"][\"total_anomalies\"]}')
for anomaly_type, count in data['anomaly_summary'].items():
    if anomaly_type != 'total_anomalies':
        print(f'{anomaly_type}: {count}개')
"
```

### 예상 출력 로그
```
[INFO] Stage 4: 이상치 탐지 시작
[INFO] 입력 파일 로드: HVDC_종합리포트_20250119_143022.xlsx
[INFO] 데이터 검증: 5,552행, 38개 컬럼
[INFO] 이상치 탐지 알고리즘 실행...
[INFO] 시간 이상치 탐지: 23개 발견
[INFO] 효율성 이상치 탐지: 45개 발견
[INFO] 지연 이상치 탐지: 34개 발견
[INFO] 데이터 품질 이상치 탐지: 28개 발견
[INFO] 패턴 이상치 탐지: 26개 발견
[INFO] 총 이상치: 156개 (2.8%)
[INFO] 색상 적용 중...
[INFO] Excel 보고서 생성: HVDC_anomaly_report.xlsx
[INFO] JSON 데이터 생성: HVDC_anomaly_report.json
[SUCCESS] Stage 4 완료: 156개 이상치 탐지 및 색상 표시
```

## ⚠️ 문제 해결

### 1. 입력 파일 없음
**증상**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'HVDC_종합리포트_*.xlsx'
```

**원인**: Stage 3이 실행되지 않았거나 출력 파일이 없음

**해결방법**:
```bash
# Stage 3 먼저 실행
python run_pipeline.py --stage 3

# 또는 전체 파이프라인 실행
python run_pipeline.py --all
```

### 2. 이상치 탐지 실패
**증상**:
```
ValueError: 데이터에 필수 컬럼이 없습니다: ['Total_Days', 'DHL_Processing_Days']
```

**원인**: Stage 3 출력 파일에 파생 컬럼이 없음

**해결방법**:
1. **Stage 3 출력 확인**:
```bash
python -c "
import pandas as pd
df = pd.read_excel('data/processed/reports/HVDC_종합리포트_*.xlsx', sheet_name=0)
print('컬럼 목록:', df.columns.tolist())
"
```

2. **전체 파이프라인 재실행**:
```bash
python run_pipeline.py --all
```

### 3. 색상 적용 실패
**증상**: 이상치는 탐지되었지만 색상이 적용되지 않음

**원인**: openpyxl 색상 적용 로직 오류

**해결방법**:
1. **의존성 확인**:
```bash
pip install openpyxl
```

2. **색상 적용 재시도**:
```bash
python scripts/stage4_anomaly/apply_anomaly_colors.py \
  --input "data/processed/reports/HVDC_종합리포트_*.xlsx" \
  --anomaly-data "data/anomaly/HVDC_anomaly_report.json"
```

### 4. 메모리 부족
**증상**:
```
MemoryError: Unable to allocate array
```

**원인**: 대용량 데이터 처리 시 메모리 부족

**해결방법**:
1. **청크 단위 처리**:
```bash
python run_pipeline.py --stage 4 --chunk-size 1000
```

2. **메모리 정리**:
```bash
# 다른 프로그램 종료
# 가상 메모리 증가
```

### 5. 이상치 탐지 정확도 문제
**증상**: 너무 많은 또는 너무 적은 이상치 탐지

**원인**: 이상치 탐지 임계값 설정 문제

**해결방법**:
1. **임계값 조정**:
```yaml
# config/pipeline_config.yaml
stage4:
  anomaly_thresholds:
    time_anomaly_percentile: 99.5
    efficiency_anomaly_percentile: 5.0
    delay_anomaly_percentile: 95.0
    quality_anomaly_percentile: 50.0
    pattern_anomaly_std_multiplier: 2.0
```

2. **수동 임계값 설정**:
```bash
python run_pipeline.py --stage 4 --custom-thresholds
```

## 🔧 고급 설정

### 이상치 탐지 알고리즘 커스터마이징
```python
# scripts/stage4_anomaly/custom_detectors.py
class CustomAnomalyDetector:
    def __init__(self, threshold_multiplier=2.0):
        self.threshold_multiplier = threshold_multiplier

    def detect(self, df):
        # 사용자 정의 이상치 탐지 로직
        mean = df['Total_Days'].mean()
        std = df['Total_Days'].std()
        threshold = mean + self.threshold_multiplier * std
        return df['Total_Days'] > threshold
```

### 색상 스키마 커스터마이징
```python
# scripts/stage4_anomaly/color_schemes.py
CUSTOM_COLOR_SCHEMES = {
    'high_contrast': {
        'time_anomaly': 'FF0000',      # 빨간색
        'efficiency_anomaly': 'FF8C00', # 진한 주황색
        'delay_anomaly': 'FFD700',     # 금색
        'quality_anomaly': '8B008B',   # 진한 보라색
        'pattern_anomaly': '0000FF'    # 파란색
    },
    'pastel': {
        'time_anomaly': 'FFB6C1',      # 연한 빨간색
        'efficiency_anomaly': 'FFE4B5', # 연한 주황색
        'delay_anomaly': 'FFFFE0',     # 연한 노란색
        'quality_anomaly': 'DDA0DD',   # 연한 보라색
        'pattern_anomaly': 'B0E0E6'    # 연한 파란색
    }
}
```

### 보고서 템플릿 커스터마이징
```python
# scripts/stage4_anomaly/report_templates.py
def create_custom_anomaly_report(anomaly_data, template_type="executive"):
    """사용자 정의 이상치 보고서 생성"""
    if template_type == "executive":
        # 경영진용 요약 보고서
        return create_executive_summary(anomaly_data)
    elif template_type == "technical":
        # 기술진용 상세 보고서
        return create_technical_report(anomaly_data)
    elif template_type == "operational":
        # 운영진용 실행 보고서
        return create_operational_report(anomaly_data)
```

## 📊 성능 최적화

### 이상치 탐지 알고리즘 최적화
```python
# 벡터화된 연산 사용
def detect_anomalies_vectorized(df):
    """벡터화된 이상치 탐지"""
    # numpy 연산으로 빠른 처리
    z_scores = np.abs((df['Total_Days'] - df['Total_Days'].mean()) / df['Total_Days'].std())
    return z_scores > 3
```

### 메모리 사용량 최적화
```python
# 청크 단위 처리
def process_large_dataset(df, chunk_size=1000):
    """대용량 데이터셋 청크 단위 처리"""
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        anomalies = detect_anomalies(chunk)
        yield anomalies
```

### 병렬 처리
```python
# multiprocessing을 사용한 병렬 처리
from multiprocessing import Pool

def parallel_anomaly_detection(df_chunks):
    """병렬 이상치 탐지"""
    with Pool() as pool:
        results = pool.map(detect_anomalies, df_chunks)
    return results
```

## 📞 추가 지원

### 관련 문서
- [Stage별 상세 가이드](STAGE_BY_STAGE_GUIDE.md)
- [Stage 3 상세 가이드](STAGE3_USER_GUIDE.md)
- [색상 문제 해결](COLOR_FIX_SUMMARY.md)

### 이상치 분석 도구
```bash
# 이상치 상세 분석
python scripts/stage4_anomaly/analyze_anomalies.py \
  --input "data/anomaly/HVDC_anomaly_report.json" \
  --output "anomaly_analysis.html"

# 이상치 시각화
python scripts/stage4_anomaly/visualize_anomalies.py \
  --input "data/anomaly/HVDC_anomaly_report.json" \
  --output "anomaly_plots.png"
```

---

**📅 최종 업데이트**: 2025-01-19
**🔖 버전**: v2.9.4
**👥 작성자**: HVDC 파이프라인 개발팀
