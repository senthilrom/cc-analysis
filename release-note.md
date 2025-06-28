
---

### 📝 `release_notes.md`

```markdown
# 📦 Credit Card Statement Consolidator - Release Notes

---

## v1.1 - [June 2025]

✅ Major Enhancements:
- Auto-categorization based on `categories.json`
- Bank detection using regex + fallback
- Unified Excel + DB storage
- Secrets and logs now stored outside `.exe` (AppData / Documents)
- GUI: Help/About/Category editor menu added
- Logging of skipped or invalid PDFs (`error.log`)
- Unit tests split: `test_extractors.py`, `test_utils.py`, etc.

🪛 Internal:
- Project refactored to modular files
- `.spec` updated to exclude sensitive files
- `.gitignore` updated

---

## v1.0 - [April 2025]

- Extract HDFC and IndusInd PDF statements
- GUI for selecting PDFs and passwords
- Bank-wise Excel file generation
- SQLite DB with deduplication