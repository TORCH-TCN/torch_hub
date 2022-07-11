from typing import List
from sqlalchemy import Column, ForeignKey, Integer, String
from torch.config.database.TorchDatabase import Entity, db
from sqlalchemy.orm import relationship


class Collection(Entity):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    catalog_number_regex = Column(String(150))
    web_base = Column(String(150))
    url_base = Column(String(150))
    institution_id = Column(Integer, ForeignKey("institution.id"))
    workflows = relationship("Workflow")


def get_collections(institutionid) -> List[Collection]:
    return Collection.query.filter_by(institution_id=institutionid).all()


def save_collection(name, code, institutionid):
    new_collection = Collection(name=name, code=code, institution_id=institutionid)

    db.session.add(new_collection)
    db.session.commit()
