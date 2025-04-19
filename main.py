# ✅ Phase 2 Update to Temple Street App – With Stock-Aware Purchase Planning (Fixed)

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import pandas as pd
import os
from datetime import datetime
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
        self.root.geometry("400x550")

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

        self.import_sales_btn = tk.Button(root, text="📂 Import Item Sales Excel File", command=self.import_sales_file)
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
            df_sales = pd.read_excel(self.sales_file_path, skiprows=11)
            df_sales.columns = ["Category", "Item", "Qty", "Total"]
            df_sales = df_sales[["Item", "Qty"]].dropna()
            df_sales.columns = ["Item", "Quantity"]
            df_sales["Item"] = df_sales["Item"].str.strip().str.lower()

            recipe_df_raw = pd.read_excel("Recipe_Report_2025_04_18_11_01_56.xlsx", skiprows=4)
            recipe_df = pd.concat([
                recipe_df_raw[[f"ItemName", f"RawMaterial{'.' + str(i) if i else ''}", f"Qty{'.' + str(i) if i else ''}", f"Unit{'.' + str(i) if i else ''}"]].rename(columns={
                    f"RawMaterial{'.' + str(i) if i else ''}": "Ingredient",
                    f"Qty{'.' + str(i) if i else ''}": "Qty",
                    f"Unit{'.' + str(i) if i else ''}": "UOM"
                }) for i in range(84) if f"RawMaterial{'.' + str(i) if i else ''}" in recipe_df_raw.columns
            ])

            recipe_df = recipe_df.dropna(subset=["Ingredient", "Qty"])
            recipe_df["Item"] = recipe_df["ItemName"].str.strip().str.lower()
            recipe_df["Ingredient"] = recipe_df["Ingredient"].str.strip().str.lower()
            recipe_df = recipe_df.rename(columns={"Qty": "IngredientQty"})

            df_stock = pd.read_excel(self.stock_file_path, skiprows=4)  # FIXED: Skip extra headers
            df_stock.columns = df_stock.columns.str.strip().str.lower()
            stock_map = dict(zip(df_stock['item'].str.lower(), df_stock['current stock']))

            merged = pd.merge(df_sales, recipe_df, on="Item", how="left")
            merged["ForecastQty"] = (merged["Quantity"] ** 1.01 + 2).round().astype(int)
            factor = float(self.adjust_entry.get()) / 100.0
            merged["AdjustedQty"] = (merged["ForecastQty"] * factor).round().astype(int)
            merged["RequiredQty"] = (merged["ForecastQty"] * merged["IngredientQty"]).round(2)
            merged["Stock"] = merged["Ingredient"].map(stock_map).fillna(0)
            merged["ToOrder"] = (merged["RequiredQty"] - merged["Stock"]).clip(lower=0)

            os.makedirs("export", exist_ok=True)
            today = datetime.now().strftime('%Y-%m-%d')
            merged.to_excel(f"export/Forecast_Purchase_Plan_{today}.xlsx", index=False)

            self.root.after(0, lambda: messagebox.showinfo("Success", "Forecast + Purchase Order generated."))
            self.status.config(text="✅ Purchase planning completed!", fg="darkgreen")

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
