#!/usr/bin/env python3
import json

# JSON 데이터 로드
with open("hvdc_anomaly_report_new.json", "r", encoding="utf-8") as f:
    anomaly_data = json.load(f)

print("=== Anomaly Types (first 10) ===")
for i, item in enumerate(anomaly_data[:10]):
    anomaly_type = item.get("Anomaly_Type", "")
    severity = item.get("Severity", "")
    print(f'{i+1}: Type="{anomaly_type}", Severity="{severity}"')

print(f"\n=== Unique Anomaly Types ===")
types = set(item.get("Anomaly_Type", "") for item in anomaly_data)
for t in sorted(types):
    print(f'  "{t}"')

print(f"\n=== Unique Severity Levels ===")
severities = set(item.get("Severity", "") for item in anomaly_data)
for s in sorted(severities):
    print(f'  "{s}"')
