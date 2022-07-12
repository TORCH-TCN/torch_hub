from flask import Blueprint, flash, jsonify, render_template, request
from sqlalchemy import Column, DateTime, Integer, String, func
from torch.config.database.TorchDatabase import Entity, db
from sqlalchemy.orm import relationship
from flask_login import current_user


class Institution(Entity):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    created_date = Column(DateTime(timezone=True), default=func.now())
    users = relationship("User")
    collections = relationship("Collection")


def get_institution_by_code(code) -> Institution:
    return Institution.query.filter_by(code=code).first()


institutions = Blueprint("institutions", __name__, url_prefix="/institutions")


@institutions.route("/", methods=["GET"])
def institutions():
    institutions = Institution.query.all()

    return render_template(
        "institutions.html", user=current_user, institutions=institutions
    )


@institutions.route("/", methods=["POST"])
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


@institutions.route("/institutions/<id>", methods=["DELETE"])
def delete(id):
    institution = Institution.query.get(id)
    if institution:
        db.session.delete(institution)
        db.session.commit()

    return jsonify({})
