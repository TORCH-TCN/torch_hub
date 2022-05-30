from . import db
from sqlalchemy.sql import func
from flask_security import RoleMixin, UserMixin

class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    code = db.Column(db.String(10), unique=True)
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    users = db.relationship('User')
    collections = db.relationship('Collection')
    
roles_users = db.Table('roles_users',
    db.Column('user_id',db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id',db.Integer, db.ForeignKey('role.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    institution_code = db.Column(db.String(10))
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role',secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    code = db.Column(db.String(10), unique=True)
    catalog_number_regex = db.Column(db.String(150))
    web_base = db.Column(db.String(150))
    url_base = db.Column(db.String(150))
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    workflows = db.relationship('Workflow')

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

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    uploaded_date = db.Column(db.DateTime(timezone=True), default=func.now())
    med_image_url = db.Column(db.Text) #possible change this to string?
    thumbnail_url = db.Column(db.Text)
    barcode = db.Column(db.String(20))
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    catalog_number = db.Column(db.String(150))

# class RunHistory(db.Model): #this should be general or by file?
#     id = db.Column(db.Integer, primary_key=True)
#     start_date = db.Column(db.DateTime(timezone=True), default=func.now())
#     end_date = db.Column(db.DateTime(timezone=True))
#     workflow_id = db.Column(db.Integer,db.ForeignKey('workflow.id'))