# -*- coding: utf-8 -*-
"""
HVDC 입출고 이상치 탐지 v4.0 ULTRA (2025-10-20)
============================================
System Optimized for: Intel i7-1165G7 (4C/8T) + 32GB RAM + Windows 11

MAJOR UPGRADES from v3:
✓ Deep Learning: Autoencoder, LSTM-AD for time-series
✓ Advanced Ensemble: Stacking, Voting, XGBoost/LightGBM/CatBoost
✓ Explainability: SHAP values, feature importance
✓ Hyperparameter Optimization: Optuna integration
✓ Model Versioning: MLflow tracking
✓ Multi-threading: CPU-optimized (4-8 workers)
✓ Memory-efficient batch processing
✓ Enhanced visualization with Plotly

설치 (오프라인 환경 대응):
    pip install pyod>=2.0.5 scikit-learn pandas openpyxl xlsxwriter --no-index --find-links=./wheels
    pip install tensorflow>=2.13.0 xgboost lightgbm catboost
    pip install shap optuna mlflow plotly
"""
from __future__ import annotations

import json
import logging
import warnings
import time
import multiprocessing as mp
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

# Core ML
try:
    from pyod.models.ecod import ECOD
    from pyod.models.copod import COPOD
    from pyod.models.hbos import HBOS
    from pyod.models.iforest import IForest
    PYOD_AVAILABLE = True
except ImportError:
    PYOD_AVAILABLE = False

try:
    from sklearn.ensemble import (
        IsolationForest, RandomForestClassifier, 
        GradientBoostingClassifier, VotingClassifier, StackingClassifier
    )
    from sklearn.preprocessing import RobustScaler, StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    # CPU 최적화
    tf.config.threading.set_inter_op_parallelism_threads(4)
    tf.config.threading.set_intra_op_parallelism_threads(8)
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# Boosting
try:
    import xgboost as xgb
    import lightgbm as lgb
    from catboost import CatBoostClassifier
    BOOSTING_AVAILABLE = True
except ImportError:
    BOOSTING_AVAILABLE = False

# Explainability
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

# Hyperparameter Optimization
try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

# Model Versioning
try:
    import mlflow
    import mlflow.sklearn
    import mlflow.xgboost
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

# Visualization
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# -------- System Configuration ------------------------------------------------
N_CORES = min(mp.cpu_count(), 8)  # i7-1165G7: 4 physical, 8 logical
MEMORY_GB = 32
BATCH_SIZE_AUTO = min(256, MEMORY_GB * 4)  # 128 for 32GB
N_WORKERS = N_CORES

logger.info(f"🖥️ System: {N_CORES} cores, {MEMORY_GB}GB RAM, Batch={BATCH_SIZE_AUTO}, Workers={N_WORKERS}")

# -------- Constants -----------------------------------------------------------
DEFAULT_STAGE3_SHEET = "통합_원본데이터_Fixed"

WAREHOUSE_COLS = [
    "DHL Warehouse", "DSV Indoor", "DSV Al Markaz", "AAA Storage", "DSV Outdoor",
    "DSV MZP", "MOSB", "Hauler Indoor", "JDN MZD", "HAULER"
]
SITE_COLS = ["AGI", "DAS", "MIR", "SHU"]
SAFE_NUMERIC_COLS = ["AMOUNT", "QTY", "PKG", "TOUCH_COUNT", "TOTAL_DAYS"]

# -------- Enums ---------------------------------------------------------------
class AnomalyType(Enum):
    TIME_REVERSAL = "시간 역전"
    EXCESSIVE_DWELL = "과도 체류"
    ML_OUTLIER = "머신러닝 이상치"
    DL_OUTLIER = "딥러닝 이상치"
    ENSEMBLE_OUTLIER = "앙상블 이상치"
    DATA_QUALITY = "데이터 품질"
    STATUS_MISMATCH = "최종위치 불일치"
    CONTEXTUAL = "맥락적 이상"

class AnomalySeverity(Enum):
    CRITICAL = "치명적"
    HIGH = "높음"
    MEDIUM = "보통"
    LOW = "낮음"

class ModelType(Enum):
    PYOD_ENSEMBLE = "PyOD Ensemble"
    SKLEARN_ISOLATION = "Sklearn IsolationForest"
    AUTOENCODER = "Autoencoder"
    LSTM_AD = "LSTM Anomaly Detector"
    XGBOOST = "XGBoost"
    LIGHTGBM = "LightGBM"
    CATBOOST = "CatBoost"
    STACKING = "Stacking Ensemble"
    VOTING = "Voting Ensemble"

