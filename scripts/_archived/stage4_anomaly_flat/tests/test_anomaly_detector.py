
# -*- coding: utf-8 -*-
import pandas as pd
from hvdc_pipeline.scripts.stage4_anomaly.anomaly_detector import (
    DetectorConfig, HybridAnomalyDetector, DEFAULT_STAGE3_SHEET
)

def _toy_df():
    return pd.DataFrame([
        {"Case No.":"C1","DSV Indoor":"2025-07-01","DSV Al Markaz":"2025-07-05","AGI":"2025-07-10","Pkg":1,"금액":100,"수량":1},
        {"Case No.":"C2","DSV Indoor":"2025-06-01","AGI":"2025-06-01","Pkg":1,"금액":100,"수량":1},  # same day → no dwell, ok
        {"Case No.":"C3","DSV Al Markaz":"2025-05-01","DSV Indoor":"2025-04-25","AGI":"2025-05-10","Pkg":1,"금액":50,"수량":1},  # reversal
    ])

def test_defaults():
    assert DEFAULT_STAGE3_SHEET == "통합_원본데이터_Fixed"

def test_run_and_summary():
    det = HybridAnomalyDetector(DetectorConfig(contamination=0.34))
    df = _toy_df()
    out = det.run(df)
    assert "anomalies" in out and "summary" in out
    assert out["summary"]["total"] == len(df)
    # at least one anomaly due to reversal
    assert any(a["anomaly_type"] == "시간 역전" for a in out["anomalies"])
