import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
from scripts.stage3_report.report_generator import CorrectedWarehouseIOCalculator


def test_vectorized_inbound_retains_external_arrivals_for_transfer_destinations():
    calculator = CorrectedWarehouseIOCalculator(use_vectorized=True)

    warehouse_data = {column: [None, None] for column in calculator.warehouse_columns}
    warehouse_data["DSV Indoor"][0] = "2023-02-10"
    warehouse_data["DSV Al Markaz"][0] = "2023-02-10"
    warehouse_data["DSV Al Markaz"][1] = "2023-02-12"

    data = {"Pkg": [10, 5]}
    data.update(warehouse_data)

    df = pd.DataFrame(data)

    inbound_result = calculator._calculate_warehouse_inbound_vectorized(df)

    assert inbound_result["total_inbound"] == 15
    assert inbound_result["by_warehouse"]["DSV Indoor"] == 10
    assert inbound_result["by_warehouse"]["DSV Al Markaz"] == 5

    inbound_items = pd.DataFrame(inbound_result["inbound_items"])
    assert not inbound_items.empty
    assert (
        inbound_items[
            (inbound_items["Warehouse"] == "DSV Al Markaz")
            & (inbound_items["Inbound_Date"] == pd.Timestamp("2023-02-10"))
        ]
        .empty
    )

    al_markaz_external = inbound_items[
        (inbound_items["Warehouse"] == "DSV Al Markaz")
        & (inbound_items["Inbound_Date"] == pd.Timestamp("2023-02-12"))
    ]
    assert not al_markaz_external.empty
    assert al_markaz_external.iloc[0]["Pkg_Quantity"] == 5

    warehouse_transfers = inbound_result["warehouse_transfers"]
    assert any(
        transfer["to_warehouse"] == "DSV Al Markaz" and transfer.get("Row_ID") == 0
        for transfer in warehouse_transfers
    )
