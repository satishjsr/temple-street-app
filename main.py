import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
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
        self.root.geometry("400x480")

        try:
            self.root.iconbitmap("assets/temple-street.ico")
        except:
            print("⚠️ Icon not found. Running without custom icon.")

        self.label = tk.Label(root, text=f"Temple Street System ({role.title()})", font=("Helvetica", 14, "bold"), pady=10)
        self.label.pack()

        self.status = tk.Label(root, text="Status: Waiting for file", fg="blue")
        self.status.pack(pady=10)

        self.import_btn = tk.Button(root, text="📂 Import Sales Excel File", command=self.import_file)
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
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.file_path = file_path
            self.status.config(text=f"File loaded: {os.path.basename(file_path)}", fg="green")
            self.process_btn.config(state=tk.NORMAL)

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
            df = pd.read_excel(self.file_path)

            adjust = float(self.adjust_entry.get())
            df["Forecast"] = "Coming Soon"
            if adjust != 100:
                df["Forecast"] += f" ({adjust}% planned)"

            output_dir = "export"
            os.makedirs(output_dir, exist_ok=True)
            filename = f"Temple_Street_Plan_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
            output_file = os.path.join(output_dir, filename)

            df.to_excel(output_file, index=False)

            self.root.after(0, lambda: messagebox.showinfo("Success", f"Forecast saved to:\n{output_file}"))
            self.root.after(0, lambda: self.status.config(text="✅ Forecast generated successfully!", fg="darkgreen"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate forecast:\n{e}"))
            self.root.after(0, lambda: self.status.config(text="Error occurred", fg="red"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)


def login_and_start():
    login_root = tk.Tk()
    login_root.title("Login")
    login_root.geometry("300x200")

    tk.Label(login_root, text="Username").pack(pady=5)
    username_entry = tk.Entry(login_root)
    username_entry.pack()

    tk.Label(login_root, text="Password").pack(pady=5)
    password_entry = tk.Entry(login_root, show="*")
    password_entry.pack()

    def attempt_login():
        username = username_entry.get()
        password = password_entry.get()
        if username in USERS and USERS[username] == password:
            login_root.destroy()
            root = tk.Tk()
            app = TempleStreetApp(root, role=username)
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    tk.Button(login_root, text="Login", command=attempt_login).pack(pady=10)
    login_root.mainloop()


if __name__ == "__main__":
    login_and_start()
