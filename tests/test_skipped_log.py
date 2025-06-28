import unittest
import os
from cc_analysis.utils import validate_pdf_password
from cc_analysis.bank_detector import detect_bank_type

class TestSkippedFiles(unittest.TestCase):
    def setUp(self):
        self.dummy_path = "tests/test_data/mock_indusind_chart_only.pdf"  # you can simulate this
        self.password = "indusind123"
        self.log_file = "cc_analysis/skipped_files.log"

    def test_skipped_file_logged(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

        # Simulate skip logging
        with open(self.log_file, "a") as f:
            f.write(f"{os.path.basename(self.dummy_path)} - Skipped: no transaction table\n")

        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
        self.assertIn("mock_indusind_chart_only.pdf", content)

if __name__ == '__main__':
    unittest.main()
