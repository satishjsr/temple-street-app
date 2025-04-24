def process_file(self):
    try:
        self.root.after(0, lambda: self.status.config(text="Processing..."))
        self.root.after(0, lambda: self.view_order_btn.config(state=tk.DISABLED))

        # Forecast Accuracy Integration (Output to Desktop/temple_export/)
        if self.consumption_file_path:
            out_file = process_forecast_accuracy(self.sales_file_path, self.consumption_file_path)
            if out_file:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"✅ Forecast Accuracy Report saved successfully!\n\nPath:\n{out_file}"
                ))
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    "Forecast accuracy report failed.\nCheck:\nDesktop > temple_export > forecast_error.log"
                ))
        else:
            self.root.after(0, lambda: messagebox.showinfo(
                "Info",
                "Consumption file not provided.\nForecast accuracy check skipped."
            ))

    except Exception as e:
        self.root.after(0, lambda: self.status.config(text=f"❌ Error: {e}", fg="red"))
        self.root.after(0, lambda: messagebox.showerror("Unexpected Error", str(e)))
    finally:
        self.root.after(0, self.progress.stop)
        self.root.after(0, self.progress.pack_forget)
