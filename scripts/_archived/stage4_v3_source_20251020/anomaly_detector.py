
# -*- coding: utf-8 -*-
"""
HVDC 입출고 이상치 탐지 v3 (Hybrid / Ensemble + Safer)
- Rule + Statistical + ML(PyOD Ensemble/Sklearn) 3-Layer 업그레이드
- ECOD/COPOD/HBOS/IsolationForest 앙상블 + ECDF 위험도 캘리브레이션
- 헤더 정규화 강화(공백 변이, "AAA  Storage" → "AAA Storage"), 기본 시트 자동
- Excel/JSON 리포트(선택), 경고 범주 & 치유 가이드 포함
- 실패하기 쉬운 에러를 사용자 메시지에 매핑(시트/컬럼 누락, 타입/날짜 파싱 실패 등)

설치(선택):
    pip install pyod>=2.0.5 scikit-learn pandas openpyxl xlsxwriter

주의: PyOD 미설치 환경에서도 sklearn IsolationForest로 자동 폴백합니다.
"""
from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# PyOD optional
try:
    from pyod.models.ecod import ECOD          # parameter-free
    from pyod.models.copod import COPOD        # parameter-free
    from pyod.models.hbos import HBOS          # fast histogram
    from pyod.models.iforest import IForest    # pyod version
    PYOD_AVAILABLE = True
except Exception:  # pragma: no cover
    PYOD_AVAILABLE = False

# sklearn fallback
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import RobustScaler
except Exception:  # pragma: no cover
    RobustScaler = None
    IsolationForest = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# -------- constants -----------------------------------------------------------
DEFAULT_STAGE3_SHEET = "통합_원본데이터_Fixed"

WAREHOUSE_COLS = [
    "DHL Warehouse","DSV Indoor","DSV Al Markaz","AAA Storage","DSV Outdoor",
    "DSV MZP","MOSB","Hauler Indoor","JDN MZD","HAULER"
]
SITE_COLS = ["AGI","DAS","MIR","SHU"]

SAFE_NUMERIC_COLS = ["AMOUNT","QTY","PKG","TOUCH_COUNT","TOTAL_DAYS"]

# -------- schema --------------------------------------------------------------
class AnomalyType(Enum):
    TIME_REVERSAL = "시간 역전"
    EXCESSIVE_DWELL = "과도 체류"
    ML_OUTLIER = "머신러닝 이상치"
    DATA_QUALITY = "데이터 품질"
    STATUS_MISMATCH = "최종위치 불일치"

class AnomalySeverity(Enum):
    CRITICAL = "치명적"
    HIGH = "높음"
    MEDIUM = "보통"
    LOW = "낮음"

@dataclass
class AnomalyRecord:
    case_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    detected_value: Optional[float] = None
    expected_range: Optional[str] = None
    location: Optional[str] = None
    timestamp: datetime = datetime.now()
    risk_score: Optional[float] = None

# -------- config --------------------------------------------------------------
@dataclass
class DetectorConfig:
    # 통계값
    iqr_k: float = 1.5
    mad_k: float = 3.5
    # ML
    contamination: float = 0.02
    random_state: int = 42
    use_pyod_first: bool = True
    # 알림
    alert_window_sec: int = 30
    min_risk_to_alert: float = 0.8
    # 컬럼 매핑(헤더 정규화에 사용)
    column_map: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.column_map is None:
            self.column_map = {
                # 키/코드
                "Case No.":"CASE_NO","CASE NO":"CASE_NO","CASE_NO":"CASE_NO",
                "HVDC CODE":"HVDC_CODE","HVDC Code":"HVDC_CODE",
                # 창고/현장(공백·대소 변형 흡수)
                "DHL Warehouse":"DHL_WAREHOUSE",
                "DSV Indoor":"DSV_INDOOR",
                "DSV Al Markaz":"DSV_AL_MARKAZ",
                "AAA Storage":"AAA_STORAGE",
                "AAA  Storage":"AAA_STORAGE",  # double-space 변형
                "DSV Outdoor":"DSV_OUTDOOR",
                "DSV MZP":"DSV_MZP",
                "MOSB":"MOSB",
                "Hauler Indoor":"HAULER_INDOOR",
                "HAULER":"HAULER",
                "JDN MZD":"JDN_MZD",
                "AGI":"AGI","DAS":"DAS","MIR":"MIR","SHU":"SHU",
                # 수량/금액
                "금액":"AMOUNT","수량":"QTY","Pkg":"PKG","PKG":"PKG","pkg":"PKG",
                # 상태
                "Status_Location":"STATUS_LOCATION",
            }

