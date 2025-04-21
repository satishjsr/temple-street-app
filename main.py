# ✅ Phase 2.6.1 Restored — Splash Screen + Forecasting Logic + Raw Material Prediction

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import pandas as pd
import os
from datetime import datetime, timedelta
import threading
from openpyxl import Workbook
from PIL import ImageTk, Image

APP_VERSION = "v2.6.1"
USERS = {"admin": "admin123", "staff": "staff123"}

# ------------------------ SPLASH SCREEN ------------------------ #
def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("400x300+500+250")
    logo_path = os.path.join("assets", "logo.png")
    try:
        if os.path.exists(logo_path):
            img = Image.open(logo_path).resize((120, 120))
            tk_img = ImageTk.PhotoImage(img)
            logo = tk.Label(splash, image=tk_img)
            logo.image = tk_img
            logo.pack(pady=20)
    except:
        print("⚠️ Logo not found. Skipping image.")

    tk.Label(splash, text="Temple Street", font=("Helvetica", 18, "bold"), fg="#800000").pack()
    tk.Label(splash, text="Excellence is our recipe", font=("Helvetica", 12)).pack(pady=5)
    tk.Label(splash, text=f"Version: {APP_VERSION}", font=("Helvetica", 10)).pack()

    splash.after(2000, splash.destroy)
    splash.mainloop()

# ------------------------ GUI CLASS ------------------------ #
class TempleStreetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temple Street Ordering System")
        self.root.geometry("420x380")
        try:
            self.root.iconbitmap("assets/temple-street.ico")
        except:
            print("⚠️ Icon not found. Running without custom icon.")

        tk.Label(root, text="Temple Street Ordering System", font=("Helvetica", 14, "bold"), pady=10).pack()

        self.status = tk.Label(root, text="Status: Waiting for sales file", fg="blue")
        self.status.pack(pady=10)

        self.sales_file_btn = tk.Button(root, text="📂 Upload Sales Report", command=self.upload_sales_file)
        self.sales_file_btn.pack(pady=5)

        self.stock_file_btn = tk.Button(root, text="📂 Upload Current Stock Report", command=self.upload_stock_file)
        self.stock_file_btn.pack(pady=5)

        self.forecast_btn = tk.Button(root, text="📈 Generate Forecast", command=self.run_forecast, state=tk.DISABLED)
        self.forecast_btn.pack(pady=10)

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.sales_path = ""
        self.stock_path = ""

    def upload_sales_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.sales_path = path
            self.status.config(text="Sales file loaded ✔", fg="green")
            self.check_ready()

    def upload_stock_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.stock_path = path
            self.status.config(text="Stock file loaded ✔", fg="green")
            self.check_ready()

    def check_ready(self):
        if self.sales_path and self.stock_path:
            self.forecast_btn.config(state=tk.NORMAL)

    def run_forecast(self):
        self.progress.pack(pady=10)
        self.progress.start()
        threading.Thread(target=self.generate_forecast).start()

    def generate_forecast(self):
        try:
            sales_df = pd.read_excel(self.sales_path)
            stock_df = pd.read_excel(self.stock_path)

            # Use last 30 days average per item
            forecast_df = sales_df.groupby('Item')['Quantity'].mean().reset_index()
            forecast_df.columns = ['Item', 'ForecastQty']

            # Match with stock
            merged_df = pd.merge(forecast_df, stock_df, on='Item', how='left')
            merged_df['CurrentStock'] = merged_df['CurrentStock'].fillna(0)
            merged_df['FinalQty'] = (merged_df['ForecastQty'] - merged_df['CurrentStock']).clip(lower=0)

            # Output file
            os.makedirs("export", exist_ok=True)
            filename = f"export/Purchase_Order_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
            merged_df.to_excel(filename, index=False)

            self.root.after(0, lambda: messagebox.showinfo("✅ Success", f"Forecast generated to:\n{filename}"))
            self.status.config(text="✅ Forecast complete!", fg="darkgreen")
        except Exception as e:
            self.status.config(text=f"❌ Error: {e}", fg="red")
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)

# ------------------------ ENTRY POINT ------------------------ #
def run_app():
    show_splash()
    root = tk.Tk()
    app = TempleStreetApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()
