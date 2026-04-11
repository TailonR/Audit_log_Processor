from main import parse_line
import pytest

def test_parse_line_success():
    line = "2026-04-09 08:15:30 INFO LOAD_START user=admin"
    event = parse_line(line)

    assert event.level == "INFO"
    assert event.event == "LOAD_START"
    assert event.fields["user"] == "admin"

def test_parse_line_timestamp():
    line = "2026-04-09 08:15:30 INFO LOAD_START user=admin"
    event = parse_line(line)

    assert event.timestamp.year == 2026
    assert event.timestamp.hour == 8

def test_parse_line_invalid():
    with pytest.raises(Exception):
        parse_line("invalid line")
