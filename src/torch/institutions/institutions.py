from flask import Blueprint, flash, jsonify, render_template, request
from sqlalchemy import func, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from torch import Base, db
from flask_security import current_user


class Institution(Base):
    __tablename__ = "institution"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    created_date = Column(DateTime(timezone=True), default=func.now())
    # users = relationship("User")
    collections = relationship("Collection")


institutions_bp = Blueprint("institutions", __name__, url_prefix="/institutions")


@institutions_bp.route("/", methods=["GET"])
def institutions():
    institutions = db.session.query(Institution).all()

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
    institution = db.session.query(Institution).get(id)
    if institution:
        db.session.delete(institution)
        db.session.commit()

    return jsonify({})
