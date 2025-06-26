import unittest
import pandas as pd
from cc_analysis.extractors import extract_hdfc, extract_indusind, append_to_excel
import os

class TestStatementExtractors(unittest.TestCase):

    def setUp(self):
        self.test_data_dir = "tests/test_data"
        os.makedirs(self.test_data_dir, exist_ok=True)

        self.dummy_df = pd.DataFrame({
            "Datetime": ["01/01/2025 10:00:00"],
            "Description": ["TEST ENTRY"],
            "Amount": [123.45]
        })

        self.excel_path = os.path.join(self.test_data_dir, "test_output.xlsx")
        self.dummy_df.to_excel(self.excel_path, index=False)

    def test_append_to_excel_dedup(self):
        new_df = self.dummy_df.copy()
        count = append_to_excel(new_df, self.excel_path, unique_cols=["Datetime", "Description", "Amount"])
        self.assertEqual(count, 1)

    def test_help_about_txt_files_exist(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cc_analysis"))
        help_path = os.path.join(base_dir, "help.txt")
        about_path = os.path.join(base_dir, "about.txt")
        self.assertTrue(os.path.exists(help_path), f"Missing: {help_path}")
        self.assertTrue(os.path.exists(about_path), f"Missing: {about_path}")

    def tearDown(self):
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)

    def test_extract_hdfc_valid(self):
        from cc_analysis.extractors import extract_hdfc
        df = extract_hdfc("tests/test_data/mock_hdfc.pdf", password=None)
        self.assertGreater(len(df), 0)

    def test_extract_indusind_valid(self):
        from cc_analysis.extractors import extract_indusind
        df = extract_indusind("tests/test_data/mock_indusind.pdf", password=None)
        self.assertGreater(len(df), 0)

    def test_hdfc_wrong_password(self):
        from cc_analysis.extractors import extract_hdfc
        with self.assertRaises(Exception):
            extract_hdfc("tests/test_data/mock_hdfc_encrypted.pdf", password="wrongpass")

    def test_hdfc_correct_password(self):
        from cc_analysis.extractors import extract_hdfc
        df = extract_hdfc("tests/test_data/mock_hdfc_encrypted.pdf", password="hdfc123")
        self.assertGreater(len(df), 0)

    def test_indusind_wrong_password(self):
        from cc_analysis.extractors import extract_indusind
        with self.assertRaises(Exception):
            extract_indusind("tests/test_data/mock_indusind_encrypted.pdf", password="wrongpass")

    def test_indusind_correct_password(self):
        from cc_analysis.extractors import extract_indusind
        df = extract_indusind("tests/test_data/mock_indusind_encrypted.pdf", password="indusind123")
        self.assertGreater(len(df), 0)

if __name__ == "__main__":
    unittest.main()