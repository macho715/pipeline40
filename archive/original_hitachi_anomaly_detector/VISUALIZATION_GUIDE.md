# HVDC 이상치 시각화 가이드 v1.0

## 📋 개요

이 문서는 HVDC 프로젝트의 이상치 탐지 시스템에서 **시간 역전 397건**을 포함한 모든 이상치를 Excel 파일에 색상으로 시각화하는 방법을 설명합니다.

`data_synchronizer_v29.py`의 색상 로직을 재사용하여 원본 Excel 파일에 직관적인 색상 표시를 제공합니다.

## 🎨 색상 코드

| 색상 | 코드 | 용도 | 대상 |
|------|------|------|------|
| 🔴 **빨강** | `FF0000` | 시간 역전 | 날짜 컬럼만 |
| 🟠 **주황** | `FFC000` | ML 이상치 (높음) | 전체 행 |
| 🟡 **노랑** | `FFFF00` | ML 이상치 (보통) | 전체 행 |
| 🟣 **보라** | `CC99FF` | 데이터 품질 | 전체 행 |

## 🚀 사용법

### 기본 명령어

```bash
cd hitachi/anomaly_detector

# 1단계: 이상치 탐지 + 색상 표시
python anomaly_detector.py \
  --input "../HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --sheet "Case List" \
  --excel-out "hvdc_anomaly_report_v2.xlsx" \
  --json-out "hvdc_anomaly_report_v2.json" \
  --visualize
```

### 고급 옵션

```bash
# 백업 없이 실행
python anomaly_detector.py \
  --input "../HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --sheet "Case List" \
  --json-out "hvdc_anomaly_report_v2.json" \
  --visualize \
  --no-backup

# 다른 Case NO 컬럼명 사용
python anomaly_detector.py \
  --input "../HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --sheet "Case List" \
  --json-out "hvdc_anomaly_report_v2.json" \
  --visualize \
  --case-col "CASE_NO"
```

## 📊 실행 결과

### 성공적인 실행 예시

```
2025-10-18 18:53:42,504 | INFO | ✅ 색상 표시 완료: ✅ 508건 이상치 색상 표시 완료
2025-10-18 18:53:42,504 | INFO |   - 시간 역전: 397건 (빨강)
2025-10-18 18:53:42,504 | INFO |   - ML 이상치: 110건 (주황/노랑)
2025-10-18 18:53:42,504 | INFO |   - 데이터 품질: 1건 (보라)
```

### 색상 적용 결과

- **총 색칠된 행**: 508개 (이상치가 있는 행만)
- **시간 역전**: 397건 → 날짜 컬럼만 빨강으로 표시
- **ML 이상치**: 110건 → 전체 행을 주황/노랑으로 표시
- **데이터 품질**: 1건 → 전체 행을 보라로 표시

## 🔧 기술적 세부사항

### 핵심 클래스

#### `AnomalyVisualizer`
```python
class AnomalyVisualizer:
    def __init__(self, anomalies: List[AnomalyRecord]):
        self.anomalies = anomalies
        self.color_map = {
            AnomalyType.TIME_REVERSAL: "FF0000",
            AnomalyType.ML_OUTLIER: self._get_ml_color,
            AnomalyType.DATA_QUALITY: "CC99FF",
        }

    def apply_anomaly_colors(self, excel_file: str, sheet_name: str, case_col: str):
        # 색상 적용 로직
```

### 주요 메서드

#### `_build_case_index()`
- Case NO 컬럼에서 케이스 번호 → 행 번호 매핑
- 유연한 컬럼명 인식 ("Case No.", "CASE_NO", "case" 등)

#### `_color_date_columns()`
- 시간 역전: 날짜 컬럼만 색칠
- `data_synchronizer_v29.py`의 `DATE_KEYS` 재사용

#### `_color_entire_row()`
- ML 이상치/데이터 품질: 전체 행 색칠
- 모든 컬럼에 동일한 색상 적용

### 날짜 컬럼 자동 인식

