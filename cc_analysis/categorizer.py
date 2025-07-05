# cc_analysis/categorizer.py

import json
import os

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")


def load_category_mappings():
    """
    Loads category mapping dictionary from categories.json.

    Returns:
        dict: {category: [keywords]}
    """
    if os.path.exists(CATEGORIES_PATH):
        try:
            with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            # Return empty mapping if JSON is malformed
            print(f"⚠️ Failed to load category mappings: {e}")
            return {}
    return {}


def assign_category(description, merchant, categories_dict):
    """
    Assigns category based on keywords in description + merchant.

    Args:
        description (str): Transaction description.
        merchant (str): Merchant name (optional).
        categories_dict (dict): {category: [keywords]}

    Returns:
        str: Matched category, or "Uncategorized"
    """
    full_text = f"{description} {merchant}".lower()

    for category, keywords in categories_dict.items():
        for keyword in keywords:
            if keyword.lower() in full_text:
                return category

    return "Uncategorized"