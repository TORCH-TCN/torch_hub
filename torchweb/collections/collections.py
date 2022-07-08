import json
from flask import Blueprint, flash, render_template, request
from flask_login import current_user
from torch.collections.collection import get_collections, save_collection
from torch.collections.image import get_images_by_upload_key, upload_images
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


@collections.route("/<collectionid>/images", methods=["POST"])
def upload():
    is_ajax = request.form.get("__ajax", None) == "true"

    batch_id = upload_images(request.files.getlist("file"))

    if is_ajax:
        return ajax_response(True, batch_id)
    else:
        flash("Upload completed!", category="success")


@collections.route("/<collectionid>/images/<batch_id>")
def upload_complete(batch_id):
    files = get_images_by_upload_key(batch_id)
    return render_template("images.html", batch_id=batch_id, files=files)


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(
        dict(
            status=status_code,
            msg=msg,
        )
    )
