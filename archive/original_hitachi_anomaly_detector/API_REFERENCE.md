# HVDC Anomaly Detector v2 API Reference

## 개요

HVDC 이상치 탐지 시스템 v2의 API 문서입니다. 모든 클래스, 메서드, 설정 옵션에 대한 상세한 설명을 제공합니다.

## 핵심 클래스

### DetectorConfig

설정 관리 클래스입니다.

```python
@dataclass
class DetectorConfig:
    # 헤더 정규화
    column_map: Dict[str, str] = None
    warehouse_columns: List[str] = None
    site_columns: List[str] = None

    # 통계 탐지 파라미터
    iqr_k: float = 1.5
    mad_k: float = 3.5

    # ML 탐지 파라미터
    use_pyod_first: bool = True
    contamination: float = 0.02
    random_state: int = 42

    # 배치/워커
    batch_size: int = 1000
    max_workers: int = 8

    # 알림
    alert_window_sec: int = 30
    min_risk_to_alert: float = 0.8
```

#### 주요 속성

| 속성 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `column_map` | Dict[str, str] | 자동 생성 | 헤더 정규화 매핑 |
| `warehouse_columns` | List[str] | 자동 생성 | 창고 컬럼 목록 |
| `site_columns` | List[str] | 자동 생성 | 현장 컬럼 목록 |
| `iqr_k` | float | 1.5 | IQR 이상치 탐지 계수 |
| `contamination` | float | 0.02 | ML 이상치 비율 |
| `batch_size` | int | 1000 | 배치 처리 크기 |
| `max_workers` | int | 8 | 최대 워커 수 |

### HybridAnomalyDetector

메인 이상치 탐지 클래스입니다.

```python
class HybridAnomalyDetector:
    def __init__(self, cfg: DetectorConfig):
        """탐지기 초기화"""

    def run(self, df_raw: pd.DataFrame,
            export_excel: Optional[str] = None,
            export_json: Optional[str] = None) -> Dict:
        """전체 파이프라인 실행"""
```

#### 메서드

##### `__init__(cfg: DetectorConfig)`
탐지기를 초기화합니다.

**매개변수:**
- `cfg`: 설정 객체

**초기화되는 컴포넌트:**
- `HeaderNormalizer`: 헤더 정규화
- `DataQualityValidator`: 데이터 품질 검증
- `RuleDetector`: 규칙 기반 탐지
- `StatDetector`: 통계 기반 탐지
- `MLDetector`: 머신러닝 탐지
- `AlertManager`: 알림 관리

##### `run(df_raw, export_excel=None, export_json=None)`
전체 이상치 탐지 파이프라인을 실행합니다.

**매개변수:**
- `df_raw` (pd.DataFrame): 입력 데이터
- `export_excel` (str, optional): Excel 출력 경로
- `export_json` (str, optional): JSON 출력 경로

**반환값:**
```python
{
    "summary": {
        "total": int,           # 총 이상치 수
        "by_type": Dict[str, int],    # 유형별 분포
        "by_severity": Dict[str, int] # 심각도별 분포
    },
    "anomalies": List[AnomalyRecord], # 이상치 레코드 목록
    "features": pd.DataFrame          # 피처 데이터
}
```

## 탐지기 클래스

### RuleDetector

규칙 기반 이상치 탐지기입니다.

```python
class RuleDetector:
    def __init__(self, cfg: DetectorConfig):
        """규칙 탐지기 초기화"""

    def time_reversal(self, row: pd.Series) -> Optional[AnomalyRecord]:
        """시간 역전 탐지"""

    def location_skip(self, row: pd.Series) -> Optional[AnomalyRecord]:
        """위치 스킵 탐지"""
```

#### 메서드

##### `time_reversal(row: pd.Series) -> Optional[AnomalyRecord]`
시간 역전을 탐지합니다.

**매개변수:**
- `row`: 데이터 행 (pandas Series)

