from urllib import request

from flask import Blueprint, request, jsonify

from torch import socketio

notifications_bp = Blueprint("notificationshub", __name__, url_prefix="/notificationshub")


@notifications_bp.route("/", methods=["POST"])
def notificationshub():
    data = request.get_json()
    print(data)
    socketio.emit('notify', data)
    return jsonify({"response": "ok"})
