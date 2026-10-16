import copy
import json

import pytest

from comic_session_logger.cli import main
from comic_session_logger.core import filter_log, summary


def data():
    return {
        "version": 1,
        "sessions": [
            {
                "id": str(i),
                "date": day,
                "series": series,
                "issue_start": "1",
                "issue_end": "1",
                "minutes": minutes,
                "interruptions": stops,
            }
            for i, (day, series, minutes, stops) in enumerate(
                [
                    ("2026-01-01", "A", 10, 1),
                    ("2026-01-02", "A", 20, 2),
                    ("2026-01-02", "A", 30, 0),
                    ("2026-01-03", "B", 40, 3),
                ]
            )
        ],
    }


def test_inclusive_distinct_sessions_aggregation_and_no_mutation():
    log = data()
    before = copy.deepcopy(log)
    selected = filter_log(log, start_date="2026-01-02", end_date="2026-01-03", series="A")
    assert [s["id"] for s in selected["sessions"]] == ["1", "2"]
    totals = summary(selected)
    assert totals["minutes"] == 50 and totals["interruptions"] == 2
    assert totals["per_series"] == {"A": {"sessions": 2, "minutes": 50, "interruptions": 2}}
    assert summary(log)["per_series"]["B"]["minutes"] == 40
    assert log == before
    assert len(filter_log(log, end_date="2026-01-01")["sessions"]) == 1
    assert len(filter_log(log, start_date="2026-01-03")["sessions"]) == 1
    assert summary(filter_log(log, series="a"))["sessions"] == 0


@pytest.mark.parametrize(
    "options",
    [
        {"start_date": "2026-02-01", "end_date": "2026-01-01"},
        {"start_date": "no"},
        {"end_date": "20260101"},
    ],
)
def test_invalid_boundaries(options):
    with pytest.raises(ValueError):
        filter_log(data(), **options)


def test_cli_preserves_exact_log_bytes(tmp_path, capsys):
    path = tmp_path / "log.json"
    original = (json.dumps(data(), separators=(",", ":")) + "  \n").encode()
    path.write_bytes(original)
    assert (
        main(
            [
                "report",
                str(path),
                "--series",
                "A",
                "--start-date",
                "2026-01-02",
                "--end-date",
                "2026-01-02",
                "--format",
                "json",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["summary"]["sessions"] == 2
    assert main(["report", str(path), "--series", "B"]) == 0
    assert "40 minutes, 3 interruptions" in capsys.readouterr().out
    assert (
        main(["report", str(path), "--start-date", "2027-01-01", "--end-date", "2026-01-01"]) == 2
    )
    assert path.read_bytes() == original
