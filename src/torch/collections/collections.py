import json
import os
from uuid import uuid4
from flask import Blueprint, flash, redirect, render_template, request, current_app
from flask_security import current_user, login_required
from sqlalchemy import Column, Integer, String, ForeignKey
from torch import db, Base
from torch.collections.specimens import Specimen
from torch.institutions.institutions import Institution
from werkzeug.utils import secure_filename

from torch.tasks.process_specimen import process_specimen


class Collection(Base):
    __tablename__ = "collection"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    catalog_number_regex = Column(String(150))
    web_base = Column(String(150))
    url_base = Column(String(150))
    institution_id = Column(Integer, ForeignKey("institution.id"))
    flow_id = Column(String(150))

    def add_specimens(self, files, config) -> Specimen:
        batch_id = str(uuid4())
        target_dir = "{}/{}".format("static/uploads", batch_id)
        os.makedirs(target_dir)

        for file in files:
            filename = secure_filename(file.filename)
            destination = os.path.join(target_dir, filename)
            file.save(destination)

            specimen = Specimen(
                name=file.filename, upload_path=destination, collection_id=self.id
            )

            process_specimen(specimen, config)


home_bp = Blueprint("home", __name__)
collections_bp = Blueprint("collections", __name__, url_prefix="/collections")


def get_default_institution():
    return db.session.query(Institution).first()


@home_bp.route("/", methods=["GET"])
@login_required
def home():
    print("home collections")
    return redirect("/collections")


@collections_bp.route("/", methods=["GET"])
@login_required
def collections():
    institution = get_default_institution()
    collections = (
        db.session.query(Collection).filter_by(institution_id=institution.id).all()
    )

    return render_template(
        "/collections/collections.html",
        user=current_user,
        institution=institution,
        collections=collections,
    )


@collections_bp.route("/", methods=["POST"])
def collectionspost():
    institution = get_default_institution()
    collection = request.form.get("collection")

    if len(collection) < 1:
        flash("Name is too short!", category="error")
    else:
        new_collection = Collection(
            name=collection,
            code=request.form.get("code"),
            institution_id=institution.id,
        )
        # new_collection.flow_id = process_specimen.register(
        #     project_name=institution.name
        # )
        db.session.add(new_collection)
        db.session.commit()

        flash("Collection added!", category="success")

    return collections()


@collections_bp.route("/<collectionid>", methods=["GET"])
def collection(collectionid):
    collection = db.session.query(Collection).filter_by(code=collectionid).first()
    return render_template("/collections/specimens.html", collection=collection)


@collections_bp.route("/<collectionid>", methods=["POST"])
def upload(collectionid):
    collection = db.session.query(Collection).filter_by(code=collectionid).first()
    files = request.files.getlist("file")
    batch_id = collection.add_specimens(files, current_app.config)

    return ajax_response(True, batch_id)


@collections_bp.route("/<collectionid>/settings", methods=["GET", "POST"])
def settings(collectionid="default"):
    return render_template("/collections/settings.html", user=current_user)


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(
        dict(
            status=status_code,
            msg=msg,
        )
    )