```python
DATE_KEYS = [
    "ETD/ATD", "ETA/ATA", "DHL Warehouse", "DSV Indoor",
    "DSV Al Markaz", "DSV Outdoor", "AAA Storage", "Hauler Indoor",
    "DSV MZP", "MOSB", "Shifting", "MIR", "SHU", "DAS", "AGI"
]
```

## 📁 파일 구조

```
hitachi/anomaly_detector/
├── anomaly_detector.py          # 메인 이상치 탐지 시스템
├── anomaly_visualizer.py        # 색상 시각화 도구
├── test_anomaly_detector.py     # 테스트 스위트
├── verify_colors.py             # 색상 검증 스크립트
├── debug_case_matching.py       # Case ID 매칭 디버깅
├── debug_anomaly_types.py       # 이상치 유형 디버깅
└── VISUALIZATION_GUIDE.md       # 이 문서
```

## 🔍 검증 및 디버깅

### 색상 적용 확인

```bash
python verify_colors.py
```

**예상 출력**:
```
📊 색상별 행 수:
  - 빨강 행: 397개 (시간 역전)
  - 주황 행: 110개 (ML 이상치 - 높음)
  - 노랑 행: 0개 (ML 이상치 - 보통)
  - 보라 행: 1개 (데이터 품질)
```

### Case ID 매칭 디버깅

```bash
python debug_case_matching.py
```

### 이상치 유형 디버깅

```bash
python debug_anomaly_types.py
```

## ⚠️ 주의사항

### 원본 파일 수정
- **자동 백업 생성**: 원본 파일이 수정되므로 타임스탬프가 포함된 백업 파일이 자동 생성됩니다
- **백업 파일명**: `HVDC WAREHOUSE_HITACHI(HE).backup_YYYYMMDD_HHMMSS.xlsx`

### Excel 버전 요구사항
- **Excel 2010 이상** 버전 필요
- **openpyxl** 라이브러리 사용

### 성능 고려사항
- **5,552건 처리 시간**: 약 20초
- **메모리 사용량**: 약 100MB
- **파일 크기 증가**: 색상 정보로 인해 약 10% 증가

## 🐛 문제 해결

### 일반적인 문제

#### 1. Case NO 컬럼을 찾을 수 없음
```
ValueError: Case NO 컬럼을 찾을 수 없습니다
```

**해결방법**:
- `--case-col` 옵션으로 정확한 컬럼명 지정
- Excel 파일의 첫 번째 행에 Case NO 컬럼이 있는지 확인

#### 2. 색상이 적용되지 않음
```
🎨 색상 적용 완료:
  - 시간 역전: 0건 (빨강)
  - ML 이상치: 0건 (주황/노랑)
  - 데이터 품질: 0건 (보라)
```

**해결방법**:
- JSON 파일이 올바르게 생성되었는지 확인
- Case ID 매칭이 정상적으로 되었는지 `debug_case_matching.py`로 확인

#### 3. 모든 행이 색칠됨
```
📊 색상별 행 수:
  - 빨강 행: 5552개 (시간 역전)
```

**원인**: 색상 범례가 데이터 행에 추가되어 모든 행이 색칠됨

**해결방법**:
- `anomaly_visualizer.py`의 `add_color_legend()` 메서드에서 범례 위치 조정

### 로그 레벨 조정

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📈 성능 최적화

### 배치 처리
- 1,000건 단위로 배치 처리하여 메모리 사용량 최적화
- `ThreadPoolExecutor`를 사용한 병렬 처리 (향후 구현)

### 캐싱
- Case NO 매핑 결과 캐싱
- 색상 정보 캐싱

## 🔄 업데이트 이력

### v1.0 (2025-10-18)
- 초기 버전 릴리스
- `data_synchronizer_v29.py` 색상 로직 재사용
- 시간 역전 397건 색상 표시 구현
- 자동 백업 기능 추가
- 색상 범례 자동 추가

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 다음을 확인하세요:

1. **로그 파일**: 실행 로그에서 오류 메시지 확인
2. **디버깅 스크립트**: `debug_*.py` 스크립트로 문제 진단
3. **테스트 실행**: `pytest test_anomaly_detector.py`로 기본 기능 확인

---

**HVDC 이상치 시각화 시스템 v1.0**
*Samsung C&T Logistics | ADNOC·DSV Partnership*

