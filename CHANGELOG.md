# Changelog

## [v3.0] - 2025-07-06
### Added
- Unified Excel sheet for CreditCard and Bank transactions.
- Deduplication logic using `['Date', 'Description', 'Debit', 'Credit', 'Bank', 'SourceType']`
- Amount column automatically derived from Credit - Debit
- Unit tests with PyTest covering:
  - Clean append
  - Deduplication
  - Malformed rows (missing values, non-numeric amounts)

### Changed
- Switched to single sheet output: `All_Transactions`
- Enforced column structure and type checks before writing

### Fixed
- Resolved issue with malformed numeric data in 'Amount'
- Correct handling of empty or incomplete rows

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