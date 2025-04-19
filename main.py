# ✅ Phase 2.1.2 Fix – Robust Date Format Handling

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import pandas as pd
import os
from datetime import datetime, timedelta
import threading
import webbrowser

USERS = {
    "admin": "admin123",
    "staff": "staff123"
}

class TempleStreetApp:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title("Temple Street Ordering System")
        self.root.geometry("400x580")

        icon_path = os.path.join("assets", "temple-street.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                print("⚠️ Icon load failed in runtime.")

        self.label = tk.Label(root, text=f"Temple Street System ({role.title()})", font=("Helvetica", 14, "bold"), pady=10)
        self.label.pack()

        self.status = tk.Label(root, text="Status: Waiting for file", fg="blue")
        self.status.pack(pady=10)

        self.import_sales_btn = tk.Button(root, text="📂 Import Day-wise Item Sales File", command=self.import_sales_file)
        self.import_sales_btn.pack(pady=5)

        self.import_stock_btn = tk.Button(root, text="📦 Import Current Stock File", command=self.import_stock_file)
        self.import_stock_btn.pack(pady=5)

        self.adjust_label = tk.Label(root, text="Optional: Adjust forecast %")
        self.adjust_label.pack(pady=(10,0))
        self.adjust_entry = tk.Entry(root)
        self.adjust_entry.insert(0, "100")
        self.adjust_entry.pack(pady=5)

        self.process_btn = tk.Button(root, text="📈 Generate Forecast & Purchase Order", command=self.run_forecast_thread, state=tk.DISABLED)
        self.process_btn.pack(pady=5)

        self.open_folder_btn = tk.Button(root, text="📁 Open Export Folder", command=self.open_export_folder)
        self.open_folder_btn.pack(pady=5)

        if role == "admin":
            self.whatsapp_btn = tk.Button(root, text="📤 Send Files via WhatsApp", command=self.send_via_whatsapp)
            self.whatsapp_btn.pack(pady=5)

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.sales_file_path = ""
        self.stock_file_path = ""

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

    def send_via_whatsapp(self):
        export_dir = os.path.abspath("export")
        messagebox.showinfo("Manual Step", "Share files from:\n" + export_dir)
        webbrowser.open(export_dir)

    def process_file(self):
        try:
            raw_df = pd.read_excel(self.sales_file_path)
            data_start_index = raw_df[raw_df.iloc[:, 0] == "Item"].index.min()
            df_sales = pd.read_excel(self.sales_file_path, skiprows=data_start_index + 1)
            df_sales.columns = df_sales.columns.str.strip().str.lower()

            df_sales = df_sales.rename(columns={
                next(col for col in df_sales.columns if "item" in col): "item",
                next(col for col in df_sales.columns if "date" in col): "date",
                next(col for col in df_sales.columns if "qty" in col): "quantity"
            })

            df_sales["item"] = df_sales["item"].str.strip().str.lower()
            df_sales["date"] = pd.to_datetime(df_sales["date"], errors="coerce", dayfirst=True)
            df_sales = df_sales.dropna(subset=["date"])

            forecast_date = datetime.now() + timedelta(days=2)
            day_df = df_sales[df_sales["date"] == forecast_date.date()]
            item_qty = day_df.groupby("item")["quantity"].sum().reset_index()
            item_qty.columns = ["item", "forecastqty"]

            recipe_df_raw = pd.read_excel("Recipe_Report_2025_04_18_11_01_56.xlsx", skiprows=4)
            recipe_df = pd.concat([
                recipe_df_raw[[f"ItemName", f"RawMaterial{'.' + str(i) if i else ''}", f"Qty{'.' + str(i) if i else ''}", f"Unit{'.' + str(i) if i else ''}"]].rename(columns={
                    f"RawMaterial{'.' + str(i) if i else ''}": "Ingredient",
                    f"Qty{'.' + str(i) if i else ''}": "Qty",
                    f"Unit{'.' + str(i) if i else ''}": "UOM"
                }) for i in range(84) if f"RawMaterial{'.' + str(i) if i else ''}" in recipe_df_raw.columns
            ])

            recipe_df = recipe_df.dropna(subset=["Ingredient", "Qty"])
            recipe_df["item"] = recipe_df["ItemName"].str.strip().str.lower()
            recipe_df["ingredient"] = recipe_df["Ingredient"].str.strip().str.lower()
            recipe_df = recipe_df.rename(columns={"Qty": "ingredientqty"})

            df_stock = pd.read_excel(self.stock_file_path, skiprows=4)
            df_stock.columns = df_stock.columns.str.strip().str.lower()
            stock_map = dict(zip(df_stock['item'].str.lower(), df_stock['current stock']))

            merged = pd.merge(item_qty, recipe_df, on="item", how="left")
            factor = float(self.adjust_entry.get()) / 100.0
            merged["adjustedqty"] = (merged["forecastqty"] * factor).round().astype(int)
            merged["requiredqty"] = (merged["forecastqty"] * merged["ingredientqty"]).round(2)
            merged["stock"] = merged["ingredient"].map(stock_map).fillna(0)
            merged["toorder"] = (merged["requiredqty"] - merged["stock"]).clip(lower=0)

            os.makedirs("export", exist_ok=True)
            today = datetime.now().strftime('%Y-%m-%d')
            merged.to_excel(f"export/Forecast_Purchase_Plan_{today}.xlsx", index=False)

            self.root.after(0, lambda: messagebox.showinfo("Success", f"Forecast for {forecast_date.strftime('%d-%b-%Y')} generated."))
            self.status.config(text="✅ Daily forecast completed!", fg="darkgreen")

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)

def prompt_login():
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
