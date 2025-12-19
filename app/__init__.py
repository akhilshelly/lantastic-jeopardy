import logging
from flask import Flask
from flask_socketio import SocketIO

from config import Config

logger = logging.getLogger(__name__)
socketio = SocketIO(cors_allowed_origins="*")


def create_app():
    global socketio
    logger.info("Creating Flask application...")
    app = Flask(__name__)

    logger.debug(f"Loading config: HOST={Config.HOST}, PORT={Config.PORT}, DEBUG={Config.DEBUG}")
    app.config.from_object(Config)

    # Initialize SocketIO with the app and proper async mode
    logger.info("Initializing SocketIO with CORS allowed for all origins")
    socketio.init_app(app)

    try:
        from app import routes, events
        app.register_blueprint(routes.bp)
        logger.info("Blueprint and event handlers registered successfully")
    except Exception as e:
        logger.error(f"Failed to register blueprint or import events: {e}", exc_info=True)
        raise

    logger.info("Flask application created successfully")
    return app
