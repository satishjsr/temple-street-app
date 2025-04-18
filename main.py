import tkinter as tk
from tkinter import simpledialog, messagebox
from purchase_app_gui import TempleStreetApp  # Assuming GUI is in a separate file for cleanliness

USERS = {
    "admin": "admin123",
    "staff": "staff123"
}

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

    # Start main app window
    root = tk.Tk()
    app = TempleStreetApp(root, role=username)
    root.mainloop()

if __name__ == "__main__":
    prompt_login()
