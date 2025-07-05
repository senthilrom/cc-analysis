# cc_analysis/bank_detector.py

import os
import re

import pdfplumber

from cc_analysis.utils import log_error

EXCEL_PATH = "consolidated_statements.xlsx"
DB_PATH = os.path.join(os.path.dirname(__file__), "transactions.db")


def detect_bank_type(pdf_path, password):
    """
    Tries to detect the issuing bank based on PDF text patterns.
    Supports: HDFC, IndusInd
    """
    # Signature line patterns
    hdfc_pattern = re.compile(r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}")
    indusind_pattern = re.compile(r"\d{2}/\d{2}/\d{4}\s+.+\s+[A-Z\s]+\s+\d+\s+[\d,]+\.\d{2}\s+(CR|DR)")

    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                for line in text.splitlines():
                    stripped = line.strip()
                    if hdfc_pattern.match(stripped):
                        return "HDFC"
                    elif indusind_pattern.match(stripped):
                        return "IndusInd"

                # Fallback heuristics
                lower_text = text.lower()
                if "reward points" in lower_text or "transaction details" in lower_text:
                    return "IndusInd"
                elif "statement of account" in lower_text or "total dues" in lower_text:
                    return "HDFC"

    except Exception as e:
        log_error(f"{pdf_path} - ❌ Error reading PDF: {str(e)}")
        raise

    return None  # Explicit fallback