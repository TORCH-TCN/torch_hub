from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime,
    ForeignKey,
    Text,
)
from config.database.TorchDatabase import Entity
from sqlalchemy.sql import func
from flask_security import RegisterForm
from wtforms import StringField


class Image(Entity):
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
