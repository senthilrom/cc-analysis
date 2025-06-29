# cc_analysis/gui.py

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import pandas as pd
import json
import subprocess
import platform
from cc_analysis.extractors import extract_hdfc, extract_indusind, append_to_excel, save_to_database
from cc_analysis.bank_detector import detect_bank_type
from cc_analysis.utils import validate_pdf_password, load_passwords, log_error
from cc_analysis.bank_statement_parser import consolidate_all
from cc_analysis.constants import BANK_DB_PATH, BANK_CSV_PATH, HELP_PATH, ABOUT_PATH, CATEGORY_MAP_PATH

def launch_gui():
    root = tk.Tk()
    root.title("Credit Card and Bank Statement Consolidator")

    PADX = 10
    PADY = 6
    ENTRY_WIDTH = 50

    passwords = load_passwords()

    menubar = tk.Menu(root)

    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    help_menu = tk.Menu(menubar, tearoff=0)

    def show_help():
        try:
            with open(HELP_PATH, "r", encoding="utf-8") as f:
                messagebox.showinfo("Help", f.read())
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load Help: {str(e)}")

    def show_about():
        try:
            with open(ABOUT_PATH, "r", encoding="utf-8") as f:
                messagebox.showinfo("About", f.read())
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load About: {str(e)}")

    help_menu.add_command(label="Help", command=show_help)
    help_menu.add_command(label="About", command=show_about)
    menubar.add_cascade(label="Help", menu=help_menu)

    tools_menu = tk.Menu(menubar, tearoff=0)
    tools_menu.add_command(label="Edit Category", command=edit_categories)
    menubar.add_cascade(label="Tools", menu=tools_menu)

    root.config(menu=menubar)

    ttk.Label(root, text="Select PDF(s)/Bank Statements:").grid(row=0, column=0, sticky="e", padx=PADX, pady=PADY)
    file_entry = ttk.Entry(root, width=ENTRY_WIDTH)
    file_entry.grid(row=0, column=1, padx=PADX, pady=PADY)

    def select_multiple_files():
        files = filedialog.askopenfilenames(filetypes=[("PDF, Excel, CSV Files", ["*.pdf", "*.xls", "*.xlsx", "*.csv"])])
        if files:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, ";".join(files))

    ttk.Button(root, text="Browse", command=select_multiple_files).grid(row=0, column=2, padx=PADX, pady=PADY)

    progress_label = ttk.Label(root, text="Progress: 0/0")
    progress_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=PADX, pady=(PADY - 3))
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=ENTRY_WIDTH * 6)
    progress_bar.grid(row=2, column=0, columnspan=3, padx=PADX, pady=PADY)

    def run_extraction():
        file_paths = file_entry.get().split(";")
        if not file_paths:
            messagebox.showerror("Error", "Please select files.")
            return

        combined_df = pd.DataFrame()
        pdf_files = []
        bank_files = []

        for f in file_paths:
            ext = os.path.splitext(f)[1].lower()
            if ext == ".pdf":
                pdf_files.append(f)
            elif ext in [".xls", ".xlsx", ".csv"]:
                bank_files.append(f)

        progress_label.config(text=f"Progress: 0/{len(file_paths)}")
        progress_var.set(0)
        root.update_idletasks()

        try:
            for idx, file in enumerate(pdf_files):
                if not os.path.exists(file):
                    continue

                bank = None
                password = None
                for bnk, pwd in passwords.items():
                    if validate_pdf_password(file, pwd):
                        bank = detect_bank_type(file, pwd)
                        password = pwd
                        break

                if not bank or not password:
                    log_error(f"{file} - ❌ Could not decrypt or detect bank")
                    messagebox.showerror("Error", f"{file} - ❌ Could not decrypt or detect bank")
                    continue

                if bank == "HDFC":
                    df = extract_hdfc(file, password)
                elif bank == "IndusInd":
                    df = extract_indusind(file, password)
                else:
                    log_error(f"❌ Unsupported bank type for file: {os.path.basename(file)}")
                    messagebox.showerror("Error", f"Unsupported bank type for file: {os.path.basename(file)}")
                    continue

                if df.empty:
                    log_error(f"{file} - ⚠️ No transaction data found, skipped.")
                    continue

                df["Bank"] = bank
                combined_df = pd.concat([combined_df, df], ignore_index=True)

                progress_label.config(text=f"Progress: {idx + 1}/{len(file_paths)}")
                progress_var.set((idx + 1) * (100 / len(file_paths)))
                root.update_idletasks()

            cc_excel_written = 0
            cc_db_written = 0
            if not combined_df.empty:
                cc_excel_written = append_to_excel(combined_df)
                cc_db_written = save_to_database(combined_df)

            if bank_files:
                consolidate_all(bank_files, db_path=str(BANK_DB_PATH), csv_path=str(BANK_CSV_PATH))
                for jdx, _ in enumerate(bank_files):
                    progress_label.config(text=f"Progress: {len(pdf_files) + jdx + 1}/{len(file_paths)}")
                    progress_var.set((len(pdf_files) + jdx + 1) * (100 / len(file_paths)))
                    root.update_idletasks()

            if cc_excel_written or bank_files:
                messagebox.showinfo(
                    "Success",
                    f"✅ Processed {len(file_paths)} files.\n"
                    f"Credit Card Excel records: {cc_excel_written}\n"
                    f"Credit Card DB records: {cc_db_written}\n"
                    f"Bank statements saved to DB and CSV."
                )
            else:
                messagebox.showinfo("Done", "⚠️ No valid data extracted from selected files.")

        except Exception as e:
            log_error(f'Error during run_extraction: {str(e)}')
            messagebox.showerror("Error", str(e))

    ttk.Button(root, text="Extract & Save", command=run_extraction).grid(row=3, column=0, columnspan=3, pady=PADY + 4)

    root.mainloop()

def edit_categories():
    if not os.path.exists(CATEGORY_MAP_PATH):
        with open(CATEGORY_MAP_PATH, "w") as f:
            json.dump({"amazon": "Shopping", "zomato": "Food"}, f, indent=4)

    if platform.system() == "Windows":
        os.startfile(CATEGORY_MAP_PATH)
    elif platform.system() == "Darwin":
        subprocess.call(["open", CATEGORY_MAP_PATH])
    else:
        subprocess.call(["xdg-open", CATEGORY_MAP_PATH])

if __name__ == "__main__":
    launch_gui()