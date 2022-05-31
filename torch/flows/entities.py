from . import db


class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    tasks = db.relationship('Task')
    settings = db.relationship('WorkflowSettings')


class WorkflowSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    category = db.Column(db.String(150))
    label = db.Column(db.String(150))
    name = db.Column(db.String(150))
    value = db.Column(db.String(150))


class WorkflowFileType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
    category = db.Column(db.String(150))
    label = db.Column(db.String(150))
    name = db.Column(db.String(150))
    file_regex = db.Column(db.String(150))
    output_sub_path = db.Column(db.String(150))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    plugin_name = db.Column(db.String(150))
    sort_order = db.Column(db.Integer)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))
