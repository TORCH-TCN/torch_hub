import json
from multiprocessing.dummy import freeze_support
import socket
import threading
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail
from prefect.agent.local import LocalAgent
from prefect.cli.server import start as start_prefect_server

# from torch.config.TorchConfig import TorchConfig


# config = TorchConfig.from_json("config.json")
app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
login_manager = LoginManager()
socketio = SocketIO(app)


def wait_for_prefect_server():
    for i in range(120):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(("127.0.0.1", int(4200)))
            s.shutdown(socket.SHUT_RDWR)
            print("Prefect Server is UP")
        except OSError:
            time.sleep(1)
            print("Prefect Server is not up yet")
        finally:
            s.close()


if __name__ == "__main__":
    freeze_support()

    app.config.from_file("config.json", load=json.load)
    # migrate.init_app(app, db)

    server = threading.Thread(target=lambda: start_prefect_server())
    server.daemon = True
    server.start()
    wait_for_prefect_server()

    login_manager.init_app(app)
    ui = threading.Thread(target=lambda: socketio.run(app))
    ui.daemon = True
    ui.start()

    LocalAgent().start()
