import json
from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user
from flask_security import RegisterForm, roles_accepted
from flask_sqlalchemy import orm
from wtforms import StringField
from torch import db
from torch.users.user import User
from torch.users.role import (
    assign_role_to_user,
    get_roles,
    unassign_role_from_user,
)
from torch.users.user import User, get_user, save_user, toggle_user_active


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    institution_code = StringField("Institution Code")


users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
@roles_accepted("admin")
def users():
    users = User.query.options(orm.joinedload("roles"))
    roles = get_roles()
    return render_template("/users/users.html", user=current_user, users=users, roles=roles)


@users_bp.route("/<userid>", methods=["GET"])
def users_get(userid):
    return render_template("/users/profile.html", user=get_user(userid))


@users_bp.route("/<userid>", methods=["POST"])
def users_post(userid):
    if request.method == "POST":
        
        save_user(
            userid,
            request.form.get("firstName"),
            request.form.get("lastName"),
            request.form.get("institutionid")
        )

        flash("Updated successfully!", category="success")

    return users_get(userid)


@users_bp.route("/<userid>/active", methods=["POST"])
@roles_accepted("admin")
def deactivate_user(userid):
    toggle_user_active(userid)
    return jsonify({})


@users_bp.route("/<userid>/roles", methods=["GET"])
def user_add_role(userid):
    return render_template("addrolemodal.html", user=current_user, userid=userid)


@users_bp.route("/<userid>/roles", methods=["POST"])
@roles_accepted("admin")
def assign_role(userid):
    data = json.loads(request.data)
    assign_role_to_user(data["userId"], data["role"])
    return jsonify({})


@users_bp.route("/<userid>/roles", methods=["DELETE"])
@roles_accepted("admin")
def delete_role_user(userid):
    data = json.loads(request.data)
    print(data)
    unassign_role_from_user(data["userId"], data["role"])
    return jsonify({})
