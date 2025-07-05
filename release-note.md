**Release Date:** 2025-07-06

## Highlights
- 🎯 Unified sheet output: All transactions stored in `All_Transactions`
- 🧹 Deduplication using Date + Description + Amount fields
- 🧪 Fully tested with unit tests for:
  - Clean appends
  - Duplicate detection
  - Malformed and invalid rows
- 💪 Robust error handling during append and parse

## Migration Notes
- Remove older multi-sheet Excel format
- Back up older data before using v3.0