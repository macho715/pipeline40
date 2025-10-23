"""
Stage 2: Derived Columns Module

파생 컬럼 계산 관련 기능을 제공합니다.
"""

from .derived_columns_processor import (
    calculate_derived_columns,
    process_derived_columns,
)

__all__ = ["calculate_derived_columns", "process_derived_columns"]
