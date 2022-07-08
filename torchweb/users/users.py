import json
from flask import Blueprint, flash, jsonify, redirect, render_template, request
from flask_login import current_user, login_required
from flask_security import roles_accepted
from torch.collections.entities import Institution
from flask_sqlalchemy import orm
from torch.collections.role import (
    assign_role_to_user,
    get_roles,
    add_role,
    unassign_role_from_user,
)
from torch.collections.user import User, get_user, save_user, toggle_user_active


users = Blueprint("users", __name__, url_prefix="/users")


@users.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        save_user(
            current_user.id, request.form.get("firstName"), request.form.get("lastName")
        )
        flash("Updated successfully!", category="success")

    return render_template("profile.html", user=get_user(current_user.id))


@users.route("/edit/<userid>", methods=["GET", "POST"])
@roles_accepted("admin")
def edit(userid):

    institutions = Institution.query.all()
    user = get_user(userid)

    if request.method == "POST":
        save_user(
            userid,
            request.form.get("firstName"),
            request.form.get("lastName"),
            request.form.get("institutionid"),
        )
        flash("User updated", category="success")
        return redirect("/users")

    return render_template(
        "edit.html", user=current_user, edituser=user, institutions=institutions
    )


@users.route("/", methods=["GET"])
@roles_accepted("admin")
def users():
    users = User.query.options(orm.joinedload("roles"))
    roles = get_roles()
    return render_template("users.html", user=current_user, users=users, roles=roles)


@users.route("/change-user-active", methods=["POST"])
@roles_accepted("admin")
def deactivate_user():
    data = json.loads(request.data)
    toggle_user_active(data["userId"])
    return jsonify({})


@users.route("/modal/<userid>")
def modal(userid=None):
    return render_template("addrolemodal.html", user=current_user, userid=userid)


@users.route("/roles", methods=["GET", "POST"])
@roles_accepted("admin")
def roles():
    if request.method == "POST":
        add_role(request.form.get("name"), request.form.get("description"))

    roles = get_roles()
    return render_template("roles.html", user=current_user, roles=roles)


@users.route("/assign-role", methods=["POST"])
@roles_accepted("admin")
def assign_role():
    data = json.loads(request.data)
    assign_role_to_user(data["userId"], data["role"])
    return jsonify({})


@users.route("/delete-role-user", methods=["POST"])
@roles_accepted("admin")
def delete_role_user():
    data = json.loads(request.data)
    unassign_role_from_user(data["userId"], data["role"])
    return jsonify({})
