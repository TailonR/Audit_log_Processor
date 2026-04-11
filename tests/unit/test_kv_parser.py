from main import parse_kv

def test_parse_kv_basic():
    s = "user=admin jobId=123"
    result = parse_kv(s)
    assert result == {"user": "admin", "jobId": "123"}

def test_parse_kv_with_spaces():
    s = 'msg=file not found code=404'
    result = parse_kv(s)
    assert result["msg"] == "file not found"

def test_parse_kv_empty_value():
    s = "key="
    result = parse_kv(s)
    assert result["key"] == ""

def test_parse_kv_duplicate_keys():
    s = "key=1 key=2"
    result = parse_kv(s)
    assert result["key"] == "2"