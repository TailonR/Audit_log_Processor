
import time
import json

from main import process_log_file, write_metrics


def test_metrics_file_valid_json():
    logs = process_log_file("event_logs.log")
    write_metrics(logs["diagnostics"])

    with open("metrics.json") as f:
        data = json.load(f)

    assert isinstance(data["total_lines"], int)
    assert isinstance(data["parse_success"], int)
    assert isinstance(data["invalid_log_format"], int)
    assert isinstance(data["parse_fail_timestamp"], int)
    assert isinstance(data["parse_fail_key_value"], int)

def test_status_alive(client):
    with open("generator_state.json", "w") as f:
        json.dump({"running": True, "timestamp": time.time()}, f)

    response = client.get("/log-status")
    data = response.get_json()

    assert data["running"] is True
    assert data["alive"] is True

def test_status_dead_state(client):
    with open("generator_state.json", "w") as f:
        json.dump({"running": True, "timestamp": time.time() - 100}, f)

    response = client.get("/log-status")
    data = response.get_json()

    assert data["alive"] is False

def test_analyze_endpoint(client):
    fake_metrics = {"total_lines": 10, "parse_success": 9}
    with open("metrics.json", "w") as f:
        json.dump(fake_metrics, f)

    response = client.get("/log-metrics")
    assert response.status_code == 200
    assert response.get_json()["total_lines"] == 10