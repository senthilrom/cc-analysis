import unittest
import os
import json
from cc_analysis.utils import validate_pdf_password, load_passwords

DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
SECRETS_PATH = os.path.join(os.path.dirname(__file__), "..", "cc_analysis", "secrets.json")

class TestUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(SECRETS_PATH) as f:
            cls.secrets = json.load(f)

    def test_valid_password_hdfc(self):
        pdf_path = os.path.join(DATA_DIR, "mock_hdfc_encrypted.pdf")
        self.assertTrue(validate_pdf_password(pdf_path, self.secrets.get("HDFC")))

    def test_invalid_password_hdfc(self):
        pdf_path = os.path.join(DATA_DIR, "mock_hdfc_encrypted.pdf")
        self.assertFalse(validate_pdf_password(pdf_path, "wrongpass"))

    def test_valid_password_indusind(self):
        pdf_path = os.path.join(DATA_DIR, "mock_indusind_encrypted.pdf")
        self.assertTrue(validate_pdf_password(pdf_path, self.secrets.get("IndusInd")))

    def test_invalid_password_indusind(self):
        pdf_path = os.path.join(DATA_DIR, "mock_indusind_encrypted.pdf")
        self.assertFalse(validate_pdf_password(pdf_path, "invalid"))

    def test_load_passwords(self):
        passwords = load_passwords()
        self.assertIn("HDFC", passwords)
        self.assertIn("IndusInd", passwords)

if __name__ == '__main__':
    unittest.main()