# -*- coding: utf-8 -*-
"""
Header Registry Module
======================

This module defines the semantic meanings of all headers used across
the HVDC pipeline. Instead of hardcoding exact column names, we define
what each column *means* and provide multiple ways that meaning could
be expressed in an Excel file.

The registry acts as a central configuration that all pipeline stages
can reference. When a new Excel format arrives with different header
names, you only need to update this registry rather than changing code
in multiple places.

Semantic Categories:
- IDENTIFICATION: Headers that identify unique records (Case No, ID, etc.)
- TEMPORAL: Headers related to dates and times (ETA, ETD, etc.)
- LOCATION: Headers for physical locations (Warehouse, Site, etc.)
- QUANTITY: Headers for measurements and counts (QTY, SQM, etc.)
- STATUS: Headers indicating current state (Status, Condition, etc.)
- DESCRIPTION: Headers with textual descriptions
- DERIVED: Calculated headers added by the pipeline
"""

from typing import Dict, List, Set
from dataclasses import dataclass, field
from enum import Enum


class HeaderCategory(Enum):
    """
    Categories for grouping semantically similar headers.

    These categories help organize the large number of headers in the
    HVDC pipeline and make it easier to understand the data model.
    """

    IDENTIFICATION = "identification"  # Case No, Item No, etc.
    TEMPORAL = "temporal"  # ETA, ETD, dates
    LOCATION = "location"  # Warehouses, sites
    QUANTITY = "quantity"  # QTY, amount, volume
    STATUS = "status"  # Status fields
    DESCRIPTION = "description"  # Text descriptions
    HANDLING = "handling"  # Handling operations
    DERIVED = "derived"  # Calculated fields
    METADATA = "metadata"  # System fields


@dataclass
class HeaderDefinition:
    """
    Complete definition of a header's semantic meaning.

    This class captures everything we need to know about a header to
    enable flexible matching across different Excel formats.

    Attributes:
        semantic_key: The canonical name we use internally (e.g., 'case_number')
        category: Which category this header belongs to
        aliases: All possible ways this header might appear in Excel files
        description: Human-readable explanation of what this header means
        required: Whether this header must exist in the file
        data_type: Expected data type (str, int, float, datetime)
    """

    semantic_key: str
    category: HeaderCategory
    aliases: List[str] = field(default_factory=list)
    description: str = ""
    required: bool = False
    data_type: str = "str"  # str, int, float, datetime, bool

    def matches_any_alias(self, normalized_name: str) -> bool:
        """
        Check if a normalized header name matches any of this header's aliases.

        Args:
            normalized_name: A header name that has been normalized

        Returns:
            True if the name matches any alias
        """
        return normalized_name in [alias.lower().replace(" ", "") for alias in self.aliases]


