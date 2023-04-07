from tkinter import SEL
import imagehash
import datetime
import importlib
import os

from operator import or_
from typing import List
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, func, exists, select
from sqlalchemy.orm import Mapped, relationship, joinedload, selectinload
from torch_web import db, Base
from prefect import context
from flask import current_app


class Collection(Base):
    __tablename__ = "collection"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    tasks: Mapped[List["CollectionTask"]] = relationship("CollectionTask", back_populates="collection", lazy="selectin")
    specimens: Mapped[List["Specimen"]] = relationship("Specimen", back_populates="collection")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class CollectionTask(Base):
    __tablename__ = "collection_tasks"
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey("collection.id"))
    func_name = Column(String(50))
    name = Column(String(100))
    sort_order = Column(Integer())
    description = Column(String())
    collection: Mapped["Collection"] = relationship("Collection", back_populates="tasks")
    parameters: Mapped[List["CollectionTaskParameter"]] = relationship("CollectionTaskParameter", back_populates="task", lazy="selectin")

    def parameters_dict(self):
        return { p.name: p.value for p in self.parameters }


class CollectionTaskParameter(Base):
    __tablename__ = "collection_tasks_parameters"
    id = Column(Integer, primary_key=True)
    collection_task_id = Column(Integer, ForeignKey("collection_tasks.id"))
    name = Column(String())
    value = Column(String())
    task: Mapped["CollectionTask"] = relationship("CollectionTask", back_populates="parameters")


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
    images: Mapped[List["SpecimenImage"]] = relationship("SpecimenImage", back_populates="specimen", lazy="selectin")
    tasks: Mapped[List["SpecimenTask"]] = relationship("SpecimenTask", back_populates="specimen")
    collection: Mapped["Collection"] = relationship("Collection", back_populates="specimens")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def card_image(self):
        if self.images is None or len(self.images) == 0:
            return None;

        sorted_images = sorted(self.images, key=lambda x: x.size)
        return sorted_images[0]


class SpecimenTask(Base):
    __tablename__ = "specimen_tasks"
    id = Column(Integer, primary_key=True)
    specimen_id = Column(Integer, ForeignKey("specimen.id"))
    func_name = Column(String())
    name = Column(String())
    sort_order = Column(Integer())
    description = Column(String())
    batch_id = Column(String())
    start_date = Column(DateTime(timezone=True), default=func.now())
    end_date = Column(DateTime(timezone=True))
    run_state = Column(String())
    run_message = Column(String())
    specimen: Mapped["Specimen"] = relationship("Specimen", back_populates="tasks")
    parameters: Mapped[List["SpecimenTaskParameter"]] = relationship("SpecimenTaskParameter", back_populates="task", lazy="selectin")


class SpecimenTaskParameter(Base):
    __tablename__ = "specimen_tasks_parameters"
    id = Column(Integer, primary_key=True)
    specimen_task_id = Column(Integer, ForeignKey("specimen_tasks.id"))
    name = Column(String())
    value = Column(String())
    task: Mapped["SpecimenTask"] = relationship("SpecimenTask", back_populates="parameters")


class SpecimenImage(Base):
    __tablename__ = "specimenimage"
    id = Column(Integer, primary_key=True)
    size = Column(String(20))
    height = Column(Integer)
    width = Column(Integer)
    url = Column(Text)
    create_date = Column(DateTime(timezone=True), default=func.now())
    specimen_id = Column(Integer, ForeignKey("specimen.id"))
    specimen: Mapped["Specimen"] = relationship("Specimen", back_populates="images")
    external_url = Column(Text)
    hash_a = Column(String(16))
    hash_b = Column(String(16))
    hash_c = Column(String(16))
    hash_d = Column(String(16))
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def average_hash(self):
        return imagehash.hex_to_hash(f'{self.hash_a}{self.hash_b}{self.hash_c}{self.hash_d}')


