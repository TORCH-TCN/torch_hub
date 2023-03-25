import json
from apiflask import APIBlueprint
from flask import flash, jsonify, render_template, request, redirect, abort
from flask_security import current_user, RegisterForm, roles_accepted
from wtforms import StringField
from torch_web.users import user, role


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")


users_bp = APIBlueprint("users", __name__, url_prefix="/users")
auth_bp = APIBlueprint("auth", __name__, url_prefix="/_auth")


@auth_bp.get("/login")
def login():
    return redirect("/login")


@auth_bp.get("/logout")
def logout():
    return redirect("/logout")


@auth_bp.get("/userinfo")
def userinfo():
    if not current_user.is_authenticated:
        abort(401, description="Not logged in.")
    
    return {
        "Id": str(current_user.id),
        "UserName": current_user.email
    }


@users_bp.get("/")
@roles_accepted("admin")
def users_getall():
    users = user.get_users(current_user.institution_id)
    roles = role.get_roles()
    return render_template(
        "/users/users.html", user=current_user, users=users, roles=roles
    )


@users_bp.get("/<userid>")
def users_get(userid):
    return render_template("/users/profile.html", user=user.get_user(userid))


@users_bp.post("/<userid>")
def users_post(userid):
    if request.method == "POST":

        user.save_user(
            userid,
            request.form.get("firstName"),
            request.form.get("lastName"),
            request.form.get("institutionid"),
        )

        flash("Updated successfully!", category="success")

    return users_get(userid)


@users_bp.post("/<userid>/active")
@roles_accepted("admin")
def deactivate_user(userid):
    user.toggle_user_active(userid)
    return jsonify({})


@users_bp.get("/<userid>/roles")
def user_add_role(userid):
    return render_template("addrolemodal.html", user=current_user, userid=userid)


@users_bp.post("/<userid>/roles")
@roles_accepted("admin")
def assign_role(userid):
    data = json.loads(request.data)
    user.assign_role_to_user(userid, data["role"])
    return jsonify({})


@users_bp.delete("/<userid>/roles")
@roles_accepted("admin")
def delete_role_user(userid):
    data = json.loads(request.data)
    print(data)
    user.unassign_role_from_user(userid, data["role"])
    return jsonify({})
