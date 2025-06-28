import unittest
from cc_analysis.categorizer import apply_category, load_categories

class TestCategorizer(unittest.TestCase):

    def setUp(self):
        self.categories = {
            "amazon": "Shopping",
            "zomato": "Food",
            "irctc": "Travel",
            "petrol": "Fuel"
        }

    def test_exact_match_in_description(self):
        desc = "ORDER FROM AMAZON MUMBAI"
        merchant = ""
        result = apply_category(desc, merchant, self.categories)
        self.assertEqual(result, "Shopping")

    def test_exact_match_in_merchant(self):
        desc = "DINNER AT HOME"
        merchant = "ZOMATO LTD"
        result = apply_category(desc, merchant, self.categories)
        self.assertEqual(result, "Food")

    def test_partial_match(self):
        desc = "IRCTC Eticketing Gurgaon"
        merchant = ""
        result = apply_category(desc, merchant, self.categories)
        self.assertEqual(result, "Travel")

    def test_no_match_returns_uncategorized(self):
        desc = "UNKNOWN PAYMENT"
        merchant = "XYZ STORE"
        result = apply_category(desc, merchant, self.categories)
        self.assertEqual(result, "Uncategorized")

    def test_load_categories(self):
        result = load_categories()
        self.assertIsInstance(result, dict)
        self.assertIn("amazon", result)

if __name__ == '__main__':
    unittest.main()