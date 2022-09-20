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
from torch import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Specimen(Base):
    __tablename__ = "specimen"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    create_date = Column(DateTime(timezone=True), default=func.now())
    upload_path = Column(Text)
    barcode = Column(String(20))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    catalog_number = Column(String(150))
    flow_run_id = Column(String(150))
    flow_run_state = Column(String(150))
    images = relationship("SpecimenImage")


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
        base_path = Path("torch") # Hardcoded for now but perhaps needs to be added to a config file or is a property of a Flask app?
        # Get realtive path from base path
        web_path = Path(self.url).relative_to(base_path)
        # Make path in URL format, adding leading slash to make it absolute path
        web_path = "/" + "/".join(web_path.parts)
        return web_path
