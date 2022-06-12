

import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_migrate import Migrate
import sys
sys.path.append('../shared/config')
from database.models import User, Role, ExtendedRegisterForm



db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_file('../../shared/config/config.json', load=json.load)

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import views
    
    app.register_blueprint(views, url_prefix='/')

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore,
            register_form=ExtendedRegisterForm)


    return app