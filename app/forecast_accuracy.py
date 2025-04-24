# Phase2.7_Stable_ForecastAccuracy (Enhanced Debugging for EXE Failures)

import pandas as pd
import os
from datetime import datetime
import traceback

# GUI-Compatible Accuracy Logic with Debug Logging and Safe Export Path
def process_forecast_accuracy(sales_file_path, consumption_file_path, export_dir=None):
    try:
        if export_dir is None:
            export_dir = os.path.join(os.path.expanduser("~"), "Desktop", "temple_export")

        os.makedirs(export_dir, exist_ok=True)

        debug_log = os.path.join(export_dir, "debug_log.txt")
        with open(debug_log, "w") as dbg:
            dbg.write("🔍 Function was called.\n")
            dbg.write(f"Sales file: {sales_file_path}\n")
            dbg.write(f"Consumption file: {consumption_file_path}\n")

        sales_df = pd.read_excel(sales_file_path)
        consumption_df = pd.read_excel(consumption_file_path)

        forecast = sales_df.groupby("Item")["Quantity"].sum().reset_index(name="ForecastedQty")
        actual = consumption_df.groupby("Item")["ConsumedQty"].sum().reset_index(name="ActualQty")

        merged = pd.merge(forecast, actual, on="Item", how="outer")
        merged["ForecastedQty"].fillna(0, inplace=True)
        merged["ActualQty"].fillna(0, inplace=True)

        # Updated Accuracy Calculation
        merged["Accuracy (%)"] = merged.apply(
            lambda row: round(100 - abs(row["ForecastedQty"] - row["ActualQty"]) / row["ActualQty"] * 100, 2)
            if row["ActualQty"] > 0 else 0,
            axis=1
        )
        merged["Accuracy (%)"] = merged["Accuracy (%)"].clip(lower=0, upper=100)

        out_file = os.path.join(export_dir, f"Forecast_vs_Actual_{datetime.now().strftime('%Y-%m-%d')}.xlsx")
        merged.to_excel(out_file, index=False)

        print(f"Forecast Accuracy Report saved at: {out_file}")
        return out_file

    except Exception as e:
        error_log_path = os.path.join(export_dir, "forecast_error.log")
        with open(error_log_path, "w") as f:
            f.write("❌ Forecast Accuracy Error Log\n")
            f.write(f"Sales file: {sales_file_path}\n")
            f.write(f"Consumption file: {consumption_file_path}\n\n")
            f.write(traceback.format_exc())
        return None

# Standalone test usage
if __name__ == '__main__':
    test_sales_path = 'data/test_sales.xlsx'
    test_consumption_path = 'data/test_consumption.xlsx'
    process_forecast_accuracy(test_sales_path, test_consumption_path)
