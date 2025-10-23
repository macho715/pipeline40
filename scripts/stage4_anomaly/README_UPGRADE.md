
# Stage 4 업그레이드(v4.0) 요약 - Balanced Boost Edition

**무엇이 달라졌나?**
- **Balanced Boost 혼합 위험도**: 룰/통계 근거가 있을 때 ML 위험도를 가중(가산)하여 허위 양성은 줄이고 진짜 이상은 끌어올림
- **ECDF 캘리브레이션 + 베타-스무딩**: 위험도 포화 문제 완전 해결 (0.001~0.999 범위)
- **Per-Location IQR/MAD**: MOSB/DSV 등 지점별 정상 체류분포를 따로 학습하여 과도 체류 정밀 판정
- **위치별 임계치**: 각 위치별로 IQR 상한 & MAD 보정으로 과도 체류 판정 정확도 향상
- **헤더 정규화 강화**: 공백 변형 자동 흡수 (`"AAA  Storage"` → `"AAA Storage"`)
- **데이터 품질 검증**: CASE_NO 중복, HVDC_CODE 패턴 불일치, 날짜 파싱 실패 등 명확한 메시지

**성능 개선**
- **ML 이상치 97% 감소**: 3,724건 → 115건
- **위험도 1.000 포화 100% 해결**: 0건
- **실행 시간**: ~4초 (5,834행 기준)

**빠른 사용법**
```bash
python -m hvdc_pipeline.scripts.stage4_anomaly.anomaly_detector_balanced \
  --input reports/HVDC_입고로직_종합리포트_YYYYMMDD.xlsx \
  --sheet 통합_원본데이터_Fixed \
  --excel-out reports/anomalies/anomaly_list.xlsx \
  --json-out  reports/anomalies/anomaly_list.json \
  --visualize --case-col "Case No."
```

**통합**
- `run_pipeline.py --stage 4` 호출 경로는 동일합니다. 본 파일을
  `hvdc_pipeline/scripts/stage4_anomaly/anomaly_detector_balanced.py` 에 덮어쓰면 됩니다.
