# ✅ Phase 2.7 – Forecast Accuracy Learning (Final Code)

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
            messagebox.showerror("Not Found", "Purchase Order file not found.")

    def send_via_whatsapp(self):
        export_dir = os.path.abspath("export")
        messagebox.showinfo("Manual Step", "Share files from:\n" + export_dir)
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
        messagebox.showinfo("Help", help_text)

    def process_file(self):
        try:
            messagebox.showinfo("Forecasting", "Forecasting process started.")
            self.status.config(text="Processing...")
            self.view_order_btn.config(state=tk.DISABLED)

            # Load and clean sales data
            df_sales = pd.read_excel(self.sales_file_path, skiprows=5)
            df_sales.columns = df_sales.columns.str.strip().str.lower()
            df_sales = df_sales.rename(columns={"item name": "item", "quantity": "quantity", "date": "date"})
            df_sales["item"] = df_sales["item"].str.strip().str.lower()
            df_sales["date"] = pd.to_datetime(df_sales["date"], errors="coerce", dayfirst=True)
            df_sales = df_sales.dropna(subset=["date"])

            forecast_date = datetime.now() + timedelta(days=2)
            forecast_weekday = forecast_date.weekday()
            target_str = forecast_date.strftime('%Y-%m-%d')

            weekday_df = df_sales[df_sales["date"].dt.weekday == forecast_weekday]
            item_qty = weekday_df.groupby("item")["quantity"].mean().round().reset_index()
            item_qty.columns = ["item", "forecastqty"]

            recipe_df = pd.read_excel("Recipe_Report_2025_04_18_11_01_56.xlsx", skiprows=4)
            recipe_df.columns = recipe_df.columns.str.strip().str.lower()
            recipe_df = recipe_df.rename(columns={
                "itemname": "item", "rawmaterial": "ingredient", "qty": "ingredientqty", "uom": "unit"
            })
            recipe_df["item"] = recipe_df["item"].str.strip().str.lower()
            recipe_df["ingredient"] = recipe_df["ingredient"].str.strip().str.lower()

            df_stock = pd.read_excel(self.stock_file_path, skiprows=4)
            df_stock.columns = df_stock.columns.str.strip().str.lower()
            stock_map = dict(zip(df_stock['item'].str.lower(), df_stock['current stock']))

            merged = pd.merge(item_qty, recipe_df, on="item", how="left")
            factor = float(self.adjust_entry.get()) / 100.0
            merged["adjustedqty"] = (merged["forecastqty"] * factor).round().astype(int)
            merged["requiredqty"] = (merged["adjustedqty"] * merged["ingredientqty"]).round(2)
            merged["stock"] = merged["ingredient"].map(stock_map).fillna(0)
            merged["toorder"] = (merged["requiredqty"] - merged["stock"]).clip(lower=0)

            # Optional comparison if consumption report is available
            if self.consumption_file_path:
                df_actual = pd.read_excel(self.consumption_file_path, skiprows=4)
                df_actual.columns = df_actual.columns.str.strip().str.lower()
                df_actual = df_actual.rename(columns={"itemname": "ingredient", "qty": "actualusage"})
                df_actual["ingredient"] = df_actual["ingredient"].str.strip().str.lower()
                actual_map = dict(zip(df_actual["ingredient"], df_actual["actualusage"]))
                merged["actualusage"] = merged["ingredient"].map(actual_map).fillna(0)
                merged["forecast_error"] = (merged["requiredqty"] - merged["actualusage"]).round(2)

            os.makedirs("export", exist_ok=True)
            forecast_file = f"export/Forecast_Purchase_Plan_{target_str}.xlsx"
            merged.to_excel(forecast_file, index=False)

            po_df = merged[["ingredient", "toorder", "unit"]]
            po_df = po_df[po_df["toorder"] > 0]
            po_file = f"export/Purchase_Order_{target_str}.xlsx"
            self.purchase_order_file = os.path.abspath(po_file)
            po_df.to_excel(po_file, index=False)

            # Archive both files in history folder
            archive_root = os.path.join("export", "history", target_str)
            os.makedirs(archive_root, exist_ok=True)
            shutil.copy(forecast_file, os.path.join(archive_root, os.path.basename(forecast_file)))
            shutil.copy(po_file, os.path.join(archive_root, os.path.basename(po_file)))

            self.view_order_btn.config(state=tk.NORMAL)
            self.status.config(text="✅ Forecast and PO generated successfully!", fg="darkgreen")
            messagebox.showinfo("Done", f"Forecast and PO for {forecast_date.strftime('%d-%b-%Y')} generated.")

        except Exception as e:
            self.status.config(text=f"❌ Error: {e}", fg="red")
            messagebox.showerror("Error", str(e))
        finally:
            self.progress.stop()
            self.progress.pack_forget()

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
