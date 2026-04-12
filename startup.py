import subprocess
import requests
import signal
import time
    
def start_logging_server():
    return subprocess.Popen(["python3", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_logging():
    return requests.post(
        "http://127.0.0.1:5000/start",
        json={"interval": 2}
    )

def analyze_logs():
    return requests.post(
        "http://127.0.0.1:5000/analyze"
    )

def health_check():
    # Placeholder for health check logic, e.g., pinging a health endpoint
    response = requests.get(
        "http://127.0.0.1:5000/status"
    )
    if response.status_code != 200:
        return { "running": False }    
    return response.json()

def graceful_shutdown(server):
    print("Shutting down processes gracefully...")
    requests.post(
        "http://127.0.0.1:5000/stop"
    )
  
    server.send_signal(signal.SIGTERM)
    server.wait()

if __name__ == "__main__":
    try:
        logging_server = start_logging_server()
        start_logging()
        while True:
            time.sleep(10)
            response = health_check()
            if not response["running"]:
                print("Logging server is not healthy. Exiting.")
                break
            
            response = analyze_logs() 
            print(response.json())
    except KeyboardInterrupt:
        print("Received interrupt signal. Exiting...")
    finally:
        graceful_shutdown(logging_server)