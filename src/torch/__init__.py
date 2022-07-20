import json
from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_security import RegisterForm, Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user, roles_accepted, roles_required
from flask_mail import Mail
from wtforms import StringField
from flask_migrate import Migrate

db = SQLAlchemy()
# migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder=".")

    app.config.from_file("config.json", load=json.load)
    
    db.init_app(app)

    # mail = Mail(app)

    from torch.users.users import users_bp, ExtendedRegisterForm
    from torch.users.roles import roles_bp
    from torch.institutions.institutions import institutions_bp
    from torch.collections.collections import collections_bp, home_bp
    
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(institutions_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(home_bp)
    
    from torch.users.users import User
    from torch.users.role import Role
    from torch.institutions.institutions import Institution
    from torch.collections.collections import Collection 

    create_database(app)

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore, register_form=ExtendedRegisterForm)

    return app


def create_database(app):
    if not path.exists('torch/torch-hub.db' ):
        db.create_all(app=app)
        print('Created Database!')