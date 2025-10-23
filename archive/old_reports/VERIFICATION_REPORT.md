# 파이프라인 실행 결과 검증 보고서

**생성 시간**: 2025-10-19 22:51:52
**검증 대상**: HVDC Invoice Audit Pipeline v2.9.4

## 📋 요약

이 보고서는 HVDC Invoice Audit Pipeline의 전체 실행 결과를 검증한 내용을 담고 있습니다.

## 📁 파일 존재 확인

| 파일 경로 | 상태 |
|-----------|------|
| `data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_v2.9.4.xlsx` | ✅ 존재 |
| `data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_colored.xlsx` | ✅ 존재 |
| `data/processed/synced/HVDC WAREHOUSE_HITACHI(HE).synced_for_stage2.xlsx` | ✅ 존재 |
| `data/processed/derived/HVDC WAREHOUSE_HITACHI(HE).derived_v2.9.4.xlsx` | ❌ 없음 |
| `data/processed/reports/HVDC_입고로직_종합리포트_20251019_221002_v3.0-corrected.xlsx` | ✅ 존재 |
| `data/anomaly/HVDC_anomaly_report.xlsx` | ✅ 존재 |

## 🔍 상세 검증 결과

### Verify Master No Sorting

❌ **검증 실패**

### Verify Colors Applied

✅ **검증 성공**

### Verify Derived Columns

✅ **검증 성공**

## 📊 전체 평가

⚠️ **일부 검증 실패**

- 일부 검증 스크립트에서 문제가 발견되었습니다
- 일부 예상 출력 파일이 생성되지 않았습니다

## 💡 권장사항

1. **문제 해결**: 실패한 검증 항목의 원인 분석 및 수정
2. **재실행**: 수정 후 파이프라인 재실행
3. **검증**: 재실행 후 다시 검증 수행
