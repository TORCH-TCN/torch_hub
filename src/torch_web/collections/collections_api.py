import json
from pathlib import Path
import click
import os

from flask import Blueprint, request, current_app, jsonify, make_response
from flask_security import current_user
from torch_web.collections import collections
from rich.console import Console
from rich.table import Table
from rich.progress import Progress


ORION_URL_DEFAULT = "http://127.0.0.1:4200/"

home_bp = Blueprint("home", __name__)
collections_bp = Blueprint("collections", __name__, url_prefix="/collections")
specimens_bp = Blueprint("specimens", __name__)

@collections_bp.get("/")
def collections_get():
    result = collections.get_collections(current_user.institution_id)
    
    return { 
        'collections': result
    }  


@collections_bp.cli.command("list")
@click.argument('institution_id')
def list_collections(institution_id):
    result = collections.get_collections(institution_id)
    table = Table(title="Current Collections")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Code", style="green")
    table.add_column("Default Workflow", style="orange3")

    for i in result:
        table.add_row(str(i["id"]), i["name"], i["code"], i["workflow"])

    Console().print(table)
    

@collections_bp.post("/")
def collections_post():
    j_collection = request.get_json()
    new_collection = collections.create_collection(
        institutionid = current_user.institution_id,
        collection_id=j_collection.get('id', None),
        name=j_collection.get('name'),
        code=j_collection.get('code', None),
        default_prefix=j_collection.get('default_prefix', None),
        catalog_number_regex=j_collection.get('catalog_number_regex', None),
        flow_id=j_collection.get('flow_id', None),
        workflow=j_collection.get('workflow', 'process_specimen'),  # todo select with workflow options
        collection_folder=j_collection.get('collection_folder', None),
        project_ids=j_collection.get('project_ids', None)
    )

    return jsonify({"collectionid": new_collection.id})


@collections_bp.delete("/<collection_id>")
def collection_delete(collection_id):
    result = collections.delete_collection(collection_id)
    if not result:
        return jsonify({"status": "error", "statusText": "Impossible to delete a collection with specimens."})

    return jsonify({"status": "ok"})


@collections_bp.get("/<collectionid>/specimens")
def collection_specimens(collectionid):
    search_string = request.args.get('search_string')
    only_error = request.args.get('only_error')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 14, type=int)
    specimens = collections.get_collection_specimens(collectionid, search_string, only_error, page, per_page)

    return {'specimens': json.dumps(specimens, indent=4, sort_keys=True, default=str),
            'total_specimens': specimens.count()}


@specimens_bp.cli.command("list")
@click.argument('collection_id')
@click.option('-s', '--search_string')
@click.option('-t', '--take', default=50)
def list_collections(collection_id, search_string, take):
    result = collections.get_collection_specimens(collection_id, search_string, False, 1, take)
    table = Table(title="Collection Specimens")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Catalog Num", style="green")
    table.add_column("Processing State", style="orange3")

    for i in result:
        table.add_row(str(i["id"]), i["name"], i["catalog_number"], i["flow_run_state"] + (" (" + i["failed_task"] + ")" if i["failed_task"] else ""))

    Console().print(table)


@collections_bp.post("/<collectionid>/specimens")
def upload(collectionid):
    files = request.files.getlist("file")
    for file in files:
        target_dir = os.path.join(config['BASE_DIR'], "static", "uploads", collection.collection_folder)
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        file = secure_filename(file.filename)
        destination = os.path.join(target_dir, filename)
        file.save(destination)

    result = collections.upload(collectionid, files, current_app.config)
    return ajax_response(result, "")


@specimens_bp.cli.command("process")
@click.argument('collection_id')
@click.argument('path')
def process_local(collection_id, path):
    if os.path.isdir(path):
        files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    else:
        files = [path]
    
    with Progress() as progress:
        collections.upload(collection_id, files, current_app.config, progress)
    


@collections_bp.get("/<collectionid>/specimens/<specimenid>")
def specimen_get(collectionid, specimenid):
    collection = collections.get_collection(collectionid)
    specimen = collections.get_specimen(specimenid)
    orion_url = current_app.config.get("PREFECT_ORION_URL", ORION_URL_DEFAULT)
    prefect_url = orion_url + "flow-run/" + specimen.flow_run_id

    return {
        'specimen': specimen,
        'collection': collection,
        'prefect_url': prefect_url
    }


@collections_bp.put("/<collectionid>/specimens/<specimenid>")
def retry(collectionid, specimenid):
    return ajax_response(collections.retry_workflow(specimenid, current_app.config), specimenid)


@collections_bp.delete("/<collectionid>/specimens/<specimenid>")
def specimen_delete(collectionid, specimenid):
    collections.delete_specimen(specimenid)
    return jsonify({"status": "ok"})


@collections_bp.get('/<collectionid>/csv')
def collection_export_csv(collectionid):
    output = make_response(collections.export_csv(collectionid))
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
