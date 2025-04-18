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

        # Icon fail-safe
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

            # Show outlet selection popup
            self.outlet_window = tk.Toplevel(self.root)
            self.outlet_window.title("Select Outlet")
            tk.Label(self.outlet_window, text="Choose your outlet:").pack(pady=10)

            outlet_var = tk.StringVar(self.outlet_window)
            outlet_var.set("Rajendra Nagar")  # default

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
        # Load Recipe Report (BOM)
        try:
            recipe_df = pd.read_excel("Recipe_Report_2025_04_02_11_07_15.xlsx")
            recipe_df = recipe_df.rename(columns={"Item": "Item", "Ingredient": "Ingredient", "Qty": "IngredientQty", "UOM": "UOM"})
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Recipe Report:
{e}")
            return
        try:
            df = pd.read_excel(self.file_path, skiprows=5)
            df = df.rename(columns={"Item": "Item", "Qty.": "Quantity"})
            df = df[["Item", "Quantity"]].copy()
            df["Outlet"] = self.selected_outlet

            adjusted_factor = float(self.adjust_entry.get()) / 100.0

            outlets = df['Outlet'].unique()
            future_date = (datetime.now() + pd.Timedelta(days=2)).strftime('%Y-%m-%d')
            os.makedirs("export", exist_ok=True)

            for outlet in outlets:
                outlet_df = df[df['Outlet'] == outlet].copy()
                outlet_df['Cuisine'] = outlet_df['Item'].apply(self.identify_cuisine)
                outlet_df['ForecastQty'] = (outlet_df['Quantity'] ** 1.01 + 2).round().astype(int)
                outlet_df['AdjustedQty'] = (outlet_df['ForecastQty'] * adjusted_factor).round().astype(int)

                # Expand item forecasts into raw ingredients
                merged_df = pd.merge(outlet_df, recipe_df, on='Item', how='left')
                merged_df['RequiredQty'] = merged_df['ForecastQty'] * merged_df['IngredientQty']
                raw_summary = merged_df.groupby(['Ingredient', 'UOM', 'Cuisine', 'Outlet'])['RequiredQty'].sum().reset_index()
                raw_summary = raw_summary[raw_summary['RequiredQty'] > 0]

                export_file = f"export/{outlet}_Forecast_{future_date}.xlsx"
                raw_summary.to_excel(export_file, index=False)

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
