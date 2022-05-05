from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    users = db.relationship('User')
    
    

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    