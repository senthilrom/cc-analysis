# Credit Card & Bank Transaction Consolidator

This project consolidates PDF, CSV, and XLS statements from multiple banks and credit cards into a single deduplicated Excel sheet.

## ✅ Features
- Parse HDFC, ICICI, IndusInd bank statements
- Normalize and unify transaction formats
- Deduplicate by key columns
- Validate numeric fields like `Amount`
- Save to Excel under `All_Transactions` sheet

## 🚀 Setup

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -r requirements.txt