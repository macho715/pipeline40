# HVDC Anomaly Detector v4.0 - 설치 및 사용 가이드

## 🖥️ 시스템 요구사항 (확인완료)

✅ **PC:** DESKTOP-GVDR89F
✅ **CPU:** Intel i7-1165G7 @ 2.80GHz (4코어/8스레드)
✅ **RAM:** 32GB
✅ **OS:** Windows 11 Enterprise 24H2
✅ **Python:** 3.8 이상 (권장 3.10)

---

## 📦 설치 (오프라인 환경 대응)

### 방법 1: 온라인 설치 (인터넷 연결 가능)
```bash
cd C:\Users\SAMSUNG\Downloads\HVDC_Invoice-20251015T070213Z-1-001\HVDC_Invoice\hvdc_pipeline\scripts\stage4_anomaly_new

# 가상환경 생성 (권장)
python -m venv venv_v4
venv_v4\Scripts\activate

# 의존성 설치
pip install -r requirements_v4.txt
```

### 방법 2: 오프라인 설치 (GitHub 접속 불가)

**Step 1: 온라인 환경에서 휠 파일 다운로드**
```bash
# 다른 PC에서 실행
pip download -r requirements_v4.txt -d ./wheels
# wheels 폴더를 USB로 복사
```

**Step 2: 오프라인 환경에서 설치**
```bash
cd C:\Users\SAMSUNG\Downloads\HVDC_Invoice-20251015T070213Z-1-001\HVDC_Invoice\hvdc_pipeline\scripts\stage4_anomaly_new

# USB에서 wheels 폴더 복사 후
pip install --no-index --find-links=./wheels -r requirements_v4.txt
```

### 방법 3: 최소 설치 (Deep Learning 제외)
```bash
pip install numpy pandas openpyxl scikit-learn pyod xgboost lightgbm
```

---

## 🚀 사용법

### 1. 기본 실행 (CLI)
```bash
python anomaly_detector_v4.py \
  --input "C:\path\to\HVDC_입고로직_종합리포트_20251020.xlsx" \
  --sheet "통합_원본데이터_Fixed" \
  --excel-out "C:\path\to\output\anomalies_v4.xlsx" \
  --json-out "C:\path\to\output\anomalies_v4.json"
```

### 2. 옵션 조정
```bash
# 딥러닝 비활성화 (빠른 실행)
python anomaly_detector_v4.py --input input.xlsx --no-dl

# 부스팅만 사용
python anomaly_detector_v4.py --input input.xlsx --no-dl

# 오염률 조정 (민감도)
python anomaly_detector_v4.py --input input.xlsx --contamination 0.05
```

### 3. Python 스크립트 통합
```python
import pandas as pd
from anomaly_detector_v4 import HybridAnomalyDetector, DetectorConfig

# 데이터 로드
df = pd.read_excel("input.xlsx", sheet_name="통합_원본데이터_Fixed")

# 설정
cfg = DetectorConfig(
    contamination=0.02,
    use_deep_learning=True,  # i7-1165G7에서 약 30-60초 소요
    use_boosting=True,       # XGBoost, LightGBM 사용
    compute_shap=True,       # 설명 가능성 (옵션)
    n_workers=4,             # CPU 코어 수
)

# 탐지 실행
detector = HybridAnomalyDetector(cfg)
result = detector.run(
    df,
    export_excel="output/anomalies_v4.xlsx",
    export_json="output/anomalies_v4.json"
)

# 결과 확인
print(f"Total Anomalies: {result['summary']['total_anomalies']}")
print(f"Models Used: {result['summary']['ml_models']}")
```

---

## 📊 출력 형식

### Excel 출력 (anomalies_v4.xlsx)

**Sheet 1: Anomalies**
| case_id | anomaly_type | severity | description | risk_score | model_source | remediation |
|---------|--------------|----------|-------------|------------|--------------|-------------|
| HVDC-001| 앙상블 이상치 | 높음 | 앙상블 이상치 탐지... | 0.95 | Ensemble(5 models) | 다차원 분석 필요... |

**Sheet 2: Source_Sample** - 원본 데이터 샘플 (1000건)

**Sheet 3: Model_Metrics** - 모델 성능 지표

