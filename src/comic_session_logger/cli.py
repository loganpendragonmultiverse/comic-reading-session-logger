from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import add_session, filter_log, load_log, render_markdown, save_log, summary


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Record and report comic reading sessions.")
    sub = result.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add")
    add.add_argument("log", type=Path)
    add.add_argument("--id", required=True)
    add.add_argument("--date", required=True)
    add.add_argument("--series", required=True)
    add.add_argument("--from-issue", required=True)
    add.add_argument("--through-issue", required=True)
    add.add_argument("--minutes", required=True, type=int)
    add.add_argument("--interruptions", type=int, default=0)
    add.add_argument("--notes")
    report = sub.add_parser("report")
    report.add_argument("log", type=Path)
    report.add_argument("--start-date")
    report.add_argument("--end-date")
    report.add_argument("--series", help="Exact, case-sensitive series name")
    report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        data = load_log(args.log)
        if args.command == "add":
            item = {
                "id": args.id,
                "date": args.date,
                "series": args.series,
                "issue_start": args.from_issue,
                "issue_end": args.through_issue,
                "minutes": args.minutes,
                "interruptions": args.interruptions,
            }
            if args.notes:
                item["notes"] = args.notes
            add_session(data, item)
            save_log(args.log, data)
            print(f"Recorded {args.id}")
        else:
            data = filter_log(
                data, start_date=args.start_date, end_date=args.end_date, series=args.series
            )
        if args.command == "report" and args.format == "json":
            print(json.dumps({"summary": summary(data), "sessions": data["sessions"]}, indent=2))
        elif args.command == "report":
            sys.stdout.write(render_markdown(data))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
