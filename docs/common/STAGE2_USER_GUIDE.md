# Stage 2: 파생 컬럼 처리 상세 사용 가이드

## 📋 개요

Stage 2는 Stage 1의 동기화된 데이터에 13개의 파생 컬럼을 추가하여 데이터 분석 기능을 강화하는 단계입니다.

### 주요 기능
- **13개 파생 컬럼 자동 계산**: 비즈니스 로직에 따른 자동 계산
- **색상 정보 보존**: Stage 1의 색상 표시 유지
- **데이터 검증**: 파생 컬럼 계산 결과 검증
- **성능 최적화**: 벡터화된 연산으로 빠른 처리

## 📁 입력 파일 요구사항

### 입력 파일
- **파일**: `data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx`
- **소스**: Stage 1 출력 파일
- **형식**: Excel (.xlsx)
- **인코딩**: UTF-8

### 필수 컬럼
Stage 1에서 동기화된 다음 컬럼들이 필요합니다:
- Case No.
- ETD/ATD, ETA/ATA
- 각종 날짜 컬럼 (DHL Warehouse, DSV Indoor 등)
- 기타 비즈니스 컬럼

## 🚀 실행 방법

### 방법 1: 전체 파이프라인 실행 (권장)
```bash
cd hvdc_pipeline
python run_pipeline.py --all
```

### 방법 2: Stage 2만 실행
```bash
cd hvdc_pipeline
python run_pipeline.py --stage 2
```

### 방법 3: 직접 스크립트 실행
```bash
cd hvdc_pipeline
python scripts/stage2_derived/derived_columns_processor.py \
  --input "data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx" \
  --output "data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx"
```

## 📊 13개 파생 컬럼 상세

### 1. 시간 관련 컬럼 (4개)

#### 1.1 총 소요일수 (Total_Days)
- **계산식**: `ETA/ATA - ETD/ATD`
- **단위**: 일
- **용도**: 전체 운송 소요 시간 분석

#### 1.2 DHL 처리일수 (DHL_Processing_Days)
- **계산식**: `DHL Warehouse - ETD/ATD`
- **단위**: 일
- **용도**: DHL 창고 처리 시간 분석

#### 1.3 DSV 처리일수 (DSV_Processing_Days)
- **계산식**: `DSV Indoor - DHL Warehouse`
- **단위**: 일
- **용도**: DSV 창고 처리 시간 분석

#### 1.4 최종 처리일수 (Final_Processing_Days)
- **계산식**: `ETA/ATA - DSV Indoor`
- **단위**: 일
- **용도**: 최종 배송 단계 시간 분석

### 2. 지연 관련 컬럼 (3개)

#### 2.1 DHL 지연일수 (DHL_Delay_Days)
- **계산식**: `DHL_Processing_Days - 예상일수`
- **단위**: 일
- **용도**: DHL 지연 분석

#### 2.2 DSV 지연일수 (DSV_Delay_Days)
- **계산식**: `DSV_Processing_Days - 예상일수`
- **단위**: 일
- **용도**: DSV 지연 분석

#### 2.3 총 지연일수 (Total_Delay_Days)
- **계산식**: `DHL_Delay_Days + DSV_Delay_Days`
- **단위**: 일
- **용도**: 전체 지연 시간 분석

### 3. 효율성 관련 컬럼 (3개)

#### 3.1 DHL 효율성 (DHL_Efficiency)
- **계산식**: `예상일수 / DHL_Processing_Days * 100`
- **단위**: %
- **용도**: DHL 처리 효율성 측정

#### 3.2 DSV 효율성 (DSV_Efficiency)
- **계산식**: `예상일수 / DSV_Processing_Days * 100`
- **단위**: %
- **용도**: DSV 처리 효율성 측정

#### 3.3 전체 효율성 (Overall_Efficiency)
- **계산식**: `예상일수 / Total_Days * 100`
- **단위**: %
- **용도**: 전체 프로세스 효율성 측정

### 4. 품질 관련 컬럼 (3개)

#### 4.1 데이터 완성도 (Data_Completeness)
- **계산식**: `필수 컬럼 채워진 비율 * 100`
- **단위**: %
- **용도**: 데이터 품질 측정

#### 4.2 일관성 점수 (Consistency_Score)
- **계산식**: `날짜 순서 일관성 점수`
- **단위**: 점 (0-100)
- **용도**: 데이터 일관성 측정

#### 4.3 품질 등급 (Quality_Grade)
- **계산식**: `A/B/C/D 등급 (완성도 + 일관성)`
- **단위**: 등급
- **용도**: 데이터 품질 분류

