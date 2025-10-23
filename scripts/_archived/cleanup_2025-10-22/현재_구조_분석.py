## 📊 현재 구조 분석 (v3)

**강점:**
- PyOD 앙상블 (ECOD/COPOD/HBOS/IForest) + sklearn 폴백
- ECDF 위험도 캘리브레이션
- 3-Layer 접근 (Rule + Statistical + ML)

**개선 영역:**
- Deep Learning 미지원
- Explainability 부족
- Time-series 특화 감지 미흡
- Hyperparameter tuning 수동
- Model versioning 없음

---

## 🚀 v4.0 업그레이드 생성

{
  `path`: `C:\\Users\\SAMSUNG\\Downloads\\HVDC_Invoice-20251015T070213Z-1-001\\HVDC_Invoice\\hvdc_pipeline\\scripts\\stage4_anomaly_new\\anomaly_detector_v4.py`,
  `file_text`: `# -*- coding: utf-8 -*-
\"\"\"
HVDC 입출고 이상치 탐지 v4.0 ULTRA (2025-10-20)a
============================================
MAJOR UPGRADES:
- Deep Learning: Autoencoder, LSTM-AD for time-series
- Advanced Ensemble: Stacking, Voting, XGBoost integration
- Explainability: SHAP values, feature importance
- Hyperparameter Optimization: Optuna integration
- Model Versioning: MLflow tracking
- Online Learning: Incremental update support
- GPU Acceleration: Optional RAPIDS/CuPy support

설치:
    pip install pyod>=2.0.5 scikit-learn pandas openpyxl xlsxwriter
    pip install tensorflow>=2.13.0 keras  # Deep Learning
    pip install xgboost lightgbm catboost  # Boosting
    pip install shap optuna mlflow  # Explainability & Tuning
    pip install plotly dash  # Enhanced visualization
    # Optional: pip install cupy-cuda11x cuml  # GPU acceleration
\"\"\"
from __future__ import annotations

import json
import logging
import warnings
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Core ML
try:
    from pyod.models.ecod import ECOD
    from pyod.models.copod import COPOD
    from pyod.models.hbos import HBOS
    from pyod.models.iforest import IForest
    PYOD_AVAILABLE = True
except Exception:
    PYOD_AVAILABLE = False

try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import RobustScaler, StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False

# Boosting
try:
    import xgboost as xgb
    import lightgbm as lgb
    from catboost import CatBoostClassifier
    BOOSTING_AVAILABLE = True
except Exception:
    BOOSTING_AVAILABLE = False

# Explainability
try:
    import shap
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False

# Hyperparameter Optimization
try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    OPTUNA_AVAILABLE = True
except Exception:
    OPTUNA_AVAILABLE = False

# Model Versioning
try:
    import mlflow
    import mlflow.sklearn
    import mlflow.xgboost
    MLFLOW_AVAILABLE = True
except Exception:
    MLFLOW_AVAILABLE = False

# GPU Acceleration
try:
    import cupy as cp
    import cuml
    GPU_AVAILABLE = True
except Exception:
    GPU_AVAILABLE = False

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=\"%(asctime)s [%(levelname)s] %(message)s\")

# -------- Constants -----------------------------------------------------------
DEFAULT_STAGE3_SHEET = \"통합_원본데이터_Fixed\"

WAREHOUSE_COLS = [
    \"DHL Warehouse\", \"DSV Indoor\", \"DSV Al Markaz\", \"AAA Storage\", \"DSV Outdoor\",
    \"DSV MZP\", \"MOSB\", \"Hauler Indoor\", \"JDN MZD\", \"HAULER\"
]
SITE_COLS = [\"AGI\", \"DAS\", \"MIR\", \"SHU\"]
SAFE_NUMERIC_COLS = [\"AMOUNT\", \"QTY\", \"PKG\", \"TOUCH_COUNT\", \"TOTAL_DAYS\"]

# -------- Enums ---------------------------------------------------------------
class AnomalyType(Enum):
    TIME_REVERSAL = \"시간 역전\"
    EXCESSIVE_DWELL = \"과도 체류\"
    ML_OUTLIER = \"머신러닝 이상치\"
    DL_OUTLIER = \"딥러닝 이상치\"
    DATA_QUALITY = \"데이터 품질\"
    STATUS_MISMATCH = \"최종위치 불일치\"
    CONTEXTUAL = \"맥락적 이상\"
    COLLECTIVE = \"집단 이상\"

class AnomalySeverity(Enum):
    CRITICAL = \"치명적\"
    HIGH = \"높음\"
    MEDIUM = \"보통\"
    LOW = \"낮음\"

class ModelType(Enum):
    PYOD_ENSEMBLE = \"PyOD Ensemble\"
    SKLEARN_ISOLATION = \"Sklearn IsolationForest\"
    AUTOENCODER = \"Autoencoder\"
    LSTM_AD = \"LSTM Anomaly Detector\"
    XGBOOST = \"XGBoost\"
    LIGHTGBM = \"LightGBM\"
    CATBOOST = \"CatBoost\"
    STACKING = \"Stacking Ensemble\"
    VOTING = \"Voting Ensemble\"

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

@dataclass
class ModelMetrics:
    model_name: str
    precision: float
    recall: float
    f1_score: float
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
    use_deep_learning: bool = True
    autoencoder_epochs: int = 50
    autoencoder_batch_size: int = 32
    lstm_sequence_length: int = 10
    
    # Boosting
    use_boosting: bool = True
    n_estimators: int = 100
    
    # Ensemble
    use_stacking: bool = True
    use_voting: bool = True
    
    # Explainability
    compute_shap: bool = True
    shap_max_samples: int = 100
    
    # Optimization
    use_optuna: bool = True
    optuna_trials: int = 50
    
    # Model Management
    use_mlflow: bool = True
    mlflow_experiment_name: str = \"HVDC_Anomaly_Detection\"
    
    # GPU
    use_gpu: bool = False
    
    # Online Learning
    enable_incremental: bool = False
    incremental_batch_size: int = 100
    
    # Alert
    alert_window_sec: int = 30
    min_risk_to_alert: float = 0.8
    
    # Column Mapping
    column_map: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.column_map is None:
            self.column_map = {
                \"Case No.\": \"CASE_NO\", \"CASE NO\": \"CASE_NO\", \"CASE_NO\": \"CASE_NO\",
                \"HVDC CODE\": \"HVDC_CODE\", \"HVDC Code\": \"HVDC_CODE\",
                \"DHL Warehouse\": \"DHL_WAREHOUSE\", \"DSV Indoor\": \"DSV_INDOOR\",
                \"DSV Al Markaz\": \"DSV_AL_MARKAZ\", \"AAA Storage\": \"AAA_STORAGE\",
                \"AAA  Storage\": \"AAA_STORAGE\", \"DSV Outdoor\": \"DSV_OUTDOOR\",
                \"DSV MZP\": \"DSV_MZP\", \"MOSB\": \"MOSB\", \"Hauler Indoor\": \"HAULER_INDOOR\",
                \"HAULER\": \"HAULER\", \"JDN MZD\": \"JDN_MZD\",
                \"AGI\": \"AGI\", \"DAS\": \"DAS\", \"MIR\": \"MIR\", \"SHU\": \"SHU\",
                \"금액\": \"AMOUNT\", \"수량\": \"QTY\", \"Pkg\": \"PKG\", \"PKG\": \"PKG\", \"pkg\": \"PKG\",
                \"Status_Location\": \"STATUS_LOCATION\",
            }

# -------- Utilities -----------------------------------------------------------
class HeaderNormalizer:
    def __init__(self, col_map: Dict[str, str]):
        self.map = {str(k).strip().lower(): v for k, v in col_map.items()}
    
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        new_cols = []
        for c in df.columns:
            key = str(c).strip().lower().replace(\"\\xa0\", \" \")
            key = \" \".join(key.split())
            new_cols.append(self.map.get(key, str(c).strip().upper().replace(\" \", \"_\")))
        out = df.copy()
        out.columns = new_cols
        return out

class ECDFCalibrator:
    def __init__(self):
        self.ref: Optional[np.ndarray] = None
    
    def fit(self, scores: np.ndarray) -> \"ECDFCalibrator\":
        self.ref = np.sort(scores.astype(float))
        return self
    
    def transform(self, scores: np.ndarray) -> np.ndarray:
        if self.ref is None or len(self.ref) == 0:
            return np.zeros_like(scores, dtype=float)
        return np.searchsorted(self.ref, scores, side=\"right\") / float(len(self.ref))

# -------- Feature Engineering -------------------------------------------------
class AdvancedFeatureBuilder:
    \"\"\"Enhanced feature engineering with temporal, interaction, and statistical features\"\"\"
    
    def __init__(self, cfg: DetectorConfig):
        self.cfg = cfg
    
    def build(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Tuple[str, str, int]], pd.Series]:
        rows = []
        dwell_list: List[Tuple[str, str, int]] = []
        last_loc = pd.Series(index=df.index, dtype=\"object\")
        
        for i, row in df.iterrows():
            case_id = str(row.get(\"CASE_NO\", \"NA\"))
            points: List[Tuple[str, pd.Timestamp]] = []
            
            for col in WAREHOUSE_COLS + SITE_COLS:
                if col in row.index and pd.notna(row[col]):
                    dt = pd.to_datetime(row[col], errors=\"coerce\")
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
            amount = pd.to_numeric(row.get(\"AMOUNT\"), errors=\"coerce\")
            qty = pd.to_numeric(row.get(\"QTY\"), errors=\"coerce\")
            pkg = pd.to_numeric(row.get(\"PKG\"), errors=\"coerce\")
            
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
            amount_per_qty = amount / max(qty, 1) if pd.notna(amount) and pd.notna(qty) else np.nan
            qty_per_pkg = qty / max(pkg, 1) if pd.notna(qty) and pd.notna(pkg) else np.nan
            
            # Warehouse distribution
            n_warehouse = sum(1 for col in WAREHOUSE_COLS if col in row.index and pd.notna(row[col]))
            n_site = sum(1 for col in SITE_COLS if col in row.index and pd.notna(row[col]))
            
            rows.append({
                \"CASE_NO\": case_id,
                \"TOUCH_COUNT\": n_touch,
                \"TOTAL_DAYS\": total_days,
                \"AMOUNT\": amount,
                \"QTY\": qty,
                \"PKG\": pkg,
                \"AVG_DWELL\": avg_dwell,
                \"VELOCITY\": velocity,
                \"DAY_OF_WEEK\": day_of_week,
                \"MONTH\": month,
                \"QUARTER\": quarter,
                \"AMOUNT_PER_QTY\": amount_per_qty,
                \"QTY_PER_PKG\": qty_per_pkg,
                \"N_WAREHOUSE\": n_warehouse,
                \"N_SITE\": n_site,
            })
        
        feat = pd.DataFrame(rows).set_index(\"CASE_NO\", drop=True)
        return feat, dwell_list, last_loc

# -------- Deep Learning Models ------------------------------------------------
class AutoencoderAD:
    \"\"\"Autoencoder for Anomaly Detection\"\"\"
    
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
        \"\"\"Build autoencoder architecture\"\"\"
        if not TF_AVAILABLE:
            raise ImportError(\"TensorFlow not available\")
        
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
        \"\"\"Train autoencoder on normal data\"\"\"
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
        
        # Calculate reconstruction errors
        reconstructions = self.model.predict(X_scaled, verbose=0)
        mse = np.mean(np.square(X_scaled - reconstructions), axis=1)
        
        # Set threshold based on contamination
        self.threshold = np.percentile(mse, 100 * (1 - self.contamination))
        
        return self
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        \"\"\"Predict anomalies\"\"\"
        X_scaled = self.scaler.transform(X)
        reconstructions = self.model.predict(X_scaled, verbose=0)
        mse = np.mean(np.square(X_scaled - reconstructions), axis=1)
        
        y_pred = (mse > self.threshold).astype(int)
        scores = mse / (self.threshold + 1e-10)  # Normalized scores
        
        return y_pred, scores

class LSTMAD:
    \"\"\"LSTM-based Anomaly Detection for Time Series\"\"\"
    
    def __init__(self, sequence_length: int = 10, lstm_units: int = 50,
                 epochs: int = 50, batch_size: int = 32, contamination: float = 0.02):
        self.sequence_length = sequence_length
        self.lstm_units = lstm_units
        self.epochs = epochs
        self.batch_size = batch_size
        self.contamination = contamination
        self.model = None
        self.threshold = None
        self.scaler = StandardScaler()
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        \"\"\"Create sequences for LSTM\"\"\"
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i + self.sequence_length])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def _build_model(self, input_shape: Tuple):
        \"\"\"Build LSTM architecture\"\"\"
        if not TF_AVAILABLE:
            raise ImportError(\"TensorFlow not available\")
        
        model = models.Sequential([
            layers.LSTM(self.lstm_units, activation='relu', 
                       input_shape=input_shape, return_sequences=True),
            layers.Dropout(0.2),
            layers.LSTM(self.lstm_units // 2, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(input_shape[1])
        ])
        
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def fit(self, X: np.ndarray):
        \"\"\"Train LSTM on normal sequences\"\"\"
        X_scaled = self.scaler.fit_transform(X)
        X_seq, y_seq = self._create_sequences(X_scaled)
        
        if len(X_seq) < self.sequence_length:
            logger.warning(f\"Not enough samples for LSTM (need {self.sequence_length}, got {len(X_seq)})\")
            return self
        
        self.model = self._build_model((X_seq.shape[1], X_seq.shape[2]))
        self.model.fit(
            X_seq, y_seq,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=0.1,
            verbose=0
        )
        
        # Calculate prediction errors
        predictions = self.model.predict(X_seq, verbose=0)
        mse = np.mean(np.square(y_seq - predictions), axis=1)
        self.threshold = np.percentile(mse, 100 * (1 - self.contamination))
        
        return self
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        \"\"\"Predict anomalies\"\"\"
        X_scaled = self.scaler.transform(X)
        X_seq, y_seq = self._create_sequences(X_scaled)
        
        if len(X_seq) < self.sequence_length:
            return np.zeros(len(X)), np.zeros(len(X))
        
        predictions = self.model.predict(X_seq, verbose=0)
        mse = np.mean(np.square(y_seq - predictions), axis=1)
        
        # Pad predictions to match original length
        scores = np.concatenate([np.zeros(self.sequence_length), mse])
        y_pred = (scores > self.threshold).astype(int)
        
        return y_pred, scores / (self.threshold + 1e-10)

# -------- Advanced ML Detector ------------------------------------------------
class AdvancedMLDetector:
    \"\"\"Enhanced ML detector with boosting, stacking, and explainability\"\"\"
    
    def __init__(self, cfg: DetectorConfig):
        self.cfg = cfg
        self.models: Dict[str, Any] = {}
        self.ensemble_predictions: Dict[str, np.ndarray] = {}
        self.feature_names: List[str] = []
        self.shap_explainer = None
    
    def _winsorize(self, X: pd.DataFrame, p: float = 0.005) -> pd.DataFrame:
        \"\"\"Winsorize extreme values\"\"\"
        lo = X.quantile(p)
        hi = X.quantile(1 - p)
        return X.clip(lower=lo, upper=hi, axis=1)
    
    def _prepare_data(self, X: pd.DataFrame) -> pd.DataFrame:
        \"\"\"Prepare data for modeling\"\"\"
        X2 = X.replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
        X2 = self._winsorize(X2, 0.01)
        self.feature_names = list(X2.columns)
        
        if RobustScaler is not None:
            scaler = RobustScaler()
            Xs = pd.DataFrame(
                scaler.fit_transform(X2),
                index=X2.index,
                columns=X2.columns
            )
        else:
            Xs = X2
        
        return Xs
    
    def _fit_pyod_ensemble(self, X: np.ndarray) -> Dict[str, Any]:
        \"\"\"Fit PyOD ensemble models\"\"\"
        if not PYOD_AVAILABLE:
            return {}
        
        models = {
            \"ECOD\": ECOD(),
            \"COPOD\": COPOD(),
            \"HBOS\": HBOS(),
            \"IForest\": IForest(
                n_estimators=self.cfg.n_estimators,
                random_state=self.cfg.random_state,
                contamination=self.cfg.contamination
            ),
        }
        
        fitted = {}
        for name, model in models.items():
            try:
                model.fit(X)
                fitted[name] = model
            except Exception as e:
                logger.warning(f\"PyOD {name} failed: {e}\")
        
        return fitted
    
    def _fit_boosting_models(self, X: np.ndarray, y: np.ndarray = None) -> Dict[str, Any`,
  `description`: `Enhanced ML anomaly detector v4.0 with deep learning, SHAP explainability, and advanced ensemble methods`
}

