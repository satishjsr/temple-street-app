
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import pandas as pd
import os
import threading
import webbrowser
from datetime import datetime
from app import batch_accuracy

USERS = {
    "admin": "admin123",
    "staff": "staff123"
}

APP_VERSION = "v2.9.7"

def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("400x300+500+250")
    splash.after(2000, splash.destroy)
    splash.mainloop()

class TempleStreetApp:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title(f"Temple Street Ordering System {APP_VERSION} - {role.title()}")
        self.root.geometry("400x600")

        self.label = tk.Label(root, text=f"Temple Street System ({role.title()})", font=("Helvetica", 14, "bold"), pady=10)
        self.label.pack()

        self.status = tk.Label(root, text="Status: Waiting for file", fg="blue")
        self.status.pack(pady=10)

        self.import_sales_btn = tk.Button(root, text="Import Day-wise Item Sales File", command=self.import_sales_file)
        self.import_sales_btn.pack(pady=5)

        self.import_stock_btn = tk.Button(root, text="Import Current Stock File", command=self.import_stock_file)
        self.import_stock_btn.pack(pady=5)

        self.adjust_label = tk.Label(root, text="Optional: Adjust forecast %")
        self.adjust_label.pack(pady=(10,0))
        self.adjust_entry = tk.Entry(root)
        self.adjust_entry.insert(0, "100")
        self.adjust_entry.pack(pady=5)

        self.process_btn = tk.Button(root, text="Generate Forecast & Purchase Order", command=self.run_forecast_thread, state=tk.DISABLED)
        self.process_btn.pack(pady=5)

        self.open_folder_btn = tk.Button(root, text="Open Export Folder", command=self.open_export_folder)
        self.open_folder_btn.pack(pady=5)

        self.view_order_btn = tk.Button(root, text="View Final Purchase Order", command=self.view_purchase_order, state=tk.DISABLED)
        self.view_order_btn.pack(pady=5)

        if role == "admin":
            self.whatsapp_btn = tk.Button(root, text="Send Files via WhatsApp", command=self.send_via_whatsapp)
            self.whatsapp_btn.pack(pady=5)

        self.batch_accuracy_btn = tk.Button(root, text="Run Batch Accuracy Report", command=self.process_batch_accuracy)
        self.batch_accuracy_btn.pack(pady=10)

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.sales_file_path = ""
        self.stock_file_path = ""
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

    def check_ready(self):
        if self.sales_file_path and self.stock_file_path:
            self.status.config(text="Files loaded. Ready to forecast.", fg="green")
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
        messagebox.showinfo("Manual Step", f"Share files from:\n{export_dir}")
        webbrowser.open(export_dir)

    def process_file(self):
        try:
            sales_df = pd.read_excel(self.sales_file_path)
            stock_df = pd.read_excel(self.stock_file_path)

            # Normalize column names
            sales_df.columns = [col.strip().lower() for col in sales_df.columns]
            stock_df.columns = [col.strip().lower() for col in stock_df.columns]

            # Rename common aliases to 'item'
            for alias in ['item name', 'menu item', 'dish']:
                if alias in sales_df.columns:
                    sales_df.rename(columns={alias: 'item'}, inplace=True)
                    break
            for alias in ['item name', 'menu item', 'dish']:
                if alias in stock_df.columns:
                    stock_df.rename(columns={alias: 'item'}, inplace=True)
                    break

            if 'item' not in sales_df.columns or 'item' not in stock_df.columns:
                raise Exception("Missing 'Item' or its aliases in sales or stock file.")

            merged = pd.merge(sales_df, stock_df, on='item', how='left')

            merged['forecastqty'] = merged['salesqty'] * float(self.adjust_entry.get()) / 100 - merged['currentstock']
            merged['forecastqty'] = merged['forecastqty'].apply(lambda x: max(x, 0))

            today = datetime.now().strftime("%Y-%m-%d")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            export_dir = os.path.join("export", today)
            os.makedirs(export_dir, exist_ok=True)

            forecast_path = os.path.join(export_dir, f"Forecast_Purchase_Plan_{timestamp}.xlsx")
            po_path = os.path.join(export_dir, f"Purchase_Order_{timestamp}.xlsx")

            merged.to_excel(forecast_path, index=False)
            po_df = merged[merged['forecastqty'] > 0]
            po_df.to_excel(po_path, index=False)

            self.purchase_order_file = po_path
            self.status.config(text=f"Files saved to export/{today}", fg="darkgreen")
            self.root.after(0, self.view_order_btn.config, {'state': tk.NORMAL})

        except Exception as e:
            error_message = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{error_message}"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)

    def process_batch_accuracy(self):
        try:
            batch_accuracy.display_batch_accuracy_ui(batch_accuracy.merged)
            batch_accuracy.export_accuracy_report_with_chart(batch_accuracy.merged)
            messagebox.showinfo("Success", "Batch Accuracy Report saved successfully with chart.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
