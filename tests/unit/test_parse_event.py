from app import parse_event

def test_parse_ok_event():
    event = {
        "event": "START_PROCESS",
        "timestamp": "2026-04-09T08:15:23",
        "level": "INFO",
        "fields": {
          "JobID": "78421",
          "User": "ASCCRLFILOTH",
          "Host": "server01"
        }
      }

    log = parse_event(event)

    assert log == "2026-04-09 08:15:23 INFO START_PROCESS JobID=78421 User=ASCCRLFILOTH Host=server01"

def test_parse_ok_event_with_spaces_in_field_values():
    event = {
      "event": "RECORD_WARNING",
      "timestamp": "2026-04-09T08:15:26",
      "level": "WARN",
      "fields": {
        "Line": "102",
        "Issue": "Missing optional field"
      }
    }
    log = parse_event(event)

    assert log == "2026-04-09 08:15:26 WARN RECORD_WARNING Line=102 Issue=Missing optional field"

def test_parse_event_empty():
    event = {
      "event": None,
      "timestamp": None,
      "level": None,
      "fields": {}
    }
    log = parse_event(event)

    assert log == "??????? ??????? ???????"

def test_parse_event_empty_fields():
    event = {
      "event": "VALIDATION_END",
      "timestamp": "2026-04-09T08:15:27",
      "level": "INFO",
      "fields": {}
    }
    log = parse_event(event)

    assert log == "2026-04-09 08:15:27 INFO VALIDATION_END"

def test_parse_event_missing_time():
    event = {
      "event": "VALIDATION_END",
      "timestamp": "2026-04-09",
      "level": "INFO",
      "fields": {}
    }
    log = parse_event(event)

    assert log == "2026-04-09 00:00:00 INFO VALIDATION_END"