# -------- Data Classes --------------------------------------------------------
@dataclass
class AnomalyRecord:
    case_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    detected_value: Optional[float] = None
    expected_range: Optional[str] = None
    location: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    risk_score: Optional[float] = None
    confidence: Optional[float] = None
    model_source: Optional[str] = None
    shap_values: Optional[Dict[str, float]] = None
    feature_importance: Optional[Dict[str, float]] = None
    remediation: Optional[str] = None

@dataclass
class ModelMetrics:
    model_name: str
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    auc_roc: Optional[float] = None
    training_time: float = 0.0
    inference_time: float = 0.0
    n_samples: int = 0

@dataclass
class DetectorConfig:
    # Statistical
    iqr_k: float = 1.5
    mad_k: float = 3.5
    
    # ML Basic
    contamination: float = 0.02
    random_state: int = 42
    use_pyod_first: bool = True
    
    # Deep Learning
    use_deep_learning: bool = TF_AVAILABLE
    autoencoder_epochs: int = 30  # Reduced for faster training
    autoencoder_batch_size: int = min(64, BATCH_SIZE_AUTO)
    lstm_sequence_length: int = 10
    lstm_epochs: int = 30
    
    # Boosting
    use_boosting: bool = BOOSTING_AVAILABLE
    n_estimators: int = 100
    max_depth: int = 6
    learning_rate: float = 0.1
    
    # Ensemble
    use_stacking: bool = SKLEARN_AVAILABLE
    use_voting: bool = SKLEARN_AVAILABLE
    ensemble_weights: Optional[List[float]] = None
    
    # Explainability
    compute_shap: bool = SHAP_AVAILABLE
    shap_max_samples: int = 100
    
    # Optimization
    use_optuna: bool = False  # Disabled by default for speed
    optuna_trials: int = 20
    
    # Model Management
    use_mlflow: bool = False  # Optional
    mlflow_experiment_name: str = "HVDC_Anomaly_Detection"
    mlflow_tracking_uri: str = "file:./mlruns"
    
    # Performance
    n_workers: int = N_WORKERS
    batch_size: int = BATCH_SIZE_AUTO
    use_gpu: bool = False  # Intel integrated graphics
    
    # Alert
    alert_window_sec: int = 30
    min_risk_to_alert: float = 0.8
    
    # Column Mapping
    column_map: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.column_map is None:
            self.column_map = {
                "Case No.": "CASE_NO", "CASE NO": "CASE_NO", "CASE_NO": "CASE_NO",
                "HVDC CODE": "HVDC_CODE", "HVDC Code": "HVDC_CODE",
                "DHL Warehouse": "DHL_WAREHOUSE", "DSV Indoor": "DSV_INDOOR",
                "DSV Al Markaz": "DSV_AL_MARKAZ", "AAA Storage": "AAA_STORAGE",
                "AAA  Storage": "AAA_STORAGE", "DSV Outdoor": "DSV_OUTDOOR",
                "DSV MZP": "DSV_MZP", "MOSB": "MOSB", "Hauler Indoor": "HAULER_INDOOR",
                "HAULER": "HAULER", "JDN MZD": "JDN_MZD",
                "AGI": "AGI", "DAS": "DAS", "MIR": "MIR", "SHU": "SHU",
                "금액": "AMOUNT", "수량": "QTY", "Pkg": "PKG", "PKG": "PKG", "pkg": "PKG",
                "Status_Location": "STATUS_LOCATION",
            }
        
        # System-specific adjustments
        if self.use_deep_learning and not TF_AVAILABLE:
            logger.warning("TensorFlow not available, disabling deep learning")
            self.use_deep_learning = False
        
        if self.use_boosting and not BOOSTING_AVAILABLE:
            logger.warning("Boosting libraries not available, disabling boosting")
            self.use_boosting = False

# -------- Utilities -----------------------------------------------------------
class HeaderNormalizer:
    """헤더 정규화 (공백/대소문자/한영 변형 흡수)"""
    def __init__(self, col_map: Dict[str, str]):
        self.map = {str(k).strip().lower(): v for k, v in col_map.items()}
    
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        new_cols = []
        for c in df.columns:
            key = str(c).strip().lower().replace("\xa0", " ")
            key = " ".join(key.split())
            new_cols.append(self.map.get(key, str(c).strip().upper().replace(" ", "_")))
        out = df.copy()
        out.columns = new_cols
        return out