# -------- helpers -------------------------------------------------------------
class HeaderNormalizer:
    def __init__(self, col_map: Dict[str,str]):
        # 소문자 key로 매핑
        self.map = {str(k).strip().lower(): v for k,v in col_map.items()}
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        new_cols = []
        for c in df.columns:
            key = str(c).strip().lower().replace("\xa0"," ")
            key = " ".join(key.split())  # collapse multiple spaces
            new_cols.append(self.map.get(key, str(c).strip().upper().replace(" ","_")))
        out = df.copy()
        out.columns = new_cols
        return out

class DataQualityValidator:
    """경량 정합성 점검 (GX 도입 전 프런트라인)
    - CASE_NO 중복, QTY/AMOUNT 음수, 날짜 파싱 실패, 명시적 NaN율 경고
    - STATUS_LOCATION과 마지막 도착 컬럼 불일치 탐지(요약만)
    """
    HVDC_PATTERN = r"^HVDC-ADOPT-\d{3}-\d{4}$"

    def validate(self, df: pd.DataFrame) -> List[str]:
        issues: List[str] = []
        if "CASE_NO" not in df.columns:
            issues.append("필수 필드 누락: CASE_NO")
        else:
            dup = df["CASE_NO"].astype(str).duplicated().sum()
            if dup:
                issues.append(f"CASE_NO 중복 {dup}건")

        if "HVDC_CODE" in df.columns:
            bad = ~df["HVDC_CODE"].astype(str).str.match(self.HVDC_PATTERN, na=False)
            n_bad = int(bad.sum())
            if n_bad:
                issues.append(f"HVDC_CODE 패턴 불일치 {n_bad}건")

        # 수량/금액 음수
        for col in ("QTY","AMOUNT","PKG"):
            if col in df.columns:
                neg = (pd.to_numeric(df[col], errors="coerce") < 0).sum()
                if neg:
                    issues.append(f"{col} 음수 {int(neg)}건")

        # 날짜 컬럼 파싱 실패
        date_cols = [c for c in WAREHOUSE_COLS + SITE_COLS if c in df.columns]
        for col in date_cols:
            coerced = pd.to_datetime(df[col], errors="coerce")
            fail = coerced.isna() & df[col].notna()
            if int(fail.sum()):
                issues.append(f"{col}: 날짜 변환 실패 {int(fail.sum())}건")

        # 결측률 경고 (핵심 수치)
        for col in ("AMOUNT","QTY","PKG"):
            if col in df.columns:
                r = df[col].isna().mean()
                if r > 0.5:
                    issues.append(f"{col} 결측률 높음({r:.0%})")

        return issues

