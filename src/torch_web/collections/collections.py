import csv
import io
import json
import os
from operator import or_
from typing import List

import sqlalchemy as sa
from flask import Blueprint, flash, redirect, render_template, request, current_app, jsonify, make_response
from flask_security import current_user
from sqlalchemy import Column, Integer, String, ForeignKey, func, Text
from sqlalchemy.orm import joinedload
from werkzeug.datastructures import FileStorage

from torch.collections.specimens import Specimen, SpecimenImage
from torch.collections.workflow import run_workflow
from torch.institutions.institutions import Institution

ORION_URL_DEFAULT = "http://127.0.0.1:4200/"

home_bp = Blueprint("home", __name__)
collections_bp = Blueprint("collections", __name__, url_prefix="/collections")


@home_bp.route("/", methods=["GET"])
def home():
    print("home collections")
    return redirect("/collections")


@collections_bp.route("/settings")
def collections_settings():
    return render_template("/collections/settings.html", user=current_user)


@collections_bp.route("/", methods=["GET"])
def collections():
    institution = get_default_institution()

    return render_template(
        "/collections/all_collections.html",
        user=current_user,
        institution=institution
    )


@collections_bp.route("/search", methods=["GET"])
def collections_search():
    result = get_collections()
    return json.dumps(result, indent=4, sort_keys=True, default=str)


@collections_bp.route("/", methods=["POST"])
def collections_post():
    j_collection = request.get_json()
    new_collection = create_collection(
        collection_id=j_collection.get('id', None),
        name=newname,
        code=j_collection.get('code', None),
        default_prefix=j_collection.get('default_prefix', None),
        catalog_number_regex=j_collection.get('catalog_number_regex', None),
        flow_id=j_collection.get('flow_id', None),
        workflow=j_collection.get('workflow', 'process_specimen'),  # todo select with workflow options
        collection_folder=j_collection.get('collection_folder', None),
        project_ids=j_collection.get('project_ids', None)
    )

    return jsonify({"collectionid": new_collection.id})


@collections_bp.route("/<collectioncode>", methods=["GET"])
def collection_get(collectioncode):
    return render_template("/collections/specimens.html", collection=get_collection(collectioncode))


@collections_bp.route("/specimens/<collectionid>", methods=["GET"])
def collection_specimens(collectionid):
    search_string = request.args.get('search_string')
    only_error = request.args.get('only_error')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 14, type=int)
    specimens = get_collection_specimens(collectionid, search_string, only_error, page, per_page)

    return {'specimens': json.dumps(specimens, indent=4, sort_keys=True, default=str),
            'total_specimens': specimens.count()}


@collections_bp.route("/specimen/retry/<specimenid>", methods=["POST"])
def retry(specimenid):
    return ajax_response(retry_workflow(specimenid), specimenid)


@collections_bp.route("/<collectionid>", methods=["POST"])
def upload(collectionid):
    files = request.files.getlist("file")
    result = upload(collectionid, files, current_app.config)
    return ajax_response(result, "")


@collections_bp.route("/<collectionid>/settings", methods=["GET", "POST"])
def settings(collectionid="default"):
    return render_template("/collections/settings.html", user=current_user, collectionid=collectionid)


@collections_bp.route("/<collectioncode>/<specimenid>", methods=["GET"])
def specimen_get(collectioncode, specimenid):
    collection = get_collection(collectioncode)
    specimen = get_specimen(specimenid)
    orion_url = current_app.config.get("PREFECT_ORION_URL", ORION_URL_DEFAULT)
    prefect_url = orion_url + "flow-run/" + specimen.flow_run_id

    return render_template("/collections/specimen.html",
                           collection=collection, specimen=specimen, prefect_url=prefect_url)


@collections_bp.route("/<collection_id>", methods=["DELETE"])
def collection_delete(collection_id):
    result = delete_collection(collection_id)
    if not result:
        return jsonify({"status": "error", "statusText": "Impossible to delete a collection with specimens."})

    return jsonify({"status": "ok"})


@collections_bp.route("specimen/<specimen_id>", methods=["DELETE"])
def specimen_delete(specimen_id):
    delete_specimen(specimen_id)
    return jsonify({"status": "ok"})


@collections_bp.route("/transferred-specimens/<collectionid>", methods=["DELETE"])
def specimen_delete_transferred(collectionid):
    delete_transfered_specimens(collectionid)
    return jsonify({"status": "ok"})


@collections_bp.route('/export-csv/<collectionid>', methods=['GET'])
def collection_export_csv(collectionid):
    output = make_response(export_csv(collectionid))
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(
        dict(
            status=status_code,
            msg=msg,
        )
    )
