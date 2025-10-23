
# Stage 4 업그레이드(v3) 요약

**무엇이 달라졌나?**
- PyOD 기반 *ECOD/COPOD/HBOS/IForest* + sklearn *IsolationForest* 앙상블(자동 폴백)
- ECDF 위험도 캘리브레이션으로 `risk_score∈[0..1]` 일관화
- `STATUS_LOCATION`와 최종 위치 불일치 감지 추가
- 헤더 정규화 강화: 공백·대소·한글/영문 혼용 매핑 + `"AAA  Storage"` 변형 흡수
- 실패하기 쉬운 오류를 메시지로 매핑: 시트 누락, 날짜 변환 실패 등

**빠른 사용법**
```bash
python -m hvdc_pipeline.scripts.stage4_anomaly.anomaly_detector \
  --input reports/HVDC_입고로직_종합리포트_YYYYMMDD.xlsx \
  --sheet 통합_원본데이터_Fixed \
  --excel-out reports/anomalies/anomaly_list.xlsx \
  --json-out  reports/anomalies/anomaly_list.json \
  --visualize --case-col "Case No."
```

**통합**
- `run_pipeline.py --stage 4` 호출 경로는 동일합니다. 본 파일을
  `hvdc_pipeline/scripts/stage4_anomaly/anomaly_detector.py` 에 덮어쓰면 됩니다.