# -------- feature engineering -------------------------------------------------
class FeatureBuilder:
    def __init__(self, cfg: DetectorConfig):
        self.cfg = cfg

    def build(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Tuple[str,str,int]], pd.Series]:
        """행 단위 스칼라 피처 + 체류 목록 + 마지막 위치"""
        rows = []
        dwell_list: List[Tuple[str,str,int]] = []
        last_loc = pd.Series(index=df.index, dtype="object")

        for i, row in df.iterrows():
            case_id = str(row.get("CASE_NO","NA"))
            points: List[Tuple[str,pd.Timestamp]] = []
            for col in WAREHOUSE_COLS + SITE_COLS:
                if col in row.index and pd.notna(row[col]):
                    dt = pd.to_datetime(row[col], errors="coerce")
                    if pd.notna(dt):
                        points.append((col, dt))

            points.sort(key=lambda x: x[1])
            if points:
                last_loc.at[i] = points[-1][0]

            if len(points) >= 2:
                for (loc_a,t_a),(loc_b,t_b) in zip(points[:-1], points[1:]):
                    dwell = max(0, (t_b - t_a).days)
                    dwell_list.append((case_id, loc_a, dwell))

            n_touch = len(points)
            total_days = (points[-1][1] - points[0][1]).days if n_touch >= 2 else np.nan

            rows.append(
                dict(
                    CASE_NO=case_id,
                    TOUCH_COUNT=n_touch,
                    TOTAL_DAYS=total_days,
                    AMOUNT=row.get("AMOUNT", np.nan),
                    QTY=row.get("QTY", np.nan),
                    PKG=row.get("PKG", np.nan),
                )
            )

        feat = pd.DataFrame(rows).set_index("CASE_NO", drop=True)
        return feat, dwell_list, last_loc

# -------- statistical detector ------------------------------------------------
class StatDetector:
    def __init__(self, iqr_k: float = 1.5, mad_k: float = 3.5) -> None:
        self.iqr_k = float(iqr_k)
        self.mad_k = float(mad_k)

    @staticmethod
    def _iqr_mask(x: pd.Series, k: float) -> pd.Series:
        q1, q3 = np.nanpercentile(x, 25), np.nanpercentile(x, 75)
        iqr = q3 - q1
        low, high = q1 - k*iqr, q3 + k*iqr
        return (x < low) | (x > high)

    @staticmethod
    def _mad_mask(x: pd.Series, k: float) -> pd.Series:
        med = np.nanmedian(x)
        mad = np.nanmedian(np.abs(x - med))
        if mad == 0 or np.isnan(mad):
            return pd.Series(False, index=x.index)
        z = 0.6745 * (x - med) / mad  # robust z
        return np.abs(z) > k

    def dwell_outliers(self, dwell_list: List[Tuple[str,str,int]]) -> List[AnomalyRecord]:
        out = []
        if not dwell_list:
            return out
        df = pd.DataFrame(dwell_list, columns=["case","loc","dwell"])
        mask = self._mad_mask(df["dwell"].astype(float), self.mad_k) | \
               self._iqr_mask(df["dwell"].astype(float), self.iqr_k)
        for _, r in df[mask].iterrows():
            out.append(
                AnomalyRecord(
                    case_id=str(r["case"]),
                    anomaly_type=AnomalyType.EXCESSIVE_DWELL,
                    severity=AnomalySeverity.MEDIUM,
                    description=f"{r['loc']} 체류일 과다({int(r['dwell'])}일)",
                    detected_value=float(r["dwell"]),
                    location=str(r["loc"]),
                )
            )
        return out

# -------- simple rule detector ------------------------------------------------
class RuleDetector:
    """시간 역전 + STATUS_LOCATION(있으면) ≠ 최종 위치"""
    def time_reversal(self, row: pd.Series) -> Optional[AnomalyRecord]:
        points: List[Tuple[str,pd.Timestamp]] = []
        for col in WAREHOUSE_COLS + SITE_COLS:
            if col in row.index and pd.notna(row[col]):
                dt = pd.to_datetime(row[col], errors="coerce")
                if pd.notna(dt):
                    points.append((col, dt))
        if not points:
            return None
        original = [c for c,_ in points]
        ordered = [c for c,_ in sorted(points, key=lambda x: x[1])]
        if original != ordered:
            return AnomalyRecord(
                case_id=str(row.get("CASE_NO","NA")),
                anomaly_type=AnomalyType.TIME_REVERSAL,
                severity=AnomalySeverity.HIGH,
                description="시간 역전(이동 순서 불일치)",
            )
        return None

    def status_mismatch(self, row: pd.Series, last_loc: Optional[str]) -> Optional[AnomalyRecord]:
        status = row.get("STATUS_LOCATION", None)
        if pd.isna(status) or not last_loc:
            return None
        if str(status).strip() != str(last_loc).strip():
            return AnomalyRecord(
                case_id=str(row.get("CASE_NO","NA")),
                anomaly_type=AnomalyType.STATUS_MISMATCH,
                severity=AnomalySeverity.MEDIUM,
                description=f"STATUS_LOCATION({status}) ≠ 최종({last_loc})",
            )
        return None

