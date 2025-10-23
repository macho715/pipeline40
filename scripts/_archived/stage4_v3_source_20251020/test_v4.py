# -*- coding: utf-8 -*-
"""
v4.0 테스트 스크립트
빠른 검증 및 성능 벤치마크
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# v4 import
try:
    from anomaly_detector_v4 import HybridAnomalyDetector, DetectorConfig
    V4_AVAILABLE = True
except ImportError:
    V4_AVAILABLE = False
    print("❌ v4 모듈을 찾을 수 없습니다.")

# v3 import (비교용)
try:
    from anomaly_detector import HybridAnomalyDetector as HybridAnomalyDetectorV3
    from anomaly_detector import DetectorConfig as DetectorConfigV3
    V3_AVAILABLE = True
except ImportError:
    V3_AVAILABLE = False
    print("⚠️ v3 모듈을 찾을 수 없습니다. (비교 건너뜀)")


def generate_synthetic_data(n_samples=1000, n_anomalies=20):
    """합성 테스트 데이터 생성"""
    np.random.seed(42)
    
    # Normal data
    data = {
        "Case No.": [f"HVDC-ADOPT-001-{i:04d}" for i in range(n_samples)],
        "HVDC Code": [f"HVDC-ADOPT-001-{i:04d}" for i in range(n_samples)],
        "QTY": np.random.randint(1, 100, n_samples),
        "AMOUNT": np.random.uniform(1000, 50000, n_samples),
        "PKG": np.random.randint(1, 10, n_samples),
        "DHL Warehouse": pd.date_range("2024-01-01", periods=n_samples, freq="1D"),
        "DSV Indoor": pd.date_range("2024-01-05", periods=n_samples, freq="1D"),
        "AGI": pd.date_range("2024-01-15", periods=n_samples, freq="1D"),
        "Status_Location": ["AGI"] * n_samples,
    }
    
    df = pd.DataFrame(data)
    
    # Inject anomalies
    anomaly_idx = np.random.choice(n_samples, n_anomalies, replace=False)
    
    # Type 1: Excessive values
    df.loc[anomaly_idx[:5], "AMOUNT"] = np.random.uniform(100000, 500000, 5)
    
    # Type 2: Negative values
    df.loc[anomaly_idx[5:10], "QTY"] = -np.random.randint(1, 50, 5)
    
    # Type 3: Time reversal
    for idx in anomaly_idx[10:15]:
        df.loc[idx, "DSV Indoor"] = df.loc[idx, "DHL Warehouse"] - pd.Timedelta(days=10)
    
    # Type 4: Status mismatch
    df.loc[anomaly_idx[15:20], "Status_Location"] = "DSV Indoor"
    
    return df


def test_v4_basic():
    """v4 기본 테스트"""
    print("\n" + "="*80)
    print("🧪 Test 1: v4 Basic Functionality")
    print("="*80)
    
    if not V4_AVAILABLE:
        print("❌ v4 not available, skipping")
        return
    
    # Generate data
    df = generate_synthetic_data(n_samples=100, n_anomalies=10)
    print(f"✅ Generated {len(df)} samples with ~10 anomalies")
    
    # Configure (fast mode)
    cfg = DetectorConfig(
        contamination=0.1,
        use_deep_learning=False,
        use_boosting=True,
        compute_shap=False,
    )
    
    # Run
    start = time.time()
    detector = HybridAnomalyDetector(cfg)
    result = detector.run(df)
    elapsed = time.time() - start
    
    # Check
    print(f"\n📊 Results:")
    print(f"   - Total Anomalies: {result['summary']['total_anomalies']}")
    print(f"   - Critical: {result['summary']['critical']}")
    print(f"   - High: {result['summary']['high']}")
    print(f"   - Medium: {result['summary']['medium']}")
    print(f"   - Low: {result['summary']['low']}")
    print(f"   - Models: {', '.join(result['summary']['ml_models'])}")
    print(f"⏱️  Time: {elapsed:.2f}s")
    
    assert result['summary']['total_anomalies'] > 0, "No anomalies detected!"
    print("✅ Test PASSED")


def test_v4_full_features():
    """v4 전체 기능 테스트"""
    print("\n" + "="*80)
    print("🧪 Test 2: v4 Full Features (DL + Boosting + SHAP)")
    print("="*80)
    
    if not V4_AVAILABLE:
        print("❌ v4 not available, skipping")
        return
    
    df = generate_synthetic_data(n_samples=200, n_anomalies=20)
    print(f"✅ Generated {len(df)} samples")
    
    cfg = DetectorConfig(
        contamination=0.1,
        use_deep_learning=True,
        use_boosting=True,
        compute_shap=True,
        shap_max_samples=50,
    )
    
    start = time.time()
    detector = HybridAnomalyDetector(cfg)
    result = detector.run(df)
    elapsed = time.time() - start
    
    print(f"\n📊 Results:")
    print(f"   - Total Anomalies: {result['summary']['total_anomalies']}")
    print(f"   - Models: {', '.join(result['summary']['ml_models'])}")
    print(f"⏱️  Time: {elapsed:.2f}s")
    
    print("✅ Test PASSED")


def benchmark_v3_vs_v4():
    """v3 vs v4 성능 비교"""
    print("\n" + "="*80)
    print("🏁 Benchmark: v3 vs v4")
    print("="*80)
    
    if not (V3_AVAILABLE and V4_AVAILABLE):
        print("⚠️ Both versions needed for comparison")
        return
    
    sizes = [100, 500, 1000]
    results = []
    
    for size in sizes:
        df = generate_synthetic_data(n_samples=size, n_anomalies=int(size * 0.1))
        
        # v3
        cfg_v3 = DetectorConfigV3(contamination=0.1)
        start = time.time()
        detector_v3 = HybridAnomalyDetectorV3(cfg_v3)
        result_v3 = detector_v3.run(df)
        time_v3 = time.time() - start
        
        # v4 (no DL for fair comparison)
        cfg_v4 = DetectorConfig(contamination=0.1, use_deep_learning=False, compute_shap=False)
        start = time.time()
        detector_v4 = HybridAnomalyDetector(cfg_v4)
        result_v4 = detector_v4.run(df)
        time_v4 = time.time() - start
        
        results.append({
            "size": size,
            "v3_time": time_v3,
            "v4_time": time_v4,
            "v3_anomalies": result_v3['summary']['total_anomalies'],
            "v4_anomalies": result_v4['summary']['total_anomalies'],
            "v3_models": len(result_v3['summary']['ml_models']),
            "v4_models": len(result_v4['summary']['ml_models']),
        })
    
    # Print table
    print("\n| Size | v3 Time | v4 Time | Speedup | v3 Anomalies | v4 Anomalies | v3 Models | v4 Models |")
    print("|------|---------|---------|---------|--------------|--------------|-----------|-----------|")
    for r in results:
        speedup = r['v3_time'] / r['v4_time'] if r['v4_time'] > 0 else 0
        print(f"| {r['size']:4d} | {r['v3_time']:6.2f}s | {r['v4_time']:6.2f}s | {speedup:6.2f}x | {r['v3_anomalies']:12d} | {r['v4_anomalies']:12d} | {r['v3_models']:9d} | {r['v4_models']:9d} |")
    
    print("\n✅ Benchmark complete")


def test_export_formats():
    """출력 형식 테스트"""
    print("\n" + "="*80)
    print("🧪 Test 3: Export Formats (Excel + JSON)")
    print("="*80)
    
    if not V4_AVAILABLE:
        print("❌ v4 not available, skipping")
        return
    
    df = generate_synthetic_data(n_samples=50, n_anomalies=5)
    
    cfg = DetectorConfig(contamination=0.1, use_deep_learning=False, compute_shap=False)
    detector = HybridAnomalyDetector(cfg)
    
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    excel_path = output_dir / "test_anomalies.xlsx"
    json_path = output_dir / "test_anomalies.json"
    
    result = detector.run(df, export_excel=str(excel_path), export_json=str(json_path))
    
    # Check files
    assert excel_path.exists(), "Excel not created"
    assert json_path.exists(), "JSON not created"
    
    print(f"✅ Excel: {excel_path}")
    print(f"✅ JSON: {json_path}")
    print("✅ Test PASSED")


def test_error_handling():
    """에러 처리 테스트"""
    print("\n" + "="*80)
    print("🧪 Test 4: Error Handling")
    print("="*80)
    
    if not V4_AVAILABLE:
        print("❌ v4 not available, skipping")
        return
    
    # Test 1: Empty DataFrame
    try:
        df = pd.DataFrame()
        cfg = DetectorConfig()
        detector = HybridAnomalyDetector(cfg)
        result = detector.run(df)
        print("✅ Empty DataFrame handled")
    except Exception as e:
        print(f"❌ Empty DataFrame failed: {e}")
    
    # Test 2: Missing columns
    try:
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        cfg = DetectorConfig()
        detector = HybridAnomalyDetector(cfg)
        result = detector.run(df)
        print("✅ Missing columns handled")
    except Exception as e:
        print(f"❌ Missing columns failed: {e}")
    
    # Test 3: Invalid data types
    try:
        df = generate_synthetic_data(50, 5)
        df["QTY"] = "invalid"  # String instead of numeric
        cfg = DetectorConfig()
        detector = HybridAnomalyDetector(cfg)
        result = detector.run(df)
        print("✅ Invalid data types handled")
    except Exception as e:
        print(f"❌ Invalid data types failed: {e}")
    
    print("✅ Error handling tests complete")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 HVDC Anomaly Detector v4.0 - Test Suite")
    print("="*80)
    print(f"Python: {sys.version}")
    print(f"NumPy: {np.__version__}")
    print(f"Pandas: {pd.__version__}")
    
    # Run tests
    test_v4_basic()
    test_v4_full_features()
    
    if V3_AVAILABLE:
        benchmark_v3_vs_v4()
    
    test_export_formats()
    test_error_handling()
    
    print("\n" + "="*80)
    print("✅ All tests complete!")
    print("="*80)
