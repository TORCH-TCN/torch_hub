import json
from flask import Blueprint, flash, render_template, request
from flask_login import current_user
from torch.collections.collection import get_collections, save_collection
from torch.collections.specimen import get_specimens_by_batch_id, upload_specimens
from torch.collections.institution import get_institution_by_code


collections = Blueprint("collections", __name__, url_prefix="/collections")


@collections.route("/", methods=["GET"])
def collections():
    institution = get_institution_by_code(current_user.institution_code)
    collections = get_collections(institution.id)

    return render_template(
        "collections.html",
        user=current_user,
        institution=institution,
        collections=collections,
    )


@collections.route("/", methods=["POST"])
def collections():
    institution = get_institution_by_code(current_user.institution_code)
    collection = request.form.get("collection")

    if len(collection) < 1:
        flash("Name is too short!", category="error")
    else:
        save_collection(collection, request.form.get("code"), institution.id)
        flash("Collection added!", category="success")

    return collections()


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
