# cc_analysis/bank_statement_parser.py

import os
import sqlite3
from io import StringIO

import pandas as pd

from cc_analysis.constants import CONSOLIDATED_DB_PATH, EXCEL_PATH
from cc_analysis.extractors import append_to_excel
from cc_analysis.utils import log_error, log_info

# === Standardize Columns for All Transactions ===

STANDARD_COLUMNS = [
    'Date', 'Description', 'Merchant', 'Category',
    'Reward Points', 'Bank', 'SourceType',
    'Debit', 'Credit', 'Balance'
]

# === Standardize Columns ===
def standardize_df(df, bank_name, source_type="Bank"):
    import numpy as np

    if not isinstance(df, pd.DataFrame):
        log_error(f"❌ Input to standardize_df is not a DataFrame (got {type(df)}). Skipping.")
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    df = df.copy()
    df['Bank'] = bank_name
    df['SourceType'] = source_type

    # --- Date ---
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    else:
        df['Date'] = pd.NaT

    # --- Description ---
    if 'Description' not in df.columns:
        df['Description'] = ''
    df['Description'] = df['Description'].fillna('').astype(str).str.strip()

    # --- Merchant ---
    if 'Merchant' not in df.columns:
        df['Merchant'] = ''
    df['Merchant'] = df['Merchant'].fillna('').astype(str)

    # --- Category ---
    if 'Category' not in df.columns:
        df['Category'] = ''
    df['Category'] = df['Category'].fillna('').astype(str)

    # --- Reward Points ---
    try:
        if 'Reward Points' not in df.columns:
            df['Reward Points'] = 0
        df['Reward Points'] = pd.to_numeric(df['Reward Points'], errors='coerce').fillna(0).astype(int)
    except Exception as e:
        log_error(f"⚠️ Error in Reward Points column: {e}")
        df['Reward Points'] = 0

    # --- Debit and Credit ---
    for col in ['Debit', 'Credit']:
        try:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        except Exception as e:
            log_error(f"⚠️ Error in {col} column: {e}")
            df[col] = 0.0

    # --- Balance ---
    try:
        if 'Balance' not in df.columns or not isinstance(df['Balance'], pd.Series):
            df['Balance'] = np.nan
        else:
            df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce')
            if bank_name in ['ICICI', 'IndusInd', 'HDFC']:
                df['Balance'] = df['Balance'].fillna(method='ffill')
            else:
                df['Balance'] = df['Balance'].fillna(np.nan)
    except Exception as e:
        log_error(f"❌ Error handling Balance column for {bank_name}: {e}")
        df['Balance'] = np.nan

    # --- Ensure all columns exist ---
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = None

    # --- Reorder and filter ---
    df = df[STANDARD_COLUMNS]
    df = df[df['Date'].notnull() & df['Description'].str.strip().ne('')]

    return df.reset_index(drop=True)


# === Helper to detect delimiter ===
def detect_delimiter(line):
    if '\t' in line:
        return '\t'
    elif ',' in line:
        return ','
    else:
        return r'\s{2,}'

