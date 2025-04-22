# ✅ Phase 2.6.1_Stable_AdjustmentFix – Final Phase Correction with Historical Comparison + Purchase Order Archive

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import pandas as pd
import os
from datetime import datetime, timedelta
import threading
import webbrowser
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image as XLImage
from PIL import ImageTk, Image
import shutil

USERS = {
    "admin": "admin123",
    "staff": "staff123"
}

APP_VERSION = "v2.8.9"

# 🖼 Splash screen before login
def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("400x300+500+250")
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        img = Image.open(logo_path).resize((120, 120))
        tk_img = ImageTk.PhotoImage(img)
        logo = tk.Label(splash, image=tk_img)
        logo.image = tk_img
        logo.pack(pady=20)

    tk.Label(splash, text="Temple Street", font=("Helvetica", 18, "bold"), fg="#800000").pack()
    tk.Label(splash, text="Excellence is our recipe", font=("Helvetica", 12)).pack(pady=5)
    tk.Label(splash, text=f"Version: {APP_VERSION}", font=("Helvetica", 10)).pack()

    splash.after(2000, splash.destroy)
    splash.mainloop()

# 🧾 Base Kitchen Production Sheet Generator
def generate_production_sheet(forecast_df, export_path):
    today = datetime.today().strftime('%Y-%m-%d')
    filename = os.path.join(export_path, f"Base_Kitchen_Production_{today}.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Production Plan"

    headers = ["Raw Material", "Required Qty", "Unit", "Dispatch Time"]
    ws.append(headers)

    for index, row in forecast_df.iterrows():
        ws.append([
            row.get("Raw Material", ""),
            row.get("AdjustedQty", 0),
            row.get("Unit", ""),
            row.get("Dispatch Time", "08:00 AM")
        ])

    ws.sheet_view.zoomScale = 110
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = "A1:D1"

    wb.save(filename)
    return filename

# Example call after forecast file is saved:
# try:
#     generate_production_sheet(forecast_df, export_folder_path)
# except Exception as e:
#     print("⚠️ Production sheet generation failed:", e)

if __name__ == "__main__":
    show_splash()
    prompt_login()