**반환값:**
- `AnomalyRecord` 또는 `None`

**탐지 로직:**
1. 창고/현장 컬럼에서 날짜 추출
2. 시간순 정렬
3. 원래 순서와 비교
4. 불일치 시 이상치 반환

### StatDetector

통계 기반 이상치 탐지기입니다.

```python
class StatDetector:
    def __init__(self, iqr_k: float = 1.5, mad_k: float = 3.5):
        """통계 탐지기 초기화"""

    def iqr_outliers(self, dwell_list: List[Tuple[str, str, int]]) -> List[AnomalyRecord]:
        """IQR 기반 이상치 탐지"""
```

#### 메서드

##### `iqr_outliers(dwell_list) -> List[AnomalyRecord]`
IQR 방법으로 체류 시간 이상치를 탐지합니다.

**매개변수:**
- `dwell_list`: [(case_id, location, dwell_days), ...]

**반환값:**
- `AnomalyRecord` 목록

**탐지 로직:**
1. Q1, Q3 계산
2. IQR = Q3 - Q1
3. 하한 = Q1 - k×IQR
4. 상한 = Q3 + k×IQR
5. 범위 벗어난 값들을 이상치로 분류

### MLDetector

머신러닝 기반 이상치 탐지기입니다.

```python
class MLDetector:
    def __init__(self, contamination: float = 0.02,
                 random_state: int = 42,
                 use_pyod_first: bool = True):
        """ML 탐지기 초기화"""

    def fit_predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """ML 모델 학습 및 예측"""
```

#### 메서드

##### `fit_predict(X) -> (y_pred, risk_scores)`
머신러닝 모델로 이상치를 탐지합니다.

**매개변수:**
- `X`: 피처 데이터 (DataFrame)

**반환값:**
- `y_pred`: 예측 결과 (0=정상, 1=이상치)
- `risk_scores`: 위험도 점수 (0-1)

**지원 모델:**
- **PyOD IForest** (우선)
- **Sklearn IsolationForest** (폴백)

## 유틸리티 클래스

### HeaderNormalizer

헤더 정규화 클래스입니다.

```python
class HeaderNormalizer:
    def __init__(self, column_map: Dict[str, str]):
        """정규화기 초기화"""

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """헤더 정규화"""
```

### DataQualityValidator

데이터 품질 검증 클래스입니다.

```python
class DataQualityValidator:
    def validate(self, df: pd.DataFrame) -> List[str]:
        """데이터 품질 검증"""
```

**검증 항목:**
- CASE_NO 중복
- HVDC_CODE 형식
- 수치형 데이터 유효성
- 날짜 변환 가능성

### ECDFCalibrator

점수 캘리브레이션 클래스입니다.

```python
class ECDFCalibrator:
    def fit(self, raw_scores: np.ndarray) -> "ECDFCalibrator":
        """캘리브레이션 학습"""

    def transform(self, raw_scores: np.ndarray) -> np.ndarray:
        """점수 변환 (0-1 위험도)"""
```

### AlertManager

알림 관리 클래스입니다.

```python
class AlertManager:
    def __init__(self, window_sec: int = 30, min_risk: float = 0.8):
        """알림 관리자 초기화"""

    def on_anomaly(self, risk: float) -> bool:
        """이상치 발생 시 알림 여부 판단"""
```

## 데이터 모델

### AnomalyRecord

이상치 레코드입니다.

```python
@dataclass(frozen=True)
class AnomalyRecord:
    case_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    detected_value: Optional[float]
    expected_range: Optional[Tuple[float, float]]
    location: Optional[str]
    timestamp: datetime
    risk_score: Optional[float] = None
```

### AnomalyType

이상치 유형 열거형입니다.

```python
class AnomalyType(Enum):
    TIME_REVERSAL = "시간 역전"
    LOCATION_SKIP = "위치 스킵"
    EXCESSIVE_DWELL = "과도 체류"
    ML_OUTLIER = "머신러닝 이상치"
    DATA_QUALITY = "데이터 품질"
```

