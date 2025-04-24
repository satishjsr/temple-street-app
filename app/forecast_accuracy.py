# Phase2.7_Stable_ForecastAccuracy (Final Version from GUI App Integration)

import pandas as pd
import os
from datetime import datetime

# GUI-Compatible Accuracy Logic

def process_forecast_accuracy(sales_file_path, consumption_file_path, export_dir="export"):
    try:
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

        os.makedirs(export_dir, exist_ok=True)
        out_file = os.path.join(export_dir, f"Forecast_vs_Actual_{datetime.now().strftime('%Y-%m-%d')}.xlsx")
        merged.to_excel(out_file, index=False)

        print(f"Forecast Accuracy Report saved at: {out_file}")
        return out_file

    except Exception as e:
        print(f"❌ Forecast Accuracy Error: {e}")
        return None

# Standalone test usage
if __name__ == '__main__':
    test_sales_path = 'data/test_sales.xlsx'
    test_consumption_path = 'data/test_consumption.xlsx'
    process_forecast_accuracy(test_sales_path, test_consumption_path)