def get_collections(institutionid):
    collections_result = db.session.scalars(select(Collection).filter_by(institution_id=institutionid)).all()

    collections_dict = []
    for c in collections_result:
        cd = c.as_dict()
        cd["cardimg"] = get_collection_card_images(c.id)
        cd["specimencount"] = db.session.query(Specimen).filter(Specimen.collection_id == c.id).count()
        collections_dict.append(cd)

    return collections_dict


def get_collection_card_images(collection_id):
    img = db.session.scalars(select(SpecimenImage).join(Specimen)
                             .where(Specimen.collection_id == collection_id)
                             .where(Specimen.deleted == 0)
                             .where(SpecimenImage.size == 'THUMB').limit(10)).all()
    return img


def create_collection(institutionid, collection_id, name, code, default_prefix, catalog_number_regex, flow_id, workflow,
                      collection_folder, project_ids):
    new_collection = Collection(
        id=collection_id,
        name=name,
        code=code,
        default_prefix=default_prefix,
        catalog_number_regex=catalog_number_regex,
        institution_id=institutionid,
        flow_id=flow_id,
        workflow=workflow,
        collection_folder=collection_folder,
        project_ids=project_ids
    )

    local_collection = db.session.merge(new_collection)
    db.session.add(local_collection)
    db.session.commit()

    return local_collection


def update_workflow(collection_id, data):
    collection = db.session.get(Collection, collection_id)
    for task in collection.tasks:
        for p in task.parameters:
            db.session.delete(p)
        db.session.delete(task)
    db.session.commit()

    collection.tasks = []
    for task in data:
        new_task = CollectionTask()
        new_task.sort_order = task["sort_order"]
        new_task.func_name = task["func_name"]
        new_task.name = task["name"]
        collection.tasks.append(new_task)
        
        for p in task["parameters"]:
            new_p = CollectionTaskParameter()
            new_p.name = p["name"]
            new_p.value = p["value"]
            new_task.parameters.append(new_p)

    db.session.commit()


def get_collection(id):
    coll = db.session.scalars(select(Collection).where(Collection.id == id)).one_or_none()
    print(coll.__dict__)
    return coll


def get_collection_specimens(collectionid, search_string, only_error, page=1, per_page=14):
    specimens = select(Specimen).where(Specimen.collection_id == collectionid).where(Specimen.deleted == 0)

    if search_string is not None:
        specimens = specimens.filter(or_(Specimen.name.contains(search_string),
                                         Specimen.barcode.contains(search_string)))  # todo filter by status (?)

    if only_error == 'true':
        specimens = specimens.filter(func.lower(Specimen.flow_run_state) == 'failed')

    specimens = specimens.order_by(Specimen.id.desc()).limit(per_page).offset((page - 1) * per_page)
    result = db.session.scalars(specimens).all()

    specimensdict = []
    for s in result:
        sd = s.as_dict()
        sd["card_image"] = s.card_image()
        specimensdict.append(sd)

    return specimensdict


def retry_workflow(specimenid):
    specimen = db.session.get(Specimen, specimenid)
    collection = db.session.get(Collection, specimen.collection_id)
    run_workflow(collection, specimen)
    return True


def upload(collectionid, files):
    collection = db.session.get(Collection, collectionid)
    for file in files:
        specimen, execute_workflow = upsert_specimen(collection, file)
        context.socketio.emit('specimen_added', specimen.id);
        run_workflow(collection, specimen)
    
    return True


def get_specimen(specimenid):
    specimen = db.session.scalars(select(Specimen).where(Specimen.id == specimenid)).first()
    images = db.session.scalars(select(SpecimenImage)
                                .filter(SpecimenImage.specimen_id == specimenid)
                                .filter(SpecimenImage.size != "DNG")).all()
    dng = db.session.scalars(select(SpecimenImage)
                             .filter(SpecimenImage.specimen_id == specimenid)
                             .filter(SpecimenImage.size == "DNG")).first()

    specimen.images = images
    specimen.images.add(dng)

    return specimen


def delete_collection(collection_id):
    collection = db.session.get(Collection, collection_id)

    if collection:
        specimens = db.session.scalars(select(Specimen).filter(Specimen.collection_id == collection_id)).all()
        print(specimens)
        if len(specimens) > 0:
            return False

        db.session.delete(collection)
        db.session.commit()

    return True


