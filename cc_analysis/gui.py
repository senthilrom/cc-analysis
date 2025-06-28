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

def launch_gui():
    root = tk.Tk()
    root.title("Credit Card Statement Consolidator")

    PADX = 10
    PADY = 6
    ENTRY_WIDTH = 50

    passwords = load_passwords()

    menubar = tk.Menu(root)

    # File Menu
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    # Help Menu
    help_menu = tk.Menu(menubar, tearoff=0)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def show_help():
        try:
            help_path = os.path.join(BASE_DIR, "help.txt")
            with open(help_path, "r", encoding="utf-8") as f:
                messagebox.showinfo("Help", f.read())
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load Help: {str(e)}")

    def show_about():
        try:
            about_path = os.path.join(BASE_DIR, "about.txt")
            with open(about_path, "r", encoding="utf-8") as f:
                messagebox.showinfo("About", f.read())
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load About: {str(e)}")

    help_menu.add_command(label="Help", command=show_help)
    help_menu.add_command(label="About", command=show_about)
    menubar.add_cascade(label="Help", menu=help_menu)

    # Tools menu already exists
    tools_menu = tk.Menu(menubar, tearoff=0)
    tools_menu.add_command(label="Edit Category", command=edit_categories)
    menubar.add_cascade(label="Tools", menu=tools_menu)

    root.config(menu=menubar)

    ttk.Label(root, text="Select PDF(s):").grid(row=0, column=0, sticky="e", padx=PADX, pady=PADY)
    pdf_entry = ttk.Entry(root, width=ENTRY_WIDTH)
    pdf_entry.grid(row=0, column=1, padx=PADX, pady=PADY)

    def select_multiple_pdfs():
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if files:
            pdf_entry.delete(0, tk.END)
            pdf_entry.insert(0, ";".join(files))

    ttk.Button(root, text="Browse", command=select_multiple_pdfs).grid(row=0, column=2, padx=PADX, pady=PADY)

    progress_label = ttk.Label(root, text="Progress: 0/0")
    progress_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=PADX, pady=(PADY - 3))
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=ENTRY_WIDTH * 6)
    progress_bar.grid(row=2, column=0, columnspan=3, padx=PADX, pady=PADY)

    def run_extraction():
        pdf_paths = pdf_entry.get().split(";")
        if not pdf_paths:
            messagebox.showerror("Error", "Please select PDF files.")
            return

        combined_df = pd.DataFrame()
        progress_label.config(text=f"Progress: 0/{len(pdf_paths)}")
        progress_var.set(0)

        try:
            for idx, pdf in enumerate(pdf_paths):
                if not os.path.exists(pdf):
                    continue

                # Try all known bank passwords to detect bank
                bank = None
                password = None
                for bnk, pwd in passwords.items():
                    if validate_pdf_password(pdf, pwd):
                        bank = detect_bank_type(pdf, pwd)
                        password = pwd
                        break

                if not bank or not password:
                    log_error(f"{pdf} - ❌ Could not decrypt or detect bank")
                    messagebox.showerror("Error", f"{pdf} - ❌ Could not decrypt or detect bank")
                    continue

                # Extract based on detected bank
                if bank == "HDFC":
                    df = extract_hdfc(pdf, password)
                elif bank == "IndusInd":
                    df = extract_indusind(pdf, password)
                else:
                    log_error(f"❌ Unsupported bank type for file: {os.path.basename(pdf)}")
                    messagebox.showerror("Error", f"Unsupported bank type for file: {os.path.basename(pdf)}")
                    continue

                # Skip chart-only or empty transaction files
                if df.empty:
                    log_error(f"{pdf} - ⚠️ No transaction data found, skipped.")
                    continue

                df["Bank"] = bank
                combined_df = pd.concat([combined_df, df], ignore_index=True)

                progress_label.config(text=f"Progress: {idx + 1}/{len(pdf_paths)}")
                progress_var.set((idx + 1) * (100 / len(pdf_paths)))
                root.update_idletasks()

            if combined_df.empty:
                log_error("No transactions were extracted.")
                messagebox.showwarning("No Data", "No transactions were extracted.")
                return

            total = append_to_excel(combined_df)
            inserted = save_to_database(combined_df, bank)
            messagebox.showinfo("Success",
                                f"✅ Processed {len(pdf_paths)} files.\nRecords saved to Excel: {total}\nRecords saved to DB: {inserted}")

        except Exception as e:
            log_error(f'Error, {str(e)}')
            messagebox.showerror("Error", str(e))

    ttk.Button(root, text="Extract & Save", command=run_extraction).grid(row=3, column=0, columnspan=3, pady=PADY + 4)

    root.mainloop()

def edit_categories():
    category_file = os.path.join(os.path.dirname(__file__), "categories.json")
    if not os.path.exists(category_file):
        with open(category_file, "w") as f:
            json.dump({"amazon": "Shopping", "zomato": "Food"}, f, indent=4)

    # Open in default editor
    if platform.system() == "Windows":
        os.startfile(category_file)
    elif platform.system() == "Darwin":
        subprocess.call(["open", category_file])
    else:
        subprocess.call(["xdg-open", category_file])


# For standalone execution
if __name__ == "__main__":
    launch_gui()