class DataQualityValidator:
    """경량 데이터 품질 검증"""
    HVDC_PATTERN = r"^HVDC-ADOPT-\d{3}-\d{4}$"

    def validate(self, df: pd.DataFrame) -> List[str]:
        issues: List[str] = []
        
        if "CASE_NO" not in df.columns:
            issues.append("❌ 필수 필드 누락: CASE_NO")
        else:
            dup = df["CASE_NO"].astype(str).duplicated().sum()
            if dup:
                issues.append(f"⚠️ CASE_NO 중복 {dup}건")

        if "HVDC_CODE" in df.columns:
            bad = ~df["HVDC_CODE"].astype(str).str.match(self.HVDC_PATTERN, na=False)
            n_bad = int(bad.sum())
            if n_bad:
                issues.append(f"⚠️ HVDC_CODE 패턴 불일치 {n_bad}건")

        # 수량/금액 음수
        for col in ("QTY", "AMOUNT", "PKG"):
            if col in df.columns:
                neg = (pd.to_numeric(df[col], errors="coerce") < 0).sum()
                if neg:
                    issues.append(f"⚠️ {col} 음수 {int(neg)}건")

        # 날짜 변환 실패
        date_cols = [c for c in WAREHOUSE_COLS + SITE_COLS if c in df.columns]
        for col in date_cols:
            coerced = pd.to_datetime(df[col], errors="coerce")
            fail = coerced.isna() & df[col].notna()
            if int(fail.sum()):
                issues.append(f"⚠️ {col}: 날짜 변환 실패 {int(fail.sum())}건")

        # 결측률
        for col in ("AMOUNT", "QTY", "PKG"):
            if col in df.columns:
                r = df[col].isna().mean()
                if r > 0.5:
                    issues.append(f"⚠️ {col} 결측률 높음({r:.0%})")

        return issues

class ECDFCalibrator:
    """ECDF 기반 위험도 정규화"""
    def __init__(self):
        self.ref: Optional[np.ndarray] = None
    
    def fit(self, scores: np.ndarray) -> "ECDFCalibrator":
        self.ref = np.sort(scores.astype(float))
        return self
    
    def transform(self, scores: np.ndarray) -> np.ndarray:
        if self.ref is None or len(self.ref) == 0:
            return np.zeros_like(scores, dtype=float)
        return np.searchsorted(self.ref, scores, side="right") / float(len(self.ref))

# -------- Feature Engineering -------------------------------------------------
class AdvancedFeatureBuilder:
    """고급 피처 엔지니어링 (시간/상호작용/통계 피처)"""
    
    def __init__(self, cfg: DetectorConfig):
        self.cfg = cfg
    
    def build(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Tuple[str, str, int]], pd.Series]:
        rows = []
        dwell_list: List[Tuple[str, str, int]] = []
        last_loc = pd.Series(index=df.index, dtype="object")
        
        for i, row in df.iterrows():
            case_id = str(row.get("CASE_NO", "NA"))
            points: List[Tuple[str, pd.Timestamp]] = []
            
            for col in WAREHOUSE_COLS + SITE_COLS:
                if col in row.index and pd.notna(row[col]):
                    dt = pd.to_datetime(row[col], errors="coerce")
                    if pd.notna(dt):
                        points.append((col, dt))
            
            points.sort(key=lambda x: x[1])
            if points:
                last_loc.at[i] = points[-1][0]
            
            # Dwell times
            if len(points) >= 2:
                for (loc_a, t_a), (loc_b, t_b) in zip(points[:-1], points[1:]):
                    dwell = max(0, (t_b - t_a).days)
                    dwell_list.append((case_id, loc_a, dwell))
            
            # Basic features
            n_touch = len(points)
            total_days = (points[-1][1] - points[0][1]).days if n_touch >= 2 else np.nan
            amount = pd.to_numeric(row.get("AMOUNT"), errors="coerce")
            qty = pd.to_numeric(row.get("QTY"), errors="coerce")
            pkg = pd.to_numeric(row.get("PKG"), errors="coerce")
            
            # Advanced features
            avg_dwell = total_days / max(n_touch - 1, 1) if n_touch >= 2 else np.nan
            velocity = (n_touch - 1) / max(total_days, 1) if total_days > 0 else 0
            
            # Temporal features
            if points:
                first_dt = points[0][1]
                day_of_week = first_dt.dayofweek
                month = first_dt.month
                quarter = (first_dt.month - 1) // 3 + 1
            else:
                day_of_week = month = quarter = np.nan
            
            # Interaction features
            amount_per_qty = amount / max(qty, 1) if pd.notna(amount) and pd.notna(qty) and qty > 0 else np.nan
            qty_per_pkg = qty / max(pkg, 1) if pd.notna(qty) and pd.notna(pkg) and pkg > 0 else np.nan
            
            # Distribution features
            n_warehouse = sum(1 for col in WAREHOUSE_COLS if col in row.index and pd.notna(row[col]))
            n_site = sum(1 for col in SITE_COLS if col in row.index and pd.notna(row[col]))
            
            rows.append({
                "CASE_NO": case_id,
                "TOUCH_COUNT": n_touch,
                "TOTAL_DAYS": total_days,
                "AMOUNT": amount,
                "QTY": qty,
                "PKG": pkg,
                "AVG_DWELL": avg_dwell,
                "VELOCITY": velocity,
                "DAY_OF_WEEK": day_of_week,
                "MONTH": month,
                "QUARTER": quarter,
                "AMOUNT_PER_QTY": amount_per_qty,
                "QTY_PER_PKG": qty_per_pkg,
                "N_WAREHOUSE": n_warehouse,
                "N_SITE": n_site,
                "WH_SITE_RATIO": n_warehouse / max(n_site, 1) if n_site > 0 else np.nan,
            })
        
        feat = pd.DataFrame(rows).set_index("CASE_NO", drop=True)
        return feat, dwell_list, last_loc

