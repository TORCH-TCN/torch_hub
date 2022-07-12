import json
from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user
from flask_security import roles_accepted
from flask_sqlalchemy import orm
from torch.collections.role import (
    assign_role_to_user,
    get_roles,
    unassign_role_from_user,
)
from torch.collections.user import User, get_user, save_user, toggle_user_active


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    institution_code = StringField("Institution Code")


users = Blueprint("users", __name__, url_prefix="/users")


@users.route("/", methods=["GET"])
@roles_accepted("admin")
def users():
    users = User.query.options(orm.joinedload("roles"))
    roles = get_roles()
    return render_template("users.html", user=current_user, users=users, roles=roles)


@users.route("/<userid>", methods=["GET"])
def users_get():
    return render_template("profile.html", user=get_user(current_user.id))


@users.route("/<userid>", methods=["POST"])
def users_post(userid):
    if request.method == "POST":
        save_user(
            userid,
            request.form.get("firstName"),
            request.form.get("lastName"),
            request.form.get("institutionid"),
        )
        flash("Updated successfully!", category="success")

    return users_get()


@users.route("/<userid>/active", methods=["POST"])
@roles_accepted("admin")
def deactivate_user(userid):
    toggle_user_active(userid)
    return jsonify({})


@users.route("/<userid>/roles", methods=["GET"])
def user_add_role(userid):
    return render_template("addrolemodal.html", user=current_user, userid=userid)


@users.route("/<userid>/roles", methods=["POST"])
@roles_accepted("admin")
def assign_role():
    data = json.loads(request.data)
    assign_role_to_user(data["userId"], data["role"])
    return jsonify({})


@users.route("/<userid>/roles", methods=["DELETE"])
@roles_accepted("admin")
def delete_role_user():
    data = json.loads(request.data)
    unassign_role_from_user(data["userId"], data["role"])
    return jsonify({})
