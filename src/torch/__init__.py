import json
from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_security import RegisterForm, Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user, roles_accepted, roles_required
from flask_mail import Mail
from wtforms import StringField
from flask_migrate import Migrate
# from torch.users.role import Role
# from torch.users.user import User

# from torch.users.users import ExtendedRegisterForm

# db = SQLAlchemy()
# migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder=".")

    app.config.from_file("config.json", load=json.load)
    
    #db.init_app(app)

    # mail = Mail(app)

    from torch.test.test import views 

    # from flows.flows import views
    # from users.users import users
    # from institutions.institutions import institutions
    # from collections.collections import collections

    app.register_blueprint(views,url_prefix='/')

    # create_database(app)

    #user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    #security = Security(app, user_datastore, register_form=ExtendedRegisterForm)

    return app
