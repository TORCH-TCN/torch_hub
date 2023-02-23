from urllib import request

from apiflask import APIBlueprint
from flask import request, jsonify

import socketio

notifications_bp = APIBlueprint("notificationshub", __name__, url_prefix="/notificationshub")


@notifications_bp.route("/", methods=["POST"])
def notificationshub():
    data = request.get_json()
    print(data)
    socketio.emit('notify', data)
    return jsonify({"response": "ok"})
