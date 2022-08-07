from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime,
    ForeignKey,
    Text,
)
from torch import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Specimen(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    create_date = Column(DateTime(timezone=True), default=func.now())
    upload_path = Column(Text)
    barcode = Column(String(20))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    catalog_number = Column(String(150))
    flow_run_id = Column(String(150))
    images = relationship("SpecimenImage")


class SpecimenImage(db.Model):
    id = Column(Integer, primary_key=True)
    size = Column(String(20))
    height = Column(Integer)
    width = Column(Integer)
    url = Column(Text)
    create_date = Column(DateTime(timezone=True), default=func.now())
    specimen_id = Column(Integer, ForeignKey("specimen.id"))