## 📋 개요

이 문서는 HVDC 프로젝트의 이상치 탐지 시스템에서 **시간 역전 397건**을 포함한 모든 이상치를 Excel 파일에 색상으로 시각화하는 방법을 설명합니다.

`data_synchronizer_v29.py`의 색상 로직을 재사용하여 원본 Excel 파일에 직관적인 색상 표시를 제공합니다.

## 🎨 색상 코드

| 색상 | 코드 | 용도 | 대상 |
|------|------|------|------|
| 🔴 **빨강** | `FF0000` | 시간 역전 | 날짜 컬럼만 |
| 🟠 **주황** | `FFC000` | ML 이상치 (높음) | 전체 행 |
| 🟡 **노랑** | `FFFF00` | ML 이상치 (보통) | 전체 행 |
| 🟣 **보라** | `CC99FF` | 데이터 품질 | 전체 행 |

## 🚀 사용법

### 기본 명령어

```bash
cd hitachi/anomaly_detector

# 1단계: 이상치 탐지 + 색상 표시
python anomaly_detector.py \
  --input "../HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --sheet "Case List" \
  --excel-out "hvdc_anomaly_report_v2.xlsx" \
  --json-out "hvdc_anomaly_report_v2.json" \
  --visualize
```

### 고급 옵션

```bash
# 백업 없이 실행
python anomaly_detector.py \
  --input "../HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --sheet "Case List" \
  --json-out "hvdc_anomaly_report_v2.json" \
  --visualize \
  --no-backup

# 다른 Case NO 컬럼명 사용
python anomaly_detector.py \
  --input "../HVDC WAREHOUSE_HITACHI(HE).xlsx" \
  --sheet "Case List" \
  --json-out "hvdc_anomaly_report_v2.json" \
  --visualize \
  --case-col "CASE_NO"
```

## 📊 실행 결과

### 성공적인 실행 예시

```
2025-10-18 18:53:42,504 | INFO | ✅ 색상 표시 완료: ✅ 508건 이상치 색상 표시 완료
2025-10-18 18:53:42,504 | INFO |   - 시간 역전: 397건 (빨강)
2025-10-18 18:53:42,504 | INFO |   - ML 이상치: 110건 (주황/노랑)
2025-10-18 18:53:42,504 | INFO |   - 데이터 품질: 1건 (보라)
```

### 색상 적용 결과

- **총 색칠된 행**: 508개 (이상치가 있는 행만)
- **시간 역전**: 397건 → 날짜 컬럼만 빨강으로 표시
- **ML 이상치**: 110건 → 전체 행을 주황/노랑으로 표시
- **데이터 품질**: 1건 → 전체 행을 보라로 표시

## 🔧 기술적 세부사항

### 핵심 클래스

#### `AnomalyVisualizer`
```python
class AnomalyVisualizer:
    def __init__(self, anomalies: List[AnomalyRecord]):
        self.anomalies = anomalies
        self.color_map = {
            AnomalyType.TIME_REVERSAL: "FF0000",
            AnomalyType.ML_OUTLIER: self._get_ml_color,
            AnomalyType.DATA_QUALITY: "CC99FF",
        }

    def apply_anomaly_colors(self, excel_file: str, sheet_name: str, case_col: str):
        # 색상 적용 로직
```

### 주요 메서드

#### `_build_case_index()`
- Case NO 컬럼에서 케이스 번호 → 행 번호 매핑
- 유연한 컬럼명 인식 ("Case No.", "CASE_NO", "case" 등)

#### `_color_date_columns()`
- 시간 역전: 날짜 컬럼만 색칠
- `data_synchronizer_v29.py`의 `DATE_KEYS` 재사용

#### `_color_entire_row()`
- ML 이상치/데이터 품질: 전체 행 색칠
- 모든 컬럼에 동일한 색상 적용

### 날짜 컬럼 자동 인식

```python
DATE_KEYS = [
    "ETD/ATD", "ETA/ATA", "DHL Warehouse", "DSV Indoor",
    "DSV Al Markaz", "DSV Outdoor", "AAA Storage", "Hauler Indoor",
    "DSV MZP", "MOSB", "Shifting", "MIR", "SHU", "DAS", "AGI"
]
```