## 🔄 처리 과정

### 1. 입력 파일 검증
```python
# 필수 컬럼 존재 확인
required_columns = ['Case No.', 'ETD/ATD', 'ETA/ATA', 'DHL Warehouse', 'DSV Indoor']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"필수 컬럼 누락: {missing_columns}")
```

### 2. 날짜 데이터 정규화
```python
# 날짜 컬럼을 datetime으로 변환
date_columns = ['ETD/ATD', 'ETA/ATA', 'DHL Warehouse', 'DSV Indoor']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')
```

### 3. 파생 컬럼 계산
```python
# 벡터화된 연산으로 모든 파생 컬럼 계산
df['Total_Days'] = (df['ETA/ATA'] - df['ETD/ATD']).dt.days
df['DHL_Processing_Days'] = (df['DHL Warehouse'] - df['ETD/ATD']).dt.days
# ... 기타 11개 컬럼
```

### 4. 색상 정보 보존
```python
# Stage 1의 색상 정보를 그대로 유지
# openpyxl을 사용하여 셀 색상 정보 보존
```

### 5. 데이터 검증
```python
# 계산 결과 검증
validation_checks = [
    df['Total_Days'] >= 0,
    df['DHL_Processing_Days'] >= 0,
    df['DSV_Processing_Days'] >= 0,
    # ... 기타 검증 규칙
]
```

## 📈 실행 결과 확인

### 성공적인 실행 확인
```bash
# 1. 출력 파일 존재 확인
ls -la data/processed/derived/
# HVDC WAREHOUSE_HITACHI(HE).xlsx 파일 확인

# 2. 파일 크기 확인
ls -lh data/processed/derived/HVDC\ WAREHOUSE_HITACHI\(HE\).xlsx

# 3. 컬럼 수 확인 (13개 파생 컬럼 추가)
python -c "
import pandas as pd
df = pd.read_excel('data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx')
print(f'총 컬럼 수: {len(df.columns)}')
print(f'파생 컬럼: {[col for col in df.columns if col.startswith(("Total_", "DHL_", "DSV_", "Data_", "Consistency_", "Quality_"))]}')
"
```

### 예상 출력 로그
```
[INFO] Stage 2: 파생 컬럼 처리 시작
[INFO] 입력 파일 로드: HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx
[INFO] 데이터 검증: 5,552행, 25개 컬럼
[INFO] 날짜 데이터 정규화 완료
[INFO] 파생 컬럼 계산 시작...
[INFO] 시간 관련 컬럼 계산: 4개
[INFO] 지연 관련 컬럼 계산: 3개
[INFO] 효율성 관련 컬럼 계산: 3개
[INFO] 품질 관련 컬럼 계산: 3개
[INFO] 색상 정보 보존 완료
[INFO] 데이터 검증 완료
[INFO] 출력 파일 저장: HVDC WAREHOUSE_HITACHI(HE).xlsx
[SUCCESS] Stage 2 완료: 13개 파생 컬럼 추가
```

## ⚠️ 문제 해결

### 1. 입력 파일 없음
**증상**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx'
```

**원인**: Stage 1이 실행되지 않았거나 출력 파일이 없음

**해결방법**:
```bash
# Stage 1 먼저 실행
python run_pipeline.py --stage 1

