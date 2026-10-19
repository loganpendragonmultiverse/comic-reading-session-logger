# Changelog

## 1.1.1 - 2026-10-19

- Use unique temporary files for log replacement, preserving unrelated temporary files and refusing symlink log destinations.
- Reject boolean counts, noncanonical dates and non-text notes; keep authored Markdown fields literal and handle closed pipes cleanly.

## 1.1.0 - 2026-10-16

- Added report-only inclusive date and exact series filters, plus per-series time and interruption totals.
- Added synthetic regression tests for boundaries, aggregation and unchanged inputs.


## 1.0.0 - 2026-07-26

- Added validated, atomically updated comic reading logs.
- Added deterministic Markdown and JSON session summaries.
- Added elapsed-time, interruption, issue-range, and note tracking.
