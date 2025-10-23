import argparse
import sys
import pandas as pd

from hvdc_excel_toolkit import derived_columns_processor as dcp
from hvdc_excel_toolkit import hvdc_excel_reporter_final_sqm_rev as reporter

def main():
    parser = argparse.ArgumentParser(prog="hvdc-cli", description="HVDC Excel Toolkit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("derive", help="Run Stage 2 derived columns on an input Excel file")
    p1.add_argument("--input", required=True, help="Path to synced Excel (.xlsx)")
    p1.add_argument("--output", required=True, help="Path to write derived output Excel (.xlsx)")

    p2 = sub.add_parser("report", help="Run final SQM reporter")
    p2.add_argument("--hitachi", required=False, help="Path to HITACHI Excel (.xlsx)")
    p2.add_argument("--simense", required=False, help="Path to SIMENSE Excel (.xlsx)")
    p2.add_argument("--invoice", required=False, help="Optional passthrough invoice Excel (.xlsx)")
    p2.add_argument("--output-dir", required=True, help="Directory to write report artifacts")

    args = parser.parse_args()

    if args.cmd == "derive":
        # Minimal pathway using the library function
        df = pd.read_excel(args.input, engine="openpyxl")
        out = dcp.calculate_derived_columns(df)
        out.to_excel(args.output, index=False)
        print(f"[OK] Derived columns saved → {args.output}")
    elif args.cmd == "report":
        # Use class if present
        calc = reporter.CorrectedWarehouseIOCalculator()
        if args.hitachi:
            calc.hitachi_file = args.hitachi
        if args.simense:
            calc.simense_file = args.simense
        if args.invoice:
            calc.invoice_file = args.invoice
        data = calc.load_real_hvdc_data()
        # Trigger core flows available in the reporter module
        # Many functions are encapsulated; here we only load & exit to confirm wiring.
        print(f"[OK] Loaded {len(data)} rows. Proceed with module-native methods executed in your environment.")
        print("Note: The bundled reporter keeps original APIs; call its methods inside Python for full workflow.")
        print("Example: from hvdc_excel_toolkit.hvdc_excel_reporter_final_sqm_rev import CorrectedWarehouseIOCalculator")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()