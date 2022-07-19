import json
from flask import Blueprint, flash, render_template, request
from flask_login import current_user
from sqlalchemy import Column, ForeignKey, Integer, String
from torch.config.database.TorchDatabase import Entity, db
from torch.institutions.institutions import Institution
from torch.collections.specimens import get_specimens_by_batch_id, upload_specimens


class Collection(Entity):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    catalog_number_regex = Column(String(150))
    web_base = Column(String(150))
    url_base = Column(String(150))
    institution_id = Column(Integer, ForeignKey("institution.id"))
    flow_id = Column(String(150))


collections = Blueprint("collections", __name__, url_prefix="/collections")


@collections.route("/", methods=["GET"])
def get_collections():
    institution = Institution.query.filter_by(
        code=current_user.institution_code
    ).first()
    collections = Collection.query.filter_by(institution_id=institution.id).all()

    return render_template(
        "collections.html",
        user=current_user,
        institution=institution,
        collections=collections,
    )


@collections.route("/", methods=["POST"])
def post_collection():
    institution = Institution.query.filter_by(
        code=current_user.institution_code
    ).first()
    collection = request.form.get("collection")

    if len(collection) < 1:
        flash("Name is too short!", category="error")
    else:
        new_collection = Collection(
            name=collection,
            code=request.form.get("code"),
            institution_id=institution.id,
        )
        db.session.add(new_collection)
        db.session.commit()

        flash("Collection added!", category="success")

    return get_collections()


@collections.route("/<collectionid>/specimens", methods=["POST"])
def upload():
    is_ajax = request.form.get("__ajax", None) == "true"

    batch_id = upload_specimens(request.files.getlist("file"))

    if is_ajax:
        return ajax_response(True, batch_id)
    else:
        flash("Upload completed!", category="success")


@collections.route("/<collectionid>/specimens/<batch_id>")
def upload_complete(batch_id):
    specimens = get_specimens_by_batch_id(batch_id)
    return render_template("specimens.html", batch_id=batch_id, files=specimens)


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(
        dict(
            status=status_code,
            msg=msg,
        )
    )
