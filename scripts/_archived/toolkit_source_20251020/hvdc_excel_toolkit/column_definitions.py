# -*- coding: utf-8 -*-
"""파생 컬럼 정의 상수 모듈/Derived column definition constants module."""

from __future__ import annotations

from typing import Final, List

WAREHOUSE_COLUMNS: Final[List[str]] = [
    "DHL Warehouse",
    "DSV Indoor",
    "DSV Al Markaz",
    "Hauler Indoor",
    "DSV Outdoor",
    "DSV MZP",
    "HAULER",
    "JDN MZD",
    "MOSB",
    "AAA  Storage",
]

SITE_COLUMNS: Final[List[str]] = ["MIR", "SHU", "AGI", "DAS"]

STATUS_WAREHOUSE_COLUMN: Final[str] = "Status_WAREHOUSE"
STATUS_SITE_COLUMN: Final[str] = "Status_SITE"
STATUS_CURRENT_COLUMN: Final[str] = "Status_Current"
STATUS_LOCATION_COLUMN: Final[str] = "Status_Location"
STATUS_LOCATION_DATE_COLUMN: Final[str] = "Status_Location_Date"
STATUS_STORAGE_COLUMN: Final[str] = "Status_Storage"
WH_HANDLING_COLUMN: Final[str] = "wh handling"
SITE_HANDLING_COLUMN: Final[str] = "site  handling"
TOTAL_HANDLING_COLUMN: Final[str] = "total handling"
MINUS_COLUMN: Final[str] = "minus"
FINAL_HANDLING_COLUMN: Final[str] = "final handling"
SQM_COLUMN: Final[str] = "SQM"
STACK_STATUS_COLUMN: Final[str] = "Stack_Status"

DERIVED_COLUMNS: Final[List[str]] = [
    STATUS_WAREHOUSE_COLUMN,
    STATUS_SITE_COLUMN,
    STATUS_CURRENT_COLUMN,
    STATUS_LOCATION_COLUMN,
    STATUS_LOCATION_DATE_COLUMN,
    STATUS_STORAGE_COLUMN,
    WH_HANDLING_COLUMN,
    SITE_HANDLING_COLUMN,
    TOTAL_HANDLING_COLUMN,
    MINUS_COLUMN,
    FINAL_HANDLING_COLUMN,
    SQM_COLUMN,
    STACK_STATUS_COLUMN,
]
