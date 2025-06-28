# cc_analysis/constants.py

import os
from pathlib import Path

# Base paths
APPDATA_DIR = Path(os.getenv("APPDATA", os.path.expanduser("~"))) / "cc-analysis"
DOCS_DIR = Path.home() / "Documents" / "cc-analysis"

# Ensure directories exist
APPDATA_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# File paths
SECRETS_PATH = APPDATA_DIR / "secrets.json"
LOG_FILE = APPDATA_DIR / "error.log"
DB_PATH = DOCS_DIR / "transactions.db"
EXCEL_PATH = DOCS_DIR / "consolidated_statements.xlsx"
CATEGORY_MAP_PATH = Path(__file__).parent / "categories.json"
HELP_PATH = Path(__file__).parent / "help.txt"
ABOUT_PATH = Path(__file__).parent / "about.txt"

# Column headers for consistent DataFrames
COLUMNS = [
    "Date", "Description", "Merchant", "Category",
    "Reward Points", "Amount", "Bank"
]
