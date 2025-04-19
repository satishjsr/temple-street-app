
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
        self.root.geometry("400x500")

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

        self.import_btn = tk.Button(root, text="📂 Import Item Sales Excel File", command=self.import_file)
        self.import_btn.pack(pady=5)

        self.adjust_label = tk.Label(root, text="Optional: Adjust forecast % (e.g., 110 for 10% more)")
        self.adjust_label.pack(pady=(10,0))
        self.adjust_entry = tk.Entry(root)
        self.adjust_entry.insert(0, "100")
        self.adjust_entry.pack(pady=5)

        self.process_btn = tk.Button(root, text="📈 Generate Forecast", command=self.run_forecast_thread, state=tk.DISABLED)
        self.process_btn.pack(pady=5)

        self.open_folder_btn = tk.Button(root, text="📁 Open Export Folder", command=self.open_export_folder)
        self.open_folder_btn.pack(pady=5)

        if role == "admin":
            self.whatsapp_btn = tk.Button(root, text="📤 Send Files via WhatsApp", command=self.send_via_whatsapp)
            self.whatsapp_btn.pack(pady=5)

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.file_path = ""

    def import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[["Excel files", "*.xlsx"]])
        if file_path:
            self.file_path = file_path
            self.status.config(text=f"File loaded: {os.path.basename(file_path)}", fg="green")

            self.outlet_window = tk.Toplevel(self.root)
            self.outlet_window.title("Select Outlet")
            tk.Label(self.outlet_window, text="Choose your outlet:").pack(pady=10)

            outlet_var = tk.StringVar(self.outlet_window)
            outlet_var.set("Rajendra Nagar")

            dropdown = tk.OptionMenu(self.outlet_window, outlet_var, "Rajendra Nagar", "Tilak Nagar")
            dropdown.pack(pady=5)

            def confirm_outlet():
                self.selected_outlet = outlet_var.get()
                self.outlet_window.destroy()
                self.process_btn.config(state=tk.NORMAL)

            confirm_btn = tk.Button(self.outlet_window, text="Confirm", command=confirm_outlet)
            confirm_btn.pack(pady=10)

    def run_forecast_thread(self):
        self.progress.pack(pady=10)
        self.progress.start()
        threading.Thread(target=self.process_file).start()

    def open_export_folder(self):
        export_dir = os.path.abspath("export")
        if os.path.exists(export_dir):
            webbrowser.open(export_dir)
        else:
            messagebox.showwarning("Not Found", "Export folder not found yet.")

    def send_via_whatsapp(self):
        export_dir = os.path.abspath("export")
        if os.path.exists(export_dir):
            messagebox.showinfo("Manual Step", "To share via WhatsApp, please manually attach files from:\n" + export_dir)
            webbrowser.open(export_dir)
        else:
            messagebox.showwarning("Missing", "Export folder does not exist yet.")

    def process_file(self):
        try:
            recipe_df_raw = pd.read_excel("Recipe_Report_2025_04_18_11_01_56.xlsx", skiprows=4)
            ingredient_blocks = []
            for i in range(0, 84):
                ing_col = f"RawMaterial" if i == 0 else f"RawMaterial.{i}"
                qty_col = f"Qty" if i == 0 else f"Qty.{i}"
                uom_col = f"Unit" if i == 0 else f"Unit.{i}"
                if ing_col in recipe_df_raw.columns:
                    block = recipe_df_raw[["ItemName", ing_col, qty_col, uom_col]].copy()
                    block.columns = ["Final Item", "Ingredient", "Qty", "UOM"]
                    ingredient_blocks.append(block)

            recipe_df = pd.concat(ingredient_blocks)
            recipe_df = recipe_df.dropna(subset=["Ingredient", "Qty"])
            recipe_df["Item"] = recipe_df["Final Item"].str.strip().str.lower()
            recipe_df["Ingredient"] = recipe_df["Ingredient"].str.strip().str.lower()
            recipe_df = recipe_df.rename(columns={"Qty": "IngredientQty"})
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Recipe Report:\n{e}")
            return

        try:
            sales_df = pd.read_excel(self.file_path, skiprows=11)
            sales_df.columns = ["Category", "Item", "Qty", "Total"]
            sales_df = sales_df[sales_df["Item"].notna()]
            df = sales_df[["Item", "Qty"]].rename(columns={"Qty": "Quantity"})
            df["Outlet"] = self.selected_outlet

            adjusted_factor = float(self.adjust_entry.get()) / 100.0
            future_date = (datetime.now() + pd.Timedelta(days=2)).strftime('%Y-%m-%d')
            os.makedirs("export", exist_ok=True)

            df["Item"] = df["Item"].str.strip().str.lower()
            recipe_df["Item"] = recipe_df["Item"].str.strip().str.lower()
            merged_df = pd.merge(df, recipe_df, on="Item", how="left")

            if merged_df["IngredientQty"].isna().all():
                raise ValueError("None of the 'Item' entries from sales matched the recipe sheet. Check spelling/casing.")

            merged_df["IngredientQty"] = merged_df["IngredientQty"].fillna(0)
            merged_df["ForecastQty"] = (merged_df["Quantity"] ** 1.01 + 2).round().astype(int)
            merged_df["AdjustedQty"] = (merged_df["ForecastQty"] * adjusted_factor).round().astype(int)
            merged_df["RequiredQty"] = merged_df["ForecastQty"] * merged_df["IngredientQty"]
            merged_df["Cuisine"] = merged_df["Item"].apply(self.identify_cuisine)

            matched_items = merged_df[~merged_df['Ingredient'].isna()]['Item'].unique()
            unmatched_items = df[~df['Item'].isin(matched_items)]
            if not unmatched_items.empty:
                unmatched_export = f"export/{self.selected_outlet}_Unmatched_Items_{future_date}.xlsx"
                unmatched_items[['Item', 'Quantity']].drop_duplicates().to_excel(unmatched_export, index=False)

            debug_export = f"export/{self.selected_outlet}_Merged_Debug_{future_date}.xlsx"
            merged_df.to_excel(debug_export, index=False)

            raw_summary = merged_df.groupby(['Ingredient', 'UOM', 'Cuisine', 'Outlet'])['RequiredQty'].sum().reset_index()
            raw_summary = raw_summary[raw_summary['RequiredQty'] > 0]

            export_file = f"export/{self.selected_outlet}_Forecast_{future_date}.xlsx"
            raw_summary.to_excel(export_file, index=False)

            if self.role == "admin":
                webbrowser.open(os.path.abspath("export"))

            self.root.after(0, lambda: messagebox.showinfo("Success", "Forecast files saved in export folder."))
            self.root.after(0, lambda: self.status.config(text="✅ Forecast generated successfully!", fg="darkgreen"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate forecast:\n{e}"))
            self.root.after(0, lambda: self.status.config(text="Error occurred", fg="red"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)

    def identify_cuisine(self, item):
        item = str(item).lower()
        if any(word in item for word in ["paneer", "dal", "roti", "sabzi"]):
            return "North Indian"
        elif any(word in item for word in ["idli", "dosa", "sambar"]):
            return "South Indian"
        elif any(word in item for word in ["noodles", "manchurian"]):
            return "Chinese"
        else:
            return "Other"

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
