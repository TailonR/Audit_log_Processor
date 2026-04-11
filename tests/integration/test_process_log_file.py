from main import process_log_file

def test_process_log_file():
    with open("test.log", "w") as file:
        file.write("2026-04-09 08:15:30 INFO LOAD_START user=admin\n")
        file.write("bad line\n")

    result = process_log_file("test.log")

    assert result["diagnostics"]["total_lines"] == 2
    assert result["diagnostics"]["parse_success"] == 1

def test_empty_file():
    with open("test.log", "w") as file:
        file.write("")

    result = process_log_file("test.log")
    assert result["diagnostics"]["total_lines"] == 0