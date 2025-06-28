import sqlite3
import pandas as pd


# # Dynamically build absolute path to db
# db_path = os.path.join(os.path.dirname(__file__), "transactions.db")
#
# # Connect to the database
# conn = sqlite3.connect(db_path)
#
# # Load into DataFrame
# df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date ASC LIMIT 10;", conn)
# print(df.head())
#
# conn.close()

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Dynamically build absolute path to db
db_path = os.path.join(os.path.dirname(__file__), "transactions.db")

# Connect to the database
conn = sqlite3.connect(db_path)

df = pd.read_sql_query("SELECT * FROM transactions", conn)
conn.close()

# Ensure datetime format
df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True, errors='coerce')
df = df.dropna(subset=['date'])
df['month'] = df['date'].dt.to_period('M')

# Group by month and bank
monthly = df.groupby(['month', 'bank'])['amount'].sum().unstack().fillna(0)

# Plot
monthly.plot(kind='bar', figsize=(14, 6), title="Monthly Spend by Bank")
plt.ylabel("Amount ₹")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

top_merchants = df['merchant'].value_counts().head(10)
print("🔟 Top Merchants:\n", top_merchants)

summary = df.groupby('bank')['amount'].agg(['count', 'sum', 'mean', 'max'])
print("\n📊 Transaction Summary:\n", summary)

if df['category'].notna().sum() > 0:
    cat_spend = df.groupby('category')['amount'].sum().sort_values(ascending=False).head(10)
    print("\n📈 Top Categories by Spend:\n", cat_spend)


