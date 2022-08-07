from flask_socketio import SocketIO
from torch import create_app


app = create_app()
socketio = SocketIO(app)
