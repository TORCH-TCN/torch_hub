import json
import os
from flask import Flask
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_socketio import SocketIO
from dotenv import load_dotenv, find_dotenv

metadata = MetaData()
Base = declarative_base(metadata=metadata)
db = SQLAlchemy(metadata=metadata)
Base.query = db.session.query_property()
# migrate = Migrate()
socketio = SocketIO()


def create_app():
    load_dotenv()

    app = Flask(__name__, template_folder=".")

    app.config.from_prefixed_env()

    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config["BASE_DIR"] = basedir

    db.init_app(app)
    socketio.init_app(app)

    from torch.users.users import users_bp, ExtendedRegisterForm
    from torch.users.roles import roles_bp
    from torch.institutions.institutions import institutions_bp
    from torch.collections.collections import collections_bp, home_bp
    from torch.reports.reports import reports_bp
    from torch.notifications.notifications import notifications_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(institutions_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)

    from torch.users.users import User
    from torch.users.role import Role

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore, register_form=ExtendedRegisterForm)

    return app
