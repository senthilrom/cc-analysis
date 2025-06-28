# cc_analysis/utils.py

import pdfplumber
import json
import os
import logging
from cc_analysis.constants import SECRETS_PATH, LOG_FILE


def validate_pdf_password(pdf_path, password):
    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            return True
    except Exception:
        return False

def load_passwords():
    try:
        with open(SECRETS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"  # append mode
)

def log_error(message):
    logging.error(message)

def load_category_mappings():
    path = os.path.join(os.path.dirname(__file__), "categories.json")
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def assign_category(description, merchant, mappings):
    text = f"{description} {merchant}".lower()
    for keyword, category in mappings.items():
        if keyword.lower() in text:
            return category
    return ""
