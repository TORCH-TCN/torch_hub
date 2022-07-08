from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required
from torch.collections.collection import get_collections, save_collection

from torch.collections.institution import (
    get_institution_by_code,
    get_institutions,
    save_institution,
)


collections = Blueprint("collections", __name__, url_prefix="/collections")


@collections.route("/institutions", methods=["GET", "POST"])
@login_required
def institutions():
    if request.method == "POST":
        institution = request.form.get("institution")

        if len(institution) < 1:
            flash("Name is too short!", category="error")
        else:
            save_institution(institution, request.form.get("code"))
            flash("Institution added!", category="success")

    institutions = get_institutions()

    return render_template(
        "institutions.html", user=current_user, institutions=institutions
    )


@collections.route("/", methods=["GET", "POST"])
@login_required
def collections():
    institution = get_institution_by_code(current_user.institution_code)

    if request.method == "POST":
        collection = request.form.get("collection")

        if len(collection) < 1:
            flash("Name is too short!", category="error")
        else:
            save_collection(collection, request.form.get("code"), institution.id)
            flash("Collection added!", category="success")

    collections = get_collections(institution.id)

    return render_template(
        "collections.html",
        user=current_user,
        institution=institution,
        collections=collections,
    )
