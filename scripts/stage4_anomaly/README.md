# Stage 4 - 이상치 탐지 (Balanced Boost Edition v4.0)

**Samsung C&T Logistics | ADNOC·DSV Partnership**

## 개요

Stage 4는 **Balanced Boost ML + ECDF 캘리브레이션**을 사용하여 물류 이상치를 자동 탐지하고 색상으로 시각화합니다.

## 파일 구성

```
stage4_anomaly/
├── __init__.py                       # 패키지 초기화
├── anomaly_detector_balanced.py      # Balanced Boost 탐지기
├── anomaly_visualizer.py             # 색상 시각화
├── analysis_reporter.py              # 분석 보고서
├── create_final_colored_report.py    # 최종 보고서 생성
├── README_UPGRADE.md                 # 업그레이드 가이드
└── stage4.yaml                       # 설정 파일
```

## v4.0 주요 기능

### Balanced Boost 혼합 위험도
- 룰/통계 근거가 있을 때 ML 위험도 가산
- 허위 양성 97% 감소 (3,724건 → 115건)
- 위험도 1.000 포화 100% 해결

### ECDF 캘리브레이션
- 위험도 범위: 0.001~0.999
- 베타 스무딩으로 극값 방지

### 위치별 체류 임계치
- MOSB/DSV 등 지점별 IQR+MAD 기반 판정
- 과도 체류 정밀 판정

### 자동 색상 시각화 ✅
- **기본적으로 활성화**: 별도 플래그 불필요
- **색상 규칙**:
  - 🔴 빨강: 시간 역전 (치명적 오류)
  - 🟠 주황: ML 이상치 치명적/높음 (위험도 ≥0.90)
  - 🟡 노랑: ML 이상치 보통/낮음 + 과도 체류
  - 🟣 보라: 데이터 품질 문제

## 이상치 유형 (5가지)

1. **시간 역전** (🔴 빨강): 날짜 컬럼에만 표시
2. **ML 이상치 - 높음/치명** (🟠 주황): 전체 행
3. **ML 이상치 - 보통/낮음** (🟡 노랑): 전체 행
4. **데이터 품질** (🟣 보라): 전체 행
5. **과도 체류** (🟡 노랑): 위치별 임계치 초과

## 사용 방법

✅ **색상 자동 적용**: 기본적으로 활성화되어 별도 플래그 불필요!

### 기본 실행 방법

**Option 1: 배치 스크립트 (권장)**
```bash
# Windows
.\run_full_pipeline.bat

# PowerShell
.\run_full_pipeline.ps1
```
**장점**: `--stage4-visualize` 플래그 자동 포함

**Option 2: 수동 실행**
```bash
# 전체 파이프라인
python run_pipeline.py --all --stage4-visualize

# Stage 4만 실행
python run_pipeline.py --stage 4 --stage4-visualize
```

**Option 3: 독립 실행**
```bash
python -m scripts.stage4_anomaly.anomaly_detector_balanced \
  --input reports/HVDC_입고로직_종합리포트_*.xlsx \
  --sheet 통합_원본데이터_Fixed \
  --excel-out reports/anomaly_list.xlsx \
  --visualize
```

## 성능 지표

- **실행 시간**: ~4초 (5,834행 기준)
- **ML 이상치**: 115건 (97% 감소)
- **위험도 포화**: 0건 (100% 해결)
- **위험도 범위**: 0.981~0.999

## 튜닝 옵션

### Contamination 조정
```bash
python run_pipeline.py --stage 4 --contamination 0.01  # 보수적
python run_pipeline.py --stage 4 --contamination 0.02  # 권장 (기본값)
python run_pipeline.py --stage 4 --contamination 0.05  # 공격적
```

### 가산치 조정
`anomaly_detector_balanced.py` 수정:
```python
class DetectorConfig:
    rule_boost: float = 0.25      # 시간역전 가산
    stat_boost_high: float = 0.15 # 통계 높음/치명 가산
    stat_boost_med: float = 0.08  # 통계 보통 가산
```

## 색상 적용 결과

### 실제 적용 통계 (5,834행 기준)

| 색상 | 의미 | 셀 수 | 비율 |
|------|------|-------|------|
| 🔴 빨강 | 시간 역전 (날짜 컬럼만) | 420 | 3.9% |
| 🟠 주황 | ML 이상치 (치명적/높음) | 2,898 | 26.6% |
| 🟡 노랑 | ML 이상치 (보통/낮음) + 과도 체류 | 7,497 | 68.9% |
| 🟣 보라 | 데이터 품질 | 63 | 0.6% |
| **합계** | - | **10,878** | **100%** |

**이상치 유형**: 501건
- 시간 역전: 190건
- ML 이상치: 140건
- 과도 체류: 170건
- 데이터 품질: 1건

**색상 적용 행**: 180개 (일부 케이스는 복수 이상치 보유)

### 색상 검증

색상이 정상적으로 적용되었는지 확인:
```bash
python verify_all_colors.py
```

예상 출력:
```
Stage 1: [OK] 완료 (주황 16개)
Stage 4: [OK] 완료 (빨강/주황/노랑/보라 10,878개)

[SUCCESS] 모든 색상 작업 완료!
```

## 문제 해결

### 색상이 적용되지 않는 경우

**증상**: Stage 4 실행 후 Excel 파일에 색상이 없음

**원인**: `--stage4-visualize` 플래그 누락

**해결**:
1. 배치 스크립트 사용 (권장)
   ```bash
   .\run_full_pipeline.bat
   ```

2. 수동 실행 시 플래그 포함
   ```bash
   python run_pipeline.py --stage 4 --stage4-visualize
   ```

3. 색상 검증
   ```bash
   python verify_all_colors.py
   ```

### 참고 문서
- [색상 작업 완료 보고서](../../COLOR_FIX_SUMMARY.md)
- [색상 검증 상세 보고서](../../COLOR_VERIFICATION_REPORT_20251022.md)

---

**버전**: v4.0.0
**최종 업데이트**: 2025-10-22
