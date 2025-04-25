import tkinter as tk
from tkinter import messagebox
from app import forecast_accuracy
from app import batch_accuracy

class TempleStreetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temple Street Forecast Accuracy System")
        self.root.geometry("400x200")
        
        self.label = tk.Label(root, text="Temple Street Forecast Accuracy Tool", font=("Arial", 14))
        self.label.pack(pady=10)

        self.ingredient_btn = tk.Button(root, text="Ingredient Accuracy", command=self.process_ingredient_accuracy)
        self.ingredient_btn.pack(pady=5)

        self.batch_btn = tk.Button(root, text="Batch Accuracy", command=self.process_batch_accuracy)
        self.batch_btn.pack(pady=5)

        self.status = tk.Label(root, text="", fg="green")
        self.status.pack(pady=5)

    def process_ingredient_accuracy(self):
        try:
            # Hardcoded example file paths; replace with file dialog if needed
            sales_file = "sales_file.xlsx"
            consumption_file = "consumption_file.xlsx"
            out_file = forecast_accuracy.process_forecast_accuracy(sales_file, consumption_file)
            if out_file:
                messagebox.showinfo("Success", f"Ingredient Accuracy Report saved at:
{out_file}")
            else:
                messagebox.showerror("Error", "Failed to generate ingredient accuracy report.")
        except Exception as e:
            messagebox.showerror("Exception", str(e))

    def process_batch_accuracy(self):
        try:
            batch_accuracy.display_batch_accuracy_ui(batch_accuracy.merged)
            batch_accuracy.export_accuracy_report_with_chart(batch_accuracy.merged)
            messagebox.showinfo("Success", "Batch Accuracy Report saved with chart.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = TempleStreetApp(root)
    root.mainloop()
