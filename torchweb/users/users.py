from flask import Blueprint, flash, redirect, render_template, request
from flask_login import current_user, login_required
from flask_security import roles_accepted
from torch.collections.entities import Institution, Role
from flask_sqlalchemy import orm
from torch.collections.user import User, get_user, save_user


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
    roles = Role.query.all()
    return render_template("users.html", user=current_user, users=users, roles=roles)


@users.route("/modal/<userid>")
def modal(userid=None):
    return render_template("addrolemodal.html", user=current_user, userid=userid)
