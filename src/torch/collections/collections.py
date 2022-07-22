import json
from flask import Blueprint, flash, redirect, render_template, request
from flask_login import current_user
from torch import db
from torch.collections.specimens import get_specimens_by_batch_id, upload_specimens
from torch.institutions.institutions import Institution


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    code = db.Column(db.String(10), unique=True)
    catalog_number_regex = db.Column(db.String(150))
    web_base = db.Column(db.String(150))
    url_base = db.Column(db.String(150))
    institution_id = db.Column(db.Integer, db.ForeignKey("institution.id"))
    flow_id = db.Column(db.String(150))


home_bp = Blueprint("home", __name__)
collections_bp = Blueprint("collections", __name__, url_prefix="/collections")


@home_bp.route("/", methods=["GET"])
def home():
    print("home collections")
    return redirect("/collections")


@collections_bp.route("/", methods=["GET"])
def collections():
    institution = Institution.query.filter_by(
        code=current_user.institution_code
    ).first()
    collections = Collection.query.filter_by(institution_id=institution.id).all()

    return render_template(
        "/collections/collections.html",
        user=current_user,
        institution=institution,
        collections=collections,
    )


@collections_bp.route("/", methods=["POST"])
def collectionspost():
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

    return collections()


@collections_bp.route("/<collectionid>/specimens", methods=["POST"])
def upload():
    is_ajax = request.form.get("__ajax", None) == "true"

    batch_id = upload_specimens(request.files.getlist("file"))

    if is_ajax:
        return ajax_response(True, batch_id)
    else:
        flash("Upload completed!", category="success")


@collections_bp.route("/<collectionid>/specimens/<batch_id>")
def upload_complete(batch_id):
    specimens = get_specimens_by_batch_id(batch_id)
    return render_template(
        "/specimens/specimens.html", batch_id=batch_id, files=specimens
    )


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(
        dict(
            status=status_code,
            msg=msg,
        )
    )
