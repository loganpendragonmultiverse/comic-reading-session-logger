import json
from unittest.mock import patch

import pytest

from comic_session_logger.cli import main
from comic_session_logger.core import (
    empty_log,
    load_log,
    render_markdown,
    save_log,
    validate_session,
)


def session(**extra):
    return {
        "id": "one",
        "date": "2026-10-19",
        "series": "Night Run",
        "issue_start": "1",
        "issue_end": "Annual 1",
        "minutes": 12,
        "interruptions": 0,
        **extra,
    }


@pytest.mark.parametrize(
    "extra",
    [
        {"minutes": True},
        {"interruptions": False},
        {"date": "20261019"},
        {"date": "2026-W43-1"},
        {"notes": []},
    ],
)
def test_invalid_loaded_values(extra, tmp_path):
    path = tmp_path / "log.json"
    path.write_text(json.dumps({"version": 1, "sessions": [session(**extra)]}))
    with pytest.raises((TypeError, ValueError)):
        load_log(path)
    assert main(["report", str(path)]) == 2


def test_boolean_log_version_rejected(tmp_path):
    path = tmp_path / "log.json"
    path.write_text('{"version":true,"sessions":[]}')
    with pytest.raises(ValueError, match="version"):
        load_log(path)


def test_unique_temp_and_replace_failure_preserve_other_files(tmp_path):
    path = tmp_path / "log.json"
    path.write_text('{"version":1,"sessions":[]}')
    old = path.read_bytes()
    unrelated = tmp_path / ".log.json.tmp"
    unrelated.write_bytes(b"keep")
    with (
        patch("comic_session_logger.core.os.replace", side_effect=OSError("synthetic failure")),
        pytest.raises(OSError),
    ):
        save_log(path, empty_log())
    assert path.read_bytes() == old
    assert unrelated.read_bytes() == b"keep"
    assert sorted(p.name for p in tmp_path.iterdir()) == [".log.json.tmp", "log.json"]
    save_log(path, empty_log())
    assert unrelated.read_bytes() == b"keep"


def test_log_symlink_refused(tmp_path):
    path = tmp_path / "log.json"
    target = tmp_path / "target"
    try:
        path.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    with pytest.raises(ValueError, match="symlink"):
        save_log(path, empty_log())
    assert not target.exists()


def test_literal_markdown_notes_and_series():
    text = render_markdown(
        {"version": 1, "sessions": [session(series="<script>*x*|name", notes="# heading\ntext")]}
    )
    assert "<script>" not in text
    assert "&lt;script&gt;" in text
    assert "&#10;" in text
    assert "\\*" in text
    validate_session(session(notes=""))
