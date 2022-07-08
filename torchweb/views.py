import os
import json
from glob import glob
from uuid import uuid4
from flask import Blueprint, render_template, request, flash, jsonify
from flask_security import (
    current_user,
)
from collections import (
    Institution,
    Workflow,
    WorkflowFileType,
    WorkflowSettings,
)

from torch.collections.image import upload_images

views = Blueprint("views", __name__)


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


