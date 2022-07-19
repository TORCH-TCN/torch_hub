import json
from multiprocessing.dummy import freeze_support
from os import path
import socket
import threading
import time
from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
from flask_socketio import SocketIO
from flask_mail import Mail
from prefect.agent.local import LocalAgent
from prefect.cli.server import start as start_prefect_server

from torch.users.user import User
from torch.users.role import Role
from torch.users.users import ExtendedRegisterForm

# from torch.config.TorchConfig import TorchConfig


# config = TorchConfig.from_json("config.json")
app = Flask(__name__)
db = SQLAlchemy()
#migrate = Migrate(app, db)
#mail = Mail(app)
login_manager = LoginManager()
socketio = SocketIO(app)
DB_NAME = 'torch-hub.db'

#class User(UserMixin, db.Model):



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

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

def create_app():
    
    app.config.from_file("config.json", load=json.load)
    #db.init_app(app)

    # from torch.flows.flows import views
    # from torch.users.users import users
    # from torch.institutions.institutions import institutions
    # from torch.collections.collections import collections

    # create_database(app)

    # user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    # security = Security(app, user_datastore, register_form=ExtendedRegisterForm)



if __name__ == "__main__":
    freeze_support()
    
    # migrate.init_app(app, db)

    server = threading.Thread(target=lambda: start_prefect_server())
    server.daemon = True
    server.start()
    wait_for_prefect_server()

    #login_manager.init_app(app)
    create_app()

    ui = threading.Thread(target=lambda: socketio.run(app))
    ui.daemon = True
    ui.start()

    LocalAgent().start()
