from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import login_required
from sqlalchemy import Column, DateTime, Integer, String, func
#from torch.config.database.TorchDatabase import Entity, db
from torch import db
from sqlalchemy.orm import relationship
from flask_security import current_user


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    code = db.Column(db.String(10), unique=True)
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    users = db.relationship('User')
    collections = db.relationship('Collection')




def get_institution_by_code(code) -> Institution:
     return Institution.query.filter_by(code=code).first()


institutions_bp = Blueprint("institutions", __name__, url_prefix="/institutions")


@institutions_bp.route("/", methods=["GET"])
@login_required
def institutions():
    institutions = Institution.query.all()

    return render_template(
        "/institutions/institutions.html", user=current_user, institutions=institutions
    )


@institutions_bp.route("/", methods=["POST"])
def post_institution():
    institution = request.form.get("institution")

    if len(institution) < 1:
        flash("Name is too short!", category="error")
    else:
        new_institution = Institution(name=institution, code=request.form.get("code"))
        db.session.add(new_institution)
        db.session.commit()

        flash("Institution added!", category="success")

    return institutions()


@institutions_bp.route("/<id>", methods=["DELETE"])
def delete(id):
    institution = Institution.query.get(id)
    if institution:
        db.session.delete(institution)
        db.session.commit()

    return jsonify({})
