import json
from pathlib import Path

from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime,
    ForeignKey,
    Text,
)
from torch import Base, db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from flask import current_app

class Specimen(Base):
    __tablename__ = "specimen"
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    create_date = Column(DateTime(timezone=True), default=func.now())
    upload_path = Column(Text)
    barcode = Column(String(20))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    catalog_number = Column(String(150))
    flow_run_id = Column(String(150))
    flow_run_state = Column(String(150))
    failed_task = Column(String(150))
    deleted = Column(Integer, default=0)
    images = relationship("SpecimenImage")


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def web_url(self):
        base_path = Path(current_app.config['BASE_DIR'])
        web_path = Path(self.upload_path).relative_to(base_path)
        web_path = "/" + "/".join(web_path.parts)
        return web_path
    
    def card_image(self):
        img = db.session.query(SpecimenImage).filter(SpecimenImage.specimen_id == self.id).filter(SpecimenImage.size == 'THUMB').first()
        return img.web_url() if img != None else self.web_url()


class SpecimenImage(Base):
    __tablename__ = "specimenimage"
    id = Column(Integer, primary_key=True)
    size = Column(String(20))
    height = Column(Integer)
    width = Column(Integer)
    url = Column(Text)
    create_date = Column(DateTime(timezone=True), default=func.now())
    specimen_id = Column(Integer, ForeignKey("specimen.id"))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def web_url(self):
        base_path = Path(current_app.config['BASE_DIR']) 
        web_path = Path(self.url).relative_to(base_path)
        web_path = "/" + "/".join(web_path.parts)
        return web_path
