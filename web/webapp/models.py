from . import db
from sqlalchemy.sql import func
from flask_security import RoleMixin, UserMixin

class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    code = db.Column(db.String(10), unique=True)
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    users = db.relationship('User')
    collections = db.relationship('Collection')
    
roles_users = db.Table('roles_users',
    db.Column('user_id',db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id',db.Integer, db.ForeignKey('role.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role',secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    code = db.Column(db.String(10), unique=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))

