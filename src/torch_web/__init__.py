import os

from dotenv import load_dotenv
from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from torch_hub.users import user, role

metadata = MetaData()
Base = declarative_base(metadata=metadata)
db = SQLAlchemy(metadata=metadata)
user_datastore = SQLAlchemyUserDatastore(db, user.User, role.Role)

Base.query = db.session.query_property()
# migrate = Migrate()
socketio = SocketIO()


def create_app():
    load_dotenv()

    app = Flask(__name__, template_folder=".")

    app.config.from_prefixed_env()
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("TORCH_HUB_DATABASE_URI")

    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config["BASE_DIR"] = basedir

    db.init_app(app)
    socketio.init_app(app)

    from torch_web.users.users import users_bp, ExtendedRegisterForm
    from torch_web.users.roles import roles_bp
    from torch_web.institutions.institutions import institutions_bp
    from torch_web.collections.collections import collections_bp, home_bp
    from torch_web.reports.reports import reports_bp
    from torch_web.notifications.notifications import notifications_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(institutions_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)

    Security(app, user_datastore, register_form=ExtendedRegisterForm)
    return app
