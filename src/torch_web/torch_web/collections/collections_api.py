import json
import click
import os
import uuid

from apiflask import APIBlueprint, Schema
from apiflask.fields import Integer, String, List, Nested, DateTime
from flask import request, current_app, jsonify, make_response, redirect
from flask_security import current_user
from torch_web.collections import collections
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Prompt
from torch_web.prefect_flows.blocks.upload_credentials import UploadCredentials
from torch_web.workflows.workflows import TorchTask
from azure.storage.blob import BlobServiceClient
from prefect import context


home_bp = APIBlueprint("home", __name__, url_prefix="")
collections_bp = APIBlueprint("collections", __name__, url_prefix="/collections")
specimens_bp = APIBlueprint("specimens", __name__)


class SpecimenImageResponse(Schema):
    id = Integer()
    external_url = String(nullable=True)
    url = String(nullable=True)
    size = String()


class SpecimenResponse(Schema):
    id = Integer()
    create_date = DateTime(timezone=True)
    collection_id = Integer()
    collection_name = String()
    collection_code = String(nullable=True)
    catalog_number = String(nullable=True)
    card_image = Nested(SpecimenImageResponse, nullable=True)
    images = List(Nested(SpecimenImageResponse))
    tasks = List(Nested(TorchTask))
    

class SpecimensResponse(Schema):
    count = Integer()
    specimens = List(Nested(SpecimenResponse))


class AddCollectionRequest(Schema):
    name = String()
    code = String()


class CollectionResponse(Schema):
    id = Integer()
    name = String()
    code = String()
    deleted_date = DateTime(timezone=True, nullable=True)
    cardimg = List(Nested(SpecimenImageResponse))
    specimencount = Integer()
    tasks = List(Nested(TorchTask))


class CollectionsResponse(Schema):
    collections = List(Nested(CollectionResponse))



@home_bp.route("/")
def home():
    app_url = os.environ.get('APP_URL')
    response = redirect(app_url)
    session_cookie = request.cookies.get('session')
    if session_cookie is not None:
        if app_url.startswith('https'):
            response.set_cookie('session', value=session_cookie, samesite='None', secure=True)
        else:
            response.set_cookie('session', value=session_cookie, samesite='Strict')
    
    return response


