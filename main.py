# ✅ Phase 2.7 – Forecast Accuracy Learning (Final Code + Error Handling Fix)

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import pandas as pd
import os
from datetime import datetime, timedelta
import threading
import webbrowser
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as XLImage
from PIL import ImageTk, Image
import shutil

USERS = {
    "admin": "admin123",
    "staff": "staff123"
}

APP_VERSION = "v2.8.11"

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

class TempleStreetApp:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title(f"Temple Street Ordering System {APP_VERSION} - {role.title()}")
        self.root.geometry("400x680")

        icon_path = os.path.join("assets", "temple-street.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                print("⚠️ Icon load failed in runtime.")

        self.label = tk.Label(root, text=f"Temple Street System ({role.title()})", font=("Helvetica", 14, "bold"), pady=10)
        self.label.pack()

        self.status = tk.Label(root, text="Status: Waiting for files", fg="blue")
        self.status.pack(pady=10)

        self.import_sales_btn = tk.Button(root, text="📂 Import Day-wise Item Sales File", command=self.import_sales_file)
        self.import_sales_btn.pack(pady=5)

        self.import_stock_btn = tk.Button(root, text="📦 Import Current Stock File", command=self.import_stock_file)
        self.import_stock_btn.pack(pady=5)

        self.import_consumption_btn = tk.Button(root, text="📥 Import Actual Consumption File", command=self.import_consumption_file)
        self.import_consumption_btn.pack(pady=5)

        self.adjust_label = tk.Label(root, text="Optional: Adjust forecast %")
        self.adjust_label.pack(pady=(10,0))
        self.adjust_entry = tk.Entry(root)
        self.adjust_entry.insert(0, "100")
        self.adjust_entry.pack(pady=5)

        self.process_btn = tk.Button(root, text="📈 Generate Forecast & Purchase Order", command=self.run_forecast_thread, state=tk.DISABLED)
        self.process_btn.pack(pady=5)

        self.open_folder_btn = tk.Button(root, text="📁 Open Export Folder", command=self.open_export_folder)
        self.open_folder_btn.pack(pady=5)

        self.view_order_btn = tk.Button(root, text="🧾 View Final Purchase Order", command=self.view_purchase_order, state=tk.DISABLED)
        self.view_order_btn.pack(pady=5)

        if role == "admin":
            self.whatsapp_btn = tk.Button(root, text="📤 Send Files via WhatsApp", command=self.send_via_whatsapp)
            self.whatsapp_btn.pack(pady=5)

        self.help_btn = tk.Button(root, text="❓ Help", command=self.show_help)
        self.help_btn.pack(pady=5)

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.sales_file_path = ""
        self.stock_file_path = ""
        self.consumption_file_path = ""
        self.purchase_order_file = ""

    def import_sales_file(self):
        path = filedialog.askopenfilename(filetypes=[["Excel files", "*.xlsx"]])
        if path:
            self.sales_file_path = path
            self.check_ready()

    def import_stock_file(self):
        path = filedialog.askopenfilename(filetypes=[["Excel files", "*.xlsx"]])
        if path:
            self.stock_file_path = path
            self.check_ready()

    def import_consumption_file(self):
        path = filedialog.askopenfilename(filetypes=[["Excel files", "*.xlsx"]])
        if path:
            self.consumption_file_path = path
            self.check_ready()

    def check_ready(self):
        if self.sales_file_path and self.stock_file_path:
            self.status.config(text="✅ Files loaded. Ready to forecast.", fg="green")
            self.process_btn.config(state=tk.NORMAL)

    def run_forecast_thread(self):
        self.progress.pack(pady=10)
        self.progress.start()
        threading.Thread(target=self.process_file).start()

    def open_export_folder(self):
        export_dir = os.path.abspath("export")
        os.makedirs(export_dir, exist_ok=True)
        webbrowser.open(export_dir)

    def view_purchase_order(self):
        if self.purchase_order_file and os.path.exists(self.purchase_order_file):
            os.startfile(self.purchase_order_file)
        else:
            self.root.after(0, lambda: messagebox.showerror("Not Found", "Purchase Order file not found."))

    def send_via_whatsapp(self):
        export_dir = os.path.abspath("export")
        self.root.after(0, lambda: messagebox.showinfo("Manual Step", "Share files from:\n" + export_dir))
        webbrowser.open(export_dir)

    def show_help(self):
        help_text = (
            "Temple Street Forecasting Help:\n\n"
            "1. Import item-wise sales Excel file from Petpooja.\n"
            "2. Import the current stock file.\n"
            "3. Optional: Adjust the forecast using a % buffer.\n"
            "4. Click Generate Forecast to create Purchase Order.\n"
            "5. Import consumption sheet (optional) to compare forecast vs actual.\n"
            "6. Use the 'Open Export Folder' to find your files.\n\n"
            "Need help? Contact: support@templestreet.in"
        )
        self.root.after(0, lambda: messagebox.showinfo("Help", help_text))

    def process_file(self):
        try:
            self.root.after(0, lambda: messagebox.showinfo("Forecasting", "Forecasting process started."))
            self.root.after(0, lambda: self.status.config(text="Processing..."))
            self.root.after(0, lambda: self.view_order_btn.config(state=tk.DISABLED))

            # Insert Forecast Accuracy Logic Here:
            if self.consumption_file_path:
                try:
                    sales_df = pd.read_excel(self.sales_file_path)
                    stock_df = pd.read_excel(self.stock_file_path)
                    consumption_df = pd.read_excel(self.consumption_file_path)

                    forecast = sales_df.groupby("Item")["Quantity"].sum().reset_index(name="ForecastedQty")
                    actual = consumption_df.groupby("Item")["ConsumedQty"].sum().reset_index(name="ActualQty")

                    merged = pd.merge(forecast, actual, on="Item", how="left")
                    merged["Accuracy"] = round((merged["ActualQty"] / merged["ForecastedQty"]) * 100, 2)
                    merged.fillna(0, inplace=True)

                    export_dir = os.path.abspath("export")
                    os.makedirs(export_dir, exist_ok=True)
                    out_file = os.path.join(export_dir, f"Forecast_vs_Actual_{datetime.now().strftime('%Y-%m-%d')}.xlsx")
                    merged.to_excel(out_file, index=False)

                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Forecast Accuracy Report saved:\n{out_file}"))

                except Exception as inner_error:
                    self.root.after(0, lambda: messagebox.showerror("Processing Error", f"Failed to process accuracy: {inner_error}"))

        except Exception as e:
            self.root.after(0, lambda: self.status.config(text=f"❌ Error: {e}", fg="red"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)

def prompt_login():
    show_splash()
    login_window = tk.Tk()
    login_window.withdraw()
    username = simpledialog.askstring("Login", "Enter your username:")
    if username not in USERS:
        messagebox.showerror("Access Denied", "Invalid username")
        return

    password = simpledialog.askstring("Login", f"Enter password for {username}:", show="*")
    if password != USERS[username]:
        messagebox.showerror("Access Denied", "Incorrect password")
        return

    root = tk.Tk()
    app = TempleStreetApp(root, role=username)
    root.mainloop()

if __name__ == "__main__":
    prompt_login()
