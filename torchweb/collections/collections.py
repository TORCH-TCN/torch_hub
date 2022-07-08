from flask import Blueprint, flash, render_template, request
from flask_login import current_user
from torch.collections.collection import get_collections, save_collection

from torch.collections.institution import (
    get_institution_by_code,
)


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