@collections_bp.get("/")
@collections_bp.output(CollectionsResponse)
@collections_bp.doc(operation_id='GetCollections')
def collections_get():
    result = collections.get_collections(current_user.institution_id)
    return {
        "collections": result
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
@collections_bp.input(AddCollectionRequest)
@collections_bp.output(CollectionResponse)
@collections_bp.doc(operation_id='AddCollection')
def collections_post(data):
    print(data)
    new_collection = collections.create_collection(
        institutionid = current_user.institution_id,
        name=data['name'],
        code=data['code']
    )

    return new_collection


@collections_bp.cli.command("create")
@click.argument("institutionid")
@click.argument("name")
@click.argument("code")
def collections_cli_create(institutionid, name, code):
    console = Console()
    default_prefix = console.input('Enter the [bold cyan]default prefix[/bold cyan] for specimen files: ')
    catalog_number_regex = console.input('Enter the [bold cyan]regular expression to obtain the catalog number[/bold cyan] from your specimen files: ')
    collection_folder = console.input('Enter the [bold cyan]path to the folder[/bold cyan] where your specimen files should be uploaded: ')
    
    new_collection = collections.create_collection(
        institutionid = institutionid,
        collection_id=None,
        flow_id=None,
        project_ids=None,
        name=name,
        code=code,
        default_prefix=default_prefix,
        catalog_number_regex=catalog_number_regex,
        collection_folder=collection_folder,
        workflow='process_specimen'
    )
    Console().print(f'Collection [bold cyan]{name}[/bold cyan] created! ID is [bold magenta]{new_collection.id}[/bold magenta].')


@collections_bp.cli.command("update-credentials")
@click.argument("id")
def collections_cli_update_credentials(id):
    console = Console()
    type = Prompt.ask('Choose the upload type: ', choices=["sftp", "s3", "minio"])
    host = console.input(f'Enter the [bold cyan]{type} host[/bold cyan]: ')
    username = console.input(f'Enter the [bold cyan]username[/bold cyan]: ')
    password = Prompt.ask(f'Enter the [bold magenta]password[/bold magenta]: ', password=True)

    credentials = UploadCredentials(
        host=host,
        type=type,
        username=username,
        password=password)

    credentials.save(name=str(id))
    console.print(f'Credentials for collection [bold cyan]{id}[/bold cyan] updated!')


class DeleteCollectionRequest(Schema):
    collection_id = Integer()    

@collections_bp.delete("/<int:collection_id>")
@collections_bp.doc(operation_id='DeleteCollection')
def collection_delete(collection_id):
    result = collections.delete_collection(collection_id)
    if not result:
        return jsonify({"status": "error", "statusText": "Impossible to delete a collection with specimens."})

    return jsonify({"status": "ok"})


@collections_bp.cli.command("delete")
@click.argument("id")
def collection_delete_cli(id):
    collections.delete_collection(id)
    Console().print(f'Collection ID [bold cyan]{id}[/bold cyan] deleted!')

    
@collections_bp.get("/<int:collectionid>")
@collections_bp.output(CollectionResponse)
@collections_bp.doc(operation_id='GetCollection')
def collection_get(collectionid):
    result = collections.get_collection(collectionid)
    return result


class GetSpecimensRequest(Schema):
    search_string = String(load_default=None)
    page = Integer()
    per_page = Integer()


@collections_bp.get("/<int:collectionid>/specimens")
@collections_bp.input(GetSpecimensRequest, location='query')
@collections_bp.output(SpecimensResponse)
@collections_bp.doc(operation_id='GetSpecimens')
def collection_specimens(collectionid, query):
    specimens = collections.get_collection_specimens(collectionid, query["search_string"], False, query["page"], query["per_page"])

    return {
        'specimens': specimens,
        'count': 0
    }


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
@collections_bp.output({}, status_code=202)
def upload(collectionid):
    files = request.files.getlist("file")
    batch_id = str(uuid.uuid4())
    blob_service_client = BlobServiceClient.from_connection_string(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"))
    
    for file in files:
        filename = str(collectionid) + '/uploads/' + batch_id + '/' + file.filename
        blob_client = blob_service_client.get_blob_client(container='torchhub', blob=filename)
        blob_client.upload_blob(file, overwrite=True)
        collections.upload(collectionid, [blob_client.url])
    return ''


@specimens_bp.cli.command("process")
@click.argument('collection_id')
@click.argument('path')
def process_local(collection_id, path):
    if os.path.isdir(path):
        files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    else:
        files = [path]
    
    with Progress() as progress:
        collections.upload(collection_id, files)
    


@collections_bp.get("/<int:collectionid>/specimens/<int:specimenid>")
@collections_bp.output(SpecimenResponse)
@collections_bp.doc(operation_id='GetSpecimen')
def specimen_get(collectionid, specimenid):
    collection = collections.get_collection(collectionid)
    specimen = collections.get_specimen(specimenid)

    return specimen


@collections_bp.put("/<collectionid>/specimens/<specimenid>")
def retry(collectionid, specimenid):
    return ajax_response(collections.retry_workflow(specimenid, current_app.config), specimenid)


class DeleteSpecimenRequest(Schema):
    specimen_id = Integer()


@collections_bp.delete("/<int:collectionid>/specimens/<int:specimenid>")
@collections_bp.doc(operation_id='DeleteSpecimen')
def specimen_delete(collectionid, specimenid):
    collections.delete_specimen(specimenid)
    context.socketio.emit('specimen_added')
    return ''


@specimens_bp.cli.command("delete")
@click.argument("id")
def specimen_delete_cli(id):
    collections.delete_specimen(id)
    Console().print(f'Specimen ID [bold cyan]{id}[/bold cyan] deleted!')


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