# 또는 전체 파이프라인 실행
python run_pipeline.py --all
```

### 2. 필수 컬럼 누락
**증상**:
```
ValueError: 필수 컬럼 누락: ['ETD/ATD', 'ETA/ATA']
```

**원인**: Stage 1 출력 파일에 필수 컬럼이 없음

**해결방법**:
1. **Stage 1 출력 확인**:
```bash
python -c "
import pandas as pd
df = pd.read_excel('data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx')
print('컬럼 목록:', df.columns.tolist())
"
```

2. **Stage 1 재실행**:
```bash
python run_pipeline.py --stage 1
```

### 3. 날짜 파싱 오류
**증상**:
```
pandas.errors.ParserError: Unknown datetime string format
```

**원인**: 날짜 형식이 예상과 다름

**해결방법**:
1. **날짜 형식 확인**:
```bash
python -c "
import pandas as pd
df = pd.read_excel('data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx')
print('ETD/ATD 샘플:', df['ETD/ATD'].head())
print('ETD/ATD 타입:', df['ETD/ATD'].dtype)
"
```

2. **Stage 1에서 날짜 정규화 확인**:
   - Stage 1의 날짜 정규화 기능이 제대로 작동했는지 확인

### 4. 계산 결과 오류
**증상**:
```
[WARNING] 음수 값 발견: Total_Days 컬럼에 -1개
[ERROR] 데이터 검증 실패: 일관성 점수 계산 오류
```

**원인**:
- 날짜 순서가 잘못됨 (ETA < ETD)
- 잘못된 날짜 형식
- 데이터 품질 문제

**해결방법**:
1. **데이터 품질 확인**:
```bash
python -c "
import pandas as pd
df = pd.read_excel('data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx')
print('ETD/ATD 최소값:', df['ETD/ATD'].min())
print('ETA/ATA 최대값:', df['ETA/ATA'].max())
print('ETD > ETA인 행 수:', (df['ETD/ATD'] > df['ETA/ATA']).sum())
"
```

2. **데이터 수정 후 재실행**:
   - 원본 데이터에서 잘못된 날짜 수정
   - Stage 1부터 재실행

### 5. 색상 정보 손실
**증상**: Stage 1의 색상이 Stage 2 출력에서 사라짐

**원인**: 색상 보존 로직 오류

**해결방법**:
1. **색상 보존 확인**:
```bash
python -c "
import openpyxl
wb = openpyxl.load_workbook('data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx')
ws = wb.active
colored_cells = 0
for row in ws.iter_rows():
    for cell in row:
        if cell.fill and cell.fill.fgColor and cell.fill.fgColor.rgb != '00000000':
            colored_cells += 1
print(f'색상이 적용된 셀 수: {colored_cells}')
"
```

2. **Stage 2 재실행**:
```bash
python run_pipeline.py --stage 2
```

## 🔧 고급 설정

### 설정 파일 수정
```yaml
# config/stage2_derived_config.yaml
derived_columns:
  time_related:
    - "Total_Days"
    - "DHL_Processing_Days"
    - "DSV_Processing_Days"
    - "Final_Processing_Days"
  delay_related:
    - "DHL_Delay_Days"
    - "DSV_Delay_Days"
    - "Total_Delay_Days"
  efficiency_related:
    - "DHL_Efficiency"
    - "DSV_Efficiency"
    - "Overall_Efficiency"
  quality_related:
    - "Data_Completeness"
    - "Consistency_Score"
    - "Quality_Grade"

validation:
  check_negative_values: true
  check_date_consistency: true
  min_completeness_rate: 0.8
```

### 커스텀 파생 컬럼 추가
```python
# scripts/stage2_derived/derived_columns_processor.py
def add_custom_derived_columns(df):
    """사용자 정의 파생 컬럼 추가"""
    # 예: 주말 제외 처리일수
    df['Weekday_Processing_Days'] = df['Total_Days'] - df['Weekend_Days']

    # 예: 월별 처리량
    df['Monthly_Volume'] = df.groupby(df['ETD/ATD'].dt.to_period('M'))['Case No.'].transform('count')

    return df
```

## 📊 성능 최적화

### 벡터화된 연산 사용
```python
# 비효율적 (반복문 사용)
for idx, row in df.iterrows():
    df.at[idx, 'Total_Days'] = (row['ETA/ATA'] - row['ETD/ATD']).days

# 효율적 (벡터화된 연산)
df['Total_Days'] = (df['ETA/ATA'] - df['ETD/ATD']).dt.days
```

### 메모리 사용량 최적화
```python
# 불필요한 컬럼 제거
df = df.drop(columns=['temp_column1', 'temp_column2'])

# 데이터 타입 최적화
df['Total_Days'] = df['Total_Days'].astype('int16')
df['DHL_Efficiency'] = df['DHL_Efficiency'].astype('float32')
```

## 📞 추가 지원

### 관련 문서
- [Stage별 상세 가이드](STAGE_BY_STAGE_GUIDE.md)
- [Stage 1 상세 가이드](STAGE1_USER_GUIDE.md)
- [Stage 3 상세 가이드](STAGE3_USER_GUIDE.md)

### 파생 컬럼 검증
```bash
# 파생 컬럼 계산 결과 검증
python -c "
import pandas as pd
df = pd.read_excel('data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).xlsx')
print('파생 컬럼 통계:')
print(df[['Total_Days', 'DHL_Processing_Days', 'DSV_Processing_Days']].describe())
"
```

---

**📅 최종 업데이트**: 2025-01-19
**🔖 버전**: v2.9.4
**👥 작성자**: HVDC 파이프라인 개발팀
