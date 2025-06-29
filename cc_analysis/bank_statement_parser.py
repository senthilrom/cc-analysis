# cc_analysis/bank_statement_parser.py

import pandas as pd
import sqlite3
import os
from io import StringIO
from cc_analysis.utils import log_error

# === Standardize Columns ===
def standardize_df(df, bank_name):
    df['Bank'] = bank_name
    df = df[['Date', 'Description', 'Debit', 'Credit', 'Balance', 'Bank']]
    df.loc[:, 'Description'] = df['Description'].astype(str)
    df = df[df['Date'].notnull() & df['Description'].notnull() & (df['Description'].str.strip() != '')]
    return df

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
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                upper_line = line.upper()
                if all(k in upper_line for k in ['SR.NO.', 'DATE', 'TYPE', 'DESCRIPTION', 'DEBIT', 'CREDIT', 'BALANCE']):
                    return 'IndusInd'
                if all(k in upper_line for k in ['DATE', 'MODE', 'PARTICULARS', 'DEPOSITS', 'WITHDRAWALS', 'BALANCE']):
                    return 'ICICI'
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
        df['Debit'] = pd.to_numeric(df.get('WITHDRAWALS', 0), errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df.get('DEPOSITS', 0), errors='coerce').fillna(0)
        df['Balance'] = pd.to_numeric(df.get('BALANCE', 0), errors='coerce').ffill()

        return standardize_df(df, 'ICICI')
    except Exception as e:
        log_error(f"Error parsing ICICI file: {e}")
        return pd.DataFrame(columns=['Date', 'Description', 'Debit', 'Credit', 'Balance', 'Bank'])

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
        df['Debit'] = pd.to_numeric(df['Debit'].replace('-', 0), errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'].replace('-', 0), errors='coerce').fillna(0)
        df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce').ffill()

        return standardize_df(df, 'IndusInd')
    except Exception as e:
        log_error(f"Error parsing IndusInd file: {e}")
        return pd.DataFrame(columns=['Date', 'Description', 'Debit', 'Credit', 'Balance', 'Bank'])

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
        df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce').ffill()

        return standardize_df(df, 'HDFC')
    except Exception as e:
        log_error(f"Error parsing HDFC file: {e}")
        return pd.DataFrame(columns=['Date', 'Description', 'Debit', 'Credit', 'Balance', 'Bank'])

# === Database Writer ===
def save_to_db(df, db_path="bank_transactions.db"):
    try:
        with sqlite3.connect(db_path) as conn:
            df.to_sql("transactions", conn, if_exists="replace", index=False)
    except Exception as e:
        log_error(f"Error writing to {db_path}: {e}")

# === Consolidation Function ===
def consolidate_all(file_paths, db_path=None, csv_path=None):
    from cc_analysis.constants import BANK_DB_PATH, BANK_CSV_PATH
    import os
    import pandas as pd

    db_path = db_path or str(BANK_DB_PATH)
    csv_path = csv_path or str(BANK_CSV_PATH)

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
                    log_error(f"Parsing {bank} file: {file}")
                    df = parse_icici(file)
                elif bank == "IndusInd":
                    log_error(f"Parsing {bank} file: {file}")
                    df = parse_indusind(file)
                else:
                    log_error(f"Unknown bank format for file: {file}")
                    continue
            else:
                continue

            if not df.empty:
                frames.append(df)

        if not frames:
            log_error("No valid transactions found in any of the uploaded files.")
            return

        numeric_df = pd.concat(frames, ignore_index=True).sort_values(by='Date')
        export_df = numeric_df.copy()
        for col in ['Debit', 'Credit', 'Balance']:
            export_df[col] = export_df[col].map(lambda x: f"{x:,.2f}")

        export_df.to_csv(csv_path, index=False)
        save_to_db(numeric_df, db_path)

    except Exception as e:
        log_error(f"Error during consolidation: {e}")

# For direct execution
if __name__ == "__main__":
    import sys
    consolidate_all(sys.argv[1:])