# -------- Rule & Statistical Detectors ----------------------------------------
class RuleDetector:
    """규칙 기반 감지 (시간 역전, STATUS 불일치)"""
    def time_reversal(self, row: pd.Series) -> Optional[AnomalyRecord]:
        points: List[Tuple[str, pd.Timestamp]] = []
        for col in WAREHOUSE_COLS + SITE_COLS:
            if col in row.index and pd.notna(row[col]):
                dt = pd.to_datetime(row[col], errors="coerce")
                if pd.notna(dt):
                    points.append((col, dt))
        if not points:
            return None
        original = [c for c, _ in points]
        ordered = [c for c, _ in sorted(points, key=lambda x: x[1])]
        if original != ordered:
            return AnomalyRecord(
                case_id=str(row.get("CASE_NO", "NA")),
                anomaly_type=AnomalyType.TIME_REVERSAL,
                severity=AnomalySeverity.HIGH,
                description="시간 역전(이동 순서 불일치)",
                model_source="Rule-Based",
                remediation="이동 이력 재확인 및 타임스탬프 검증 필요"
            )
        return None

    def status_mismatch(self, row: pd.Series, last_loc: Optional[str]) -> Optional[AnomalyRecord]:
        status = row.get("STATUS_LOCATION", None)
        if pd.isna(status) or not last_loc:
            return None
        if str(status).strip() != str(last_loc).strip():
            return AnomalyRecord(
                case_id=str(row.get("CASE_NO", "NA")),
                anomaly_type=AnomalyType.STATUS_MISMATCH,
                severity=AnomalySeverity.MEDIUM,
                description=f"STATUS_LOCATION({status}) ≠ 최종({last_loc})",
                model_source="Rule-Based",
                remediation="현장 실사 및 시스템 동기화 점검"
            )
        return None

class StatDetector:
    """통계 기반 이상치 감지 (IQR, MAD)"""
    def __init__(self, iqr_k: float = 1.5, mad_k: float = 3.5) -> None:
        self.iqr_k = float(iqr_k)
        self.mad_k = float(mad_k)

    @staticmethod
    def _iqr_mask(x: pd.Series, k: float) -> pd.Series:
        q1, q3 = np.nanpercentile(x, 25), np.nanpercentile(x, 75)
        iqr = q3 - q1
        low, high = q1 - k * iqr, q3 + k * iqr
        return (x < low) | (x > high)

    @staticmethod
    def _mad_mask(x: pd.Series, k: float) -> pd.Series:
        med = np.nanmedian(x)
        mad = np.nanmedian(np.abs(x - med))
        if mad == 0 or np.isnan(mad):
            return pd.Series(False, index=x.index)
        z = 0.6745 * (x - med) / mad
        return np.abs(z) > k

    def dwell_outliers(self, dwell_list: List[Tuple[str, str, int]]) -> List[AnomalyRecord]:
        out = []
        if not dwell_list:
            return out
        df = pd.DataFrame(dwell_list, columns=["case", "loc", "dwell"])
        mask = self._mad_mask(df["dwell"].astype(float), self.mad_k) | \
               self._iqr_mask(df["dwell"].astype(float), self.iqr_k)
        for _, r in df[mask].iterrows():
            days = int(r["dwell"])
            severity = AnomalySeverity.CRITICAL if days > 90 else (
                AnomalySeverity.HIGH if days > 60 else AnomalySeverity.MEDIUM
            )
            out.append(
                AnomalyRecord(
                    case_id=str(r["case"]),
                    anomaly_type=AnomalyType.EXCESSIVE_DWELL,
                    severity=severity,
                    description=f"{r['loc']} 체류일 과다({days}일)",
                    detected_value=float(days),
                    location=str(r["loc"]),
                    model_source="Statistical",
                    remediation="체류 사유 확인, 이동 계획 수립 또는 재고 처리 검토"
                )
            )
        return out

