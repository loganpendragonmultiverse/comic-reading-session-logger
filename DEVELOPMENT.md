# Development

Run `python -m pip install -e ".[dev]"`, `ruff format --check .`, `ruff check .`, `pytest`, and `python -m build`.

## 1.1.0: Filtered reports

Report filters `--start-date` and `--end-date` accept inclusive YYYY-MM-DD boundaries; reversed ranges fail. `--series` matches an exact case-sensitive series name. Filters combine, retain distinct session IDs, and never rewrite the log. JSON summaries retain the `series` session counts and add `per_series` with sessions, minutes and interruptions. Markdown includes the same totals. Empty selections produce zero totals.

```bash
comic-session report reading.json --start-date 2026-07-01 --end-date 2026-07-31 --series "Night Run"
```
