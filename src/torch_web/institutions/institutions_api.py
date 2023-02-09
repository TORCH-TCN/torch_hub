from flask import Blueprint, jsonify, render_template, request
from flask_security import current_user
from torch_web.institutions import institutions


institutions_bp = Blueprint("institutions", __name__, url_prefix="/institutions")


@institutions_bp.get("/")
def institutions_get():
    return render_template(
        "/institutions/institutions.html", user=current_user, institutions=institutions.get_institutions()
    )


@institutions_bp.post("/")
def post_institution():
    name = request.form.get("institution")
    code = request.form.get("code")
    institutions.create_institution(name, code)
    return institutions.get_institutions()


@institutions_bp.delete("/<institution_id>")
def delete(institution_id):
    institutions.delete_institution(institution_id)
    return jsonify({})
