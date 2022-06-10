

import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_migrate import Migrate
from . import views
import sys
sys.path.append('../shared/collections')
from entities import Role, ExtendedRegisterForm
from user import User


app = Flask(__name__)
app.config.from_file('../shared/config/config.json', load=json.load)

db = SQLAlchemy(app)

migrate = Migrate()
migrate.init_app(app, db)

app.register_blueprint(views, url_prefix='/')

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
Security(app, user_datastore,
         register_form=ExtendedRegisterForm)


if __name__ == '__main__':
    app.run(debug=True)
