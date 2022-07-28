from torch import db
from flask import Blueprint, jsonify, render_template, request, flash
from flask_security import current_user

workflow_bp = Blueprint("workflow", __name__, url_prefix="/workflows")

class WorkflowSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.String(150))
    watch_directory_path = db.Column(db.String(500))

def save_workflowsettings(id, workflow_id, watch_directory_path):
    ws = WorkflowSettings.query.get(id)
    
    ws.workflow_id = workflow_id
    ws.watch_directory_path = watch_directory_path

    db.session.commit()

@workflow_bp.route("/settings", methods=["GET"])
def workflowsettings():
    workflowsettings = WorkflowSettings.query.all()

    return render_template("/flows/index_workflow_settings.html", user = current_user, workflowsettings = workflowsettings)

@workflow_bp.route("/settings", methods=["POST"])
def post_workflowsettings():
    workflow = request.form.get("workflow_id")

    if len(workflow) < 1:
        flash("Name is too short!", category="error")
    else:
        new_workflow = WorkflowSettings(workflow_id=workflow, watch_directory_path=request.form.get("watch_directory_path"))
        db.session.add(new_workflow)
        db.session.commit()

        flash("Workflow added!", category="success")

    return workflowsettings()

@workflow_bp.route("/settings/<id>", methods=["GET"])
def workflowsetting_get(id):
    workflow = WorkflowSettings.query.get(id)

    return render_template("/flows/edit_workflow_settings.html", user = current_user, ws = workflow) 

@workflow_bp.route("/settings/<id>", methods=["POST"])
def workflowsettings_update(id):
    if request.method == "POST":
        
        save_workflowsettings(
            id,
            request.form.get("workflow_id"),
            request.form.get("watch_directory_path"),
        )

        flash("Updated successfully!", category="success")
        
    return workflowsettings()

@workflow_bp.route("/settings/<id>", methods=["DELETE"])
def delete(id):
    workflow = WorkflowSettings.query.get(id)
    print(workflow)
    print("printei")
    if workflow:
        db.session.delete(workflow)
        db.session.commit()

    return jsonify({})


    

