from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_migrate import Migrate
from collections import User, Role, ExtendedRegisterForm
from . import views


app = Flask(__name__)
app.config.from_file('config/config.json')

db = SQLAlchemy(app)

migrate = Migrate()
migrate.init_app(app, db)

app.register_blueprint(views, url_prefix='/')

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
Security(app, user_datastore,
         register_form=ExtendedRegisterForm)


if __name__ == '__main__':
    app.run(debug=True)
