import unittest
import os
import json
import pandas as pd
from cc_analysis.extractors import extract_hdfc, extract_indusind, append_to_excel
from cc_analysis.utils import validate_pdf_password

DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")

class TestExtractors(unittest.TestCase):

    def setUp(self):
        self.excel_path = os.path.join(DATA_DIR, "test_output.xlsx")
        self.dummy_df = pd.DataFrame({
            "Date": ["01/01/2025"],
            "Description": ["TEST ENTRY"],
            "Amount": [123.45],
            "Bank": ["HDFC"]
        })
        self.dummy_df.to_excel(self.excel_path, index=False)

    def tearDown(self):
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)

    def test_append_to_excel_dedup(self):
        count = append_to_excel(self.dummy_df.copy(), self.excel_path)
        self.assertEqual(count, 1)

    def test_extract_hdfc_valid(self):
        pdf_path = os.path.join(DATA_DIR, "mock_hdfc.pdf")
        self.assertTrue(validate_pdf_password(pdf_path, password=None))

    def test_extract_indusind_valid(self):
        pdf_path = os.path.join(DATA_DIR, "mock_indusind.pdf")
        self.assertTrue(validate_pdf_password(pdf_path, password=None))

if __name__ == '__main__':
    unittest.main()