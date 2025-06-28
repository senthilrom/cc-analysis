# 💳 Credit Card Statement Consolidator

A Python-based desktop application that extracts and consolidates credit card statements (PDF) from **HDFC** and **IndusInd** banks into a single `.xlsx` file and `.db` database — with auto-categorization and pattern analysis.

---

## 🔧 Features

- 🔐 Password-protected PDF extraction
- 🧠 Auto-detect bank type (HDFC / IndusInd)
- 🧮 Auto-categorize expenses using keywords (`categories.json`)
- 📊 Summary charts generated in Excel
- 📁 Consolidated Excel + SQLite DB for analytics
- 🧠 Remembers processed entries (deduplicated)
- 📝 Edit categories easily from GUI
- 🪵 Logs all skipped/invalid PDFs to `error.log`
- 🖼️ Easy GUI with Tkinter (no console window)

---

## 🗂️ File Structure

| File/Folder                      | Purpose                           |
|----------------------------------|-----------------------------------|
| `cc_analysis/`                   | Main app logic (extractors, GUI)  |
| `transactions.db`                | SQLite DB with all transactions   |
| `consolidated_statements.xlsx`   | Merged Excel file                 |
| `secrets.json`                   | PDF passwords (stored in AppData) |
| `categories.json`                | User-defined keyword mappings     |
| `error.log`                      | All errors and skipped files      |

---

## 🚀 Getting Started

### Installation

```bash
git clone https://github.com/senthilrom/cc-analysis.git
cd cc-analysis
pip install -r requirements.txt
python cc_analysis/__main__.py
