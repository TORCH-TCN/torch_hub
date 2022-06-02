import os
import json
from glob import glob
from uuid import uuid4
from flask import Blueprint, render_template, request, flash, jsonify
from flask_security import (
    login_required,
    current_user,
    roles_accepted,
    SQLAlchemyUserDatastore,
)
from collections import (
    Collection,
    Institution,
    Role,
    User,
    Workflow,
    WorkflowFileType,
    WorkflowSettings,
)

views = Blueprint("views", __name__)


@views.route("/roles", methods=["GET", "POST"])
@roles_accepted("admin")
def roles():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        new_role = Role(name=name, description=description)
        db.session.add(new_role)
        db.session.commit()
        # user_datastore
    roles = Role.query.all()
    return render_template("roles/roles.html", user=current_user, roles=roles)


@views.route("/files", methods=["GET", "POST"])
# @login_required
def files():
    if request.method == "POST":
        current_user.first_name = request.form.get("firstName")
        current_user.last_name = request.form.get("lastName")
        db.session.commit()
        flash("Updated successfully!", category="success")

    return render_template("files.html", user=current_user)


@views.route("/history", methods=["GET", "POST"])
# @login_required
def history():
    if request.method == "POST":
        current_user.first_name = request.form.get("firstName")
        current_user.last_name = request.form.get("lastName")
        db.session.commit()
        flash("Updated successfully!", category="success")

    return render_template("history.html", user=current_user)


@views.route("/workflow-settings/<workflowid>", methods=["GET", "POST"])
# @login_required
def settings(workflowid=1):
    if request.method == "POST":
        config_format = WorkflowSettings.query.filter_by(name="config_format").first()
        config_format.value = request.form.get("config_format")

        folder_increment = WorkflowSettings.query.filter_by(
            name="folder_increment"
        ).first()
        folder_increment.value = request.form.get("folder_increment")

        number_pad = WorkflowSettings.query.filter_by(name="number_pad").first()
        number_pad.value = request.form.get("number_pad")

        output_base_path = WorkflowSettings.query.filter_by(
            name="output_base_path"
        ).first()
        output_base_path.value = request.form.get("output_base_path")

        input_path = WorkflowSettings.query.filter_by(name="input_path").first()
        input_path.value = request.form.get("input_path")

        db.session.commit()

        flash("Updated successfully!", category="success")

    workflow = Workflow.query.filter_by(id=workflowid).first()
    settings = WorkflowSettings.query.filter_by(workflow_id=workflowid).all()
    filetypes = WorkflowFileType.query.filter_by(workflow_id=workflowid).all()

    categories = WorkflowSettings.query.group_by(WorkflowSettings.category)

    return render_template(
        "settings.html",
        user=current_user,
        settings=settings,
        filetypes=filetypes,
        workflow=workflow,
        categories=categories,
    )


@views.route("/overview", methods=["GET", "POST"])
# @login_required
def overview():
    if request.method == "POST":
        current_user.first_name = request.form.get("firstName")
        current_user.last_name = request.form.get("lastName")
        db.session.commit()
        flash("Updated successfully!", category="success")

    return render_template("overview.html", user=current_user)


@views.route("/history", methods=["GET", "POST"])
@views.route("/delete-institution", methods=["POST"])
def delete_institution():
    institution = json.loads(request.data)
    institutionId = institution["institutionId"]
    institution = Institution.query.get(institutionId)
    if institution:
        db.session.delete(institution)
        db.session.commit()

    return jsonify({})


@views.route("/assign-role", methods=["POST"])
@roles_accepted("admin")
def assign_role():
    data = json.loads(request.data)
    userId = data["userId"]
    role = data["role"]

    user = User.query.get(userId)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.add_role_to_user(user, role)
    db.session.commit()

    return jsonify({})


@views.route("/delete-role-user", methods=["POST"])
@roles_accepted("admin")
def delete_role_user():
    data = json.loads(request.data)
    userId = data["userId"]
    role = data["role"]

    user = User.query.get(userId)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.remove_role_from_user(user, role)
    db.session.commit()

    return jsonify({})


@views.route("/change-user-active", methods=["POST"])
@roles_accepted("admin")
def deactivate_user():
    data = json.loads(request.data)
    userId = data["userId"]

    user = User.query.get(userId)
    user.active = 0 if user.active == 1 else 1

    db.session.commit()

    return jsonify({})


@views.route("/institutions", methods=["GET", "POST"])
@login_required
def institutions():
    if request.method == "POST":
        institution = request.form.get("institution")
        code = request.form.get("code")

        if len(institution) < 1:
            flash("Name is too short!", category="error")
        else:
            new_institution = Institution(name=institution, code=code)
            db.session.add(new_institution)
            db.session.commit()
            flash("Institution added!", category="success")

    institutions = Institution.query.all()

    return render_template(
        "institutions.html", user=current_user, institutions=institutions
    )


@views.route("/", methods=["GET", "POST"])
@views.route("collections/<institutionid>", methods=["GET", "POST"])
@login_required
def collections(institutionid=None):

    if current_user.has_role("admin") and institutionid == None:
        institutionid = 1

    if institutionid == None:
        institutionid = (
            Institution.query.filter_by(code=current_user.institution_code).first().id
        )

    if request.method == "POST":
        collection = request.form.get("collection")
        code = request.form.get("code")

        if len(collection) < 1:
            flash("Name is too short!", category="error")
        else:
            new_collection = Collection(
                name=collection, code=code, institution_id=institutionid
            )
            db.session.add(new_collection)
            db.session.commit()
            flash("Collection added!", category="success")

    institution = Institution.query.filter_by(id=institutionid).first()
    collections = Collection.query.filter_by(institution_id=institutionid).all()

    return render_template(
        "collections.html",
        user=current_user,
        institution=institution,
        collections=collections,
    )


@views.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = "webapp/static/uploads/{}".format(upload_key)
    try:
        os.mkdir(target)
    except:
        if is_ajax:
            return ajax_response(
                False, "Couldn't create upload directory: {}".format(target)
            )
        else:
            return "Couldn't create upload directory: {}".format(target)

    print("=== Form Data ===")
    for key, value in list(form.items()):
        print(key, "=>", value)

    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        flash("Upload completed!", category="success")


@views.route("/files/<uuid>")
def upload_complete(uuid):

    # Get their files.
    root = "webapp/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)

    return render_template(
        "files.html",
        uuid=uuid,
        files=files,
    )


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(
        dict(
            status=status_code,
            msg=msg,
        )
    )
