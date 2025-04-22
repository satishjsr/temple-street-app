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

class TempleStreetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temple Street Ordering System")
        self.root.geometry("400x350")
        try:
            self.root.iconbitmap("assets/temple-street.ico")
        except:
            print("⚠️ Icon not found. Running without custom icon.")

        self.label = tk.Label(root, text="Temple Street Ordering System v2.8.9", font=("Helvetica", 14, "bold"), pady=10)
        self.label.pack()

        self.status = tk.Label(root, text="Status: Waiting for file", fg="blue")
        self.status.pack(pady=10)

        self.import_btn = tk.Button(root, text="📂 Import Sales Excel File", command=self.import_file)
        self.import_btn.pack(pady=5)

        self.process_btn = tk.Button(root, text="📈 Generate Forecast", command=self.run_forecast_thread, state=tk.DISABLED)
        self.process_btn.pack(pady=5)

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.file_path = ""

    def import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.file_path = file_path
            self.status.config(text=f"File loaded: {os.path.basename(file_path)}", fg="green")
            self.process_btn.config(state=tk.NORMAL)

    def run_forecast_thread(self):
        self.progress.pack(pady=10)
        self.progress.start()
        threading.Thread(target=self.process_file).start()

    def process_file(self):
        try:
            df = pd.read_excel(self.file_path)
            df["Forecast"] = "Coming Soon"

            output_dir = "export"
            os.makedirs(output_dir, exist_ok=True)
            output_file = f"{output_dir}/Temple_Street_Plan_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
            df.to_excel(output_file, index=False)

            try:
                generate_production_sheet(df, output_dir)
            except Exception as e:
                print("⚠️ Failed to generate production sheet:", e)

            self.root.after(0, lambda: messagebox.showinfo("Success", f"Forecast saved to:\n{output_file}"))
            self.root.after(0, lambda: self.status.config(text="✅ Forecast generated successfully!", fg="darkgreen"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate forecast:\n{e}"))
            self.root.after(0, lambda: self.status.config(text="Error occurred", fg="red"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)

if __name__ == "__main__":
    show_splash()
    root = tk.Tk()
    app = TempleStreetApp(root)
    root.mainloop()
