import pandas as pd
import os
from datetime import datetime

print("=" * 45)
print("Temple Street Ordering System v1.0.0")
print("=" * 45)
print("✅ Forecast Engine Initialized")
print("📦 Loading purchase plan...")

# Step 1: Ask for file input
file_path = input("\n📂 Enter full path of the sales Excel file (.xlsx): ")

# Step 2: Validate and read file
if not os.path.exists(file_path):
    print("\n❌ File not found. Please check the path and try again.")
else:
    try:
        df = pd.read_excel(file_path)
        print("\n🔍 File loaded successfully. Rows:", len(df))

        # Step 3: Placeholder processing (we'll add actual logic later)
        print("\n📈 Forecasting raw material needs...")
        df["Forecast"] = "Coming Soon"

        # Step 4: Save output
        output_dir = "export"
        os.makedirs(output_dir, exist_ok=True)
        output_file = f"{output_dir}/Temple_Street_Plan_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n✅ Forecast saved to: {output_file}")

    except Exception as e:
        print("\n🚫 Error reading file:", e)

input("\nPress Enter to exit...")
