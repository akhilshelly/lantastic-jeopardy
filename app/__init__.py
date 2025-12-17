from flask import Flask
from flask_socketio import SocketIO
from config import Config

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    global socketio
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SocketIO with the app and proper async mode
    socketio.init_app(app)

    from app import routes, events
    app.register_blueprint(routes.bp)
    
    return app
