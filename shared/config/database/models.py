# import sys
# sys.path.append('../shared/config/database')
from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime,
    ForeignKey,
    Text,
    Table,
    Boolean
)
from database.TorchDatabase import Entity, db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from flask_security import RegisterForm, RoleMixin, UserMixin
from wtforms import StringField




class Institution(Entity):
    __tablename__ = 'institution'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    created_date = Column(DateTime(timezone=True), default=func.now())
    users = relationship("User")
    collections = relationship("Collection")


class Role(Entity, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class Collection(Entity):
    __tablename__ = 'collection'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    catalog_number_regex = Column(String(150))
    web_base = Column(String(150))
    url_base = Column(String(150))
    institution_id = Column(Integer, ForeignKey("institution.id"))
    # workflows = relationship("Workflow")


class Image(Entity):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    uploaded_date = Column(DateTime(timezone=True), default=func.now())
    med_image_url = Column(Text)  # possible change this to string?
    thumbnail_url = Column(Text)
    barcode = Column(String(20))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    catalog_number = Column(String(150))


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    institution_code = StringField("Institution Code")



roles_users = Table(
    "roles_users",
    Entity.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("role_id", Integer, ForeignKey("role.id")),
)


class User(Entity, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True)
    password = Column(String(150))
    first_name = Column(String(150))
    last_name = Column(String(150))
    active = Column(Boolean)
    confirmed_at = Column(DateTime)
    institution_code = Column(String(10))
    institution_id = Column(Integer, ForeignKey("institution.id"))
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    roles = relationship(
        "Role", secondary=roles_users, backref=backref("users", lazy="dynamic")
    )


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