### AnomalySeverity

이상치 심각도 열거형입니다.

```python
class AnomalySeverity(Enum):
    CRITICAL = "치명적"
    HIGH = "높음"
    MEDIUM = "보통"
    LOW = "낮음"
```

## 사용 예제

### 기본 사용법

```python
from anomaly_detector import HybridAnomalyDetector, DetectorConfig
import pandas as pd

# 설정 생성
config = DetectorConfig()
config.batch_size = 1000
config.contamination = 0.02

# 데이터 로딩
df = pd.read_excel("data.xlsx", sheet_name="Case List")

# 탐지기 생성 및 실행
detector = HybridAnomalyDetector(config)
result = detector.run(df, export_excel="report.xlsx")

# 결과 확인
print(f"총 이상치: {result['summary']['total']}")
for anomaly in result['anomalies'][:5]:
    print(f"- {anomaly.anomaly_type.value}: {anomaly.description}")
```

### 커스텀 설정

```python
# 커스텀 헤더 매핑
config = DetectorConfig()
config.column_map["Custom Case"] = "CASE_NO"
config.column_map["Custom HVDC"] = "HVDC_CODE"

# 성능 튜닝
config.batch_size = 500
config.max_workers = 4
config.contamination = 0.05

# 알림 설정
config.alert_window_sec = 60
config.min_risk_to_alert = 0.9
```

### 개별 탐지기 사용

```python
from anomaly_detector import RuleDetector, StatDetector, MLDetector

# 규칙 기반 탐지
rule_detector = RuleDetector(config)
for _, row in df.iterrows():
    anomaly = rule_detector.time_reversal(row)
    if anomaly:
        print(f"시간 역전 발견: {anomaly.case_id}")

# 통계 기반 탐지
stat_detector = StatDetector(iqr_k=2.0)
dwell_list = [(case_id, loc, days) for ...]  # 체류 데이터
anomalies = stat_detector.iqr_outliers(dwell_list)

# ML 기반 탐지
ml_detector = MLDetector(contamination=0.01)
features = df[['TOUCH_COUNT', 'TOTAL_DAYS', 'AMOUNT']]
y_pred, risk_scores = ml_detector.fit_predict(features)
```

## 오류 처리

### 일반적인 오류

1. **데이터 로딩 실패**
   ```python
   if not isinstance(df, pd.DataFrame):
       logger.error(f"데이터 로딩 실패: {type(df)}")
   ```

2. **의존성 누락**
   ```python
   try:
       from sklearn.ensemble import IsolationForest
       SKLEARN_AVAILABLE = True
   except ImportError:
       SKLEARN_AVAILABLE = False
   ```

3. **메모리 부족**
   - `batch_size` 감소
   - `max_workers` 감소

### 로깅

```python
import logging
logger = logging.getLogger("hvdc.anomaly")

# 로그 레벨 설정
logging.basicConfig(level=logging.INFO)

# 사용자 정의 로그
logger.info("탐지 완료")
logger.warning("데이터 품질 이슈 발견")
logger.error("심각한 이상치 탐지")
```

## 성능 최적화

### 배치 처리
```python
config = DetectorConfig()
config.batch_size = 1000  # 기본값
config.max_workers = 8    # 기본값
```

### 메모리 관리
```python
# 대용량 데이터 처리
for chunk in pd.read_excel("large_file.xlsx", chunksize=1000):
    result = detector.run(chunk)
    # 결과 처리
```

### 병렬 처리
```python
from concurrent.futures import ThreadPoolExecutor

def process_chunk(chunk):
    return detector.run(chunk)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_chunk, data_chunks))
```

---

**API 버전**: v2.0.0
**최종 업데이트**: 2025-10-18
**호환성**: Python 3.8+
