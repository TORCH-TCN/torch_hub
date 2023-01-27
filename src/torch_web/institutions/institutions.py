from flask import Blueprint, flash, jsonify, render_template, request
from flask_security import current_user


institutions_bp = Blueprint("institutions", __name__, url_prefix="/institutions")


@institutions_bp.route("/", methods=["GET"])
def institutions_get():
    return render_template(
        "/institutions/institutions.html", user=current_user, institutions=get_institutions()
    )


@institutions_bp.route("/", methods=["POST"])
def post_institution():
    name = request.form.get("institution")
    code = request.form.get("code")
    create_institution(name, code)
    return get_institutions()


@institutions_bp.route("/<institution_id>", methods=["DELETE"])
def delete(institution_id):
    delete_institution(institution_id)
    return jsonify({})
