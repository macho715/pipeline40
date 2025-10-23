# -*- coding: utf-8 -*-
"""
HVDC Pipeline Core Module
=========================

Central header matching and detection system for all pipeline stages.
This module provides robust, flexible header matching with zero hardcoding.

Main Components:
- header_detector: Automatically finds where headers start in Excel files
- header_normalizer: Normalizes header names handling all edge cases
- semantic_matcher: Matches headers based on meaning, not exact strings
- header_registry: Configuration for semantic mappings across all stages
- data_parser: Core data parsing utilities (Stack_Status, SQM, unit conversions)
"""

from .header_detector import HeaderDetector, detect_header_row
from .header_normalizer import HeaderNormalizer, normalize_header
from .semantic_matcher import SemanticMatcher, find_header_by_meaning
from .header_registry import HeaderRegistry, HVDC_HEADER_REGISTRY, HeaderCategory, HeaderDefinition
from .data_parser import parse_stack_status, calculate_sqm, convert_mm_to_cm, map_stack_status

__version__ = "1.0.0"
__all__ = [
    "HeaderDetector",
    "detect_header_row",
    "HeaderNormalizer",
    "normalize_header",
    "SemanticMatcher",
    "find_header_by_meaning",
    "HeaderRegistry",
    "HVDC_HEADER_REGISTRY",
    "HeaderCategory",
    "HeaderDefinition",
    "parse_stack_status",
    "calculate_sqm",
    "convert_mm_to_cm",
    "map_stack_status",
]
