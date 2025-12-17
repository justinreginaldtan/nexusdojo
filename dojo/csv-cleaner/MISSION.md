# CSV Cleaner (CLI Data Pipeline)

Build a CLI that cleans a CSV file, normalizes fields, drops bad rows, and outputs stats.

## Requirements
- Accept input path and output path via CLI; stream rows to avoid loading everything into memory.
- Validate required columns (configurable list); drop rows missing required values; normalize strings (trim, lowercase certain columns) and numbers (convert, handle blanks).
- Write cleaned rows to the output CSV and emit a JSON summary of counts: total rows, dropped rows (with reasons), and per-column null counts.
- Provide exit code 0 on success, non-zero on fatal errors; print a short summary to stdout.

## Stretch
- Add a `--schema` option to enforce column types with friendly error reporting.
- Support gzip input/output if file ends with `.gz`.