# -------- ECDF calibrator -----------------------------------------------------
class ECDFCalibrator:
    def __init__(self):
        self.ref: Optional[np.ndarray] = None
    def fit(self, scores: np.ndarray) -> "ECDFCalibrator":
        self.ref = np.sort(scores.astype(float))
        return self
    def transform(self, scores: np.ndarray) -> np.ndarray:
        if self.ref is None or len(self.ref) == 0:
            return np.zeros_like(scores, dtype=float)
        # 위험도: 상위 tail로 갈수록 1.0
        return np.searchsorted(self.ref, scores, side="right") / float(len(self.ref))

# -------- ML detector (ensemble) ---------------------------------------------
class MLDetector:
    """파라미터 프리(ECOD/COPOD/HBOS) + 트리(IForest)의 가벼운 앙상블.
    - PyOD 설치 시 4모델, 미설치 시 sklearn IsolationForest만 사용
    - 모델별 decision_function/score_ → ECDF 위험도로 정규화 후 평균
    """
    def __init__(self, contamination: float = 0.02, random_state: int = 42, use_pyod_first: bool = True):
        self.contamination = float(contamination)
        self.random_state = int(random_state)
        self.use_pyod_first = (use_pyod_first and PYOD_AVAILABLE)
        self.calib = ECDFCalibrator()

    def _winsorize(self, x: pd.DataFrame, p: float = 0.005) -> pd.DataFrame:
        lo = x.quantile(p)
        hi = x.quantile(1-p)
        return x.clip(lower=lo, upper=hi, axis=1)

    def fit_predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        if X is None or len(X) == 0:
            return np.array([], dtype=int), np.array([], dtype=float), {"models": []}

        # 전처리: 스케일러(있을 때만) + 극단값 완화
        X2 = X.replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
        X2 = self._winsorize(X2, 0.01)
        if RobustScaler is not None:
            Xs = pd.DataFrame(RobustScaler().fit_transform(X2), index=X2.index, columns=X2.columns)
        else:
            Xs = X2

        scores = []
        used = []

        # PyOD 우선
        if self.use_pyod_first:
            try:
                models = [
                    ("ECOD", ECOD()),
                    ("COPOD", COPOD()),
                    ("HBOS", HBOS()),
                    ("IForest", IForest(n_estimators=256, random_state=self.random_state, contamination=self.contamination)),
                ]
                for name, m in models:
                    m.fit(Xs.values)
                    try:
                        s = m.decision_function(Xs.values)  # 클수록 정상
                    except Exception:
                        s = -getattr(m, "decision_scores_", np.zeros(len(Xs)))
                        s = -s  # 점수 방향 통일을 위해 반전
                    scores.append(ECDFCalibrator().fit(np.asarray(s)).transform(np.asarray(s)))
                    used.append(name)
            except Exception as e:
                logger.warning("PyOD 앙상블 실패 → sklearn IForest로 폴백: %s", e)

        # sklearn 폴백
        if not used and IsolationForest is not None:
            iso = IsolationForest(n_estimators=256, random_state=self.random_state, contamination=self.contamination)
            iso.fit(Xs)
            dec = iso.decision_function(Xs)  # +: 정상, -: 이상
            scores.append(ECDFCalibrator().fit(dec).transform(dec))
            used.append("sklearn_IForest")

        if not scores:
            # 마지막 안전망
            base = np.zeros(len(Xs), dtype=float)
            return (base >= 1).astype(int), base, {"models": []}

        # 위험도: 각 모델 ECDF 위험도 평균
        risk = np.mean(np.vstack(scores), axis=0)
        y = (risk >= (1 - self.contamination)).astype(int)
        meta = {"models": used, "n_models": len(used)}
        return y, risk, meta