### JSON 출력 (anomalies_v4.json)
```json
{
  "anomalies": [
    {
      "case_id": "HVDC-001",
      "anomaly_type": "앙상블 이상치",
      "severity": "높음",
      "risk_score": 0.95,
      "model_source": "Ensemble(5 models)",
      "shap_top3": "{\"AMOUNT\": 0.42, \"TOTAL_DAYS\": 0.38, ...}"
    }
  ],
  "summary": {
    "total_cases": 1000,
    "total_anomalies": 25,
    "ml_models": ["ECOD", "COPOD", "HBOS", "IForest", "XGBoost", "LightGBM", "Autoencoder"]
  }
}
```

---

## ⚡ 성능 최적화 (i7-1165G7)

### 처리 속도 예상치
| 데이터 규모 | v3 (기존) | v4 (최적화) | 모델 수 |
|------------|----------|------------|--------|
| 100건 | ~5초 | ~8초 | 7개 |
| 1,000건 | ~15초 | ~25초 | 7개 |
| 5,000건 | ~60초 | ~90초 | 7개 |
| 10,000건 | ~120초 | ~180초 | 7개 |

**속도 개선 팁:**
```python
# 1. 딥러닝 비활성화 (30% 빨라짐)
cfg = DetectorConfig(use_deep_learning=False)

# 2. 부스팅 모델 수 감소
cfg = DetectorConfig(n_estimators=50)  # 기본 100

# 3. SHAP 비활성화
cfg = DetectorConfig(compute_shap=False)

# 4. 배치 크기 증가 (메모리 충분 시)
cfg = DetectorConfig(batch_size=256)  # 기본 128
```

---

## 🔍 v3 → v4 업그레이드 비교

| 항목 | v3 | v4 |
|------|----|----|
| **모델 수** | 4개 | 7-10개 |
| **알고리즘** | PyOD만 | PyOD + XGBoost + LightGBM + Autoencoder + LSTM |
| **설명 가능성** | ❌ | ✅ SHAP values |
| **CPU 최적화** | 단일스레드 | 멀티스레드 (4-8 workers) |
| **메모리 효율** | 보통 | 배치 처리 최적화 |
| **앙상블 방식** | 평균 | ECDF 캘리브레이션 + 가중평균 |
| **Remediation** | ❌ | ✅ 개선 가이드 포함 |

---

## 🧪 테스트 실행

```bash
# 샘플 데이터로 테스트
python test_v4.py

# 실제 데이터로 빠른 검증
python anomaly_detector_v4.py \
  --input "C:\...\reports\HVDC_입고로직_종합리포트_latest.xlsx" \
  --no-dl --no-shap \
  --excel-out test_output.xlsx
```

---

## 📝 로그 확인

실행 중 다음과 같은 로그가 출력됩니다:
```
2025-10-20 15:30:00 [INFO] System: 8 cores, 32GB RAM, Batch=128, Workers=8
2025-10-20 15:30:05 [INFO] Features built: (1000, 15), 2543 dwell records
2025-10-20 15:30:10 [INFO] Rule detection: 12 anomalies (0.52s)
2025-10-20 15:30:15 [INFO] Statistical detection: 8 anomalies (0.38s)
2025-10-20 15:30:45 [INFO] ML ensemble: 15 anomalies detected with 7 models (30.12s)
2025-10-20 15:30:45 [INFO] Detection complete: 35 anomalies in 45.82s
```

---

## ⚠️ 문제 해결

### 1. TensorFlow 설치 실패
```bash
# CPU 버전 수동 설치
pip install tensorflow-cpu==2.13.1
```

### 2. XGBoost 빌드 오류
```bash
# 사전 빌드 휠 다운로드
# https://www.lfd.uci.edu/~gohlke/pythonlibs/
pip install xgboost-1.7.0-cp310-cp310-win_amd64.whl
```

### 3. 메모리 부족
```python
# 배치 크기 감소
cfg = DetectorConfig(batch_size=64)
```

### 4. 느린 실행 속도
```python
# 최소 모드
cfg = DetectorConfig(
    use_deep_learning=False,
    use_boosting=False,
    compute_shap=False
)
```

---

## 📞 지원

- **이슈:** `stage4_anomaly_new/` 폴더의 로그 파일 확인
- **문서:** `README_v4_UPGRADE.md` 참조
- **커스터마이징:** `DetectorConfig` 클래스 파라미터 조정

---

**Last Updated:** 2025-10-20
**Version:** 4.0.0
**Optimized for:** Intel i7-1165G7 + 32GB RAM + Windows 11
