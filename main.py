# ✅ Phase 2.8.11 – Forecast Accuracy Comparison Fully Patched

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import pandas as pd
import os
from datetime import datetime, timedelta
import threading
import webbrowser
from openpyxl import Workbook

# Simulated user roles
USERS = {"admin": "admin123", "staff": "staff123"}

APP_VERSION = "v2.8.11"

class TempleStreetApp:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title(f"Temple Street Ordering System {APP_VERSION} - {role.title()}")
        self.root.geometry("420x450")

        self.label = tk.Label(root, text="Temple Street Forecasting", font=("Helvetica", 14, "bold"), pady=10)
        self.label.pack()

        self.status = tk.Label(root, text="Status: Waiting for files", fg="blue")
        self.status.pack(pady=10)

        self.sales_btn = tk.Button(root, text="📂 Import Item Sales Report", command=self.import_sales)
        self.sales_btn.pack(pady=5)

        self.stock_btn = tk.Button(root, text="📦 Import Current Stock", command=self.import_stock)
        self.stock_btn.pack(pady=5)

        self.consumption_btn = tk.Button(root, text="📉 Import Consumption Report", command=self.import_consumption)
        self.consumption_btn.pack(pady=5)

        self.process_btn = tk.Button(root, text="📈 Generate Forecast Accuracy Report", command=self.run_forecast_thread, state=tk.DISABLED)
        self.process_btn.pack(pady=5)

        self.progress = ttk.Progressbar(root, mode='indeterminate')

        self.sales_file = ""
        self.stock_file = ""
        self.consumption_file = ""

    def import_sales(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.sales_file = path
            self.check_ready()

    def import_stock(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.stock_file = path
            self.check_ready()

    def import_consumption(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.consumption_file = path
            self.check_ready()

    def check_ready(self):
        if self.sales_file and self.stock_file and self.consumption_file:
            self.status.config(text="✅ All files ready", fg="green")
            self.process_btn.config(state=tk.NORMAL)

    def run_forecast_thread(self):
        self.progress.pack(pady=10)
        self.progress.start()
        threading.Thread(target=self.compare_forecast).start()

    def compare_forecast(self):
        try:
            forecast_df = pd.read_excel(self.sales_file)
            actual_df = pd.read_excel(self.consumption_file)

            forecast_df = forecast_df.rename(columns={"Item": "Item Name", "Quantity": "Forecast Quantity"})
            actual_df = actual_df.rename(columns={"Item": "Item Name", "Quantity": "Actual Quantity"})

            merged = pd.merge(forecast_df, actual_df, on="Item Name", how="outer")
            merged = merged.fillna(0)
            merged["Variance"] = merged["Actual Quantity"] - merged["Forecast Quantity"]
            merged["Accuracy %"] = 100 - abs(merged["Variance"] / merged["Forecast Quantity"]).replace([float('inf'), -float('inf')], 0) * 100
            merged["Accuracy %"] = merged["Accuracy %"].fillna(0).round(2)

            export_path = os.path.join("export", "forecast_vs_actual_{}.xlsx".format(datetime.now().strftime("%Y-%m-%d")))
            os.makedirs("export", exist_ok=True)
            merged.to_excel(export_path, index=False)

            self.status.config(text="✅ Forecast accuracy report ready!", fg="darkgreen")
            messagebox.showinfo("Done", f"Comparison file saved to:\n{export_path}")
            os.startfile(export_path)

        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")

        finally:
            self.progress.stop()
            self.progress.pack_forget()

def prompt_login():
    login = tk.Tk()
    login.withdraw()
    user = simpledialog.askstring("Login", "Username:")
    if user not in USERS:
        messagebox.showerror("Denied", "User not found")
        return
    pwd = simpledialog.askstring("Login", "Password:", show="*")
    if pwd != USERS[user]:
        messagebox.showerror("Denied", "Wrong password")
        return

    root = tk.Tk()
    app = TempleStreetApp(root, role=user)
    root.mainloop()

if __name__ == "__main__":
    prompt_login()
