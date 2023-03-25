import os

from dotenv import load_dotenv
from apiflask import APIFlask
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from flask_cors import CORS

metadata = MetaData()
Base = declarative_base(metadata=metadata)
db = SQLAlchemy(metadata=metadata)

def create_app():
    load_dotenv()

    app = APIFlask(__name__, template_folder=".", title="TorchHub API", version="1.0")
    app.config.from_prefixed_env()
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("TORCH_HUB_DATABASE_URI")
    CORS(app)

    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config["BASE_DIR"] = basedir

    db.init_app(app)

    from torch_web.users.users_api import users_bp, auth_bp, ExtendedRegisterForm
    from torch_web.users.roles_api import roles_bp
    from torch_web.institutions.institutions_api import institutions_bp
    from torch_web.collections.collections_api import collections_bp, home_bp, specimens_bp
    from torch_web.reports.reports_api import reports_bp
    from torch_web.notifications.notifications_api import notifications_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(institutions_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(specimens_bp)
    app.register_blueprint(auth_bp)

    from torch_web.users.user import User
    from torch_web.users.role import Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    Security(app, user_datastore, register_form=ExtendedRegisterForm)
    return app
