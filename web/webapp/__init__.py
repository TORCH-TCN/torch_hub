from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_security import RegisterForm, Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user, roles_accepted, roles_required
from flask_mail import Mail
from wtforms import StringField
#from flask_migrate import Migrate

db = SQLAlchemy()
#migrate = Migrate()
DB_NAME = 'torch-hub.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'TORCH1WEBAPP'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_PASSWORD_SALT'] = 'torchsalt'
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = False #set this to true, uncomnent mail_config and set configs in file in case we need
    app.config['SECURITY_RECOVERABLE'] = True
    app.config['SECURITY_CHANGEABLE'] = True
    #app.config.from_pyfile('mail_config.cfg')

    db.init_app(app)
    #migrate.init_app(app,db)
    #mail = Mail(app)

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    from .models import User, Role, Institution

    create_database(app)

    class ExtendedRegisterForm(RegisterForm):
        first_name = StringField('First Name')
        last_name = StringField('Last Name')

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore, register_form=ExtendedRegisterForm)
        
    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')