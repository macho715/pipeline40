#!/usr/bin/env python3
"""
간단한 이상치 탐지 실행 스크립트
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from anomaly_detector import main

if __name__ == "__main__":
    # 기본 설정으로 실행
    sys.argv = [
        "anomaly_detector.py",
        "--input",
        "../pipe1/HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "--excel-out",
        "hvdc_anomaly_report_v2.xlsx",
        "--json-out",
        "hvdc_anomaly_report_v2.json",
        "--visualize",
    ]

    main()
