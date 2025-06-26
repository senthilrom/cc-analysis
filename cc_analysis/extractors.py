# cc_analysis/extractors.py

import pdfplumber
import pandas as pd
import os
import re

def extract_hdfc(pdf_path, password):
    pattern = re.compile(r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})\s+(.+?)\s+([\d,]+\.\d{2})(\s+Cr)?$")
    transactions = []
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
                    transactions.append([datetime_str, description.strip(), amount])
    return pd.DataFrame(transactions, columns=["Datetime", "Description", "Amount"])

def extract_indusind(pdf_path, password):
    pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([A-Z\s]+)\s+(\d+)\s+([\d,]+\.\d{2})\s+(CR|DR)")
    transactions = []
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
                    transactions.append([date, desc.strip(), merchant.strip(), "", points, amount])
    return pd.DataFrame(transactions, columns=[
        "Date", "Transaction Details", "Merchant", "Category", "Reward Points", "Amount"
    ])

def append_to_excel(df, excel_path, unique_cols):
    if os.path.exists(excel_path):
        df_existing = pd.read_excel(excel_path)
        frames = [df_existing, df]
        frames = [f for f in frames if not f.empty and not f.isna().all(axis=None)]
        df_combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        df_combined.drop_duplicates(subset=unique_cols, inplace=True)
    else:
        df_combined = df
    df_combined.to_excel(excel_path, index=False)
    return len(df_combined)