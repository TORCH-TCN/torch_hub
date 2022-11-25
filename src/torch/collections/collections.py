import csv
import io
import json
import os
from operator import or_
from typing import List

import sqlalchemy as sa
from flask import Blueprint, flash, redirect, render_template, request, current_app, jsonify, make_response
from flask_security import current_user
from sqlalchemy import Column, Integer, String, ForeignKey, func, Text
from sqlalchemy.orm import joinedload
from werkzeug.datastructures import FileStorage

from torch import db, Base
from torch.collections.specimens import Specimen, SpecimenImage
from torch.collections.workflow import run_workflow
from torch.institutions.institutions import Institution

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


home_bp = Blueprint("home", __name__)
collections_bp = Blueprint("collections", __name__, url_prefix="/collections")


def get_default_institution():
    return db.session.query(Institution).first()


@home_bp.route("/", methods=["GET"])
def home():
    print("home collections")
    return redirect("/collections")


@collections_bp.route("/settings")
def collections_settings():
    return render_template("/collections/settings.html", user=current_user)


@collections_bp.route("/", methods=["GET"])
def collections():
    institution = get_default_institution()

    return render_template(
        "/collections/all_collections.html",
        user=current_user,
        institution=institution
    )


@collections_bp.route("/search", methods=["GET"])
def collections_search():
    institution = get_default_institution()

    collections_result = (
        db.session.query(Collection).filter_by(institution_id=institution.id).all()
    )

    collections_dict = []
    for c in collections_result:
        cd = c.as_dict()
        cd["cardimg"] = get_collection_card_image(c.id)
        collections_dict.append(cd)

    return json.dumps(collections_dict, indent=4, sort_keys=True, default=str)


def get_collection_card_image(collection_id):
    img = db.session.query(SpecimenImage).join(Specimen).filter(Specimen.collection_id == collection_id).filter(
        Specimen.deleted == 0).filter(SpecimenImage.size == 'THUMB').first()
    return img.web_url() if img is not None else "../static/images/default.jpg"


@collections_bp.route("/", methods=["POST"])
def collections_post():
    institution = get_default_institution()

    j_collection = request.get_json()
    newname = j_collection['name']

    if len(newname) < 1:
        flash("Name is too short!", category="error")
        return jsonify({})
    else:
        new_collection = Collection(
            id=j_collection.get('id', None),
            name=newname,
            code=j_collection.get('code', None),
            default_prefix=j_collection.get('default_prefix', None),
            catalog_number_regex=j_collection.get('catalog_number_regex', None),
            institution_id=institution.id,
            flow_id=j_collection.get('flow_id', None),
            workflow=j_collection.get('workflow', 'process_specimen'),  # todo select with workflow options
            collection_folder=j_collection.get('collection_folder', None),
            project_ids=j_collection.get('project_ids', None)
        )

        local_collection = db.session.merge(new_collection)
        db.session.add(local_collection)
        db.session.commit()

    return jsonify({"collectionid": new_collection.id})


@collections_bp.route("/<collectioncode>", methods=["GET"])
def collection_get(collectioncode):
    collection = db.session.query(Collection).filter(func.lower(Collection.code) == func.lower(collectioncode)).first()
    return render_template("/collections/specimens.html", collection=collection)


@collections_bp.route("/specimens/<collectionid>", methods=["GET"])
def collection_specimens(collectionid):
    search_string = request.args.get('search_string')
    only_error = request.args.get('only_error')
    collection = db.session.query(Collection).get(collectionid)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 14, type=int)

    specimens = db.session.query(Specimen).filter(Specimen.collection_id == collectionid).filter(Specimen.deleted == 0)

    if search_string is not None:
        specimens = specimens.filter(or_(Specimen.name.contains(search_string),
                                         Specimen.barcode.contains(search_string)))  # todo filter by status (?)

    if only_error == 'true':
        specimens = specimens.filter(func.lower(Specimen.flow_run_state) == 'failed')

    total_specimens = specimens.count()

    specimens = specimens.order_by(Specimen.id.desc()).paginate(page, per_page=per_page)

    specimensdict = []
    for s in specimens.items:
        sd = s.as_dict()
        sd["cardimg"] = s.card_image()
        specimensdict.append(sd)

    return {'specimens': json.dumps(specimensdict, indent=4, sort_keys=True, default=str),
            'total_specimens': total_specimens,
            'collection': json.dumps(collection.as_dict(), indent=4, sort_keys=True, default=str)}


