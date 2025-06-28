import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "transactions.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
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
                amount REAL,
                unique_key TEXT UNIQUE
            )
        ''')
        conn.commit()


def generate_unique_key(bank, date, description, amount):
    hash_input = f"{bank}|{date}|{description.strip().lower()}|{amount}"
    return hashlib.sha256(hash_input.encode()).hexdigest()


def insert_transactions(df, bank_name):
    """
    Inserts a DataFrame into the DB. Adds a 'unique_key' column to prevent duplicates.
    """
    if df.empty:
        return 0

    init_db()
    inserted_count = 0
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for _, row in df.iterrows():
            date = row.get("Datetime") or row.get("Date")
            description = row.get("Description") or row.get("Transaction Details")
            merchant = row.get("Merchant", "")
            category = row.get("Category", "")
            reward_points = row.get("Reward Points", 0)
            amount = row["Amount"]

            unique_key = generate_unique_key(bank_name, date, description, amount)

            try:
                c.execute('''
                    INSERT INTO transactions (bank, date, description, merchant, category, reward_points, amount, unique_key)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (bank_name, date, description, merchant, category, reward_points, amount, unique_key))
                inserted_count += 1
            except sqlite3.IntegrityError:
                continue  # Duplicate

        conn.commit()

    return inserted_count
