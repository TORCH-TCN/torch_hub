# Initialize Flask database

from flask_mail import Mail
#from torch_web import create_app, db, #socketio
from torch_web import create_app, db
from torch_web.collections.collections import Collection
from torch_web.institutions.institutions import Institution
from torch_web.users.role import Role
from torch_web.users.user import User

app = create_app()
mail = Mail(app)

db.create_all()