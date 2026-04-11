from main import process_log_file

def test_alert_detection():
    with open("test.log", "w") as file:
        file.write("2026-04-09 08:15:30 ERROR LOAD_FAILURE user=admin\n")

    process_log_file("test.log")

    with open("alerts_detected.txt") as f:
        content = f.read()
        assert "LOAD_FAILURE" in content