# === Identify CSV format by headers ===
def identify_csv_bank(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                normalized_line = line.strip().upper().replace('"', '').replace("'", "")
                if all(keyword in normalized_line for keyword in ['SR.NO.', 'DATE', 'TYPE', 'DESCRIPTION', 'DEBIT', 'CREDIT', 'BALANCE']):
                    return 'IndusInd'
                if all(keyword in normalized_line for keyword in ['DATE', 'MODE', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']):
                    return 'ICICI'
        log_error(f"⚠️ Could not identify bank type from CSV: {file_path}")
    except Exception as e:
        log_error(f"Error identifying bank from CSV: {e}")
    return None

# === ICICI Bank Parser ===
def parse_icici(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        header_keywords = ['DATE', 'MODE', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']
        header_line_index = next((i for i, line in enumerate(lines) if all(k in line.upper() for k in header_keywords)), None)
        if header_line_index is None:
            raise ValueError("Could not find the transaction table header in ICICI file.")

        delimiter = detect_delimiter(lines[header_line_index])
        headers = [h.strip().upper() for h in lines[header_line_index].strip().split(delimiter)]
        data_str = "".join(lines[header_line_index + 1:])
        df = pd.read_csv(StringIO(data_str), sep=delimiter, names=headers, engine='python', on_bad_lines='skip')

        df['Date'] = pd.to_datetime(df['DATE'], format='%d-%m-%Y', errors='coerce')
        df['Description'] = df.get('MODE', '').fillna('') + ' ' + df['PARTICULARS'].fillna('')
        df['Debit'] = pd.to_numeric(df.get('WITHDRAWALS'), errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df.get('DEPOSITS'), errors='coerce').fillna(0)
        df['Balance'] = pd.to_numeric(df.get('BALANCE'), errors='coerce').fillna(method='ffill')

        log_info(f"{file_path} - ✅ ICICI parse successful, rows extracted: {len(df)}")

        if 'Amount' not in df.columns:
            df['Amount'] = df['Credit'] - df['Debit']

        return standardize_df(df, 'ICICI')

    except Exception as e:
        log_error(f"Error parsing ICICI file: {e}")
        return pd.DataFrame(columns=STANDARD_COLUMNS)

# === IndusInd Bank Parser ===
def parse_indusind(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        header_keywords = ['SR.NO.', 'DATE', 'TYPE', 'DESCRIPTION', 'DEBIT', 'CREDIT', 'BALANCE']
        header_line_index = next((i for i, line in enumerate(lines) if all(k in line.upper() for k in header_keywords)), None)
        if header_line_index is None:
            raise ValueError("Could not find transaction header in IndusInd file.")

        delimiter = detect_delimiter(lines[header_line_index])
        data_str = "".join(lines[header_line_index + 1:])
        headers = ['SrNo', 'Date', 'Type', 'Description', 'Debit', 'Credit', 'Balance']

        df = pd.read_csv(StringIO(data_str), sep=delimiter, names=headers, engine='python', on_bad_lines='skip', dtype=str)
        df['Date'] = pd.to_datetime(df['Date'], format='%d %b %Y', errors='coerce')
        df['Description'] = df['Description'].astype(str)
        df['Debit'] = pd.to_numeric(df['Debit'].replace('-', '0'), errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'].replace('-', '0'), errors='coerce').fillna(0)
        df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce').fillna(method='ffill')

        log_info(f"{file_path} - ✅ IndusInd parse successful, rows extracted: {len(df)}")
        if 'Amount' not in df.columns:
            df['Amount'] = df['Credit'] - df['Debit']

        return standardize_df(df, 'IndusInd')

    except Exception as e:
        log_error(f"Error parsing IndusInd file: {e}")
        return pd.DataFrame(columns=STANDARD_COLUMNS)

# === HDFC Bank Parser ===
def parse_hdfc(file_path):
    try:
        df_raw = pd.read_excel(file_path, dtype=str)
        df_raw.columns = df_raw.columns.str.strip()

        header_row_index = next((i for i, row in df_raw.iterrows() if 'DATE' in str(row.iloc[0]).strip().upper()), None)
        if header_row_index is None:
            raise ValueError("Could not locate HDFC transaction table in the Excel file.")

        df = pd.read_excel(file_path, skiprows=header_row_index + 1)
        df.columns = ['Date', 'Narration', 'ChqRefNo', 'ValueDate', 'Withdrawal', 'Deposit', 'Balance']

        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y', errors='coerce')
        df['Description'] = df['Narration']
        df['Debit'] = pd.to_numeric(df['Withdrawal'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Deposit'], errors='coerce').fillna(0)
        df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce').fillna(method='ffill')

        log_info(f"{file_path} - ✅ HDFC parse successful, rows extracted: {len(df)}")
        if 'Amount' not in df.columns:
            df['Amount'] = df['Credit'] - df['Debit']

        return standardize_df(df, 'HDFC')

    except Exception as e:
        log_error(f"Error parsing HDFC file: {e}")
        return pd.DataFrame(columns=STANDARD_COLUMNS)

# === Consolidated Database Writer ===
def save_to_consolidated_db(df, source_type, db_path=CONSOLIDATED_DB_PATH):
    try:
        df = df.copy()
        df['SourceType'] = source_type

        # Ensure all standard columns exist
        for col in STANDARD_COLUMNS:
            if col not in df.columns:
                df[col] = None

        # Convert Date to string (SQLite doesn't support Timestamp)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')

        # Ensure correct column order
        df = df[STANDARD_COLUMNS]

        with sqlite3.connect(db_path) as conn:
            table_exists = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'").fetchone()
            if table_exists:
                existing_df = pd.read_sql("SELECT * FROM transactions", conn)
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df.drop_duplicates(inplace=True)
            else:
                combined_df = df

            combined_df.to_sql("transactions", conn, if_exists="replace", index=False)

    except Exception as e:
        log_error(f"Error writing to consolidated DB: {e}")

# === Consolidation Function ===
def consolidate_all(file_paths, db_path=None):
    db_path = db_path or str(CONSOLIDATED_DB_PATH)

    try:
        frames = []
        for file in file_paths:
            ext = os.path.splitext(file)[1].lower()
            df = pd.DataFrame()

            if ext in [".xls", ".xlsx"]:
                df = parse_hdfc(file)

            elif ext == ".csv":
                bank = identify_csv_bank(file)
                if bank == "ICICI":
                    log_info(f"Parsing ICICI file: {file}")
                    df = parse_icici(file)
                elif bank == "IndusInd":
                    log_info(f"Parsing IndusInd file: {file}")
                    df = parse_indusind(file)
                else:
                    log_error(f"❌ Unknown bank format for file: {file}")
                    continue
            else:
                log_error(f"❌ Unsupported file type: {file}")
                continue

            if not df.empty:
                frames.append(df)
            else:
                log_error(f"⚠️ No transactions extracted from file: {file}")

        if not frames:
            log_error("🚫 No valid transactions found in any of the uploaded files.")
            return

        numeric_df = pd.concat(frames, ignore_index=True)
        numeric_df = numeric_df.sort_values(by='Date', key=lambda col: pd.to_datetime(col, errors='coerce'))

        # --- Ensure numeric fields are numeric ---
        for col in ['Debit', 'Credit']:
            if col not in numeric_df.columns:
                numeric_df[col] = 0.0
            else:
                numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce').fillna(0.0)

        # --- Create Amount column ---
        if 'Amount' not in numeric_df.columns:
            numeric_df['Amount'] = numeric_df['Credit'] - numeric_df['Debit']
            log_info("🧮 Created 'Amount' column from Credit - Debit")

        # --- Optional formatting for export ---
        export_df = numeric_df.copy()
        for col in ['Debit', 'Credit', 'Balance']:
            if col in export_df.columns:
                export_df[col] = export_df[col].map(lambda x: f"{x:,.2f}" if pd.notnull(x) else '')

        # ✅ Save to DB
        save_to_consolidated_db(numeric_df, source_type="Bank", db_path=db_path)

        log_info(f"✅ Final columns before append_to_excel: {numeric_df.columns.tolist()}")

        # ✅ Save to Excel
        append_to_excel(numeric_df, source_type="Bank", excel_path=EXCEL_PATH)

    except Exception as e:
        log_error(f"❌ Error during consolidation: {e}")

# For direct execution
if __name__ == "__main__":
    import sys
    consolidate_all(sys.argv[1:])