
import os
import subprocess
import time
import json

from main import process_log_file

def test_all_layers():
    gen = subprocess.Popen(["python3", "log_generator.py"])
    time.sleep(5)

    analyzer = subprocess.Popen(["python3", "main.py"])


    gen.terminate()
    analyzer.terminate()

    with open("metrics.json") as f:
        metrics = json.load(f)

    assert metrics["total_lines"] > 0
    assert metrics["parse_success"] > 0
    assert (
        metrics["parse_success"]
        + metrics["invalid_log_format"]
        + metrics["parse_fail_timestamp"]
        + metrics["parse_fail_key_value"]
        == metrics["total_lines"]
    )

def test_concurrent_read_write():
    gen = subprocess.Popen(["python", "log_generator.py"])
    analyzer = subprocess.Popen(["python", "main.py"])

    time.sleep(10)

    gen.terminate()
    analyzer.terminate()

    assert os.path.exists("event_logs.log")
    assert os.path.exists("metrics.json")

def test_alert_generation():
    process_log_file("event_logs.log")

    assert os.path.exists("alerts_detected.txt")
    assert os.path.exists("warnings_detected.txt")

    with open("alerts_detected.txt") as f:
      lines = f.readlines()
      assert all("LOAD_FAILURE" in line or "AUTH_FAILURE" in line for line in lines)