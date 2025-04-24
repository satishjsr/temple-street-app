import pandas as pd
import os
from datetime import datetime
import traceback

def process_forecast_accuracy(sales_file_path, consumption_file_path, export_dir="export"):
    try:
        sales_df = pd.read_excel(sales_file_path)
        consumption_df = pd.read_excel(consumption_file_path)

        forecast = sales_df.groupby("Item")["Quantity"].sum().reset_index(name="ForecastedQty")
        actual = consumption_df.groupby("Item")["ConsumedQty"].sum().reset_index(name="ActualQty")

        merged = pd.merge(forecast, actual, on="Item", how="outer")
        merged["ForecastedQty"].fillna(0, inplace=True)
        merged["ActualQty"].fillna(0, inplace=True)

        merged["Accuracy (%)"] = merged.apply(
            lambda row: round(100 - abs(row["ForecastedQty"] - row["ActualQty"]) / row["ActualQty"] * 100, 2)
            if row["ActualQty"] > 0 else 0,
            axis=1
        )
        merged["Accuracy (%)"] = merged["Accuracy (%)"].clip(lower=0, upper=100)

        os.makedirs(export_dir, exist_ok=True)
        out_file = os.path.join(export_dir, f"Forecast_vs_Actual_{datetime.now().strftime('%Y-%m-%d')}.xlsx")
        merged.to_excel(out_file, index=False)

        return out_file

    except Exception as e:
        os.makedirs(export_dir, exist_ok=True)
        error_log = os.path.join(export_dir, "forecast_error.log")
        with open(error_log, "w") as f:
            f.write("❌ Forecast Accuracy Error:\n")
            f.write(traceback.format_exc())
        return None
