import sys
sys.path.append('../shared/config/database')
from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime,
    ForeignKey,
    Text
)
from TorchDatabase import Entity
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from flask_security import RegisterForm, RoleMixin
from wtforms import StringField


class Institution(Entity):
    __tablename__ = 'Institution'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    created_date = Column(DateTime(timezone=True), default=func.now())
    users = relationship("User")
    collections = relationship("Collection")


class Role(Entity, RoleMixin):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class Collection(Entity):
    __tablename__ = 'Collection'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    catalog_number_regex = Column(String(150))
    web_base = Column(String(150))
    url_base = Column(String(150))
    institution_id = Column(Integer, ForeignKey("Institution.id"))
    # workflows = relationship("Workflow")


class Image(Entity):
    __tablename__ = 'Image'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    uploaded_date = Column(DateTime(timezone=True), default=func.now())
    med_image_url = Column(Text)  # possible change this to string?
    thumbnail_url = Column(Text)
    barcode = Column(String(20))
    collection_id = Column(Integer, ForeignKey("Collection.id"))
    catalog_number = Column(String(150))


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    institution_code = StringField("Institution Code")
