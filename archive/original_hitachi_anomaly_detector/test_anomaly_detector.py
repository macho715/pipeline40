# -*- coding: utf-8 -*-
"""
HVDC Anomaly Detector v2 - Test Suite
pytest 기반 단위 테스트
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from anomaly_detector import (
    AnomalyType,
    AnomalySeverity,
    AnomalyRecord,
    DetectorConfig,
    HeaderNormalizer,
    DataQualityValidator,
    FeatureBuilder,
    RuleDetector,
    StatDetector,
    MLDetector,
    ECDFCalibrator,
    AlertManager,
    HybridAnomalyDetector,
    SKLEARN_AVAILABLE,
    PYOD_AVAILABLE,
    OPENPYXL_AVAILABLE,
)


# Test data fixtures
@pytest.fixture
def sample_data():
    """테스트용 샘플 데이터"""
    return pd.DataFrame(
        {
            "Case No.": ["CASE-001", "CASE-002", "CASE-003", "CASE-004"],
            "HVDC CODE": [
                "HVDC-ADOPT-001-2024",
                "HVDC-ADOPT-002-2024",
                "HVDC-ADOPT-003-2024",
                "HVDC-ADOPT-004-2024",
            ],
            "DSV Indoor": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
            ),
            "DSV Al Markaz": pd.to_datetime(
                ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
            ),
            "AGI": pd.to_datetime(
                ["2024-01-05", "2024-01-06", "2024-01-07", "2024-01-08"]
            ),
            "AMOUNT": [1000.0, 2000.0, 3000.0, 4000.0],
            "QTY": [10, 20, 30, 40],
            "PKG": [1, 2, 3, 4],
        }
    )


@pytest.fixture
def config():
    """기본 설정"""
    return DetectorConfig()


class TestHeaderNormalizer:
    """헤더 정규화 테스트"""

    def test_header_normalization(self, config):
        """헤더 정규화 기능 테스트"""
        normalizer = HeaderNormalizer(config.column_map)

        # 다양한 헤더 형태
        df = pd.DataFrame(
            {
                "Case No.": [1, 2, 3],
                "CASE NO": [1, 2, 3],
                "case_no": [1, 2, 3],
                "DSV Indoor": [1, 2, 3],
                "DSV Al Markaz": [1, 2, 3],
                "Unknown Column": [1, 2, 3],
            }
        )

        normalized = normalizer.normalize(df)

        # 정규화된 컬럼명 확인
        expected_cols = [
            "CASE_NO",
            "CASE_NO",
            "CASE_NO",
            "DSV_INDOOR",
            "DSV_AL_MARKAZ",
            "UNKNOWN_COLUMN",
        ]
        assert list(normalized.columns) == expected_cols


class TestDataQualityValidator:
    """데이터 품질 검증 테스트"""

    def test_data_quality_validator(self, config):
        """데이터 품질 검증 기능 테스트"""
        validator = DataQualityValidator()

        # 정상 데이터
        good_df = pd.DataFrame(
            {
                "CASE_NO": ["CASE-001", "CASE-002", "CASE-003"],
                "HVDC_CODE": [
                    "HVDC-ADOPT-001-2024",
                    "HVDC-ADOPT-002-2024",
                    "HVDC-ADOPT-003-2024",
                ],
                "AMOUNT": [1000.0, 2000.0, 3000.0],
            }
        )

        issues = validator.validate(good_df)
        assert len(issues) == 0

        # 문제가 있는 데이터
        bad_df = pd.DataFrame(
            {
                "CASE_NO": ["CASE-001", "CASE-001", "CASE-003"],  # 중복
                "HVDC_CODE": [
                    "INVALID-CODE",
                    "HVDC-ADOPT-002-2024",
                    "HVDC-ADOPT-003-2024",
                ],  # 잘못된 형식
                "AMOUNT": ["invalid", 2000.0, 3000.0],  # 비숫자 값
            }
        )

        issues = validator.validate(bad_df)
        assert len(issues) > 0
        assert any("CASE_NO 중복" in issue for issue in issues)
        assert any("HVDC_CODE 형식 오류" in issue for issue in issues)
        assert any("AMOUNT 비숫자 값" in issue for issue in issues)


class TestFeatureBuilder:
    """피처 빌더 테스트"""

    def test_feature_builder_dwell(self, config, sample_data):
        """체류 기간(dwell time) 계산 검증"""
        fb = FeatureBuilder(config)
        normalized_data = HeaderNormalizer(config.column_map).normalize(sample_data)

        features, dwell_list = fb.build(normalized_data)

        # 피처 데이터프레임 구조 확인
        assert "TOUCH_COUNT" in features.columns
        assert "TOTAL_DAYS" in features.columns
        assert "AMOUNT" in features.columns
        assert "QTY" in features.columns
        assert "PKG" in features.columns

        # dwell_list 구조 확인
        assert len(dwell_list) > 0
        for case_id, location, dwell_days in dwell_list:
            assert isinstance(case_id, str)
            assert isinstance(location, str)
            assert isinstance(dwell_days, int)
            assert dwell_days >= 0


class TestRuleDetector:
    """규칙 기반 탐지 테스트"""

    def test_rule_time_reversal(self, config):
        """시간 역전 탐지 검증"""
        detector = RuleDetector(config)

        # 정상 순서 (설정된 컬럼 순서에 맞춤)
        normal_row = pd.Series(
            {
                "CASE_NO": "CASE-001",
                "DSV_AL_MARKAZ": pd.to_datetime("2024-01-01"),  # 설정 순서에 맞춤
                "DSV_INDOOR": pd.to_datetime("2024-01-02"),
                "AGI": pd.to_datetime("2024-01-03"),
            }
        )

        result = detector.time_reversal(normal_row)
        assert result is None

        # 시간 역전 (DSV Indoor가 DSV Al Markaz보다 이전)
        reversed_row = pd.Series(
            {
                "CASE_NO": "CASE-002",
                "DSV_AL_MARKAZ": pd.to_datetime("2024-01-02"),
                "DSV_INDOOR": pd.to_datetime("2024-01-01"),  # 시간 역전
                "AGI": pd.to_datetime("2024-01-03"),
            }
        )

        result = detector.time_reversal(reversed_row)
        assert result is not None
        assert result.anomaly_type == AnomalyType.TIME_REVERSAL
        assert result.severity == AnomalySeverity.HIGH


class TestStatDetector:
    """통계 기반 탐지 테스트"""

    def test_iqr_outliers(self):
        """IQR 기반 이상치 탐지 테스트"""
        detector = StatDetector(iqr_k=1.5)

        # 정상 dwell 데이터
        normal_dwell = [
            ("CASE-001", "DSV_INDOOR", 1),
            ("CASE-002", "DSV_INDOOR", 2),
            ("CASE-003", "DSV_INDOOR", 3),
            ("CASE-004", "DSV_INDOOR", 4),
            ("CASE-005", "DSV_INDOOR", 5),
        ]

        anomalies = detector.iqr_outliers(normal_dwell)
        assert len(anomalies) == 0

        # 이상치 포함 dwell 데이터
        outlier_dwell = normal_dwell + [
            ("CASE-006", "DSV_INDOOR", 50),  # 명백한 이상치
            ("CASE-007", "DSV_INDOOR", 100),  # 더 큰 이상치
        ]

        anomalies = detector.iqr_outliers(outlier_dwell)
        assert len(anomalies) > 0
        assert all(a.anomaly_type == AnomalyType.EXCESSIVE_DWELL for a in anomalies)


class TestECDFCalibrator:
    """ECDF 캘리브레이션 테스트"""

    def test_ecdf_calibrator(self):
        """원점수 → [0..1] 위험도 변환 검증"""
        calibrator = ECDFCalibrator()

        # 테스트 점수 (작을수록 이상치)
        raw_scores = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        calibrator.fit(raw_scores)

        # 변환 테스트
        test_scores = np.array([0.05, 0.5, 0.95])
        risk_scores = calibrator.transform(test_scores)

        # 위험도는 [0, 1] 범위 내
        assert all(0 <= r <= 1 for r in risk_scores)

        # 작은 점수일수록 높은 위험도
        assert risk_scores[0] > risk_scores[1] > risk_scores[2]


@pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="sklearn missing")
class TestMLDetector:
    """머신러닝 탐지 테스트"""

    def test_ml_layer_flags_outliers(self):
        """Isolation Forest 이상치 탐지 검증"""
        detector = MLDetector(contamination=0.2, random_state=42)  # contamination 증가

        # 정상 데이터 (더 많은 샘플)
        normal_data = pd.DataFrame(
            {
                "TOUCH_COUNT": [3, 4, 3, 4, 5, 3, 4, 3, 4, 5],
                "TOTAL_DAYS": [10, 12, 11, 13, 14, 10, 12, 11, 13, 14],
                "AMOUNT": [1000, 1200, 1100, 1300, 1400, 1000, 1200, 1100, 1300, 1400],
                "QTY": [10, 12, 11, 13, 14, 10, 12, 11, 13, 14],
                "PKG": [1, 1, 1, 2, 2, 1, 1, 1, 2, 2],
            }
        )

        # 명백한 이상치 데이터 추가 (더 극단적인 값)
        outlier_data = normal_data.copy()
        outlier_data.loc[10] = [1, 1000, 100000, 1, 1]  # 매우 극단적인 이상치
        outlier_data.loc[11] = [10, 1, 1, 100, 100]  # 또 다른 극단적 이상치

        y_pred, risk_scores = detector.fit_predict(outlier_data)

        # 예측 결과 검증
        assert len(y_pred) == len(outlier_data)
        assert len(risk_scores) == len(outlier_data)
        assert all(0 <= r <= 1 for r in risk_scores)

        # 이상치로 분류된 케이스가 있는지 확인
        # contamination=0.2이므로 12개 중 최소 2개는 이상치로 분류되어야 함
        assert sum(y_pred) >= 2


class TestAlertManager:
    """알림 관리자 테스트"""

    def test_alert_threshold(self):
        """30초 알림 임계값 테스트"""
        manager = AlertManager(window_sec=1, min_risk=0.8)  # 테스트를 위해 1초로 설정

        # 낮은 위험도
        assert not manager.on_anomaly(0.5)

        # 높은 위험도 (첫 번째)
        assert not manager.on_anomaly(0.9)  # 첫 번째는 알림 안 함

        # 시간 경과 후 다시 높은 위험도
        import time

        time.sleep(1.1)  # 1초 대기
        assert manager.on_anomaly(0.9)  # 이제 알림 발생


class TestHybridAnomalyDetector:
    """통합 이상치 탐지기 테스트"""

    def test_full_pipeline(self, config, sample_data):
        """전체 파이프라인 테스트"""
        detector = HybridAnomalyDetector(config)

        # 시간 역전 케이스 추가
        anomaly_data = sample_data.copy()
        anomaly_data.loc[4] = {
            "Case No.": "CASE-005",
            "HVDC CODE": "HVDC-ADOPT-005-2024",
            "DSV Indoor": pd.to_datetime("2024-01-03"),
            "DSV Al Markaz": pd.to_datetime("2024-01-01"),  # 시간 역전
            "AGI": pd.to_datetime("2024-01-05"),
            "AMOUNT": 5000.0,
            "QTY": 50,
            "PKG": 5,
        }

        result = detector.run(anomaly_data)

        # 결과 구조 검증
        assert "summary" in result
        assert "anomalies" in result
        assert "features" in result

        # 요약 정보 검증
        summary = result["summary"]
        assert "total" in summary
        assert "by_type" in summary
        assert "by_severity" in summary

        # 이상치 발견 확인
        assert summary["total"] > 0
        assert len(result["anomalies"]) > 0

        # 시간 역전 이상치 확인
        time_reversal_anomalies = [
            a
            for a in result["anomalies"]
            if a.anomaly_type == AnomalyType.TIME_REVERSAL
        ]
        assert len(time_reversal_anomalies) > 0


class TestAnomalyRecord:
    """이상치 레코드 테스트"""

    def test_anomaly_record_creation(self):
        """이상치 레코드 생성 및 변환 테스트"""
        record = AnomalyRecord(
            case_id="CASE-001",
            anomaly_type=AnomalyType.TIME_REVERSAL,
            severity=AnomalySeverity.HIGH,
            description="시간 역전 발생",
            detected_value=1.5,
            expected_range=(0.0, 1.0),
            location="DSV_INDOOR",
            timestamp=datetime.now(),
            risk_score=0.95,
        )

        # 딕셔너리 변환 테스트
        record_dict = record.to_dict()

        assert record_dict["Case_ID"] == "CASE-001"
        assert record_dict["Anomaly_Type"] == "시간 역전"
        assert record_dict["Severity"] == "높음"
        assert record_dict["Risk_Score"] == 0.95


# Integration tests
class TestIntegration:
    """통합 테스트"""

    def test_config_defaults(self):
        """기본 설정값 테스트"""
        config = DetectorConfig()

        assert config.batch_size == 1000
        assert config.max_workers == 8
        assert config.alert_window_sec == 30
        assert config.min_risk_to_alert == 0.8
        assert "CASE_NO" in config.column_map.values()
        assert "DSV_INDOOR" in config.warehouse_columns
        assert "AGI" in config.site_columns

    def test_optional_dependencies(self):
        """선택적 의존성 확인"""
        # 이 테스트는 환경에 따라 결과가 다를 수 있음
        assert isinstance(SKLEARN_AVAILABLE, bool)
        assert isinstance(PYOD_AVAILABLE, bool)
        assert isinstance(OPENPYXL_AVAILABLE, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