## 📁 파일 구조

```
hitachi/anomaly_detector/
├── anomaly_detector.py          # 메인 이상치 탐지 시스템
├── anomaly_visualizer.py        # 색상 시각화 도구
├── test_anomaly_detector.py     # 테스트 스위트
├── verify_colors.py             # 색상 검증 스크립트
├── debug_case_matching.py       # Case ID 매칭 디버깅
├── debug_anomaly_types.py       # 이상치 유형 디버깅
└── VISUALIZATION_GUIDE.md       # 이 문서
```

## 🔍 검증 및 디버깅

### 색상 적용 확인

```bash
python verify_colors.py
```

**예상 출력**:
```
📊 색상별 행 수:
  - 빨강 행: 397개 (시간 역전)
  - 주황 행: 110개 (ML 이상치 - 높음)
  - 노랑 행: 0개 (ML 이상치 - 보통)
  - 보라 행: 1개 (데이터 품질)
```

### Case ID 매칭 디버깅

```bash
python debug_case_matching.py
```

### 이상치 유형 디버깅

```bash
python debug_anomaly_types.py
```

## ⚠️ 주의사항

### 원본 파일 수정
- **자동 백업 생성**: 원본 파일이 수정되므로 타임스탬프가 포함된 백업 파일이 자동 생성됩니다
- **백업 파일명**: `HVDC WAREHOUSE_HITACHI(HE).backup_YYYYMMDD_HHMMSS.xlsx`

### Excel 버전 요구사항
- **Excel 2010 이상** 버전 필요
- **openpyxl** 라이브러리 사용

### 성능 고려사항
- **5,552건 처리 시간**: 약 20초
- **메모리 사용량**: 약 100MB
- **파일 크기 증가**: 색상 정보로 인해 약 10% 증가

## 🐛 문제 해결

### 일반적인 문제

#### 1. Case NO 컬럼을 찾을 수 없음
```
ValueError: Case NO 컬럼을 찾을 수 없습니다
```

**해결방법**:
- `--case-col` 옵션으로 정확한 컬럼명 지정
- Excel 파일의 첫 번째 행에 Case NO 컬럼이 있는지 확인

#### 2. 색상이 적용되지 않음
```
🎨 색상 적용 완료:
  - 시간 역전: 0건 (빨강)
  - ML 이상치: 0건 (주황/노랑)
  - 데이터 품질: 0건 (보라)
```

**해결방법**:
- JSON 파일이 올바르게 생성되었는지 확인
- Case ID 매칭이 정상적으로 되었는지 `debug_case_matching.py`로 확인

#### 3. 모든 행이 색칠됨
```
📊 색상별 행 수:
  - 빨강 행: 5552개 (시간 역전)
```

**원인**: 색상 범례가 데이터 행에 추가되어 모든 행이 색칠됨

**해결방법**:
- `anomaly_visualizer.py`의 `add_color_legend()` 메서드에서 범례 위치 조정

### 로그 레벨 조정

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📈 성능 최적화

### 배치 처리
- 1,000건 단위로 배치 처리하여 메모리 사용량 최적화
- `ThreadPoolExecutor`를 사용한 병렬 처리 (향후 구현)

### 캐싱
- Case NO 매핑 결과 캐싱
- 색상 정보 캐싱

## 🔄 업데이트 이력

### v1.0 (2025-10-18)
- 초기 버전 릴리스
- `data_synchronizer_v29.py` 색상 로직 재사용
- 시간 역전 397건 색상 표시 구현
- 자동 백업 기능 추가
- 색상 범례 자동 추가

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 다음을 확인하세요:

1. **로그 파일**: 실행 로그에서 오류 메시지 확인
2. **디버깅 스크립트**: `debug_*.py` 스크립트로 문제 진단
3. **테스트 실행**: `pytest test_anomaly_detector.py`로 기본 기능 확인

---

**HVDC 이상치 시각화 시스템 v1.0**
*Samsung C&T Logistics | ADNOC·DSV Partnership*
