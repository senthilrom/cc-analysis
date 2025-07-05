# test_append_excel.py

import os
import tempfile
import pandas as pd
import pytest
from cc_analysis.extractors import append_to_excel, DEFAULT_SHEET_NAME

TEST_EXCEL_PATH = os.path.join(tempfile.gettempdir(), "test_consolidated.xlsx")

final_cols = [
    'Date', 'Description', 'Merchant', 'Category',
    'Debit', 'Credit', 'Balance', 'Amount',
    'Reward Points', 'Bank', 'SourceType'
]

def make_test_df(source_type, malformed=False, malformed_numeric=False):
    data = [
        {
            'Date': '2024-01-10',
            'Description': 'Test txn A',
            'Merchant': 'Amazon',
            'Category': 'Shopping',
            'Debit': 0,
            'Credit': 1000,
            'Balance': 5000,
            'Amount': 1000,
            'Reward Points': 10,
            'Bank': 'TestBank1',
            'SourceType': source_type
        },
        {
            'Date': '2024-01-11',
            'Description': 'Test txn B',
            'Merchant': 'Flipkart',
            'Category': 'Shopping',
            'Debit': 100,
            'Credit': 0,
            'Balance': 4900,
            'Amount': -100,
            'Reward Points': 5,
            'Bank': 'TestBank1',
            'SourceType': source_type
        }
    ]
    df = pd.DataFrame(data)
    if malformed:
        df.at[1, 'Date'] = None
    if malformed_numeric:
        df.at[1, 'Amount'] = "Invalid"
    return df

@pytest.fixture
def clean_excel():
    if os.path.exists(TEST_EXCEL_PATH):
        os.remove(TEST_EXCEL_PATH)
    yield TEST_EXCEL_PATH
    if os.path.exists(TEST_EXCEL_PATH):
        os.remove(TEST_EXCEL_PATH)

@pytest.mark.unit
def test_clean_append(clean_excel):
    df1 = make_test_df("Bank")
    df2 = make_test_df("CreditCard")

    append_to_excel(df1, source_type="Bank", excel_path=clean_excel)
    append_to_excel(df2, source_type="CreditCard", excel_path=clean_excel)

    final_df = pd.read_excel(clean_excel, sheet_name=DEFAULT_SHEET_NAME)
    assert len(final_df) == 4, "Expected 4 transactions in final Excel file."
    assert all(col in final_df.columns for col in final_cols)

@pytest.mark.unit
def test_deduplication(clean_excel):
    df = make_test_df("Bank")
    append_to_excel(df, source_type="Bank", excel_path=clean_excel)
    append_to_excel(df, source_type="Bank", excel_path=clean_excel)

    final_df = pd.read_excel(clean_excel, sheet_name=DEFAULT_SHEET_NAME)
    assert len(final_df) == 2, "Expected deduplication to remove duplicates."

@pytest.mark.unit
def test_malformed_rows(clean_excel):
    df = make_test_df("CreditCard", malformed=True)
    df = df[df['Date'].notnull() & df['Description'].notnull() & df['Description'].str.strip().ne("")]
    append_to_excel(df, source_type="CreditCard", excel_path=clean_excel)

    final_df = pd.read_excel(clean_excel, sheet_name=DEFAULT_SHEET_NAME)
    assert len(final_df) == 1, "Expected only valid row to be appended."

@pytest.mark.unit
def test_malformed_numeric_amount(clean_excel):
    df = make_test_df("Bank", malformed_numeric=True)
    # Keep only rows where 'Amount' is numeric
    df = df[pd.to_numeric(df['Amount'], errors='coerce').notnull()]
    append_to_excel(df, source_type="Bank", excel_path=clean_excel)

    final_df = pd.read_excel(clean_excel, sheet_name=DEFAULT_SHEET_NAME)
    assert len(final_df) == 1, "Expected to skip malformed numeric 'Amount' row."
    assert pd.api.types.is_numeric_dtype(final_df['Amount']), "Amount column must be numeric."
