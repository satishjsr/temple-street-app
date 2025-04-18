import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from datetime import datetime
import threading

class TempleStreetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temple Street Ordering System")
        self.root.geometry("400x350")
        self.root.iconbitmap("assets/temple-street.ico")  # Icon path

        self.label = tk.Label(root, text="Temple Street Ordering System v1.0.0", font=("Helvetica", 14, "bold"), pady=10)
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

            self.root.after(0, lambda: messagebox.showinfo("Success", f"Forecast saved to:\n{output_file}"))
            self.root.after(0, lambda: self.status.config(text="✅ Forecast generated successfully!", fg="darkgreen"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate forecast:\n{e}"))
            self.root.after(0, lambda: self.status.config(text="Error occurred", fg="red"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)

if __name__ == "__main__":
    root = tk.Tk()
    app = TempleStreetApp(root)
    root.mainloop()
