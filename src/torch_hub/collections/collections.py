import csv
import io
import os
from operator import or_
from typing import List

import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, ForeignKey, func, Text
from sqlalchemy.orm import joinedload
from werkzeug.datastructures import FileStorage

from torch_hub import db, Base
from torch_hub.collections.specimens import Specimen, SpecimenImage
from torch_hub.institutions.institutions import Institution
from torch_hub.collections.workflow import run_workflow

ORION_URL_DEFAULT = "http://127.0.0.1:4200/"


class Collection(Base):
    __tablename__ = "collection"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    default_prefix = Column(String(15))
    catalog_number_regex = Column(Text)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    flow_id = Column(String(150))
    workflow = Column(String(150))
    collection_folder = Column(String(150))
    project_ids = Column(String(150))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def add_specimens(self, files: List[FileStorage], config):
        for file in files:
            run_workflow(self, file, config)


def get_default_institution():
    return db().query(Institution).first()


def get_collections():
    institution = get_default_institution()

    collections_result = (
        db().query(Collection).filter_by(institution_id=institution.id).all()
    )

    collections_dict = []
    for c in collections_result:
        cd = c.as_dict()
        cd["cardimg"] = get_collection_card_image(c.id)
        collections_dict.append(cd)

    return collections_dict


def get_collection_card_image(collection_id):
    img = db().query(SpecimenImage).join(Specimen).filter(Specimen.collection_id == collection_id).filter(
        Specimen.deleted == 0).filter(SpecimenImage.size == 'THUMB').first()
    return img.web_url() if img is not None else "/static/images/default.jpg"


def create_collection(collection_id, name, code, default_prefix, catalog_number_regex, flow_id, workflow,
                      collection_folder, project_ids):
    institution = get_default_institution()

    if len(name) < 1:
        flash("Name is too short!", category="error")
        return None
    else:
        new_collection = Collection(
            id=collection_id,
            name=name,
            code=code,
            default_prefix=default_prefix,
            catalog_number_regex=catalog_number_regex,
            institution_id=institution.id,
            flow_id=flow_id,
            workflow=workflow,
            collection_folder=collection_folder,
            project_ids=project_ids
        )

        local_collection = db.session.merge(new_collection)
        db.session.add(local_collection)
        db.session.commit()

    return new_collection


def get_collection(collectioncode):
    return db().query(Collection).filter(func.lower(Collection.code) == func.lower(collectioncode)).first()


def get_collection_specimens(collectionid, search_string, only_error, page=1, per_page=14):
    specimens = db().query(Specimen).filter(Specimen.collection_id == collectionid).filter(Specimen.deleted == 0)

    if search_string is not None:
        specimens = specimens.filter(or_(Specimen.name.contains(search_string),
                                         Specimen.barcode.contains(search_string)))  # todo filter by status (?)

    if only_error == 'true':
        specimens = specimens.filter(func.lower(Specimen.flow_run_state) == 'failed')

    specimens = specimens.order_by(Specimen.id.desc()).paginate(page=page, per_page=per_page)

    specimensdict = []
    for s in specimens.items:
        sd = s.as_dict()
        sd["cardimg"] = s.card_image()
        specimensdict.append(sd)

    return specimensdict


def retry_workflow(specimenid):
    specimen = db().query(Specimen).get(specimenid)
    collection = db().query(Collection).get(specimen.collection_id)
    run_workflow(collection, specimen, config=current_app.config)
    return True


def upload(collectionid, files, config):
    collection = db().query(Collection).filter_by(code=collectionid).first()
    collection.add_specimens(files, config)
    return True


def get_specimen(specimenid):
    specimen = db().query(Specimen).filter(Specimen.id == specimenid).first()
    images = db().query(SpecimenImage).filter(SpecimenImage.specimen_id == specimenid).filter(
        SpecimenImage.size != "DNG").all()
    dng = db().query(SpecimenImage).filter(SpecimenImage.specimen_id == specimenid).filter(
        SpecimenImage.size == "DNG").first()

    specimen.images = images
    specimen.images.add(dng)

    return specimen


def delete_collection(collection_id):
    collection = db().query(Collection).get(collection_id)

    if collection:
        specimens = db().query(Specimen).filter(Specimen.collection_id == collection_id).all()
        print(specimens)
        if len(specimens) > 0:
            return False

        db.session.delete(collection)
        db.session.commit()

    return True


def delete_specimen(specimen_id):
    specimen = db().query(Specimen).options(joinedload("images")).get(specimen_id)

    if specimen:
        for i in specimen.images:
            delete_img_file(i.url)

        delete_img_file(specimen.upload_path)
        specimen.deleted = 1
        db.session.commit()

    return True


def delete_transfered_specimens(collectionid):
    collection = db().query(Collection).get(collectionid)

    if collection:
        specimens_has_non_transferred_images = sa.exists(
            sa.select([SpecimenImage.id])
            .select_from(SpecimenImage)
            .where((SpecimenImage.specimen_id == Specimen.id) &
                   (SpecimenImage.external_url is None))
        )

        specimens_with_transferred_images = (sa.select([Specimen.id])
                                             .select_from(Specimen)
                                             .where((Specimen.collection_id == collectionid) &
                                                    (Specimen.deleted == 0) &
                                                    ~specimens_has_non_transferred_images)
                                             )

        specimens_ids = list(map(lambda x: x.id, db.session.execute(specimens_with_transferred_images)))

        specimens = db().query(Specimen).options(joinedload("images")).filter(Specimen.id.in_(specimens_ids))

        for s in specimens:
            for i in s.images:
                delete_img_file(i.url)

            delete_img_file(s.upload_path)
            s.deleted = 1
            db.session.commit()

    return True


def delete_img_file(upload_path):
    if os.path.exists(upload_path):
        os.remove(upload_path)
    else:
        print("The file does not exist")


def export_csv(collectionid):
    collection = db().query(Collection).get(collectionid)

    if collection:
        specimens = db().query(Specimen).options(joinedload("images")).filter(
            Specimen.collection_id == collectionid).filter(Specimen.deleted == 0).order_by(Specimen.id.desc()).all()

        si = io.StringIO()
        fieldnames = ['catalog_number', 'large', 'web', 'thumbnail']
        writer = csv.DictWriter(si, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()

        for s in specimens:
            large = get_specimen_img_url(s.images, 'FULL')
            web = get_specimen_img_url(s.images, 'MED')
            thumbnail = get_specimen_img_url(s.images, 'THUMB')
            if s.catalog_number is None:
                s.catalog_number = s.name
            writer.writerow({'catalog_number': s.catalog_number, 'large': large, 'web': web, 'thumbnail': thumbnail})

        return si.getvalue()


def get_specimen_img_url(specimen_images, size):
    list_imgs = list(filter(lambda x: x.size == size, specimen_images))
    if len(list_imgs) > 0:
        return list_imgs[0].external_url
    return None
