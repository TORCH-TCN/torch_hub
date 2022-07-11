from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user

from torch.collections.institution import (
    delete_institution,
    get_institutions,
    save_institution,
)


collections = Blueprint("institutions", __name__, url_prefix="/institutions")


@collections.route("/", methods=["GET"])
def institutions():
    institutions = get_institutions()

    return render_template(
        "institutions.html", user=current_user, institutions=institutions
    )


@collections.route("/", methods=["POST"])
def post_institution():
    institution = request.form.get("institution")

    if len(institution) < 1:
        flash("Name is too short!", category="error")
    else:
        save_institution(institution, request.form.get("code"))
        flash("Institution added!", category="success")

    return institutions()


@collections.route("/institutions/<id>", methods=["DELETE"])
def delete(id):
    delete_institution(id)
    return jsonify({})
