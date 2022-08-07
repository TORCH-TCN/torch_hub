import json
import os
from typing import List
from uuid import uuid4
from flask import Blueprint, flash, redirect, render_template, request
from flask_security import current_user

from torch import db
from torch.collections.specimens import Specimen
from torch.institutions.institutions import Institution
from torch.tasks.process_specimen import process_specimen
from werkzeug import FileStorage
from werkzeug.utils import secure_filename
from prefect import Client


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    code = db.Column(db.String(10), unique=True)
    catalog_number_regex = db.Column(db.String(150))
    web_base = db.Column(db.String(150))
    url_base = db.Column(db.String(150))
    institution_id = db.Column(db.Integer, db.ForeignKey("institution.id"))
    flow_id = db.Column(db.String(150))

    def add_specimens(self, files: List[FileStorage]) -> Specimen:
        batch_id = str(uuid4())
        target_dir = "{}/{}".format("static/uploads", batch_id)
        os.makedirs(target_dir)

        for file in files:
            filename = secure_filename(file.filename)
            destination = os.path.join(target_dir, filename)
            file.save(destination)

            client = Client()
            flow_run_id = client.create_flow_run(flow_id=self.flow_id)

            specimen = Specimen(
                name=file.filename,
                upload_path=destination,
                collection_id=self.id,
                flow_run_id=flow_run_id,
            )

            db.session.add(specimen)

        db.session.commit()


home_bp = Blueprint("home", __name__)
collections_bp = Blueprint("collections", __name__, url_prefix="/collections")


def get_user_institution():
    code = current_user.institution_code if current_user.is_authenticated else "default"
    return Institution.query.filter_by(code=code).first()


@home_bp.route("/", methods=["GET"])
def home():
    print("home collections")
    return redirect("/collections")


@collections_bp.route("/", methods=["GET"])
def collections():
    institution = get_user_institution()
    collections = Collection.query.filter_by(institution_id=institution.id).all()

    return render_template(
        "/collections/collections.html",
        user=current_user,
        institution=institution,
        collections=collections,
    )


@collections_bp.route("/", methods=["POST"])
def collectionspost():
    institution = get_user_institution()
    collection = request.form.get("collection")

    if len(collection) < 1:
        flash("Name is too short!", category="error")
    else:
        new_collection = Collection(
            name=collection,
            code=request.form.get("code"),
            institution_id=institution.id,
        )
        new_collection.flow_id = process_specimen.register(
            project_name=institution.name
        )
        db.session.add(new_collection)
        db.session.commit()

        flash("Collection added!", category="success")

    return collections()


@collections_bp.route("/<collectionid>", methods=["GET"])
def collection(collectionid):
    collection = Collection.query.filter_by(code=collectionid).first()
    return render_template("/collections/specimens.html", collection=collection)


@collections_bp.route("/<collectionid>", methods=["POST"])
def upload(collectionid):
    collection = Collection.query.filter_by(code=collectionid).first()
    files = request.files.getlist("file")
    batch_id = collection.add_specimens(files)

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
