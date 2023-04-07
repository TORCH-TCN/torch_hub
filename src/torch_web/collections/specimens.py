import json
from pathlib import Path
from typing import List
import imagehash

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
from sqlalchemy.orm import relationship, Mapped
from flask import current_app

from torch_web.collections.collections import Collection


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
    images: Mapped[List["SpecimenImage"]] = relationship(back_populates="specimen", lazy="selectin")
    tasks: Mapped[List["SpecimenTask"]] = relationship(back_populates="specimen")
    collection: Mapped["Collection"] = relationship(back_populates="specimens")

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
        return img


class SpecimenTask(Base):
    __tablename__ = "specimen_tasks"
    id = Column(Integer, primary_key=True)
    func_name = String()
    name = String()
    description = String(nullable=True)
    specimen: Mapped["Specimen"] = relationship(back_populates="tasks")
    parameters: Mapped[List["SpecimenTaskParameter"]] = relationship(back_populates="task", lazy="selectin")


class SpecimenTaskParameter(Base):
    __tablename__ = "specimen_tasks_parameters"
    id = Column(Integer, primary_key=True)
    collection_task_id = Column(Integer, ForeignKey("specimen_tasks.id"))
    name = String()
    value = String()
    task: Mapped["SpecimenTask"] = relationship(back_populates="parameters")


class SpecimenImage(Base):
    __tablename__ = "specimenimage"
    id = Column(Integer, primary_key=True)
    size = Column(String(20))
    height = Column(Integer)
    width = Column(Integer)
    url = Column(Text)
    create_date = Column(DateTime(timezone=True), default=func.now())
    specimen_id = Column(Integer, ForeignKey("specimen.id"))
    specimen: Mapped["Specimen"] = relationship(back_populates="images")
    external_url = Column(Text)
    hash_a = Column(String(16))
    hash_b = Column(String(16))
    hash_c = Column(String(16))
    hash_d = Column(String(16))
    
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

    def average_hash(self):
        return imagehash.hex_to_hash(f'{self.hash_a}{self.hash_b}{self.hash_c}{self.hash_d}')
