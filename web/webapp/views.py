from flask import Blueprint, redirect, render_template, request, flash, jsonify
from flask_security import login_required, current_user, roles_accepted, SQLAlchemyUserDatastore
from .models import Collection, Institution, Role, User
from . import db
from flask_sqlalchemy import orm
import json

views = Blueprint('views', __name__)


# @views.route('/', methods=['GET', 'POST'])
# @login_required
# def home():
#     if request.method == 'POST':
#         institution = request.form.get('institution')

#         if len(institution) < 1:
#             flash('Name is too short!', category='error')
#         else:
#             new_institution = Institution(name=institution)
#             db.session.add(new_institution)
#             db.session.commit()
#             flash('Institution added!', category='success')

#     institutions = Institution.query.all()

#     return render_template("home.html", user=current_user, institutions=institutions)

@views.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('firstName')
        current_user.last_name = request.form.get('lastName')
        db.session.commit()
        flash('Updated successfully!', category='success')

    return render_template("profile.html",user=current_user)

@views.route('/users/edit/<userid>', methods=['GET','POST'])
@roles_accepted('admin')
def users_edit(userid=None):
    
    institutions = Institution.query.all()
    user = User.query.filter_by(id=userid).first()
    
    if request.method == 'POST':
        institution = Institution.query.filter_by(id=request.form.get('institutionid')).first()
        user.institution_id = institution.id
        user.institution_code =institution.code
        # current_user.first_name = request.form.get('institution')
        # current_user.last_name = request.form.get('lastName')
        db.session.commit()
        flash("User updated", category='success')
        return redirect('/users')

    if(user.institution_id == None and user.institution_code != None):
        institution = Institution.query.filter_by(code=user.institution_code).first()
        user.institution_id = institution.id
        db.session.commit()
    

    return render_template("users/edit.html", user=current_user, edituser=user, institutions=institutions)

@views.route('/users', methods=['GET'])
@roles_accepted('admin')
def users():
    users = User.query.options(orm.joinedload('roles'))
    roles = Role.query.all()
    return render_template("users/users.html", user=current_user, users=users, roles=roles)

@views.route('users/modal/<userid>')
def modal(userid=None):
    return render_template("users/addrolemodal.html", user=current_user, userid=userid)

@views.route('/roles', methods=['GET', 'POST'])
@roles_accepted('admin')
def roles():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        new_role = Role(name=name,description=description)
        db.session.add(new_role)
        db.session.commit()
        #user_datastore
    roles = Role.query.all()
    return render_template("roles/roles.html", user=current_user, roles=roles)

@views.route('/delete-institution', methods=['POST'])
def delete_institution():
    institution = json.loads(request.data)
    institutionId = institution['institutionId']
    institution = Institution.query.get(institutionId)
    if institution:
        db.session.delete(institution)
        db.session.commit()

    return jsonify({})

@views.route('/assign-role', methods=['POST'])
@roles_accepted('admin')
def assign_role():
    data = json.loads(request.data)
    userId = data['userId']
    role = data['role']
    
    user = User.query.get(userId)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.add_role_to_user(user,role)
    db.session.commit()

    return jsonify({})

@views.route('/delete-role-user', methods=['POST'])
@roles_accepted('admin')
def delete_role_user():
    data = json.loads(request.data)
    userId = data['userId']
    role = data['role']
    
    user = User.query.get(userId)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.remove_role_from_user(user,role)
    db.session.commit()

    return jsonify({})


@views.route('/change-user-active', methods=['POST'])
@roles_accepted('admin')
def deactivate_user():
    data = json.loads(request.data)
    userId = data['userId']
        
    user = User.query.get(userId)
    user.active = 0 if user.active == 1 else 1

    db.session.commit()

    return jsonify({})


@views.route('/institutions', methods=['GET', 'POST'])
@login_required
def institutions():
    if request.method == 'POST':
        institution = request.form.get('institution')
        code = request.form.get('code')

        if len(institution) < 1:
            flash('Name is too short!', category='error')
        else:
            new_institution = Institution(name = institution, code = code)
            db.session.add(new_institution)
            db.session.commit()
            flash('Institution added!', category='success')

    institutions = Institution.query.all()

    return render_template("institutions.html", user=current_user, institutions=institutions)

@views.route('/', methods=['GET', 'POST'])
@views.route('collections/<institutionid>', methods=['GET', 'POST'])
@login_required
def collections(institutionid=None):
    
    if current_user.has_role('admin') and institutionid == None:
        institutionid = 1
    
    if(institutionid == None):
        institutionid = Institution.query.filter_by(code=current_user.institution_code).first().id
    
    
    if request.method == 'POST':
        collection = request.form.get('collection')
        code = request.form.get('code')

        if len(collection) < 1:
            flash('Name is too short!', category='error')
        else:
            new_collection = Collection(name = collection, code = code, institution_id=institutionid)
            db.session.add(new_collection)
            db.session.commit()
            flash('Collection added!', category='success')

    

    institution = Institution.query.filter_by(id=institutionid).first()
    collections = Collection.query.filter_by(institution_id = institutionid).all()

    return render_template("collections.html", user=current_user, institution=institution, collections=collections)