def delete_specimen(specimen_id):
    specimen = db.session.scalars(select(Specimen)
                                  .options(joinedload(Specimen.images))
                                  .where(id == specimen_id)).first()
    
    if specimen:
        for i in specimen.images:
            delete_img_file(i.url)

        delete_img_file(specimen.upload_path)
        specimen.deleted = 1
        db.session.commit()

    return True


def delete_transfered_specimens(collectionid):
    collection = db.session.get(Collection, collectionid)

    if collection:
        specimens_has_non_transferred_images = exists(
            select([SpecimenImage.id])
            .select_from(SpecimenImage)
            .where((SpecimenImage.specimen_id == Specimen.id) &
                   (SpecimenImage.external_url is None))
        )

        specimens_with_transferred_images = (select([Specimen.id])
                                             .select_from(Specimen)
                                             .where((Specimen.collection_id == collectionid) &
                                                    (Specimen.deleted == 0) &
                                                    ~specimens_has_non_transferred_images)
                                             )

        specimens_ids = list(map(lambda x: x.id, db.session.scalars(specimens_with_transferred_images)))

        specimens = db.session.scalars(select(Specimen).options(joinedload(Specimen.images)).filter(Specimen.id.in_(specimens_ids))).all()

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
    collection = db.session.get(Collection, collectionid)

    if collection:
        specimens = db.session.scalars(select(Specimen).options(joinedload(Specimen.images))
                                       .filter(Specimen.collection_id == collectionid)
                                       .filter(Specimen.deleted == 0)
                                       .order_by(Specimen.id.desc())).all()

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


def notify(task, specimen, state, message=None):
    task.run_state = state
    task.run_message = message
    db.session.commit()
    context.socketio.emit(task.func_name, (specimen.id, task.func_name, task.run_state))
    context.socketio.emit('specimen_updated_' + str(specimen.id), (specimen.catalog_number, task.func_name + ': ' + task.run_state))
     

def run_workflow(collection, specimen):
    db.session.merge(specimen)
        
    for task in collection.tasks:
        specimen_task_parameters = [SpecimenTaskParameter(name=p.name, value=p.value) for p in task.parameters]
        specimen_task = SpecimenTask(func_name=task.func_name, name=task.name, description=task.description, sort_order=task.sort_order, parameters=specimen_task_parameters)
        specimen.tasks.append(specimen_task)

        notify(specimen_task, specimen, 'Running')
            
        module = importlib.import_module('workflows.tasks.' + task.func_name)
        func = getattr(module, task.func_name)
        result = func(specimen, **task.parameters_dict())
            
        specimen_task.end_date = datetime.datetime.now()
        if isinstance(result, str):
            notify(specimen_task, specimen, 'Error', result)
            break
            
        notify(task, specimen, 'Success')


def upsert_specimen(collection, file):
    filename = os.path.basename(file).split(".")[0]
    extension = os.path.basename(file).split(".")[1]

    execute_workflow = True

    specimen = db.session.scalars(select(Specimen).filter(Specimen.name == filename)).first()

    if specimen is not None:
        if extension.lower() == "dng":
            specimen.has_dng = 1
            execute_workflow = False

        else:
            execute_workflow = specimen.flow_run_id is not None

    else:
        specimen = Specimen(
            name=filename, upload_path=file, collection_id=collection.id
        )
        db.session.add(specimen)
        db.session.commit()

    upsert_specimen_image(specimen, file, extension.lower())

    return specimen, execute_workflow


def upsert_specimen_image(specimen, destination, extension):
    size = "FULL"
    if extension == "dng":
        size = "DNG"


    web_url = destination.replace(current_app.config['BASE_DIR'] + "\\", '').replace("\\", "/")
    si = next((img for img in specimen.images if img.size == size), None)

    if si is None:
        new_si = SpecimenImage(specimen_id=specimen.id, url=destination, external_url=web_url, size=size)
        specimen.images.append(new_si)
    else:
        si.url = web_url
    
    db.session.commit()
