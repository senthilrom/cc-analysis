# cc_analysis/gui.py

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import pandas as pd
from cc_analysis.extractors import extract_hdfc, extract_indusind, append_to_excel
import pdfplumber
from datetime import datetime
import sys

def launch_gui():
    root = tk.Tk()
    root.title("Credit Card Statement Extractor")
    style = ttk.Style()
    style.theme_use('xpnative') # Try 'vista', 'xpnative', 'alt', 'clam'

    PADX, PADY, ENTRY_WIDTH = 10, 6, 50
    is_dark_mode = False

    def select_multiple_pdfs():
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if files:
            pdf_entry.delete(0, tk.END)
            pdf_entry.insert(0, ";".join(files))

    def get_resource_path(filename):
        """ Get path to resource, works for dev and PyInstaller .exe """
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, filename)
        return os.path.join(os.path.dirname(__file__), filename)

    def show_about():
        try:
            with open(get_resource_path("about.txt"), "r", encoding="utf-8") as f:
                about_text = f.read()
        except FileNotFoundError:
            about_text = "About file not found."
        messagebox.showinfo("About", about_text)

    def show_help():
        try:
            with open(get_resource_path("help.txt"), "r", encoding="utf-8") as f:
                help_text = f.read()
        except FileNotFoundError:
            help_text = "Help file not found."
        messagebox.showinfo("Help / User Guide", help_text)

    def validate_pdf_password(pdf_path, password):
        try:
            with pdfplumber.open(pdf_path, password=password) as pdf:
                if pdf.pages:
                    return True
        except Exception as e:
            log_error(f"Failed to open PDF: {pdf_path}\nError: {e}")
        return False

    def log_error(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("error.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

    def run_extraction():
        pdf_paths = pdf_entry.get().split(";")
        password = pwd_entry.get()
        bank = bank_var.get()

        if not all([pdf_paths, password, bank]):
            messagebox.showerror("Error", "Please fill all fields.")
            return

        folder = os.path.dirname(pdf_paths[0])
        excel = os.path.join(folder, f"{bank.lower()}_statements.xlsx")
        combined_df = pd.DataFrame()
        progress_label.config(text=f"Progress: 0/{len(pdf_paths)}")
        progress_var.set(0)

        try:
            # Validate password with the first file only
            if not validate_pdf_password(pdf_paths[0], password):
                messagebox.showerror("Wrong Password",
                                     "❌ Failed to decrypt PDF.\nPlease check and enter the correct password.")
                return

            for idx, pdf in enumerate(pdf_paths):
                if not os.path.exists(pdf):
                    continue

                if bank == "HDFC":
                    df = extract_hdfc(pdf, password)
                    unique_cols = ["Datetime", "Description", "Amount"]
                else:
                    df = extract_indusind(pdf, password)
                    unique_cols = ["Date", "Transaction Details", "Amount"]

                if not df.empty:
                    combined_df = pd.concat([combined_df, df], ignore_index=True)

                progress_label.config(text=f"Progress: {idx + 1}/{len(pdf_paths)}")
                progress_var.set((idx + 1) * (100 / len(pdf_paths)))
                root.update_idletasks()

            if not os.path.exists(excel):
                with pd.ExcelWriter(excel) as writer:
                    pd.DataFrame(columns=combined_df.columns).to_excel(writer, index=False)

            total = append_to_excel(combined_df, excel, unique_cols)
            messagebox.showinfo("Success", f"✅ Saved to: {excel}\nProcessed {len(pdf_paths)} files.\nTotal records: {total}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # === GUI Layout ===
    ttk.Label(root, text="Select PDF(s):").grid(row=0, column=0, sticky="e", padx=PADX, pady=PADY)
    pdf_entry = ttk.Entry(root, width=ENTRY_WIDTH)
    pdf_entry.grid(row=0, column=1, padx=PADX, pady=PADY)
    ttk.Button(root, text="Browse", command=select_multiple_pdfs).grid(row=0, column=2, padx=PADX, pady=PADY)

    ttk.Label(root, text="PDF Password:").grid(row=1, column=0, sticky="e", padx=PADX, pady=PADY)
    pwd_entry = ttk.Entry(root, width=ENTRY_WIDTH, show="*")
    pwd_entry.grid(row=1, column=1, columnspan=2, padx=PADX, pady=PADY, sticky="w")

    ttk.Label(root, text="Bank:").grid(row=2, column=0, sticky="e", padx=PADX, pady=PADY)
    bank_var = tk.StringVar()
    bank_combo = ttk.Combobox(root, textvariable=bank_var, values=["HDFC", "IndusInd"], state="readonly", width=ENTRY_WIDTH - 4)
    bank_combo.set("HDFC")
    bank_combo.grid(row=2, column=1, columnspan=2, sticky="w", padx=PADX, pady=PADY)

    progress_label = ttk.Label(root, text="Progress: 0/0")
    progress_label.grid(row=3, column=1, columnspan=2, sticky="w", padx=PADX, pady=(PADY - 3))

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=ENTRY_WIDTH * 6)
    progress_bar.grid(row=4, column=0, columnspan=3, padx=PADX, pady=PADY)

    ttk.Button(root, text="Extract & Save", command=run_extraction).grid(row=5, column=0, columnspan=3, pady=PADY + 4)
    ttk.Button(root, text="About", command=show_about).grid(row=6, column=1, sticky="e", padx=5)
    ttk.Button(root, text="Help", command=show_help).grid(row=6, column=2, sticky="w", padx=5)

    root.mainloop()