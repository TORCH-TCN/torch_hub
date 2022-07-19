from click import DateTime
from flask_security import UserMixin
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from torch.institutions.institutions import Institution
#from torch.config.database.TorchDatabase import Entity, db
from torch import db


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
    institution_code = db.Column(db.String(10))
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role',secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

def get_user(id) -> User:
    return User.query.filter_by(id=id).first()


def save_user(id, first_name, last_name, institution_id):
    user = get_user(id)
    user.first_name = first_name
    user.last_name = last_name

    if institution_id is not None:
        institution = Institution.query.filter_by(id=institution_id).first()
        user.institution_id = institution.id
        user.institution_code = institution.code
    elif user.institution_code is not None:
        institution = Institution.query.filter_by(code=user.institution_code).first()
        user.institution_id = institution.id

    db.commit()


def toggle_user_active(id):
    user = User.query.get(id)
    user.active = 0 if user.active == 1 else 1

    db.session.commit()
