# Stage 4 Balanced Boost 빠른 시작 가이드

**HVDC Pipeline v4.0 - 실무 담당자용**

## 🎯 개요

Stage 4 Balanced Boost Edition은 위험도 포화 문제를 해결하고 실무에서 활용 가능한 정확한 이상치 탐지 시스템입니다.

### 주요 개선사항
- **위험도 정규화**: 0.981~0.999 범위로 정렬/비교 가능
- **ML 이상치 97% 감소**: 3,724건 → 115건
- **Balanced Boost**: 룰/통계 근거 기반 정확도 향상

---

## 🚀 빠른 실행

### 1. 전체 파이프라인 실행
```bash
python run_pipeline.py --all
```

### 2. Stage 4만 실행
```bash
python run_pipeline.py --stage 4 --stage4-visualize
```

### 3. 결과 확인
```bash
# JSON 결과 확인
python -c "import json; data=json.load(open('data/anomaly/HVDC_anomaly_report.json', encoding='utf-8')); print(f'총 이상치: {len(data)}건')"

# Excel 결과 확인
# 파일: data/anomaly/HVDC_anomaly_report.xlsx
```

---

## 📊 위험도 기반 우선순위 처리

### 1. 위험도별 정렬
```python
import json

# JSON 결과 로드
with open('data/anomaly/HVDC_anomaly_report.json', encoding='utf-8') as f:
    anomalies = json.load(f)

# 위험도 내림차순 정렬
sorted_anomalies = sorted(
    anomalies,
    key=lambda x: x.get('Risk_Score', 0),
    reverse=True
)

# 상위 10건 우선 처리
for i, anomaly in enumerate(sorted_anomalies[:10], 1):
    print(f"{i}. Case: {anomaly['Case_ID']}")
    print(f"   Type: {anomaly['Anomaly_Type']}")
    print(f"   Risk: {anomaly['Risk_Score']:.3f}")
    print(f"   Description: {anomaly['Description']}\n")
```

### 2. 심각도별 필터링
```python
# 심각도별 분류
critical = [a for a in anomalies if a['Severity'] == '치명적']
high = [a for a in anomalies if a['Severity'] == '높음']
medium = [a for a in anomalies if a['Severity'] == '보통']

print(f"치명적: {len(critical)}건")
print(f"높음: {len(high)}건")
print(f"보통: {len(medium)}건")
```

---

## 🔔 심각도별 알람 설정

### 1. 알람 임계값 설정
```python
# 알람 임계값 정의
ALERT_THRESHOLDS = {
    'CRITICAL': 0.97,  # 즉시 대응
    'HIGH': 0.90,      # 당일 대응
    'MEDIUM': 0.80,    # 주간 검토
}

# 임계값별 케이스 분류
critical_cases = [
    a for a in anomalies
    if a.get('Risk_Score', 0) >= ALERT_THRESHOLDS['CRITICAL']
]

print(f"즉시 대응 필요: {len(critical_cases)}건")
```

### 2. 이메일 알람 템플릿
```python
def generate_alert_email(anomalies):
    """이상치 알람 이메일 생성"""
    critical_count = len([a for a in anomalies if a['Severity'] == '치명적'])

    subject = f"[HVDC] 이상치 알람 - 치명적 {critical_count}건"
    body = f"""
    HVDC 파이프라인 이상치 탐지 결과

    총 이상치: {len(anomalies)}건
    - 치명적: {critical_count}건
    - 높음: {len([a for a in anomalies if a['Severity'] == '높음'])}건
    - 보통: {len([a for a in anomalies if a['Severity'] == '보통'])}건

    상세 내용은 첨부 파일을 확인하세요.
    """
    return subject, body
```

---

## 🎯 이상치 유형별 대응 프로세스

### 1. 시간 역전 (Time Reversal)
**특징**: 날짜 순서가 역전된 케이스
**위험도**: 0.999 (최고)
**대응 프로세스**:
1. 데이터 수정 요청
2. 원본 데이터 확인
3. 재처리 후 검증

```python
time_reversal_cases = [
    a for a in anomalies
    if a['Anomaly_Type'] == '시간 역전'
]
print(f"시간 역전 케이스: {len(time_reversal_cases)}건")
```

### 2. ML 이상치 (Machine Learning Outliers)
**특징**: 통계적 패턴에서 벗어난 케이스
**위험도**: 0.981~0.999
**대응 프로세스**:
- **치명적 (≥0.97)**: 현장 확인 + 원인 분석
- **높음 (0.90~0.96)**: 문서 검토 + 데이터 검증
- **보통 (0.80~0.89)**: 모니터링

```python
ml_cases = [
    a for a in anomalies
    if a['Anomaly_Type'] == '머신러닝 이상치'
]

# 위험도별 분류
critical_ml = [a for a in ml_cases if a.get('Risk_Score', 0) >= 0.97]
high_ml = [a for a in ml_cases if 0.90 <= a.get('Risk_Score', 0) < 0.97]
medium_ml = [a for a in ml_cases if a.get('Risk_Score', 0) < 0.90]

print(f"ML 이상치 - 치명적: {len(critical_ml)}건")
print(f"ML 이상치 - 높음: {len(high_ml)}건")
print(f"ML 이상치 - 보통: {len(medium_ml)}건")
```

### 3. 과도 체류 (Excessive Dwell)
**특징**: 특정 위치에서 예상보다 오래 체류
**위험도**: 위치별 IQR+MAD 기준
**대응 프로세스**:
1. 위치별 운영 점검
2. 체류 사유 확인
3. 프로세스 개선 검토

