# cc_analysis/categorizer.py
import os
import json

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

def load_category_mappings():
    if os.path.exists(CATEGORIES_PATH):
        with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def assign_category(description, merchant, categories_dict):
    full_text = f"{description} {merchant}".lower()
    for category, keywords in categories_dict.items():
        for keyword in keywords:
            if keyword.lower() in full_text:
                return category  # ✅ Return first matching category
    return "Uncategorized"
