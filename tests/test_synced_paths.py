"""
Test shared synced path configuration between Stage 1 and Stage 2.

This test ensures that Stage 1 and Stage 2 use the same synced path configuration
to avoid path mismatches and ensure data consistency.
"""

from pathlib import Path

import pytest

from scripts.stage1_sync.data_synchronizer import resolve_synced_output_path
from scripts.stage2_derived.derived_columns_processor import resolve_synced_input_path


def test_stage1_stage2_shared_synced_path():
    """Test that Stage 1 and Stage 2 use the same synced path configuration."""
    # Test with default configuration
    stage1_path = resolve_synced_output_path("test_warehouse.xlsx")
    stage2_path = resolve_synced_input_path()

    # Both should resolve to the same directory structure
    assert stage1_path.parent == stage2_path.parent
    assert "synced" in str(stage1_path.parent)
    assert "synced" in str(stage2_path.parent)

    # Test with custom configuration
    custom_config = Path(__file__).parent.parent / "config" / "pipeline_config.yaml"
    if custom_config.exists():
        stage1_custom = resolve_synced_output_path(
            "test_warehouse.xlsx", config_path=custom_config
        )
        stage2_custom = resolve_synced_input_path(pipeline_config_path=custom_config)

        assert stage1_custom.parent == stage2_custom.parent


def test_synced_path_consistency():
    """Test that synced paths are consistent across different warehouse files."""
    warehouse_files = [
        "HVDC WAREHOUSE_HITACHI(HE).xlsx",
        "HVDC WAREHOUSE_SIMENSE(SIM).xlsx",
        "test_warehouse.xlsx",
    ]

    paths = []
    for warehouse_file in warehouse_files:
        path = resolve_synced_output_path(warehouse_file)
        paths.append(path.parent)

    # All should resolve to the same parent directory
    assert all(path == paths[0] for path in paths)


if __name__ == "__main__":
    pytest.main([__file__])
