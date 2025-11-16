# run.py
from server import server

if __name__ == "__main__":
    # Launch the browser-based server (classic Mesa ModularServer)
    server.port = 8521  # default
    print("Starting Mesa ModularServer on http://127.0.0.1:8521")
    server.launch()
