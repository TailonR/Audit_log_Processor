from log_analyzer import parse_line, ParseException, ParseError
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

def test_parse_line_invalid_timestamp_1():
    line = "2026-04-09 fwefwfw INFO LOAD_START user=admin"
    with pytest.raises(ParseException) as exc_info:
        parse_line(line)

    assert exc_info.value.error_type == ParseError.MALFORMED_TIMESTAMP

def test_parse_line_invalid_timestamp_2():
    line = "2026-04-09 INFO LOAD_START user=admin"
    with pytest.raises(ParseException) as exc_info:
        parse_line(line)

    assert exc_info.value.error_type == ParseError.INVALID_LOG_FORMAT

def test_parse_line_missing_log_level():
    line = "2026-04-09 08:15:30 LOAD_START user=admin"
    with pytest.raises(ParseException) as exc_info:
        parse_line(line)

    assert exc_info.value.error_type == ParseError.INVALID_LOG_FORMAT

def test_parse_line_bad_log_level():
    line = "2026-04-09 08:15:30 BAD LOAD_START user=admin"
    with pytest.raises(ParseException) as exc_info:
        parse_line(line)

    assert exc_info.value.error_type == ParseError.INVALID_LOG_FORMAT

def test_parse_line_missing_event():
    line = "2026-04-09 08:15:30 INFO user=admin"
    with pytest.raises(ParseException) as exc_info:
        parse_line(line)

    assert exc_info.value.error_type == ParseError.INVALID_LOG_FORMAT

def test_parse_line_missing_message():
    line = "2026-04-09 08:15:30 INFO"
    with pytest.raises(ParseException) as exc_info:
        parse_line(line)

    assert exc_info.value.error_type == ParseError.INVALID_LOG_FORMAT

def test_parse_line_invalid():
    with pytest.raises(ParseException) as exc_info:
        parse_line("invalid line")

    assert exc_info.value.error_type == ParseError.INVALID_LOG_FORMAT

def test_kv_edge_cases():
    line = "2026-04-09 10:00:00 INFO LOGIN user= role=admin"
    with pytest.raises(ParseException) as exc_info:
        parse_line(line)

    assert exc_info.value.error_type == ParseError.INVALID_KEY_VALUE