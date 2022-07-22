from multiprocessing.dummy import freeze_support
from flask_socketio import SocketIO
from flask_mail import Mail
from torch import create_app


app = create_app()
mail = Mail(app)
