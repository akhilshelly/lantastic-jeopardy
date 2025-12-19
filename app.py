import logging
import socket

from app import create_app, socketio
from config import Config

from app.logging_config import setup_logging

logger = logging.getLogger(__name__)

def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        logger.error("Could not determine local IP address, defaulting to localhost.")
        return "localhost"


app = create_app()

if __name__ == '__main__':
    setup_logging()
    local_ip = get_local_ip()
    logger.info(f"\n{'=' * 60}")
    logger.info(f"🎮 JEOPARDY GAME SERVER")
    logger.info(f"{'=' * 60}")
    logger.info(f"🌐 Host Interface: {Config.HOST}")
    logger.info(f"🔌 Port: {Config.PORT}")
    logger.info(f"📱 Trebek URL: http://{local_ip}:{Config.PORT}/")
    logger.info(f"📱 Players Join: http://{local_ip}:{Config.PORT}/join")
    logger.info(f"📺 Display: http://{local_ip}:{Config.PORT}/display")
    logger.info(f"{'=' * 60}\n")

    socketio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, allow_unsafe_werkzeug=True)
