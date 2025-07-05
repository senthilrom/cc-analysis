# cc_analysis/utils.py

import json
import logging
import os
from datetime import datetime

import pdfplumber

from cc_analysis.constants import SECRETS_PATH, LOG_FILE

FAILED_FILES_LOG = "failed_files.log"  # new audit log path

# PDF password validation
def validate_pdf_password(pdf_path, password):
    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            return True
    except Exception:
        return False

# Load bank statement passwords
def load_passwords():
    try:
        with open(SECRETS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

# Logger setup
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"  # append mode
)

# Enhanced log_error function
def log_error(message, file=None, reason=None):
    logging.error(message)

    # Optional audit entry for failed files
    if file and reason:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"{timestamp} | {reason:<15} | {file}\n"
            with open(FAILED_FILES_LOG, "a", encoding="utf-8") as f_log:
                f_log.write(entry)
        except Exception as e:
            logging.error(f"Failed to write to failed_files.log: {e}")

def log_info(message):
    logging.info(message)

# Category mappings for transactions
def load_category_mappings():
    path = os.path.join(os.path.dirname(__file__), "categories.json")
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Assigns category based on description/merchant
def assign_category(description, merchant, mappings):
    text = f"{description} {merchant}".lower()
    for keyword, category in mappings.items():
        if keyword.lower() in text:
            return category
    return ""