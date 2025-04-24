# ✅ Temple Street App – Updated for Phase 2.7 Forecast Accuracy Integration

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import pandas as pd
import os
from datetime import datetime
import threading
import webbrowser
from PIL import ImageTk, Image
from app.forecast_accuracy import process_forecast_accuracy

USERS = {
    "admin": "admin123",
    "staff": "staff123"
}

APP_VERSION = "v2.8.16"

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
        self.setup_ui()

    def setup_ui(self):
        icon_path = os.path.join("assets", "temple-street.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                print("⚠️ Icon load failed in runtime.")

        tk.Label(self.root, text=f"Temple Street System ({self.role.title()})", font=("Helvetica", 14, "bold")).pack(pady=10)
        self.status = tk.Label(self.root, text="Status: Waiting for files", fg="blue")
        self.status.pack(pady=10)

        tk.Button(self.root, text="📂 Import Day-wise Item Sales File", command=self.import_sales_file).pack(pady=5)
        tk.Button(self.root, text="📦 Import Current Stock File", command=self.import_stock_file).pack(pady=5)
        tk.Button(self.root, text="📥 Import Actual Consumption File", command=self.import_consumption_file).pack(pady=5)

        tk.Label(self.root, text="Optional: Adjust forecast %").pack(pady=(10, 0))
        self.adjust_entry = tk.Entry(self.root)
        self.adjust_entry.insert(0, "100")
        self.adjust_entry.pack(pady=5)

        self.process_btn = tk.Button(self.root, text="📈 Generate Forecast & Purchase Order", command=self.run_forecast_thread, state=tk.DISABLED)
        self.process_btn.pack(pady=5)

        tk.Button(self.root, text="📁 Open Export Folder", command=self.open_export_folder).pack(pady=5)
        self.view_order_btn = tk.Button(self.root, text="🧾 View Final Purchase Order", command=self.view_purchase_order, state=tk.DISABLED)
        self.view_order_btn.pack(pady=5)

        if self.role == "admin":
            tk.Button(self.root, text="📤 Send Files via WhatsApp", command=self.send_via_whatsapp).pack(pady=5)

        tk.Button(self.root, text="❓ Help", command=self.show_help).pack(pady=5)

        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
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

    def process_file(self):
        try:
            self.root.after(0, lambda: self.status.config(text="Processing..."))
            self.root.after(0, lambda: self.view_order_btn.config(state=tk.DISABLED))

            # Forecast Accuracy Processing
            if self.consumption_file_path:
                out_file = process_forecast_accuracy(self.sales_file_path, self.consumption_file_path)
                if out_file:
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Forecast Accuracy Report saved:\n{out_file}"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Forecast accuracy report failed."))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Skipped", "No consumption file imported. Skipping accuracy check."))

        except Exception as e:
            self.root.after(0, lambda: self.status.config(text=f"❌ Error: {e}", fg="red"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)

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
            "1. Import sales and stock Excel files from Petpooja.\n"
            "2. (Optional) Import consumption sheet for accuracy report.\n"
            "3. Adjust forecast if needed.\n"
            "4. Click to generate forecasts and purchase orders.\n"
            "5. Use 'Open Export Folder' to access generated files."
        )
        self.root.after(0, lambda: messagebox.showinfo("Help", help_text))

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
