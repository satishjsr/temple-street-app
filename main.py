# Add this inside your class (e.g., App or MainWindow)
def process_batch_accuracy(self):
    try:
        import app.batch_accuracy as batch_mod
        batch_mod.display_batch_accuracy_ui(batch_mod.merged)
        batch_mod.export_accuracy_report_with_chart(batch_mod.merged)

        self.root.after(0, lambda: messagebox.showinfo(
            "Success",
            "✅ Batch Accuracy Report saved successfully!\n\nCheck your folder for Excel + Chart."
        ))

    except Exception as e:
        self.root.after(0, lambda: messagebox.showerror("Batch Accuracy Error", str(e)))
