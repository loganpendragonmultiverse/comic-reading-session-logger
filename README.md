# Comic Reading Session Logger

[![CI](https://github.com/loganpendragonmultiverse/comic-reading-session-logger/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/comic-reading-session-logger/actions/workflows/ci.yml)

Comic Reading Session Logger records issue ranges, elapsed time, interruptions, and notes in a portable local JSON file. It separates actual reading sessions from collection inventory and produces Markdown or JSON summaries.

## Three-minute start

```bash
python -m pip install .
comic-session add reading.json --id sunday-1 --date 2026-07-26 --series "Night Run" --from-issue 1 --through-issue 4 --minutes 55 --interruptions 1
comic-session report reading.json
```

New records are validated before an atomic file replacement. Session IDs must be unique, dates use ISO `YYYY-MM-DD`, minutes must be positive, and interruptions cannot be negative.

## Boundaries

This is a session log, not a comic reader, collection manager, or automatic activity monitor. It never opens archives, contacts reading services, or modifies comic files. Notes stay local unless the user shares the log.

## Development

Requires Python 3.10 or newer. Run `python -m pip install -e ".[dev]"`, `ruff format --check .`, `ruff check .`, `pytest`, and `python -m build`.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## 1.1.0: Filtered reports

Report filters `--start-date` and `--end-date` accept inclusive YYYY-MM-DD boundaries; reversed ranges fail. `--series` matches an exact case-sensitive series name. Filters combine, retain distinct session IDs, and never rewrite the log. JSON summaries retain the `series` session counts and add `per_series` with sessions, minutes and interruptions. Markdown includes the same totals. Empty selections produce zero totals.

```bash
comic-session report reading.json --start-date 2026-07-01 --end-date 2026-07-31 --series "Night Run"
```

## Log validation and writes

Dates must be canonical YYYY-MM-DD, counts must be integers (booleans are not
counts), and optional notes must be text. Issue labels remain authored strings:
annuals, decimals and ranges are not inferred or reordered. Missing logs start
empty; add creates a log and report shows an empty summary.

Log saves use unique temporary files beside the log and replace the destination
only after writing succeeds. Symlink log destinations are refused. Use one writer
at a time: this is not a concurrent database or a power-loss durability guarantee.
A failed stdout confirmation after add does not undo the recorded session; inspect
the log before retrying. Closed output pipes and invalid inputs return exit status 2.

Install a downloaded release wheel with python -m pip install ./PACKAGE.whl,
replacing the filename with the actual wheel name. Handoff documents are included
under share/comic-reading-session-logger/ in the installation prefix.
