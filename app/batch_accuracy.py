# Virtual Batch Accuracy Module (Integrated with Forecast Accuracy UI)
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load batch master table (replace with uploaded version in deployment)
batch_master = pd.DataFrame({
    "Raw Material Name": [
        "batch parantha dough",
        "batch amritsari kulcha stuffing aloo pyaz",
        "rm mint chutney",
        "batch chole masala gravy"
    ],
    "Linked Menu Items": [
        ["Murthal Parantha", "Parantha"],
        ["Amritsari Kulcha"],
        ["Aloo Chaat", "Chole Bhature", "Rajma Chawal"],
        ["Chole Bhature"]
    ],
    "Consumption Per Sale Unit": [120, 80, 20, 150],
    "Unit": ["GM", "GM", "GM", "GM"]
})

# Step 2: Load POS Sales Data (from Petpooja)
sales_data = pd.DataFrame({
    "Item Name": ["Murthal Parantha", "Amritsari Kulcha", "Chole Bhature", "Rajma Chawal"],
    "Quantity Sold": [480, 350, 270, 180]
})

# Step 3: Load Forecasted Batch Quantities (from Final Forecast file)
forecast_batch = pd.DataFrame({
    "Raw Material": [
        "batch parantha dough",
        "batch amritsari kulcha stuffing aloo pyaz",
        "rm mint chutney",
        "batch chole masala gravy"
    ],
    "Forecast Quantity": [60000, 28000, 16000, 40500],
    "Unit": ["GM", "GM", "GM", "GM"]
})

# Step 4: Calculate virtual batch consumption
def calculate_virtual_batch_consumption(batch_master, sales_data):
    records = []
    for _, row in batch_master.iterrows():
        total_virtual_consumption = 0
        for menu_item in row['Linked Menu Items']:
            matched = sales_data[sales_data['Item Name'].str.lower() == menu_item.lower()]
            if not matched.empty:
                qty_sold = matched.iloc[0]['Quantity Sold']
                total_virtual_consumption += qty_sold * row['Consumption Per Sale Unit']
        records.append({
            'Raw Material': row['Raw Material Name'],
            'Unit': row['Unit'],
            'Virtual Quantity Used': total_virtual_consumption
        })
    return pd.DataFrame(records)

# Step 5: Merge with Forecast and calculate accuracy
virtual_usage = calculate_virtual_batch_consumption(batch_master, sales_data)
merged = pd.merge(forecast_batch, virtual_usage, on=['Raw Material', 'Unit'], how='outer')
merged['Forecast Quantity'] = merged['Forecast Quantity'].fillna(0)
merged['Virtual Quantity Used'] = merged['Virtual Quantity Used'].fillna(0)
merged['Difference'] = merged['Virtual Quantity Used'] - merged['Forecast Quantity']
merged['% Error'] = (merged['Difference'] / merged['Forecast Quantity'].replace(0, 1)) * 100
merged['Status'] = merged['% Error'].apply(
    lambda x: 'Accurate' if abs(x) <= 10 else ('Over Forecasted' if x < -10 else 'Under Forecasted')
)

# Step 6: Display Batch Accuracy Report
def display_batch_accuracy_ui(df):
    print("\n\n====== Batch Forecast Accuracy Report ======")
    print(df[['Raw Material', 'Forecast Quantity', 'Virtual Quantity Used', 'Difference', '% Error', 'Status']])

# Step 7: Generate Excel + Charts
def export_accuracy_report_with_chart(df, filename="Batch_Accuracy_Report.xlsx"):
    # Save to Excel
    df.to_excel(filename, index=False)

    # Create chart
    plt.figure(figsize=(10, 6))
    plt.bar(df['Raw Material'], df['Forecast Quantity'], label='Forecast', alpha=0.7)
    plt.bar(df['Raw Material'], df['Virtual Quantity Used'], label='Used', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Quantity (GM)')
    plt.title('Batch Forecast vs Virtual Usage')
    plt.legend()
    plt.tight_layout()
    chart_path = filename.replace(".xlsx", ".png")
    plt.savefig(chart_path)
    print(f"\nReport saved to: {filename}\nChart saved to: {chart_path}")

# Run everything only when executed directly
if __name__ == "__main__":
    display_batch_accuracy_ui(merged)
    export_accuracy_report_with_chart(merged)
