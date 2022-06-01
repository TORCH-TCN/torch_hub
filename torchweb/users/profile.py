from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required

from torch.collections.user import get_user, save_user


users = Blueprint("users", __name__, url_prefix="/users")


@users.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        save_user(current_user.id, request.form["firstName"], request.form["lastName"])
        flash("Updated successfully!", category="success")

    return render_template("profile.html", user=get_user(current_user.id))
