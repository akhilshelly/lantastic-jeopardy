import socket

from app import create_app, socketio
from config import Config


def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


app = create_app()

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"\n{'=' * 60}")
    print(f"🎮 JEOPARDY GAME SERVER")
    print(f"{'=' * 60}")
    print(f"🌐 Host Interface: {Config.HOST}")
    print(f"🔌 Port: {Config.PORT}")
    print(f"📱 Trebek URL: http://{local_ip}:{Config.PORT}/")
    print(f"📱 Players Join: http://{local_ip}:{Config.PORT}/join")
    print(f"{'=' * 60}\n")

    socketio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, allow_unsafe_werkzeug=True)
