from flask import Blueprint, render_template, request
from flask_security import current_user, roles_accepted
from torch_web.users import user, role


roles_bp = Blueprint("roles", __name__, url_prefix="/roles")


@roles_bp.get("/")
@roles_accepted("admin")
def roles_get():
    roles = role.get_roles()
    return render_template("/users/roles.html", user=current_user, roles=roles)


@roles_bp.post("/")
@roles_accepted("admin")
def roles_post():
    role.add_role(request.form.get("name"), request.form.get("description"))
    return role.roles_get()
