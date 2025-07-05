# cc_analysis/db.py

import hashlib
import sqlite3

import pandas as pd

from cc_analysis.constants import CONSOLIDATED_DB_PATH
from cc_analysis.utils import log_error, log_info


def init_db():
    with sqlite3.connect(CONSOLIDATED_DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank TEXT,
                date TEXT,
                description TEXT,
                merchant TEXT,
                category TEXT,
                reward_points INTEGER,
                debit REAL,
                credit REAL,
                balance REAL,
                source_type TEXT,
                unique_key TEXT UNIQUE
            )
        ''')
        conn.commit()


def generate_unique_key(bank, date, description, debit, credit, source_type):
    hash_input = f"{bank}|{date}|{description.strip().lower()}|{debit}|{credit}|{source_type}"
    return hashlib.sha256(hash_input.encode()).hexdigest()


def insert_transactions(df, bank_name, source_type="CreditCard"):
    """
    Inserts transactions into DB using 'Debit' and 'Credit' columns.
    Adds a unique key hash for duplicate prevention.
    """
    if df.empty:
        log_info("insert_transactions: Empty dataframe provided.")
        return 0

    init_db()
    inserted_count = 0

    with sqlite3.connect(CONSOLIDATED_DB_PATH) as conn:
        c = conn.cursor()
        for _, row in df.iterrows():
            date = pd.to_datetime(row.get("Date") or row.get("Datetime"), errors='coerce').date()
            description = row.get("Description", "")
            merchant = row.get("Merchant", "")
            category = row.get("Category", "")
            reward_points = int(row.get("Reward Points", 0) or 0)
            debit = float(row.get("Debit", 0.0) or 0)
            credit = float(row.get("Credit", 0.0) or 0)
            balance = row.get("Balance")
            balance = float(balance) if pd.notnull(balance) else None

            try:
                unique_key = generate_unique_key(bank_name, date, description, debit, credit, source_type)
                c.execute('''
                    INSERT INTO transactions (
                        bank, date, description, merchant, category,
                        reward_points, debit, credit, balance, source_type, unique_key
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bank_name, date, description, merchant, category,
                    reward_points, debit, credit, balance, source_type, unique_key
                ))
                inserted_count += 1

            except sqlite3.IntegrityError:
                log_info(f"Duplicate skipped for: {description} on {date}")
                continue
            except Exception as e:
                log_error(f"Failed to insert row: {e} | {row.to_dict()}")

        conn.commit()

    log_info(f"Inserted {inserted_count} new transactions for {bank_name}")
    return inserted_count