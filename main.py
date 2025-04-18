df = pd.read_excel(self.file_path, skiprows=5)

            # Petpooja-standard column structure enforcement
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

                outlet_df['Item'] = outlet_df['Item'].str.strip().str.lower()
                recipe_df['Item'] = recipe_df['Item'].str.strip().str.lower()
                merged_df = pd.merge(outlet_df, recipe_df, on='Item', how='left')
                merged_df['IngredientQty'] = merged_df['IngredientQty'].fillna(0)
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
