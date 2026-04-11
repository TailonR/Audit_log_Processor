from main import validate_line, ParseError

def test_validate_line_ok():
    line = "2026-04-09 08:15:30 INFO LOAD_START jobId=123 user=admin"
    result = validate_line(line)
    assert result["result"] == ParseError.OK

def test_validate_line_corrupted():
    line = "???? bad data"
    result = validate_line(line)
    assert result["result"] == ParseError.CORRUPTED_LINE

def test_validate_line_missing_fields():
    line = "2026-04-09 INFO"
    result = validate_line(line)
    assert result["result"] == ParseError.MISSING_FIELDS

def test_validate_line_bad_timestamp():
    line = "2026-99-99 25:61:61 INFO LOAD_START key=value"
    result = validate_line(line)
    assert result["result"] == ParseError.MALFORMED_TIMESTAMP

def test_validate_line_invalid_kv():
    line = "2026-04-09 08:15:30 INFO LOAD_START keyvalue"
    result = validate_line(line)
    assert result["result"] == ParseError.INVALID_KEY_VALUE

def test_long_line():
    line = "2026-04-09 08:15:30 INFO LOAD_START " + "a=1 " * 1000
    result = validate_line(line)
    assert result["result"] == ParseError.OK

def test_special_characters():
    line = '2026-04-09 08:15:30 INFO LOAD_START msg=hello@world!'
    result = validate_line(line)
    assert result["result"] == ParseError.OK