# -------- Orchestrator --------------------------------------------------------
class HybridAnomalyDetector:
    def __init__(self, cfg: DetectorConfig):
        self.cfg = cfg
        self.normalizer = HeaderNormalizer(cfg.column_map)
        self.validator = DataQualityValidator()
        self.rule = RuleDetector()
        self.stat = StatDetector(cfg.iqr_k, cfg.mad_k)
        self.ml = MLDetector(cfg.contamination, cfg.random_state, cfg.use_pyod_first)

    def _export(self, anomalies: List[AnomalyRecord], export_excel: Optional[str], export_json: Optional[str], df_source: Optional[pd.DataFrame] = None) -> None:
        rows = [dict(
            case_id=a.case_id,
            anomaly_type=a.anomaly_type.value,
            severity=a.severity.value,
            description=a.description,
            detected_value=a.detected_value,
            expected_range=a.expected_range,
            location=a.location,
            timestamp=a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            risk_score=a.risk_score,
        ) for a in anomalies]

        if export_json:
            with open(export_json, "w", encoding="utf-8") as f:
                json.dump({"anomalies": rows}, f, ensure_ascii=False, indent=2)

        if export_excel:
            df = pd.DataFrame(rows)
            with pd.ExcelWriter(export_excel, engine="xlsxwriter") as w:
                df.to_excel(w, index=False, sheet_name="Anomalies")
                if df_source is not None:
                    df_source.head(1000).to_excel(w, index=False, sheet_name="Source_Sample")

    def run(self, df_raw: pd.DataFrame, export_excel: Optional[str] = None, export_json: Optional[str] = None) -> Dict[str, Any]:
        # 0) 헤더 정규화 + 경량 밸리데이션
        df = self.normalizer.normalize(df_raw)
        issues = self.validator.validate(df)

        anomalies: List[AnomalyRecord] = []
        if issues:
            anomalies.append(
                AnomalyRecord(
                    case_id=str(df.iloc[0].get("CASE_NO", "NA")) if len(df) else "NA",
                    anomaly_type=AnomalyType.DATA_QUALITY,
                    severity=AnomalySeverity.MEDIUM,
                    description="; ".join(issues),
                )
            )

        # 1) 피처 구성
        fb = FeatureBuilder(self.cfg)
        feat, dwell_list, last_loc = fb.build(df)

        # 2) 규칙 감지
        for i, row in df.iterrows():
            r1 = self.rule.time_reversal(row)
            if r1: anomalies.append(r1)
            r2 = self.rule.status_mismatch(row, last_loc.get(i, None))
            if r2: anomalies.append(r2)

        # 3) 통계 감지
        anomalies.extend(self.stat.dwell_outliers(dwell_list))

        # 4) ML 앙상블
        use_cols = [c for c in SAFE_NUMERIC_COLS if c in feat.columns]
        X = feat[use_cols].fillna(0.0)
        y, risk, meta = self.ml.fit_predict(X)

        for case_id, yi, ri in zip(X.index, y, risk):
            if yi == 1:
                sev = AnomalySeverity.CRITICAL if ri >= 0.98 else (AnomalySeverity.HIGH if ri >= 0.9 else AnomalySeverity.MEDIUM)
                anomalies.append(
                    AnomalyRecord(
                        case_id=str(case_id),
                        anomaly_type=AnomalyType.ML_OUTLIER,
                        severity=sev,
                        description=f"ML 이상치(위험도 {ri:.3f})",
                        detected_value=float(ri),
                        risk_score=float(ri),
                    )
                )

        # 5) 요약
        summary = dict(
            total=len(df),
            anomalies=len(anomalies),
            ml_models=meta.get("models", []),
            ml_contamination=self.cfg.contamination,
        )

        # 6) 출력
        self._export(anomalies, export_excel, export_json, df_source=df)
        return {"anomalies":[asdict(a) | {"anomaly_type": a.anomaly_type.value, "severity": a.severity.value} for a in anomalies],
                "summary": summary}
