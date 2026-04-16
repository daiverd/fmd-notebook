import re
from datetime import date

from fmd import _date_stem, _week_stem, _SHORTCUTS

WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")


def test_date_stem_iso():
    assert _date_stem(date(2026, 4, 15)) == "2026-04-15"


def test_date_stem_single_digit_day():
    assert _date_stem(date(2026, 1, 3)) == "2026-01-03"


def test_week_stem_zero_padded():
    d = date(2026, 1, 30)  # ISO week 5
    assert _week_stem(d) == "2026-W05"


def test_week_stem_format():
    assert WEEK_RE.match(_week_stem(date(2026, 6, 15)))


def test_week_across_year_boundary():
    assert _week_stem(date(2027, 1, 1)) == "2026-W53"


def test_shortcut_names():
    expected = {"yesterday", "today", "tomorrow", "last_week", "this_week", "next_week"}
    assert set(_SHORTCUTS.keys()) == expected


def test_day_shortcuts_consistent():
    t = date.fromisoformat(_SHORTCUTS["today"]())
    y = date.fromisoformat(_SHORTCUTS["yesterday"]())
    tm = date.fromisoformat(_SHORTCUTS["tomorrow"]())
    assert (t - y).days == 1
    assert (tm - t).days == 1


def test_week_shortcuts_format():
    for name in ("last_week", "this_week", "next_week"):
        assert WEEK_RE.match(_SHORTCUTS[name]()), f"{name} format wrong"
