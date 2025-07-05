import sqlite3
import pandas as pd
from cc_analysis.constants import CONSOLIDATED_DB_PATH

def check_source_types(db_path=CONSOLIDATED_DB_PATH):
    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql("SELECT DISTINCT SourceType FROM transactions", conn)

            print("\n📊 Source Types found in database:")
            print(df.to_string(index=False))

            has_bank = 'Bank' in df['SourceType'].values
            has_cc = 'CreditCard' in df['SourceType'].values

            print(f"\n✅ Bank data present: {has_bank}")
            print(f"✅ Credit Card data present: {has_cc}")

            df_counts = pd.read_sql("SELECT SourceType, COUNT(*) as Count FROM transactions GROUP BY SourceType", conn)
            print("\n🔢 Transaction Counts by Source:")
            print(df_counts)

            return {
                "Bank": has_bank,
                "CreditCard": has_cc,
                "AllTypes": df['SourceType'].tolist()
            }
    except Exception as e:
        print(f"❌ Error reading DB: {e}")
        return None

# If run as a script
if __name__ == "__main__":
    check_source_types()