```python
dwell_cases = [
    a for a in anomalies
    if a['Anomaly_Type'] == '과도 체류'
]

# 위치별 분류
location_groups = {}
for case in dwell_cases:
    loc = case.get('Location', 'Unknown')
    if loc not in location_groups:
        location_groups[loc] = []
    location_groups[loc].append(case)

for loc, cases in location_groups.items():
    print(f"{loc}: {len(cases)}건")
```

### 4. 데이터 품질 (Data Quality)
**특징**: 시스템적 데이터 이슈
**대응 프로세스**:
1. 시스템 정비
2. 데이터 정합성 검증
3. 프로세스 개선

```python
quality_cases = [
    a for a in anomalies
    if a['Anomaly_Type'] == '데이터 품질'
]

for case in quality_cases:
    print(f"데이터 품질 이슈: {case['Description']}")
```

---

## ⚙️ 튜닝 팁

### 1. Contamination 조정
```bash
# 보수적 (1% 이상치 가정)
python run_pipeline.py --stage 4 --contamination 0.01

# 권장 (2% 이상치 가정) - 기본값
python run_pipeline.py --stage 4 --contamination 0.02

# 공격적 (5% 이상치 가정)
python run_pipeline.py --stage 4 --contamination 0.05
```

**조정 가이드**:
- **0.01**: 확실한 이상치만 탐지 (미탐 위험)
- **0.02**: 균형 잡힌 탐지 (권장)
- **0.05**: 의심 케이스 포함 (허위 양성 위험)

### 2. 가산치 조정
`scripts/stage4_anomaly/anomaly_detector_balanced.py` 수정:

```python
class DetectorConfig:
    # 시간 역전 가산치 (기본: 0.25)
    rule_boost: float = 0.25

    # 통계 이상(높음/치명) 가산치 (기본: 0.15)
    stat_boost_high: float = 0.15

    # 통계 이상(보통) 가산치 (기본: 0.08)
    stat_boost_med: float = 0.08
```

**조정 가이드**:
- **가산치 증가**: 룰/통계 근거를 더 강하게 반영 (허위 양성↓, 미탐↑)
- **가산치 감소**: ML 판정을 더 신뢰 (허위 양성↑, 미탐↓)

### 3. 위치별 임계치 조정
```python
class DetectorConfig:
    # IQR 배수 (기본: 1.5)
    iqr_k: float = 1.5

    # MAD 배수 (기본: 3.5)
    mad_k: float = 3.5

    # 최소 표본 수 (기본: 10)
    min_group_size: int = 10
```

**조정 가이드**:
- **iqr_k/mad_k 증가**: 더 관대한 판정 (과도 체류 감소)
- **iqr_k/mad_k 감소**: 더 엄격한 판정 (과도 체류 증가)
- **min_group_size 증가**: 더 보수적 판정 (표본 부족 시 스킵)

---

## 📈 성능 모니터링

### 1. 실행 시간 모니터링
```bash
# 실행 시간 측정
time python run_pipeline.py --stage 4

# 메모리 사용량 모니터링
python -m memory_profiler run_pipeline.py --stage 4
```

### 2. 결과 품질 검증
```python
def validate_results(json_path):
    """결과 품질 검증"""
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    # 위험도 범위 검증
    risk_scores = [a.get('Risk_Score', 0) for a in data if a.get('Risk_Score')]
    min_risk = min(risk_scores) if risk_scores else 0
    max_risk = max(risk_scores) if risk_scores else 0

    print(f"위험도 범위: {min_risk:.3f} ~ {max_risk:.3f}")
    print(f"위험도 1.000 개수: {sum(1 for r in risk_scores if r == 1.0)}건")

    # 유형별 분포
    types = {}
    for anomaly in data:
        t = anomaly['Anomaly_Type']
        types[t] = types.get(t, 0) + 1

    for t, count in types.items():
        print(f"{t}: {count}건")

# 검증 실행
validate_results('data/anomaly/HVDC_anomaly_report.json')
```

---

## 🚨 문제 해결

### 1. 일반적인 문제

**Q: 위험도가 여전히 높게 나옵니다**
A: contamination 값을 낮추거나(0.01), 가산치를 감소시키세요.

**Q: PyOD 설치가 필요한가요?**
A: 선택사항입니다. sklearn IsolationForest로 자동 폴백됩니다.

**Q: 기존 JSON 포맷과 호환되나요?**
A: 네, 100% 호환됩니다. Risk_Score 필드만 정규화됩니다.

**Q: 과도 체류 판정이 너무 많습니다**
A: iqr_k를 1.5→2.0으로 증가시키거나, min_group_size를 늘리세요.

### 2. 로그 확인
```bash
# 파이프라인 로그
tail -f logs/pipeline.log

# Stage 4 로그만 필터링
grep "balanced_boost" logs/pipeline.log
```

### 3. 디버그 모드
```bash
# 상세 로그와 함께 실행
python run_pipeline.py --stage 4 --verbose
```

---

## 📞 지원 및 문의

### 추가 문서
- [상세 업그레이드 보고서](../STAGE4_BALANCED_BOOST_UPGRADE_REPORT.md)
- [파이프라인 실행 가이드](PIPELINE_EXECUTION_GUIDE.md)
- [Stage 4 사용자 가이드](STAGE4_USER_GUIDE.md)

### 기술 지원
- **로그 확인**: `logs/pipeline.log`
- **설정 파일**: `config/pipeline_config.yaml`
- **코드 위치**: `scripts/stage4_anomaly/anomaly_detector_balanced.py`

---

**버전**: v4.0 Balanced Boost Edition
**최종 업데이트**: 2025-10-22
**작성**: AI Development Team
**승인**: Samsung C&T Logistics & ADNOC·DSV Partnership