class HeaderRegistry:
    """
    Central registry of all header definitions used in the HVDC pipeline.

    This registry serves as the single source of truth for what headers
    exist and how they should be matched. All pipeline stages reference
    this registry when looking for columns in Excel files.

    The registry supports:
    - Semantic lookup (find header by meaning)
    - Category filtering (get all temporal headers)
    - Alias expansion (find all ways a header could be written)
    - Validation (check if required headers are present)
    """

    def __init__(self):
        """
        Initialize the registry with all HVDC pipeline header definitions.

        This constructor builds the complete registry of headers. Each header
        is defined with its semantic meaning, possible variations, and metadata
        that helps with matching and validation.
        """
        self.definitions: Dict[str, HeaderDefinition] = {}
        self._initialize_definitions()

    def _initialize_definitions(self):
        """
        Define all headers used across the HVDC pipeline.

        This is the core configuration where all headers are registered.
        When new Excel formats arrive, you add aliases here rather than
        modifying code throughout the pipeline.
        """

        # ===== IDENTIFICATION HEADERS =====
        # These headers uniquely identify records

        self.register(
            HeaderDefinition(
                semantic_key="case_number",
                category=HeaderCategory.IDENTIFICATION,
                aliases=[
                    "Case No",
                    "Case No.",
                    "CASE NO",
                    "case number",
                    "Case Number",
                    "Case_No",
                    "CaseNo",
                    "case-no",
                    "CASE_NUMBER",
                    "case_no",
                    "케이스번호",
                    "케이스 번호",
                    "Case",
                ],
                description="Unique identifier for each case/shipment",
                required=True,
                data_type="str",
            )
        )

        self.register(
            HeaderDefinition(
                semantic_key="item_number",
                category=HeaderCategory.IDENTIFICATION,
                aliases=[
                    "No",
                    "No.",
                    "Number",
                    "Item No",
                    "Item Number",
                    "NO",
                    "Num",
                    "Item_No",
                    "ItemNo",
                    "번호",
                    "아이템번호",
                ],
                description="Sequential item number or index",
                required=False,
                data_type="int",
            )
        )

        # ===== TEMPORAL HEADERS =====
        # Date and time related fields

        self.register(
            HeaderDefinition(
                semantic_key="etd_atd",
                category=HeaderCategory.TEMPORAL,
                aliases=[
                    "ETD/ATD",
                    "ETD",
                    "ATD",
                    "ETD_ATD",
                    "Estimated Departure",
                    "Actual Departure",
                    "Departure Date",
                    "Departure",
                    "출발일",
                    "ETD-ATD",
                    "etd/atd",
                    "ETD / ATD",
                ],
                description="Estimated/Actual Time of Departure",
                required=False,
                data_type="datetime",
            )
        )

        self.register(
            HeaderDefinition(
                semantic_key="eta_ata",
                category=HeaderCategory.TEMPORAL,
                aliases=[
                    "ETA/ATA",
                    "ETA",
                    "ATA",
                    "ETA_ATA",
                    "Estimated Arrival",
                    "Actual Arrival",
                    "Arrival Date",
                    "Arrival",
                    "도착일",
                    "ETA-ATA",
                    "eta/ata",
                    "ETA / ATA",
                ],
                description="Estimated/Actual Time of Arrival",
                required=False,
                data_type="datetime",
            )
        )

        # ===== LOCATION HEADERS - WAREHOUSES =====
        # Physical warehouse and storage locations

        warehouse_locations = [
            (
                "dhl_wh",
                "DHL WH",
                [
                    "DHL WH",
                    "DHL",
                    "DHL Warehouse",
                    "DHL_WH",
                    "DHL_Warehouse",
                    "DHL창고",
                    "DHL 창고",
                ],
            ),
            (
                "dsv_indoor",
                "DSV Indoor",
                ["DSV Indoor", "DSV_Indoor", "DSV In", "DSV실내", "DSV 실내", "DSV-Indoor"],
            ),
            (
                "dsv_al_markaz",
                "DSV Al Markaz",
                [
                    "DSV Al Markaz",
                    "DSV_Al_Markaz",
                    "DSV AlMarkaz",
                    "DSV Al-Markaz",
                    "DSV Markaz",
                    "Al Markaz",
                ],
            ),
            (
                "dsv_outdoor",
                "DSV Outdoor",
                ["DSV Outdoor", "DSV_Outdoor", "DSV Out", "DSV실외", "DSV 실외", "DSV-Outdoor"],
            ),
            ("dsv_mzp", "DSV MZP", ["DSV MZP", "DSV_MZP", "MZP", "DSV-MZP"]),
            (
                "jdn_mzd",
                "JDN MZD",
                ["JDN MZD", "JDN_MZD", "JDN-MZD", "JDN", "MZD", "JDN창고", "MZD창고"],
            ),
            (
                "hauler_indoor",
                "Hauler Indoor",
                [
                    "Hauler Indoor",
                    "Hauler_Indoor",
                    "Hauler In",
                    "HAULER Indoor",
                    "HAULER",
                    "Hauler",
                    "운송사실내",
                ],
            ),
            (
                "aaa_storage",
                "AAA Storage",
                ["AAA Storage", "AAA  Storage", "AAA_Storage", "AAA", "AAA창고", "AAA 창고"],
            ),
            ("mosb", "MOSB", ["MOSB", "MOS B", "MOS-B", "MOSB창고"]),
        ]

        for key, desc, aliases in warehouse_locations:
            self.register(
                HeaderDefinition(
                    semantic_key=key,
                    category=HeaderCategory.LOCATION,
                    aliases=aliases,
                    description=desc,
                    required=False,
                    data_type="datetime",
                )
            )

        # ===== LOCATION HEADERS - SITES =====
        # Final installation sites

        site_locations = [
            ("mir", "MIR Site", ["MIR", "MIR Site", "MIR_Site", "MIR사이트"]),
            ("shu", "SHU Site", ["SHU", "SHU Site", "SHU_Site", "SHU사이트"]),
            ("agi", "AGI Site", ["AGI", "AGI Site", "AGI_Site", "AGI사이트"]),
            ("das", "DAS Site", ["DAS", "DAS Site", "DAS_Site", "DAS사이트"]),
            ("shifting", "Shifting", ["Shifting", "SHIFTING", "Shift", "이동"]),
        ]

        for key, desc, aliases in site_locations:
            self.register(
                HeaderDefinition(
                    semantic_key=key,
                    category=HeaderCategory.LOCATION,
                    aliases=aliases,
                    description=desc,
                    required=False,
                    data_type="datetime",
                )
            )

        # ===== DESCRIPTION HEADERS =====

        self.register(
            HeaderDefinition(
                semantic_key="description",
                category=HeaderCategory.DESCRIPTION,
                aliases=[
                    "Description",
                    "Desc",
                    "DESC",
                    "Detail",
                    "Details",
                    "Name",
                    "Item Name",
                    "Item Description",
                    "설명",
                    "상세",
                    "Description/명칭",
                ],
                description="Textual description of the item",
                required=False,
                data_type="str",
            )
        )

        # ===== QUANTITY HEADERS =====

        quantity_fields = [
            (
                "quantity",
                "Quantity",
                ["QTY", "Qty", "Quantity", "Q'ty", "Qty.", "수량", "QUANTITY", "Amount", "Count"],
            ),
            (
                "sqm",
                "Square Meters",
                ["SQM", "sqm", "Square Meters", "㎡", "면적", "Square_Meters", "SQ M", "SQ.M"],
            ),
            (
                "weight",
                "Weight",
                ["Weight", "WT", "Wt", "무게", "중량", "WEIGHT", "Weight(kg)", "Weight (kg)"],
            ),
            (
                "volume",
                "Volume",
                ["Volume", "Vol", "부피", "VOLUME", "Vol.", "CBM", "Volume(m3)", "Volume (m3)"],
            ),
            # === DIMENSIONS (cm) ===
            (
                "length_cm",
                "Length in cm",
                [
                    "L(CM)",
                    "L (CM)",
                    "Length (cm)",
                    "Length(cm)",
                    "L CM",
                    "Length",
                    "L(mm)",
                    "L(MM)",
                    "Length (mm)",
                    "Length(mm)",
                    "L MM",  # mm도 포함, 후처리에서 cm 변환
                ],
            ),
            (
                "width_cm",
                "Width in cm",
                [
                    "W(CM)",
                    "W (CM)",
                    "Width (cm)",
                    "Width(cm)",
                    "W CM",
                    "Width",
                    "W(mm)",
                    "W(MM)",
                    "Width (mm)",
                    "Width(mm)",
                    "W MM",  # mm도 포함, 후처리에서 cm 변환
                ],
            ),
            (
                "height_cm",
                "Height in cm",
                [
                    "H(CM)",
                    "H (CM)",
                    "Height (cm)",
                    "Height(cm)",
                    "H CM",
                    "Height",
                    "H(mm)",
                    "H(MM)",
                    "Height (mm)",
                    "Height(mm)",
                    "H MM",  # mm도 포함, 후처리에서 cm 변환
                ],
            ),
        ]

        for key, desc, aliases in quantity_fields:
            self.register(
                HeaderDefinition(
                    semantic_key=key,
                    category=HeaderCategory.QUANTITY,
                    aliases=aliases,
                    description=desc,
                    required=False,
                    data_type="float",
                )
            )

        # ===== STATUS HEADERS =====

        status_fields = [
            (
                "status_warehouse",
                "Warehouse Status",
                [
                    "Status_WAREHOUSE",
                    "Status WAREHOUSE",
                    "Warehouse Status",
                    "WH Status",
                    "창고상태",
                    "Status-WH",
                ],
            ),
            (
                "status_site",
                "Site Status",
                ["Status_SITE", "Status SITE", "Site Status", "사이트상태", "Status-SITE"],
            ),
            (
                "status_current",
                "Current Status",
                ["Status_Current", "Current Status", "Status", "현재상태", "Current_Status"],
            ),
            (
                "status_location",
                "Current Location",
                [
                    "Status_Location",
                    "Location",
                    "Current Location",
                    "위치",
                    "현재위치",
                    "Status-Location",
                ],
            ),
            (
                "status_location_date",
                "Location Date",
                ["Status_Location_Date", "Location Date", "위치일자", "Status Location Date"],
            ),
            (
                "status_storage",
                "Storage Status",
                ["Status_Storage", "Storage Status", "Storage", "저장상태", "보관상태"],
            ),
            (
                "stack_status",
                "Stack Status",
                ["Stack_Status", "Stack Status", "Stacking", "적재상태", "Stack-Status"],
            ),
            (
                "stackability_text",
                "Stackability Text",
                [
                    "Stackability",
                    "Stackable",
                    "Stack ability",
                    "Stack status",
                    "Stack",
                    "Stackability note",
                    "Stackable note",
                    "적재가능성",
                    "적재상태",
                ],
            ),
        ]

        for key, desc, aliases in status_fields:
            self.register(
                HeaderDefinition(
                    semantic_key=key,
                    category=HeaderCategory.STATUS,
                    aliases=aliases,
                    description=desc,
                    required=False,
                    data_type="str",
                )
            )

        # ===== HANDLING HEADERS =====

        handling_fields = [
            (
                "wh_handling",
                "Warehouse Handling",
                [
                    "wh handling",
                    "WH Handling",
                    "Warehouse Handling",
                    "wh_handling",
                    "창고핸들링",
                    "WH-Handling",
                ],
            ),
            (
                "site_handling",
                "Site Handling",
                [
                    "site handling",
                    "site  handling",
                    "Site Handling",
                    "site_handling",
                    "사이트핸들링",
                    "Site-Handling",
                ],
            ),
            (
                "total_handling",
                "Total Handling",
                [
                    "total handling",
                    "Total Handling",
                    "total_handling",
                    "전체핸들링",
                    "Total-Handling",
                ],
            ),
            (
                "final_handling",
                "Final Handling",
                [
                    "final handling",
                    "Final Handling",
                    "final_handling",
                    "최종핸들링",
                    "Final-Handling",
                ],
            ),
            ("minus", "Minus/Deduction", ["minus", "Minus", "MINUS", "차감", "-"]),
        ]

        for key, desc, aliases in handling_fields:
            self.register(
                HeaderDefinition(
                    semantic_key=key,
                    category=HeaderCategory.HANDLING,
                    aliases=aliases,
                    description=desc,
                    required=False,
                    data_type="float",
                )
            )

        # ===== DERIVED HEADERS =====
        # These are calculated by the pipeline, not present in source data

        # Note: Derived headers don't need aliases because they're created
        # by the pipeline itself, not matched from Excel files

    def register(self, definition: HeaderDefinition):
        """
        Register a new header definition in the registry.

        Args:
            definition: The header definition to register
        """
        self.definitions[definition.semantic_key] = definition

    def get_definition(self, semantic_key: str) -> HeaderDefinition:
        """
        Get the definition for a specific semantic key.

        Args:
            semantic_key: The internal semantic key

        Returns:
            The header definition

        Raises:
            KeyError: If the semantic key is not registered
        """
        if semantic_key not in self.definitions:
            raise KeyError(f"No header definition found for '{semantic_key}'")
        return self.definitions[semantic_key]

    def get_aliases(self, semantic_key: str) -> List[str]:
        """
        Get all possible aliases for a semantic key.

        Args:
            semantic_key: The internal semantic key

        Returns:
            List of all aliases that could match this header
        """
        definition = self.get_definition(semantic_key)
        return definition.aliases

    def get_by_category(self, category: HeaderCategory) -> List[HeaderDefinition]:
        """
        Get all header definitions in a specific category.

        Args:
            category: The category to filter by

        Returns:
            List of header definitions in that category
        """
        return [defn for defn in self.definitions.values() if defn.category == category]

    def get_required_headers(self) -> List[str]:
        """
        Get list of all required header semantic keys.

        Returns:
            List of semantic keys that must be present
        """
        return [key for key, defn in self.definitions.items() if defn.required]

    def get_all_semantic_keys(self) -> List[str]:
        """
        Get all registered semantic keys.

        Returns:
            List of all semantic keys in the registry
        """
        return list(self.definitions.keys())


