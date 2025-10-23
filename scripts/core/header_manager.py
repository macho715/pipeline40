# -*- coding: utf-8 -*-
"""헤더 정규화와 탐지를 통합 관리합니다. / Central manager for header normalization and detection."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
import unicodedata
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd

from .header_detector import HeaderDetector
from .header_normalizer import HeaderNormalizer
from .header_registry import HeaderRegistry, HVDC_HEADER_REGISTRY
from .semantic_matcher import MatchReport, SemanticMatcher


@dataclass
class HeaderManager:
    """헤더 정규화/탐지/매칭을 단일 인터페이스로 제공합니다. / Provide one-stop header normalization, detection, and matching."""

    registry: HeaderRegistry = field(default_factory=lambda: HVDC_HEADER_REGISTRY)
    normalizer: HeaderNormalizer = field(default_factory=HeaderNormalizer)
    detector: HeaderDetector = field(default_factory=HeaderDetector)
    matcher: SemanticMatcher = field(init=False)

    def __post_init__(self) -> None:
        """SemanticMatcher를 초기화합니다. / Initialize the semantic matcher."""

        self.matcher = SemanticMatcher(
            registry=self.registry,
            normalizer=self.normalizer,
        )

    # ------------------------------------------------------------------
    # Normalization helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _clean_label(label: str) -> str:
        """라벨의 공백과 폭을 정규화합니다. / Normalize whitespace and width for a label."""

        text = unicodedata.normalize("NFKC", str(label))
        text = re.sub(r"\s+", " ", text, flags=re.UNICODE)
        return text.strip()

    def clean_columns(self, columns: Sequence[str]) -> pd.Index:
        """컬럼 라벨을 정규화한 Index를 반환합니다. / Return normalized column Index."""

        return pd.Index([self._clean_label(col) for col in columns])

    def normalize_token(self, header: str) -> str:
        """매칭용 토큰을 생성합니다. / Produce a normalized token for matching."""

        return self.normalizer.normalize(header)

    # ------------------------------------------------------------------
    # Synonym handling
    # ------------------------------------------------------------------
    def apply_synonyms(self, df: pd.DataFrame) -> pd.DataFrame:
        """레지스트리에 정의된 대표 표기로 컬럼명을 통합합니다. / Harmonize column names to preferred aliases."""

        if df is None or df.empty and not df.columns.any():
            return df

        rename_map: Dict[str, str] = {}
        existing: Dict[str, str] = {}

        for column in df.columns:
            token = self.normalize_token(column)
            existing.setdefault(token, column)

        used_targets: set[str] = set()

        for semantic_key, definition in self.registry.definitions.items():
            preferred = self._clean_label(self.registry.get_preferred_alias(semantic_key))
            preferred_token = self.normalize_token(preferred)

            if preferred_token in existing:
                current = existing[preferred_token]
                cleaned = self._clean_label(current)
                target = cleaned or preferred
                if target not in used_targets and target != current:
                    rename_map[current] = target
                    used_targets.add(target)
                else:
                    used_targets.add(target)
                continue

            for alias in definition.aliases:
                alias_token = self.normalize_token(alias)
                if alias_token in existing:
                    current = existing[alias_token]
                    target = preferred
                    if target not in used_targets:
                        rename_map[current] = target
                        used_targets.add(target)
                    break

        if rename_map:
            df = df.rename(columns=rename_map)

        df.columns = self.clean_columns(df.columns)
        return df

    def prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """헤더 정규화와 동의어 통합을 동시에 수행합니다. / Clean and harmonize headers in one pass."""

        if df is None:
            return df
        df = df.copy()
        df.columns = self.clean_columns(df.columns)
        return self.apply_synonyms(df)

    # ------------------------------------------------------------------
    # Detection and matching
    # ------------------------------------------------------------------
    def detect_header_row(self, file_path: str, sheet_name: Optional[str] = None) -> Tuple[int, float]:
        """엑셀 파일에서 헤더 행을 추론합니다. / Detect the header row inside an Excel file."""

        return self.detector.detect_from_file(file_path, sheet_name=sheet_name)

    def match_columns(
        self,
        df: pd.DataFrame,
        semantic_keys: Optional[List[str]] = None,
        required_only: bool = False,
    ) -> MatchReport:
        """Semantic key 기반 컬럼 매칭 리포트를 생성합니다. / Build a semantic column matching report."""

        return self.matcher.match_dataframe(df, semantic_keys=semantic_keys, required_only=required_only)

    def find_column(self, df: pd.DataFrame, semantic_key: str, required: bool = False) -> Optional[str]:
        """특정 semantic key에 대응하는 컬럼을 찾습니다. / Find a column for the semantic key."""

        return self.matcher.find_column(df, semantic_key=semantic_key, required=required)

    # ------------------------------------------------------------------
    # Location inference
    # ------------------------------------------------------------------
    def get_canonical_locations(self, group: str) -> List[str]:
        """그룹의 대표 위치 라벨 목록을 제공합니다. / Return preferred location labels for a group."""

        canonical = [
            self._clean_label(self.registry.get_preferred_alias(key))
            for key in self.registry.get_semantic_keys_by_group(group)
        ]
        return canonical

    def infer_location_columns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """창고/현장 등 위치 컬럼을 능동적으로 탐지합니다. / Infer warehouse and site columns dynamically."""

        if df is None:
            return {"warehouse": [], "site": []}

        working = df.copy()
        working.columns = self.clean_columns(working.columns)
        normalized_map = {self.normalize_token(col): self._clean_label(col) for col in working.columns}

        def _collect(group: str) -> List[str]:
            preferred_order = self.get_canonical_locations(group)
            results: List[str] = []
            matched_tokens: set[str] = set()

            for definition in self.registry.get_definitions_by_group(group):
                preferred = self._clean_label(self.registry.get_preferred_alias(definition.semantic_key))
                preferred_token = self.normalize_token(preferred)
                if preferred_token in normalized_map:
                    label = normalized_map[preferred_token]
                    results.append(label)
                    matched_tokens.add(preferred_token)
                    continue
                for alias in definition.aliases:
                    alias_token = self.normalize_token(alias)
                    if alias_token in normalized_map and alias_token not in matched_tokens:
                        label = normalized_map[alias_token]
                        results.append(label)
                        matched_tokens.add(alias_token)
                        break

            # heuristic fallback based on preferred tokens
            preferred_tokens = [self.normalize_token(name) for name in preferred_order]
            for column in working.columns:
                token = self.normalize_token(column)
                if token in matched_tokens:
                    continue
                if any(pref in token for pref in preferred_tokens if pref):
                    results.append(self._clean_label(column))
                    matched_tokens.add(token)

            deduped = list(dict.fromkeys(results))
            order_index = {name: idx for idx, name in enumerate(preferred_order)}
            deduped.sort(key=lambda name: (order_index.get(name, len(order_index)), name))
            return deduped

        return {
            "warehouse": _collect("warehouse_location"),
            "site": _collect("site_location"),
        }


_DEFAULT_HEADER_MANAGER: Optional[HeaderManager] = None


def get_header_manager() -> HeaderManager:
    """전역 헤더 매니저 인스턴스를 반환합니다. / Return the shared header manager instance."""

    global _DEFAULT_HEADER_MANAGER
    if _DEFAULT_HEADER_MANAGER is None:
        _DEFAULT_HEADER_MANAGER = HeaderManager()
    return _DEFAULT_HEADER_MANAGER


HEADER_MANAGER = get_header_manager()

__all__ = ["HeaderManager", "HEADER_MANAGER", "get_header_manager"]
