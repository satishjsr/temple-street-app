
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pandas as pd
import traceback
from datetime import datetime

EXPORT_FOLDER = "export"

def clean_column(col):
    return str(col).strip().lower().replace(" ", "").replace(".", "").replace("_", "")

def smart_read_excel(filepath, required_cols):
    for i in range(10):
        try:
            df = pd.read_excel(filepath, header=i)
            cleaned = [clean_column(c) for c in df.columns]
            if all(any(req in c for c in cleaned) for req in required_cols):
                df.columns = cleaned
                return df
        except Exception:
            continue
    raise ValueError(f"Required columns {required_cols} not found in {filepath}")

def generate_forecast(sales_path, stock_path):
    df_sales = smart_read_excel(sales_path, ['item', 'qty'])
    df_stock = smart_read_excel(stock_path, ['item', 'currentstock'])

    merged = pd.merge(df_sales, df_stock, on='item', how='left')
    merged['forecast'] = merged['qty'] - merged['currentstock']
    merged['forecast'] = merged['forecast'].apply(lambda x: max(x, 0))

    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H-%M-%S")
    folder = os.path.join(EXPORT_FOLDER, today)
    os.makedirs(folder, exist_ok=True)

    forecast_path = os.path.join(folder, f"Forecast_Purchase_Plan_{timestamp}.xlsx")
    po_path = os.path.join(folder, f"Purchase_Order_{timestamp}.xlsx")

    merged.to_excel(forecast_path, index=False)
    merged[merged['forecast'] > 0].to_excel(po_path, index=False)

    return forecast_path, po_path

class ForecastApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temple Street Forecasting App")
        self.root.geometry("400x300")

        self.sales_path = None
        self.stock_path = None

        tk.Button(root, text="Upload Sales File", command=self.load_sales).pack(pady=10)
        tk.Button(root, text="Upload Stock File", command=self.load_stock).pack(pady=10)
        tk.Button(root, text="Generate Forecast", command=self.run_forecast).pack(pady=20)

    def load_sales(self):
        path = filedialog.askopenfilename(title="Select Sales File")
        if path:
            self.sales_path = path
            messagebox.showinfo("Loaded", f"Sales file loaded:
{path}")

    def load_stock(self):
        path = filedialog.askopenfilename(title="Select Stock File")
        if path:
            self.stock_path = path
            messagebox.showinfo("Loaded", f"Stock file loaded:
{path}")

    def run_forecast(self):
        try:
            if not self.sales_path or not self.stock_path:
                raise FileNotFoundError("Please upload both sales and stock files.")
            forecast, po = generate_forecast(self.sales_path, self.stock_path)
            messagebox.showinfo("Success", f"Forecast saved:
{forecast}
{po}")
        except Exception as e:
            with open("log.txt", "w") as f:
                f.write(traceback.format_exc())
            messagebox.showerror("Error", f"Something went wrong:
{e}")

def prompt_launch():
    root = tk.Tk()
    app = ForecastApp(root)
    root.mainloop()

if __name__ == "__main__":
    prompt_launch()
