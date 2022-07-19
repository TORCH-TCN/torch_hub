from flask import Blueprint, render_template

views = Blueprint("views", __name__)

@views.route("/",methods=["GET"])
def home():
    return render_template("/test/laura.html")