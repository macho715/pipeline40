#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
import json
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

json_path = Path("data/anomaly/HVDC_anomaly_report.json")
with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

print(f"Total: {len(data)}")
print(f"\nSample anomalies (first 10):")
for i, a in enumerate(data[:10]):
    atype = a.get('Anomaly_Type', 'N/A')
    sev = a.get('Severity', 'N/A')
    case_id = a.get('Case_ID', 'N/A')
    print(f"{i+1}. Case: {case_id}")
    print(f"   Type: [{atype}] (len={len(str(atype))})")
    print(f"   Severity: [{sev}] (len={len(str(sev))})")
    print(f"   Type repr: {repr(atype)}")
    print()

