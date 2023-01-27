from sqlalchemy import func, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from torch_hub import Base, db


class Institution(Base):
    __tablename__ = "institution"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    created_date = Column(DateTime(timezone=True), default=func.now())
    # users = relationship("User")
    collections = relationship("Collection")


def get_institutions():
    return db().query(Institution).all()


def create_institution(name, code):
    if len(name) < 1:
        flash("Name is too short!", category="error")
        return None

    new_institution = Institution(name=name, code=code)
    db.session.add(new_institution)
    db.session.commit()
    return new_institution


def delete_institution(institution_id):
    institution = db().query(Institution).get(institution_id)
    if institution:
        db.session.delete(institution)
        db.session.commit()

    return True
