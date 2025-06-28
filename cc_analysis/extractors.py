# cc_analysis/extractors.py

import os
import re
import pdfplumber
import pandas as pd
from cc_analysis.db import insert_transactions
from cc_analysis.excel_summary import update_excel_summary
from cc_analysis.categorizer import assign_category, load_category_mappings
from cc_analysis.constants import COLUMNS
from cc_analysis.constants import EXCEL_PATH

def extract_hdfc(pdf_path, password):
    pattern = re.compile(r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})\s+(.+?)\s+([\d,]+\.\d{2})(\s+Cr)?$")
    transactions = []
    categories = load_category_mappings()

    with pdfplumber.open(pdf_path, password=password) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split("\n"):
                match = pattern.match(line.strip())
                if match:
                    datetime_str, description, amount_str, credit_flag = match.groups()
                    amount = float(amount_str.replace(",", ""))
                    if credit_flag:
                        amount = -amount
                    category = assign_category(description, "", categories)
                    transactions.append([
                        datetime_str,         # Date
                        description.strip(),  # Description
                        "",                   # Merchant
                        category,             # Category
                        0,                    # Reward Points
                        amount,               # Amount
                        "HDFC"                # Bank
                    ])
    return pd.DataFrame(transactions, columns=COLUMNS)

def extract_indusind(pdf_path, password):
    pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([A-Z\s]+)\s+(\d+)\s+([\d,]+\.\d{2})\s+(CR|DR)")
    transactions = []
    categories = load_category_mappings()

    with pdfplumber.open(pdf_path, password=password) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.splitlines():
                match = pattern.match(line.strip())
                if match:
                    date, desc, merchant, points, amount_str, cr_dr = match.groups()
                    amount = float(amount_str.replace(",", ""))
                    if cr_dr == "DR":
                        amount = -amount
                    category = assign_category(desc, merchant, categories)
                    transactions.append([
                        date,
                        desc.strip(),
                        merchant.strip(),
                        str(category),  # 💡 Ensure it's a string
                        int(points),
                        amount,
                        "IndusInd"
                    ])
    return pd.DataFrame(transactions, columns=COLUMNS)

def append_to_excel(df, excel_path=EXCEL_PATH):
    if os.path.exists(excel_path):
        df_existing = pd.read_excel(excel_path)
        df_combined = pd.concat([df_existing, df], ignore_index=True)
        df_combined.drop_duplicates(subset=["Date", "Description", "Amount", "Bank"], inplace=True)
    else:
        df_combined = df

    df_combined.to_excel(excel_path, index=False)
    update_excel_summary(excel_path)
    return len(df_combined)


def save_to_database(df, bank):
    return insert_transactions(df, bank)