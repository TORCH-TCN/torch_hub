from typing import List
from sqlalchemy import Column, DateTime, Integer, String, func
from torch.config.database.TorchDatabase import Entity, db
from sqlalchemy.orm import relationship


class Institution(Entity):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    created_date = Column(DateTime(timezone=True), default=func.now())
    users = relationship("User")
    collections = relationship("Collection")


def get_institutions() -> List[Institution]:
    return Institution.query.all()


def get_institution(id) -> Institution:
    return Institution.query.filter_by(id=id).first()


def get_institution_by_code(code) -> Institution:
    return Institution.query.filter_by(code=code).first()


def save_institution(institution, code):
    new_institution = Institution(name=institution, code=code)
    db.session.add(new_institution)
    db.session.commit()


def delete_institution(id):
    institution = Institution.query.get(id)
    if institution:
        db.session.delete(institution)
        db.session.commit()