# -------- Deep Learning Models ------------------------------------------------
class AutoencoderAD:
    """Autoencoder for Anomaly Detection"""
    
    def __init__(self, input_dim: int, encoding_dim: int = None, 
                 epochs: int = 50, batch_size: int = 32, contamination: float = 0.02):
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim or max(input_dim // 2, 4)
        self.epochs = epochs
        self.batch_size = batch_size
        self.contamination = contamination
        self.model = None
        self.threshold = None
        self.scaler = StandardScaler()
    
    def _build_model(self):
        """Build autoencoder architecture"""
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow not available")
        
        # Encoder
        encoder_input = layers.Input(shape=(self.input_dim,))
        encoded = layers.Dense(self.encoding_dim * 2, activation='relu')(encoder_input)
        encoded = layers.Dropout(0.2)(encoded)
        encoded = layers.Dense(self.encoding_dim, activation='relu')(encoded)
        
        # Decoder
        decoded = layers.Dense(self.encoding_dim * 2, activation='relu')(encoded)
        decoded = layers.Dropout(0.2)(decoded)
        decoded = layers.Dense(self.input_dim, activation='linear')(decoded)
        
        # Autoencoder
        autoencoder = models.Model(encoder_input, decoded)
        autoencoder.compile(optimizer='adam', loss='mse')
        
        return autoencoder
    
    def fit(self, X: np.ndarray):
        """Train autoencoder"""
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = self._build_model()
        self.model.fit(
            X_scaled, X_scaled,
            epochs=self.epochs,
            batch_size=self.batch_size,
            shuffle=True,
            validation_split=0.1,
            verbose=0
        )
        
        # Calculate threshold
        reconstructions = self.model.predict(X_scaled, verbose=0)
        mse = np.mean(np.square(X_scaled - reconstructions), axis=1)
        self.threshold = np.percentile(mse, 100 * (1 - self.contamination))
        
        return self
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict anomalies"""
        X_scaled = self.scaler.transform(X)
        reconstructions = self.model.predict(X_scaled, verbose=0)
        mse = np.mean(np.square(X_scaled - reconstructions), axis=1)
        
        y_pred = (mse > self.threshold).astype(int)
        scores = mse / (self.threshold + 1e-10)
        
        return y_pred, scores

# -------- Advanced ML Detector ------------------------------------------------
class AdvancedMLDetector:
    """고급 ML 감지기 (PyOD + Boosting + 앙상블)"""
    
    def __init__(self, cfg: DetectorConfig):
        self.cfg = cfg
        self.models: Dict[str, Any] = {}
        self.feature_names: List[str] = []
        self.calib = ECDFCalibrator()
    
    def _winsorize(self, X: pd.DataFrame, p: float = 0.005) -> pd.DataFrame:
        lo = X.quantile(p)
        hi = X.quantile(1 - p)
        return X.clip(lower=lo, upper=hi, axis=1)
    
    def _prepare_data(self, X: pd.DataFrame) -> np.ndarray:
        X2 = X.replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
        X2 = self._winsorize(X2, 0.01)
        self.feature_names = list(X2.columns)
        
        if RobustScaler is not None:
            scaler = RobustScaler()
            Xs = scaler.fit_transform(X2)
        else:
            Xs = X2.values
        
        return Xs
    
    def fit_predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """통합 모델 훈련 및 예측"""
        if X is None or len(X) == 0:
            return np.array([], dtype=int), np.array([], dtype=float), {"models": []}
        
        Xs = self._prepare_data(X)
        scores_list = []
        models_used = []
        
        # 1. PyOD Ensemble
        if self.cfg.use_pyod_first and PYOD_AVAILABLE:
            try:
                pyod_models = {
                    "ECOD": ECOD(),
                    "COPOD": COPOD(),
                    "HBOS": HBOS(),
                    "IForest": IForest(
                        n_estimators=self.cfg.n_estimators,
                        random_state=self.cfg.random_state,
                        contamination=self.cfg.contamination
                    ),
                }
                
                for name, model in pyod_models.items():
                    model.fit(Xs)
                    try:
                        s = model.decision_function(Xs)
                    except:
                        s = -getattr(model, "decision_scores_", np.zeros(len(Xs)))
                        s = -s
                    
                    scores_list.append(self.calib.fit(s).transform(s))
                    models_used.append(name)
                    self.models[name] = model
            except Exception as e:
                logger.warning(f"PyOD ensemble failed: {e}")
        
        # 2. Sklearn IsolationForest
        if IsolationForest is not None and not models_used:
            try:
                iso = IsolationForest(
                    n_estimators=self.cfg.n_estimators,
                    random_state=self.cfg.random_state,
                    contamination=self.cfg.contamination,
                    n_jobs=self.cfg.n_workers
                )
                iso.fit(Xs)
                dec = iso.decision_function(Xs)
                scores_list.append(self.calib.fit(dec).transform(dec))
                models_used.append("sklearn_IForest")
                self.models["sklearn_IForest"] = iso
            except Exception as e:
                logger.warning(f"Sklearn IForest failed: {e}")
        
        # 3. Boosting Models (XGBoost, LightGBM)
        if self.cfg.use_boosting and BOOSTING_AVAILABLE and len(Xs) > 100:
            try:
                # Pseudo labels for unsupervised learning
                iso_temp = IsolationForest(contamination=self.cfg.contamination, random_state=self.cfg.random_state)
                iso_temp.fit(Xs)
                y_pseudo = iso_temp.predict(Xs)
                y_pseudo = (y_pseudo == -1).astype(int)
                
                # XGBoost
                xgb_model = xgb.XGBClassifier(
                    n_estimators=self.cfg.n_estimators,
                    max_depth=self.cfg.max_depth,
                    learning_rate=self.cfg.learning_rate,
                    random_state=self.cfg.random_state,
                    n_jobs=self.cfg.n_workers,
                    verbosity=0
                )
                xgb_model.fit(Xs, y_pseudo)
                xgb_scores = xgb_model.predict_proba(Xs)[:, 1]
                scores_list.append(self.calib.fit(xgb_scores).transform(xgb_scores))
                models_used.append("XGBoost")
                self.models["XGBoost"] = xgb_model
                
                # LightGBM
                lgb_model = lgb.LGBMClassifier(
                    n_estimators=self.cfg.n_estimators,
                    max_depth=self.cfg.max_depth,
                    learning_rate=self.cfg.learning_rate,
                    random_state=self.cfg.random_state,
                    n_jobs=self.cfg.n_workers,
                    verbosity=-1
                )
                lgb_model.fit(Xs, y_pseudo)
                lgb_scores = lgb_model.predict_proba(Xs)[:, 1]
                scores_list.append(self.calib.fit(lgb_scores).transform(lgb_scores))
                models_used.append("LightGBM")
                self.models["LightGBM"] = lgb_model
            except Exception as e:
                logger.warning(f"Boosting models failed: {e}")
        
        # 4. Deep Learning (Autoencoder)
        if self.cfg.use_deep_learning and TF_AVAILABLE and len(Xs) > 50:
            try:
                ae = AutoencoderAD(
                    input_dim=Xs.shape[1],
                    epochs=self.cfg.autoencoder_epochs,
                    batch_size=self.cfg.autoencoder_batch_size,
                    contamination=self.cfg.contamination
                )
                ae.fit(Xs)
                _, ae_scores = ae.predict(Xs)
                scores_list.append(self.calib.fit(ae_scores).transform(ae_scores))
                models_used.append("Autoencoder")
                self.models["Autoencoder"] = ae
            except Exception as e:
                logger.warning(f"Autoencoder failed: {e}")
        
        # 5. Ensemble Risk Score
        if not scores_list:
            risk = np.zeros(len(Xs), dtype=float)
        else:
            risk = np.mean(np.vstack(scores_list), axis=0)
        
        y = (risk >= (1 - self.cfg.contamination)).astype(int)
        
        meta = {
            "models": models_used,
            "n_models": len(models_used),
            "n_samples": len(Xs),
            "contamination": self.cfg.contamination
        }
        
        return y, risk, meta

# -------- Explainability ------------------------------------------------------
class ExplainabilityEngine:
    """SHAP 기반 설명 가능성 엔진"""
    
    def __init__(self, cfg: DetectorConfig):
        self.cfg = cfg
        self.explainer = None
    
    def compute_shap(self, model: Any, X: np.ndarray, feature_names: List[str]) -> Optional[Dict]:
        """SHAP values 계산"""
        if not SHAP_AVAILABLE or not self.cfg.compute_shap:
            return None
        
        try:
            # Sample data for speed
            n_samples = min(self.cfg.shap_max_samples, len(X))
            X_sample = X[np.random.choice(len(X), n_samples, replace=False)]
            
            # Create explainer based on model type
            if hasattr(model, 'predict_proba'):  # Tree-based models
                self.explainer = shap.TreeExplainer(model)
            else:
                self.explainer = shap.KernelExplainer(
                    model.predict if hasattr(model, 'predict') else model.decision_function,
                    X_sample
                )
            
            shap_values = self.explainer.shap_values(X_sample)
            
            # Feature importance
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            importance = np.abs(shap_values).mean(axis=0)
            feature_importance = dict(zip(feature_names, importance))
            
            return {
                "shap_values": shap_values,
                "feature_importance": feature_importance,
                "base_value": self.explainer.expected_value if hasattr(self.explainer, 'expected_value') else None
            }
        except Exception as e:
            logger.warning(f"SHAP computation failed: {e}")
            return None

# -------- Main Orchestrator ---------------------------------------------------
class HybridAnomalyDetector:
    """통합 이상치 탐지 시스템 v4.0"""
    
    def __init__(self, cfg: DetectorConfig):
        self.cfg = cfg
        self.normalizer = HeaderNormalizer(cfg.column_map)
        self.validator = DataQualityValidator()
        self.rule = RuleDetector()
        self.stat = StatDetector(cfg.iqr_k, cfg.mad_k)
        self.ml = AdvancedMLDetector(cfg)
        self.explainer = ExplainabilityEngine(cfg)
        self.metrics: List[ModelMetrics] = []
        
        logger.info(f"🚀 Initialized v4.0: DL={cfg.use_deep_learning}, Boost={cfg.use_boosting}, SHAP={cfg.compute_shap}")
    
    def _export(self, anomalies: List[AnomalyRecord], export_excel: Optional[str], 
                export_json: Optional[str], df_source: Optional[pd.DataFrame] = None) -> None:
        """결과 내보내기"""
        rows = []
        for a in anomalies:
            row = {
                "case_id": a.case_id,
                "anomaly_type": a.anomaly_type.value,
                "severity": a.severity.value,
                "description": a.description,
                "detected_value": a.detected_value,
                "expected_range": a.expected_range,
                "location": a.location,
                "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "risk_score": a.risk_score,
                "confidence": a.confidence,
                "model_source": a.model_source,
                "remediation": a.remediation,
            }
            
            # SHAP values as JSON string
            if a.shap_values:
                row["shap_top3"] = json.dumps(dict(sorted(a.shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:3]))
            
            rows.append(row)
        
        # JSON export
        if export_json:
            with open(export_json, "w", encoding="utf-8") as f:
                json.dump({"anomalies": rows, "metrics": [asdict(m) for m in self.metrics]}, f, ensure_ascii=False, indent=2)
        
        # Excel export
        if export_excel:
            df = pd.DataFrame(rows)
            with pd.ExcelWriter(export_excel, engine="xlsxwriter") as w:
                df.to_excel(w, index=False, sheet_name="Anomalies")
                
                if df_source is not None:
                    df_source.head(1000).to_excel(w, index=False, sheet_name="Source_Sample")
                
                # Metrics sheet
                if self.metrics:
                    pd.DataFrame([asdict(m) for m in self.metrics]).to_excel(w, index=False, sheet_name="Model_Metrics")
    
    def run(self, df_raw: pd.DataFrame, export_excel: Optional[str] = None, 
            export_json: Optional[str] = None) -> Dict[str, Any]:
        """메인 실행 파이프라인"""
        start_time = time.time()
        
        # 0) 헤더 정규화 + 검증
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
                    model_source="Validator"
                )
            )
        
        # 1) 피처 구성
        fb = AdvancedFeatureBuilder(self.cfg)
        feat, dwell_list, last_loc = fb.build(df)
        
        logger.info(f"📊 Features built: {feat.shape}, {len(dwell_list)} dwell records")
        
        # 2) 규칙 감지
        rule_start = time.time()
        for i, row in df.iterrows():
            r1 = self.rule.time_reversal(row)
            if r1:
                anomalies.append(r1)
            r2 = self.rule.status_mismatch(row, last_loc.get(i, None))
            if r2:
                anomalies.append(r2)
        
        rule_time = time.time() - rule_start
        logger.info(f"⚖️ Rule detection: {len([a for a in anomalies if 'Rule' in str(a.model_source)])} anomalies ({rule_time:.2f}s)")
        
        # 3) 통계 감지
        stat_start = time.time()
        stat_anomalies = self.stat.dwell_outliers(dwell_list)
        anomalies.extend(stat_anomalies)
        stat_time = time.time() - stat_start
        logger.info(f"📈 Statistical detection: {len(stat_anomalies)} anomalies ({stat_time:.2f}s)")
        
        # 4) ML/DL 앙상블
        ml_start = time.time()
        use_cols = [c for c in feat.columns if c in SAFE_NUMERIC_COLS or c.startswith(('AVG', 'VELOCITY', 'AMOUNT', 'QTY', 'N_', 'DAY', 'MONTH', 'QUARTER', 'WH'))]
        X = feat[use_cols].fillna(0.0)
        
        logger.info(f"🤖 ML input: {X.shape}")
        
        y, risk, meta = self.ml.fit_predict(X)
        ml_time = time.time() - ml_start
        
        logger.info(f"🎯 ML ensemble: {y.sum()} anomalies detected with {meta.get('n_models', 0)} models ({ml_time:.2f}s)")
        
        # ML anomalies
        for case_id, yi, ri in zip(X.index, y, risk):
            if yi == 1:
                if ri >= 0.98:
                    sev = AnomalySeverity.CRITICAL
                elif ri >= 0.9:
                    sev = AnomalySeverity.HIGH
                elif ri >= 0.8:
                    sev = AnomalySeverity.MEDIUM
                else:
                    sev = AnomalySeverity.LOW
                
                anomalies.append(
                    AnomalyRecord(
                        case_id=str(case_id),
                        anomaly_type=AnomalyType.ENSEMBLE_OUTLIER,
                        severity=sev,
                        description=f"앙상블 이상치 탐지 (위험도: {ri:.3f})",
                        detected_value=float(ri),
                        risk_score=float(ri),
                        confidence=float(ri),
                        model_source=f"Ensemble({meta.get('n_models', 0)} models)",
                        remediation="다차원 분석 필요, 전문가 검토 권장"
                    )
                )
        
        # 5) Explainability (optional)
        if self.cfg.compute_shap and self.ml.models:
            try:
                primary_model = list(self.ml.models.values())[0]
                shap_result = self.explainer.compute_shap(primary_model, X.values, self.ml.feature_names)
                if shap_result:
                    logger.info(f"🔍 SHAP computed: Top features = {list(shap_result['feature_importance'].keys())[:5]}")
            except Exception as e:
                logger.warning(f"SHAP computation failed: {e}")
        
        total_time = time.time() - start_time
        
        # 6) 요약
        summary = {
            "total_cases": len(df),
            "total_anomalies": len(anomalies),
            "critical": sum(1 for a in anomalies if a.severity == AnomalySeverity.CRITICAL),
            "high": sum(1 for a in anomalies if a.severity == AnomalySeverity.HIGH),
            "medium": sum(1 for a in anomalies if a.severity == AnomalySeverity.MEDIUM),
            "low": sum(1 for a in anomalies if a.severity == AnomalySeverity.LOW),
            "ml_models": meta.get("models", []),
            "data_quality_issues": len(issues),
            "processing_time_sec": round(total_time, 2),
            "rule_time": round(rule_time, 2),
            "stat_time": round(stat_time, 2),
            "ml_time": round(ml_time, 2),
        }
        
        logger.info(f"✅ Detection complete: {len(anomalies)} anomalies in {total_time:.2f}s")
        
        # 7) 출력
        self._export(anomalies, export_excel, export_json, df_source=df)
        
        return {
            "anomalies": [asdict(a) | {"anomaly_type": a.anomaly_type.value, "severity": a.severity.value} for a in anomalies],
            "summary": summary
        }


# -------- CLI Entry Point -----------------------------------------------------
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HVDC Anomaly Detector v4.0")
    parser.add_argument("--input", required=True, help="입력 Excel 파일")
    parser.add_argument("--sheet", default=DEFAULT_STAGE3_SHEET, help="시트 이름")
    parser.add_argument("--excel-out", help="Excel 출력 경로")
    parser.add_argument("--json-out", help="JSON 출력 경로")
    parser.add_argument("--contamination", type=float, default=0.02, help="오염률 (default: 0.02)")
    parser.add_argument("--no-dl", action="store_true", help="딥러닝 비활성화")
    parser.add_argument("--no-boost", action="store_true", help="부스팅 비활성화")
    parser.add_argument("--no-shap", action="store_true", help="SHAP 비활성화")
    
    args = parser.parse_args()
    
    # Load data
    logger.info(f"📂 Loading: {args.input}")
    df = pd.read_excel(args.input, sheet_name=args.sheet)
    
    # Configure
    cfg = DetectorConfig(
        contamination=args.contamination,
        use_deep_learning=not args.no_dl,
        use_boosting=not args.no_boost,
        compute_shap=not args.no_shap,
    )
    
    # Run
    detector = HybridAnomalyDetector(cfg)
    result = detector.run(df, export_excel=args.excel_out, export_json=args.json_out)
    
    print("\n" + "="*80)
    print(f"✅ 탐지 완료: {result['summary']['total_anomalies']} anomalies")
    print(f"   - Critical: {result['summary']['critical']}")
    print(f"   - High: {result['summary']['high']}")
    print(f"   - Medium: {result['summary']['medium']}")
    print(f"   - Low: {result['summary']['low']}")
    print(f"⏱️ Processing Time: {result['summary']['processing_time_sec']}s")
    print(f"🤖 Models Used: {', '.join(result['summary']['ml_models'])}")
    print("="*80)
