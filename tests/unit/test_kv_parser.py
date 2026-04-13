from log_analyzer import parse_kv
import pytest
from log_analyzer import ParseException, ParseError
def test_parse_kv_basic():
    s = "user=admin jobId=123"
    result = parse_kv(s)
    assert result == {"user": "admin", "jobId": "123"}

def test_parse_kv_with_spaces():
    s = 'msg=file not found code=404'
    result = parse_kv(s)
    assert result["msg"] == "file not found"

def test_parse_kv_empty_key():
    s = "=value"
    with pytest.raises(ParseException) as exc_info:
        result = parse_kv(s)
        
    assert exc_info.value.error_type == ParseError.INVALID_KEY_VALUE

def test_parse_kv_empty_value():
    s = "key="
    with pytest.raises(ParseException) as exc_info:
        result = parse_kv(s)

    assert exc_info.value.error_type == ParseError.INVALID_KEY_VALUE

def test_parse_kv_duplicate_keys():
    s = "key=1 key=2"
    result = parse_kv(s)
    assert result["key"] == "2"