"""Stage 3 헬퍼 함수들이 Core 헤더 매니저를 재사용하도록 제공합니다. / Stage 3 helpers delegating to the Core header manager."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from scripts.core import HEADER_MANAGER, HeaderManager


def _manager() -> HeaderManager:
    """공유 헤더 매니저를 반환합니다. / Return the shared header manager."""

    return HEADER_MANAGER


def normalize_columns(columns: Iterable[str]) -> pd.Index:
    """컬럼명을 정규화합니다. / Normalize column labels."""

    return _manager().clean_columns(columns)


def apply_column_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    """동의어를 해소하여 컬럼명을 통일합니다. / Resolve synonyms for column labels."""

    return _manager().apply_synonyms(df)
