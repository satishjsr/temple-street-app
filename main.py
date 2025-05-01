
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import pandas as pd
import os
import threading
import webbrowser
from datetime import datetime
from app import batch_accuracy
import re

APP_VERSION = "v2.9.13"

def clean_column_name(name):
    return re.sub(r'[^a-z0-9]', '', str(name).strip().lower())

def smart_read_excel(filepath, required_cols):
    for header_row in range(10):
        try:
            df = pd.read_excel(filepath, header=header_row)
            cleaned_cols = [clean_column_name(c) for c in df.columns]
            if all(req in cleaned_cols for req in required_cols):
                df.columns = cleaned_cols
                df.dropna(axis=1, how='all', inplace=True)
                return df
        except Exception:
            continue
    raise Exception(f"CleanScan failed: Required columns {required_cols} not found in any of first 10 rows.")
