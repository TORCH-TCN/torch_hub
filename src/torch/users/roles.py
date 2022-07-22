from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_security import roles_accepted
from torch.users.role import (
    get_roles,
    add_role,
)


roles_bp = Blueprint("roles", __name__, url_prefix="/roles")


@roles_bp.route("/", methods=["GET"])
@roles_accepted("admin")
def roles_get():
    roles = get_roles()
    return render_template("/users/roles.html", user=current_user, roles=roles)


@roles_bp.route("/", methods=["POST"])
@roles_accepted("admin")
def roles_post():
    add_role(request.form.get("name"), request.form.get("description"))
    return roles_get()