@collections_bp.route("/specimen/retry/<specimenid>", methods=["POST"])
def retry(specimenid):
    specimen = db.session.query(Specimen).get(specimenid)
    collection = db.session.query(Collection).get(specimen.collection_id)
    run_workflow(collection, specimen, config=current_app.config)
    return ajax_response(True, specimenid)


@collections_bp.route("/<collectionid>", methods=["POST"])
def upload(collectionid):
    collection = db.session.query(Collection).filter_by(code=collectionid).first()
    files = request.files.getlist("file")
    collection.add_specimens(files, current_app.config)

    return ajax_response(True, "")


@collections_bp.route("/<collectionid>/settings", methods=["GET", "POST"])
def settings(collectionid="default"):
    return render_template("/collections/settings.html", user=current_user, collectionid=collectionid)


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(
        dict(
            status=status_code,
            msg=msg,
        )
    )


@collections_bp.route("/<collectioncode>/<specimenid>", methods=["GET"])
def specimen_get(collectioncode, specimenid):
    collection = db.session.query(Collection).filter(func.lower(Collection.code) == func.lower(collectioncode)).first()
    specimen = db.session.query(Specimen).filter(Specimen.id == specimenid).first()
    images = db.session.query(SpecimenImage).filter(SpecimenImage.specimen_id == specimenid).filter(
        SpecimenImage.size != "DNG").all()
    dng = db.session.query(SpecimenImage).filter(SpecimenImage.specimen_id == specimenid).filter(
        SpecimenImage.size == "DNG").first()

    orion_url = current_app.config.get("PREFECT_ORION_URL", ORION_URL_DEFAULT)
    prefect_url = orion_url + "flow-run/" + specimen.flow_run_id

    return render_template("/collections/specimen.html", collection=collection, specimen=specimen, images=images,
                           prefect_url=prefect_url, dng=dng)


@collections_bp.route("/<collection_id>", methods=["DELETE"])
def delete(collection_id):
    collection = db.session.query(Collection).get(collection_id)

    if collection:
        specimens = db.session.query(Specimen).filter(Specimen.collection_id == collection_id).all()
        print(specimens)
        if len(specimens) > 0:
            return jsonify({"status": "error", "statusText": "Impossible to delete a collection with specimens."})

        db.session.delete(collection)
        db.session.commit()

    return jsonify({"status": "ok"})


@collections_bp.route("specimen/<specimen_id>", methods=["DELETE"])
def delete_specimen(specimen_id):
    specimen = db.session.query(Specimen).options(joinedload("images")).get(specimen_id)

    if specimen:
        for i in specimen.images:
            delete_img_file(i.url)

        delete_img_file(specimen.upload_path)
        specimen.deleted = 1
        db.session.commit()

    return jsonify({"status": "ok"})


@collections_bp.route("/transferred-specimens/<collectionid>", methods=["DELETE"])
def delete_transfered_specimens(collectionid):
    collection = db.session.query(Collection).get(collectionid)

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

        specimens = db.session.query(Specimen).options(joinedload("images")).filter(Specimen.id.in_(specimens_ids))

        for s in specimens:
            for i in s.images:
                delete_img_file(i.url)

            delete_img_file(s.upload_path)
            s.deleted = 1
            db.session.commit()

    return jsonify({"status": "ok"})


def delete_img_file(upload_path):
    if os.path.exists(upload_path):
        os.remove(upload_path)
    else:
        print("The file does not exist")


@collections_bp.route('/export-csv/<collectionid>', methods=['GET'])
def export_csv(collectionid):
    collection = db.session.query(Collection).get(collectionid)

    if collection:
        specimens = db.session.query(Specimen).options(joinedload("images")).filter(
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

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output


def get_specimen_img_url(specimen_images, size):
    list_imgs = list(filter(lambda x: x.size == size, specimen_images))
    if len(list_imgs) > 0:
        return list_imgs[0].external_url
    return None
