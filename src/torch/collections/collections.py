import json
import os
from uuid import uuid4
from flask import Blueprint, flash, redirect, render_template, request, current_app, jsonify
from flask_security import current_user, login_required
from sqlalchemy import Column, Integer, String, ForeignKey, func
from torch import db, Base
from torch.collections.specimens import Specimen, SpecimenImage
from torch.institutions.institutions import Institution
from werkzeug.utils import secure_filename
from prefect.client import get_client
from prefect.orion.schemas.filters import FlowFilter, FlowRunFilter, FlowRunFilterId
from torch.tasks.process_specimen import process_specimen
import asyncio

class Collection(Base):
    __tablename__ = "collection"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    catalog_number_regex = Column(String(150))
    web_base = Column(String(150))
    url_base = Column(String(150))
    institution_id = Column(Integer, ForeignKey("institution.id"))
    flow_id = Column(String(150))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def add_specimens(self, files, config) -> Specimen:
        batch_id = str(uuid4())
        target_dir = os.path.join("src","torch","static","uploads", batch_id)
        os.makedirs(target_dir)

        for file in files:
            filename = secure_filename(file.filename)
            destination = os.path.join(target_dir, filename)
            
            file.save(destination)

            specimen = Specimen(
                name=file.filename, upload_path=destination, collection_id=self.id
            )

            # db.session.add(specimen)
            # db.session.commit()

            asyncio.run(process_specimen(specimen, config))


home_bp = Blueprint("home", __name__)
collections_bp = Blueprint("collections", __name__, url_prefix="/collections")


def get_default_institution():
    return db.session.query(Institution).first()


@home_bp.route("/", methods=["GET"])
def home():
    print("home collections")
    return redirect("/collections")

@collections_bp.route("/settings")
def collections_settings():
    return render_template("/collections/settings.html",user=current_user)

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
    institution = get_default_institution()
    
    collections = (
        db.session.query(Collection).filter_by(institution_id=institution.id).all()
    )
    
    return json.dumps([ob.as_dict() for ob in collections],indent=4, sort_keys=True, default=str)


@collections_bp.route("/", methods=["POST"])
def collectionspost():
    institution = get_default_institution()
    
    jcollection = request.get_json()
    newname = jcollection['name']
    newcode = jcollection['code']

    if len(newname) < 1:
        flash("Name is too short!", category="error")
    else:
        new_collection = Collection(
            name=newname,
            code=newcode,
            institution_id=institution.id,
        )
       
        db.session.add(new_collection)
        db.session.commit()

        # flash("Collection added!", category="success")

    return jsonify({"collectionid": new_collection.id})


@collections_bp.route("/<collectioncode>", methods=["GET"])
def collection(collectioncode):
    collection = db.session.query(Collection).filter(func.lower(Collection.code) == func.lower(collectioncode)).first()
    return render_template("/collections/specimens.html", collection=collection)

@collections_bp.route("/specimens/<collectionid>", methods=["GET"])
def collection_specimens(collectionid):
    specimens = db.session.query(Specimen).filter(Specimen.collection_id == collectionid).all() #todo filter by status (?)
    
    return json.dumps([ob.as_dict() for ob in specimens],indent=4, sort_keys=True, default=str)



@collections_bp.route("/<collectionid>", methods=["POST"])
def upload(collectionid):
    collection = db.session.query(Collection).filter_by(code=collectionid).first()
    files = request.files.getlist("file")
    batch_id = collection.add_specimens(files, current_app.config)

    return ajax_response(True, batch_id)


@collections_bp.route("/<collectionid>/settings", methods=["GET", "POST"])
def settings(collectionid="default"):
    return render_template("/collections/settings.html", user=current_user)


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(
        dict(
            status=status_code,
            msg=msg,
        )
    )

@collections_bp.route("/<collectioncode>/<specimenid>", methods=["GET"])
async def specimen(collectioncode, specimenid):
    collection = db.session.query(Collection).filter(func.lower(Collection.code) == func.lower(collectioncode)).first()
    specimen = db.session.query(Specimen).filter(Specimen.id == specimenid).first()
    images = db.session.query(SpecimenImage).filter(SpecimenImage.specimen_id == specimenid).all()
    
    # prefect errors and flows
    url = get_client().api_url

    async with get_client() as client:
        response = await client.hello()
        flow = await client.read_flow_run(specimen.flow_run_id)
        # filter = FlowRunFilter(id=specimen.flow_run_id)
        # tasks = await client.read_task_runs(flow_run_filter={id:specimen.flow_run_id})
        print(response.json())

    

    return render_template("/collections/specimen.html", collection=collection, specimen=specimen, images=images)
    