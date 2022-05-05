from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Institution, User
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        institution = request.form.get('institution')

        if len(institution) < 1:
            flash('Name is too short!', category='error')
        else:
            new_institution = Institution(name=institution)
            db.session.add(new_institution)
            db.session.commit()
            flash('Institution added!', category='success')

    institutions = Institution.query.all()

    return render_template("home.html", user=current_user, institutions=institutions)


@views.route('/delete-institution', methods=['POST'])
def delete_institution():
    institution = json.loads(request.data)
    institutionId = institution['institutionId']
    institution = Institution.query.get(institutionId)
    if institution:
        db.session.delete(institution)
        db.session.commit()

    return jsonify({})