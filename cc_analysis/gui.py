# cc_analysis/gui.py

import json
import os
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import pandas as pd

from cc_analysis.bank_detector import detect_bank_type
from cc_analysis.bank_statement_parser import consolidate_all, save_to_consolidated_db
from cc_analysis.constants import HELP_PATH, ABOUT_PATH, CATEGORY_MAP_PATH, EXCEL_PATH
from cc_analysis.extractors import extract_hdfc, extract_indusind, append_to_excel
from cc_analysis.utils import validate_pdf_password, load_passwords, log_error, log_info
from statement_checker.gui_statement_checker import launch_gui as launch_statement_gui

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
    tools_menu.add_command(label="Statement Organizer", command=launch_statement_gui)
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
        skipped_files = []
        failed_decrypts = []
        unsupported_files = []
        empty_parsed = []

        for f in file_paths:
            if not os.path.exists(f):
                skipped_files.append(f)
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext == ".pdf":
                pdf_files.append(f)
            elif ext in [".xls", ".xlsx", ".csv"]:
                bank_files.append(f)
            else:
                unsupported_files.append(f)

        total_files = len(pdf_files) + len(bank_files)
        progress_label.config(text=f"Progress: 0/{total_files}")
        progress_var.set(0)
        root.update_idletasks()

        try:
            for idx, file in enumerate(pdf_files):
                bank = None
                password = None
                for bnk, pwd in passwords.items():
                    if validate_pdf_password(file, pwd):
                        bank = detect_bank_type(file, pwd)
                        password = pwd
                        break

                if not bank or not password:
                    failed_decrypts.append(file)
                    log_error(f"{file} - ❌ Could not decrypt or detect bank")
                    continue

                if bank == "HDFC":
                    df = extract_hdfc(file, password)
                elif bank == "IndusInd":
                    df = extract_indusind(file, password)
                else:
                    unsupported_files.append(file)
                    log_error(f"❌ Unsupported bank type for file: {os.path.basename(file)}")
                    continue

                if df.empty:
                    empty_parsed.append(file)
                    log_error(f"{file} - ⚠️ No transaction data found, skipped.")
                    continue

                df["Bank"] = bank  # Tag bank
                log_info(f"{file} - ✅ Extracted {len(df)} transactions using {bank} extractor")

                # Sanity check for required columns
                expected = {'Date', 'Description', 'Merchant', 'Category', 'Reward Points', 'Bank', 'SourceType',
                            'Debit', 'Credit', 'Balance'}
                missing = expected - set(df.columns)
                if missing:
                    log_error(f"{file} - ❌ Missing expected columns: {missing}")
                    continue

                combined_df = pd.concat([combined_df, df], ignore_index=True)

                # Update progress
                progress_label.config(text=f"Progress: {idx + 1}/{total_files}")
                progress_var.set((idx + 1) * (100 / total_files))
                root.update_idletasks()

            cc_excel_written = 0
            cc_db_written = 0
            if not combined_df.empty:
                cc_excel_written = append_to_excel(combined_df, source_type="CreditCard", excel_path=EXCEL_PATH)
                cc_db_written = save_to_consolidated_db(combined_df, source_type="CreditCard")

            # Process bank files
            if bank_files:
                consolidate_all(bank_files)
                for jdx, _ in enumerate(bank_files):
                    progress_label.config(text=f"Progress: {len(pdf_files) + jdx + 1}/{total_files}")
                    progress_var.set((len(pdf_files) + jdx + 1) * (100 / total_files))
                    root.update_idletasks()

            # === Final summary ===
            summary = f"✅ Processed {total_files} files.\n"
            if cc_excel_written:
                summary += f"• Credit Card Excel records: {cc_excel_written}\n"
            if cc_db_written:
                summary += f"• Credit Card DB records: {cc_db_written}\n"
            if bank_files:
                summary += f"• Bank statements saved to DB\n"

            if skipped_files:
                summary += f"\n⚠️ Skipped (not found): {len(skipped_files)}"
            if failed_decrypts:
                summary += f"\n🔐 Decrypt failed: {len(failed_decrypts)}"
            if unsupported_files:
                summary += f"\n❌ Unsupported format: {len(unsupported_files)}"
            if empty_parsed:
                summary += f"\n📭 Empty transactions: {len(empty_parsed)}"

            messagebox.showinfo("Process Summary", summary.strip())

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