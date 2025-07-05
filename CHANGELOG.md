v3.0.0 - 2025-06-29

🔄 Unified database (consolidated.db) for credit card and bank statements

🆕 Added SourceType column to distinguish between CreditCard and Bank

📊 Enhanced analytics foundation for consolidated spend pattern analysis

📁 Excel consolidated into consolidated_statements_v3.xlsx

📈 Future-proof structure for monthly & category-wise spend insights

v2.0.0 - 2025-06-29

✅ Integrated credit card and bank statement processing into a unified GUI.

📁 Implemented support for .pdf, .csv, .xls, .xlsx in a single upload flow.

🔒 Added secure and flexible password-based bank detection for PDF.

🏦 Added ICICI, HDFC, IndusInd bank parsers.

📂 Added standardized storage paths to Documents/cc-analysis.

💾 Auto-save to transactions.db, bank_transactions.db.

🧠 Intelligent CSV bank-type identification via header matching.

🧮 Formatted debit/credit/balance amounts with commas.

🪵 All logs redirected to error.log via log_error().