# Global registry instance that all pipeline stages can import and use
HVDC_HEADER_REGISTRY = HeaderRegistry()


if __name__ == "__main__":
    """
    Test and demonstration of the header registry.
    """

    print("=" * 60)
    print("HVDC Header Registry - Configuration Summary")
    print("=" * 60)

    registry = HVDC_HEADER_REGISTRY

    # Show statistics by category
    print("\nHeaders by Category:")
    print("-" * 60)

    for category in HeaderCategory:
        headers = registry.get_by_category(category)
        print(f"\n{category.value.upper():20s}: {len(headers):3d} headers")

        # Show first 3 examples
        for defn in headers[:3]:
            aliases_preview = ", ".join(defn.aliases[:3])
            if len(defn.aliases) > 3:
                aliases_preview += f" ... (+{len(defn.aliases)-3} more)"
            print(f"  • {defn.semantic_key:20s} → {aliases_preview}")

    # Show required headers
    print("\n" + "=" * 60)
    print("Required Headers:")
    print("-" * 60)

    required = registry.get_required_headers()
    for key in required:
        defn = registry.get_definition(key)
        print(f"  • {key:20s} - {defn.description}")

    # Demonstrate alias lookup
    print("\n" + "=" * 60)
    print("Example Alias Mappings:")
    print("-" * 60)

    examples = ["case_number", "eta_ata", "dhl_warehouse", "sqm"]

    for key in examples:
        defn = registry.get_definition(key)
        print(f"\n{key} ({defn.category.value}):")
        for i, alias in enumerate(defn.aliases[:5], 1):
            print(f"  {i}. '{alias}'")
        if len(defn.aliases) > 5:
            print(f"  ... and {len(defn.aliases)-5} more variations")

    print("\n" + "=" * 60)
    print(f"Total Headers Registered: {len(registry.definitions)}")
    print("=" * 60)
