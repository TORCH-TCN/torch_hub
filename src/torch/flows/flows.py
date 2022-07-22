from flask import Blueprint, render_template, request, flash
from flask_security import (
    current_user,
)
from torch.collections.collections import (
    Workflow,
    WorkflowFileType,
    WorkflowSettings,
)
from torch import db

flows_bp = Blueprint("flows", __name__)


# @flows_bp.route("/history", methods=["GET", "POST"])
# def history():
#     if request.method == "POST":
#         current_user.first_name = request.form.get("firstName")
#         current_user.last_name = request.form.get("lastName")
#         db.session.commit()
#         flash("Updated successfully!", category="success")

#     return render_template("history.html", user=current_user)


@flows_bp.route("/workflow-settings/<workflowid>", methods=["GET", "POST"])
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
        "/flows/settings.html",
        user=current_user,
        settings=settings,
        filetypes=filetypes,
        workflow=workflow,
        categories=categories,
    )


@flows_bp.route("/overview", methods=["GET", "POST"])
def overview():
    if request.method == "POST":
        current_user.first_name = request.form.get("firstName")
        current_user.last_name = request.form.get("lastName")
        db.session.commit()
        flash("Updated successfully!", category="success")

    return render_template("/flows/overview.html", user=current_user)
