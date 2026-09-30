from waitress import serve
from app import app
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("=" * 60)
    print("  EASY MED Production Server (Waitress WSGI)")
    print("=" * 60)
    print(f"  Local Access:      http://127.0.0.1:5000")
    print(f"  Network Access:    http://{local_ip}:5000")
    print("=" * 60)
    print("Press Ctrl+C to stop the server.\n")
    serve(app, host="0.0.0.0", port=5000, threads=6)
