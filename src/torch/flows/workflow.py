from torch import db
from flask import Blueprint, render_template, request, flash
from flask_security import current_user

workflow_bp = Blueprint("workflow", __name__, url_prefix="/workflows")

class WorkflowSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.String(150))
    watch_directory_path = db.Column(db.String(500))

@workflow_bp.route("/settings", methods=["GET"])
def workflowsettings():
    workflowsettings = WorkflowSettings.query.all()

    return render_template("/flows/index_workflow_settings.html", user = current_user, workflowsettings = workflowsettings)

# @workflow_bp.route("/", methods=["POST"])
# def post_workflowsettings():
#     institution = request.form.get("institution")

#     if len(institution) < 1:
#         flash("Name is too short!", category="error")
#     else:
#         new_institution = Institution(name=institution, code=request.form.get("code"))
#         db.session.add(new_institution)
#         db.session.commit()

#         flash("Institution added!", category="success")

#     return institutions()

# @workflow_bp.route("/workflow-settings/<workflowid>", methods=["GET", "POST"])    
# def workflow():
    

