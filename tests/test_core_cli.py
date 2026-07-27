import json

import pytest

from comic_session_logger.cli import main
from comic_session_logger.core import (
    add_session,
    empty_log,
    load_log,
    render_markdown,
    summary,
    validate_session,
)


def session(item_id="s1"):
    return {
        "id": item_id,
        "date": "2026-07-26",
        "series": "Night Run",
        "issue_start": "1",
        "issue_end": "3",
        "minutes": 42,
        "interruptions": 1,
    }


def test_add_summary_and_render():
    data = empty_log()
    add_session(data, session())
    assert summary(data) == {
        "sessions": 1,
        "minutes": 42,
        "interruptions": 1,
        "series": {"Night Run": 1},
    }
    assert "Night Run 1–3" in render_markdown(data)
    with pytest.raises(ValueError, match="duplicate"):
        add_session(data, session())


def test_validation(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"version": 2}', encoding="utf-8")
    with pytest.raises(ValueError, match="version 1"):
        load_log(path)
    invalid = session("bad")
    invalid["minutes"] = 0
    with pytest.raises(ValueError, match="positive"):
        add_session(empty_log(), invalid)
    with pytest.raises(TypeError, match="object"):
        validate_session(None)
    with pytest.raises(ValueError, match="requires"):
        validate_session({})
    invalid = session("date")
    invalid["date"] = "tomorrow"
    with pytest.raises(ValueError, match="YYYY"):
        validate_session(invalid)
    invalid = session("interruptions")
    invalid["interruptions"] = -1
    with pytest.raises(ValueError, match="non-negative"):
        validate_session(invalid)
    path.write_text('{"version": 1, "sessions": {}}', encoding="utf-8")
    with pytest.raises(TypeError, match="list"):
        load_log(path)


def test_cli_add_and_report(tmp_path, capsys):
    path = tmp_path / "sessions.json"
    args = [
        "add",
        str(path),
        "--id",
        "s1",
        "--date",
        "2026-07-26",
        "--series",
        "Night Run",
        "--from-issue",
        "1",
        "--through-issue",
        "2",
        "--minutes",
        "25",
    ]
    assert main(args) == 0
    assert json.loads(path.read_text(encoding="utf-8"))["sessions"][0]["minutes"] == 25
    assert main(["report", str(path), "--format", "json"]) == 0
    assert '"sessions": 1' in capsys.readouterr().out
    assert main(["report", str(path)]) == 0
    assert "Night Run" in capsys.readouterr().out
    assert main(args + ["--notes", "Good stopping point"]) == 2
