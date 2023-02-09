import glob
import os
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
from torch_web import Base, db
from sqlalchemy.sql import func, select
from sqlalchemy.orm import relationship
from flask import current_app
from PIL import Image


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
    has_dng = Column(Integer, default=0)
    images = relationship("SpecimenImage")

    def to_json(self):
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
        img = db.session.scalars(select(SpecimenImage)
                                 .filter(SpecimenImage.specimen_id == self.id)
                                 .filter(SpecimenImage.size == 'THUMB')).first()
        return img.external_url if img is not None else None


def get_specimens_by_batch_id(batch_id):
    root = "webapp/static/uploads/{}".format(batch_id)
    files = []

    if not os.path.isdir(root):
        return files

    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)


def is_portrait(image_path=None):
    try:
        with Image.open(image_path) as im:
            width, height = im.size
            if height > width:
                return True
            else:
                return False
    except Exception as e:
        print('Error: ', e)
        raise



class SpecimenImage(Base):
    __tablename__ = "specimenimage"
    id = Column(Integer, primary_key=True)
    size = Column(String(20))
    height = Column(Integer)
    width = Column(Integer)
    url = Column(Text)
    create_date = Column(DateTime(timezone=True), default=func.now())
    specimen_id = Column(Integer, ForeignKey("specimen.id"))
    external_url = Column(Text)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def web_url(self):
        base_path = Path(current_app.config['BASE_DIR'])
        web_path = Path(self.url).relative_to(base_path)
        web_path = "/" + "/".join(web_path.parts)
        return web_path
