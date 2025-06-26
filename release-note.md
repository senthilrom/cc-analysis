# 📦 Release Notes – Credit Card Statement Extractor

This document tracks all feature updates, enhancements, and fixes for the `cc-analysis` GUI tool.

---

## ✅ Version 1.0.0 – Initial Release (2025-06-26)

### ✨ Features
- GUI for extracting and saving HDFC / IndusInd credit card statements
- Bulk PDF upload support
- Secure password input for encrypted PDFs
- Smart Excel de-duplication
- Dark mode toggle
- Progress bar for batch processing
- “Help” and “About” popups

### 📄 Format Support
- HDFC: `DD/MM/YYYY HH:MM:SS + Description + Amount`
- IndusInd: `Date + Merchant + Category + Reward Points + Amount`

---

## 🔐 Version 1.1.0 – Encrypted PDF Support (TBD)

### 🔒 New
- Encrypted PDF validation before processing
- Error logging to `error.log`
- One error popup per batch on wrong password

### 🧪 Test Improvements
- Auto-generated mock HDFC & IndusInd PDFs
- Encrypted test PDF coverage
- Full test suite (8+ unit tests)

---

## 🔧 Version 1.2.0 – PyInstaller & Deployment Ready (TBD)

### 📦 Packaging
- `.spec` file for clean `.exe` builds
- Embedded `help.txt` and `about.txt` support
- `.ico` app icon
- Compatible with PyInstaller `--onefile --windowed`

---

## 📍 Planned for 1.3.x

- Add Axis, SBI format support
- Export logs or reports to PDF
- SQLite history or backup option
- Auto-updater or splash screen

---

> Created by Senthil | Maintained by ChatGPT  
> Last updated: 2025-06-26