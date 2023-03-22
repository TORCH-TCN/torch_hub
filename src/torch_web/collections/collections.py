from operator import or_

from sqlalchemy import Column, Integer, String, ForeignKey, func, Text, exists, select
from sqlalchemy.orm import joinedload

from torch_web import db, Base
from torch_web.collections.specimens import Specimen, SpecimenImage
from torch_web.collections.workflow import run_workflow

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

    def add_specimens(self, files, config, progress):
        for file in files:
            run_workflow(self, file, config, progress)


def get_collections(institutionid):
    collections_result = db.session.scalars(select(Collection).filter_by(institution_id=institutionid)).all()

    collections_dict = []
    for c in collections_result:
        cd = c.as_dict()
        cd["cardimg"] = get_collection_card_image(c.id)
        collections_dict.append(cd)

    return collections_dict


def get_collection_card_image(collection_id):
    img = db.session.scalars(select(SpecimenImage).join(Specimen)
                             .where(Specimen.collection_id == collection_id)
                             .where(Specimen.deleted == 0)
                             .where(SpecimenImage.size == 'THUMB')).first()
    return img.external_url if img is not None else "/static/images/default.jpg"


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


def get_collection(collectioncode):
    return db.session.scalars(select(Collection).where(Collection.code == collectioncode)).one_or_none()


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
        sd["cardimg"] = s.card_image()
        specimensdict.append(sd)

    return specimensdict


def retry_workflow(specimenid, config):
    specimen = db.session.get(Specimen, specimenid)
    collection = db.session.get(Collection, specimen.collection_id)
    run_workflow(collection, specimen, config=config)
    return True


def upload(collectionid, files, config, progress):
    collection = db.session.get(Collection, collectionid)
    collection.add_specimens(files, config, progress)
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
